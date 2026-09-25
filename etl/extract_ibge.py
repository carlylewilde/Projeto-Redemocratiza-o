"""Extrator genérico para tabelas do SIDRA/IBGE."""
from __future__ import annotations
import logging, re
import pandas as pd
from etl.common import build_session, cache_path, read_cache, request_json, save_cache, standardize
LOGGER=logging.getLogger(__name__); BASE_URL="https://apisidra.ibge.gov.br/values"

def _sidra_period_to_date(code: str, frequency: str) -> pd.Timestamp:
    digits=re.sub(r"\D","",str(code))
    if len(digits)<6: return pd.NaT
    year,slot=int(digits[:4]),int(digits[4:6])
    if frequency=="quarterly":
        month=min(max(slot,1),4)*3
        return pd.Timestamp(year=year,month=month,day=1)+pd.offsets.MonthEnd(0)
    month=min(max(slot,1),12)
    return pd.Timestamp(year=year,month=month,day=1)+pd.offsets.MonthEnd(0)

def extract_sidra_table(table_id:int, indicator:str, start:str, end:str, *, unit:str, frequency:str, variable:str="allxp", variable_name_contains:str|None=None, classification_value_contains:str|None=None, territorial_path:str="n1/all", extra_path:str="", force:bool=False)->pd.DataFrame:
    path=cache_path("ibge",indicator)
    if path.exists() and not force:
        cached=read_cache(path,start,end)
        if cached is not None and not cached.empty: return cached
    url=f"{BASE_URL}/t/{table_id}/{territorial_path}/v/{variable}/p/all"
    if extra_path: url+="/"+extra_path.strip("/")
    payload=request_json(build_session(),url,params={"formato":"json"})
    if not payload: return standardize(pd.DataFrame(columns=["data","valor"]),source=f"IBGE/SIDRA/{table_id}",unit=unit,indicator=indicator)
    df=pd.DataFrame(payload[1:] if len(payload)>1 else payload)
    def find_col(*cands):
        for c in df.columns:
            n=str(c).lower()
            if any(x.lower()==n for x in cands): return c
        for c in df.columns:
            n=str(c).lower()
            if any(x.lower() in n for x in cands): return c
        return None
    period_col=find_col("D3C","Período (Código)","periodo codigo") or next((c for c in df if str(c).endswith("C") and df[c].astype(str).str.match(r"\d{6}").mean()>.8),None)
    value_col=find_col("V","Valor"); var_name_col=find_col("D2N","Variável")
    if variable_name_contains and var_name_col: df=df[df[var_name_col].astype(str).str.contains(variable_name_contains,case=False,na=False)]
    if classification_value_contains:
        text_cols=[c for c in df.columns if str(c).endswith("N") or df[c].dtype==object]
        mask=pd.Series(False,index=df.index)
        for c in text_cols: mask|=df[c].astype(str).str.contains(classification_value_contains,case=False,na=False)
        df=df[mask]
    if period_col is None or value_col is None: raise ValueError(f"Não foi possível identificar período/valor na tabela SIDRA {table_id}. Colunas: {list(df.columns)}")
    parsed=pd.DataFrame({"data":df[period_col].map(lambda x:_sidra_period_to_date(x,frequency)),"valor":pd.to_numeric(df[value_col].astype(str).str.replace("...","",regex=False).str.replace("-","",regex=False).str.replace(",",".",regex=False),errors="coerce")})
    out=standardize(parsed,source=f"IBGE/SIDRA/{table_id}",unit=unit,indicator=indicator)
    out=out[(out["data"]>=pd.Timestamp(start))&(out["data"]<=pd.Timestamp(end))]; save_cache(out,path); return out

def extract_default_ibge(start:str,end:str,force:bool=False)->dict[str,pd.DataFrame]:
    jobs={
      "pib_real_trimestral":dict(table_id=6612,unit="índice/valor encadeado",frequency="quarterly",classification_value_contains="PIB a preços de mercado"),
      "pib_nominal_trimestral":dict(table_id=1846,unit="R$ milhões",frequency="quarterly",classification_value_contains="PIB a preços de mercado"),
      "desemprego_trimestral":dict(table_id=4099,unit="%",frequency="quarterly",variable_name_contains="Taxa de desocupação"),
      "desemprego_movel":dict(table_id=6381,unit="%",frequency="monthly",variable_name_contains="Taxa de desocupação")}
    result={}
    for indicator,kwargs in jobs.items():
        try: result[indicator]=extract_sidra_table(indicator=indicator,start=start,end=end,force=force,**kwargs)
        except Exception as exc: LOGGER.exception("Falha SIDRA em %s: %s",indicator,exc); result[indicator]=pd.DataFrame()
    return result

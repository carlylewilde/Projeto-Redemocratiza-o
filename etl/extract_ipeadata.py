"""Extração de séries longas do IpeaData via API OData."""
from __future__ import annotations
import logging, os
from functools import lru_cache
import pandas as pd
from etl.common import build_session, cache_path, read_cache, request_json, save_cache, standardize
LOGGER=logging.getLogger(__name__); ODATA="http://www.ipeadata.gov.br/api/odata4"

@lru_cache(maxsize=1)
def metadata()->pd.DataFrame:
    payload=request_json(build_session(),f"{ODATA}/Metadados")
    return pd.DataFrame(payload.get("value",payload) if isinstance(payload,dict) else payload)

def discover_series(keyword:str)->pd.DataFrame:
    meta=metadata(); text_cols=[c for c in meta.columns if any(k in c.upper() for k in ["NOME","COMENT","FONTE","UNIDADE"])]
    if not text_cols: return meta.iloc[0:0]
    mask=pd.Series(False,index=meta.index)
    for c in text_cols: mask|=meta[c].astype(str).str.contains(keyword,case=False,na=False,regex=False)
    return meta[mask].copy()

def resolve_series_code(keyword:str,env_var:str|None=None)->str:
    if env_var and os.getenv(env_var): return os.environ[env_var]
    candidates=discover_series(keyword)
    if candidates.empty: raise LookupError(f"Nenhuma série IpeaData encontrada para '{keyword}'.")
    code_col=next((c for c in candidates.columns if "SERCODIGO" in c.upper()),None); name_col=next((c for c in candidates.columns if "SERNOME" in c.upper()),None)
    if code_col is None: raise LookupError("Metadados do IpeaData não expuseram SERCODIGO.")
    if name_col: candidates=candidates.assign(_len=candidates[name_col].astype(str).str.len()).sort_values("_len")
    chosen=str(candidates.iloc[0][code_col])
    if len(candidates)>1: LOGGER.warning("IpeaData: %d séries encontradas para '%s'; usando %s. Defina %s para override.",len(candidates),keyword,chosen,env_var)
    return chosen

def extract_ipea_series(series_code:str,indicator:str,unit:str,start:str,end:str,*,force:bool=False)->pd.DataFrame:
    path=cache_path("ipeadata",indicator)
    if path.exists() and not force:
        cached=read_cache(path,start,end)
        if cached is not None and not cached.empty: return cached
    payload=request_json(build_session(),f"{ODATA}/ValoresSerie(SERCODIGO='{series_code}')")
    df=pd.DataFrame(payload.get("value",payload) if isinstance(payload,dict) else payload)
    date_col=next((c for c in df.columns if c.upper() in {"VALDATA","DATA"}),None); value_col=next((c for c in df.columns if c.upper() in {"VALVALOR","VALOR"}),None)
    if date_col is None or value_col is None: raise ValueError(f"Formato inesperado do IpeaData para {series_code}: {list(df.columns)}")
    parsed=pd.DataFrame({"data":pd.to_datetime(df[date_col],errors="coerce"),"valor":pd.to_numeric(df[value_col],errors="coerce")})
    out=standardize(parsed,source=f"IPEADATA/{series_code}",unit=unit,indicator=indicator)
    out=out[(out["data"]>=pd.Timestamp(start))&(out["data"]<=pd.Timestamp(end))]; save_cache(out,path); return out

def extract_default_ipeadata(start:str,end:str,force:bool=False)->dict[str,pd.DataFrame]:
    specs={"gini":("Gini","índice","IPEA_GINI_SERIES"),"salario_minimo_real":("salário mínimo real","R$ reais","IPEA_SALARIO_MINIMO_REAL_SERIES"),"pobreza":("pobreza","% ou pessoas","IPEA_POBREZA_SERIES")}; out={}
    for indicator,(keyword,unit,env) in specs.items():
        try: out[indicator]=extract_ipea_series(resolve_series_code(keyword,env),indicator,unit,start,end,force=force)
        except Exception as exc: LOGGER.exception("Falha IpeaData em %s: %s",indicator,exc); out[indicator]=pd.DataFrame()
    return out

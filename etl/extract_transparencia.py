"""Portal da Transparência / CGU.

A API exige token em TRANSPARENCIA_API_KEY. Para grandes volumes e séries históricas, os downloads de dados abertos são preferíveis; o módulo também agrega CSVs locais.
"""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
from etl.common import build_session, cache_path, request_json, save_cache, standardize
BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"

def extract_functional_expenses(start_year:int,end_year:int,indicator:str,*,function_code:str|None=None,unit:str="R$",force:bool=False)->pd.DataFrame:
    token=os.getenv("TRANSPARENCIA_API_KEY")
    if not token: raise RuntimeError("Defina TRANSPARENCIA_API_KEY para usar a API da CGU.")
    session=build_session(); rows=[]
    for year in range(start_year,end_year+1):
        page=1
        while True:
            params={"ano":year,"pagina":page}
            if function_code: params["codigoFuncao"]=function_code
            batch=request_json(session,f"{BASE}/despesas/por-funcional-programatica",params=params,headers={"chave-api-dados":token})
            if not batch: break
            rows.extend(batch if isinstance(batch,list) else batch.get("data",[])); page+=1
            if page>1000: raise RuntimeError("Paginação anormalmente longa; interrompida por segurança.")
    raw=pd.DataFrame(rows)
    if raw.empty: return standardize(pd.DataFrame(columns=["data","valor"]),source="PortalTransparencia/CGU",unit=unit,indicator=indicator)
    value_candidates=[c for c in raw.columns if any(k in c.lower() for k in ["pago","liquidado","empenhado","valor"])]
    if not value_candidates: raise ValueError(f"Nenhum campo monetário identificado: {list(raw.columns)}")
    value_col=value_candidates[0]; year_col=next((c for c in raw.columns if c.lower() in {"ano","exercicio"}),None)
    if year_col is None: raw["_ano"]=start_year; year_col="_ano"
    parsed=raw.groupby(year_col,as_index=False)[value_col].sum(numeric_only=False)
    parsed=pd.DataFrame({"data":pd.to_datetime(parsed[year_col].astype(str)+"-12-31"),"valor":pd.to_numeric(parsed[value_col],errors="coerce")})
    out=standardize(parsed,source="PortalTransparencia/CGU",unit=unit,indicator=indicator); save_cache(out,cache_path("transparencia",indicator)); return out

def aggregate_open_data_csvs(files:list[str|Path],indicator:str,date_col:str,value_col:str,unit:str="R$")->pd.DataFrame:
    frames=[pd.read_csv(f,sep=None,engine="python",encoding_errors="ignore") for f in files]; raw=pd.concat(frames,ignore_index=True)
    parsed=pd.DataFrame({"data":pd.to_datetime(raw[date_col],errors="coerce"),"valor":pd.to_numeric(raw[value_col],errors="coerce")})
    parsed=parsed.groupby(parsed["data"].dt.to_period("M").dt.to_timestamp("M"),as_index=False)["valor"].sum()
    return standardize(parsed,source="PortalTransparencia/DadosAbertos",unit=unit,indicator=indicator)

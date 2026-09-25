"""World Bank Indicators API - cross-check internacional e séries complementares."""
from __future__ import annotations
import logging
import pandas as pd
from etl.common import build_session, cache_path, read_cache, request_json, save_cache, standardize
LOGGER=logging.getLogger(__name__)
BASE="https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
WORLD_BANK_INDICATORS={
 "pib_per_capita_usd_constante":("NY.GDP.PCAP.KD","US$ constantes"),
 "crescimento_pib":("NY.GDP.MKTP.KD.ZG","% a.a."),
 "expectativa_vida":("SP.DYN.LE00.IN","anos"),
 "mortalidade_infantil":("SP.DYN.IMRT.IN","por 1.000 nascidos vivos"),
 "gini_wb":("SI.POV.GINI","índice 0-100")}

def extract_worldbank_indicator(wb_code:str,indicator:str,unit:str,start_year:int,end_year:int,*,country:str="BRA",force:bool=False)->pd.DataFrame:
    path=cache_path("worldbank",indicator)
    if path.exists() and not force:
        cached=read_cache(path,f"{start_year}-01-01",f"{end_year}-12-31")
        if cached is not None and not cached.empty: return cached
    payload=request_json(build_session(),BASE.format(country=country,indicator=wb_code),params={"date":f"{start_year}:{end_year}","format":"json","per_page":20000})
    rows=payload[1] if isinstance(payload,list) and len(payload)>1 and payload[1] else []
    parsed=pd.DataFrame({"data":[pd.Timestamp(year=int(r["date"]),month=12,day=31) for r in rows if r.get("value") is not None],"valor":[r["value"] for r in rows if r.get("value") is not None]})
    out=standardize(parsed,source=f"WorldBank/{wb_code}",unit=unit,indicator=indicator); save_cache(out,path); return out.sort_values("data")

def extract_default_worldbank(start_year:int=1985,end_year:int=2024,force:bool=False):
    out={}
    for name,(code,unit) in WORLD_BANK_INDICATORS.items():
        try: out[name]=extract_worldbank_indicator(code,name,unit,start_year,end_year,force=force)
        except Exception as exc: LOGGER.exception("Falha World Bank em %s: %s",name,exc); out[name]=pd.DataFrame()
    return out

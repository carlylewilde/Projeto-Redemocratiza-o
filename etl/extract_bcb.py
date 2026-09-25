"""Extração da API SGS do Banco Central do Brasil."""
from __future__ import annotations
import logging
import pandas as pd
from etl.common import build_session, cache_covers, cache_path, read_cache, request_json, save_cache, standardize

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
BCB_SERIES = {
    "cambio_venda": (1, "BRL/USD"),
    "selic_meta": (432, "% a.a."),
    "ipca_mensal": (433, "% a.m."),
    "igpm_mensal": (189, "% a.m."),
    "divida_bruta_pib": (13762, "% PIB"),
    "reservas_internacionais": (13621, "US$ milhões"),
}

def _chunks(start: pd.Timestamp, end: pd.Timestamp, years: int = 9):
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + pd.DateOffset(years=years) - pd.Timedelta(days=1), end)
        yield cursor, chunk_end
        cursor = chunk_end + pd.Timedelta(days=1)

def extract_sgs_series(code: int, indicator: str, unit: str, start: str, end: str, *, force: bool = False) -> pd.DataFrame:
    path = cache_path("bcb", indicator)
    if not force and cache_covers(path, start, end):
        LOGGER.info("BCB cache hit: %s", indicator)
        return read_cache(path, start, end)
    session = build_session(); rows = []
    for a,b in _chunks(pd.Timestamp(start), pd.Timestamp(end)):
        payload = request_json(session, BASE_URL.format(code=code), params={"formato":"json","dataInicial":a.strftime("%d/%m/%Y"),"dataFinal":b.strftime("%d/%m/%Y")})
        rows.extend(payload)
    df = pd.DataFrame(rows)
    if df.empty:
        return standardize(pd.DataFrame(columns=["data","valor"]), source="BCB/SGS", unit=unit, indicator=indicator)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"].astype(str).str.replace(",",".",regex=False), errors="coerce")
    out = standardize(df[["data","valor"]], source=f"BCB/SGS/{code}", unit=unit, indicator=indicator)
    save_cache(out, path)
    return out[(out["data"] >= pd.Timestamp(start)) & (out["data"] <= pd.Timestamp(end))]

def extract_default_bcb(start: str, end: str, force: bool = False) -> dict[str,pd.DataFrame]:
    return {name: extract_sgs_series(code,name,unit,start,end,force=force) for name,(code,unit) in BCB_SERIES.items()}

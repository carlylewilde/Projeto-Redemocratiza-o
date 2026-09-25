"""Extrator parametrizável para consultas TabNet/DataSUS."""
from io import StringIO
from typing import Mapping
import pandas as pd
from etl.common import build_session, cache_path, read_cache, request_text, save_cache, standardize

def extract_tabnet_table(url: str, form_data: Mapping[str, str | list[str]], indicator: str, unit: str, *, date_column: str, value_column: str, start: str, end: str, force: bool = False) -> pd.DataFrame:
    path = cache_path("datasus", indicator)
    if path.exists() and not force:
        cached = read_cache(path, start, end)
        if cached is not None and not cached.empty:
            return cached
    html = request_text(build_session(), url, data=form_data)
    tables = pd.read_html(StringIO(html), decimal=",", thousands=".")
    if not tables:
        raise ValueError("TabNet não retornou tabela HTML.")
    table = max(tables, key=lambda x: x.shape[0] * max(x.shape[1], 1))
    parsed = pd.DataFrame({"data": pd.to_datetime(table[date_column].astype(str), errors="coerce"), "valor": pd.to_numeric(table[value_column], errors="coerce")})
    out = standardize(parsed, source="DATASUS/TabNet", unit=unit, indicator=indicator)
    out = out[(out["data"] >= pd.Timestamp(start)) & (out["data"] <= pd.Timestamp(end))]
    save_cache(out, path)
    return out

def infant_mortality_from_counts(infant_deaths: pd.DataFrame, live_births: pd.DataFrame) -> pd.DataFrame:
    d = infant_deaths[["data", "valor"]].rename(columns={"valor": "obitos"})
    b = live_births[["data", "valor"]].rename(columns={"valor": "nascidos_vivos"})
    x = d.merge(b, on="data", how="inner")
    x["valor"] = x["obitos"] / x["nascidos_vivos"] * 1000.0
    return standardize(x[["data", "valor"]], source="DATASUS/SIM+SINASC", unit="por 1.000 nascidos vivos", indicator="mortalidade_infantil")

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import RAW_DIR

LOGGER = logging.getLogger(__name__)
STANDARD_COLUMNS = ["data", "valor", "unidade", "fonte", "data_extracao"]


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def extraction_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_session(total_retries: int = 5, backoff_factor: float = 1.0) -> requests.Session:
    retry = Retry(total=total_retries, read=total_retries, connect=total_retries, status=total_retries,
                  backoff_factor=backoff_factor, status_forcelist=(429,500,502,503,504),
                  allowed_methods=frozenset(["GET","POST"]), respect_retry_after_header=True)
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry)); session.mount("http://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent":"brasil-redemocratizacao-data/1.0"})
    return session


def cache_path(source: str, indicator: str, ext: str = "csv") -> Path:
    safe = indicator.lower().replace(" ", "_").replace("/", "_")
    return RAW_DIR / f"{source}_{safe}.{ext}"


def read_cache(path: Path, start: str | None = None, end: str | None = None) -> pd.DataFrame | None:
    if not path.exists(): return None
    try:
        df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], errors="coerce")
            if start: df = df[df["data"] >= pd.Timestamp(start)]
            if end: df = df[df["data"] <= pd.Timestamp(end)]
        return df
    except Exception as exc:
        LOGGER.warning("Falha ao ler cache %s: %s", path, exc); return None


def cache_covers(path: Path, start: str, end: str) -> bool:
    cached = read_cache(path)
    if cached is None or cached.empty or "data" not in cached: return False
    dates = pd.to_datetime(cached["data"], errors="coerce").dropna()
    return bool(len(dates) and dates.min() <= pd.Timestamp(start) and dates.max() >= pd.Timestamp(end))


def save_cache(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        old = read_cache(path)
        if old is not None and not old.empty:
            df = pd.concat([old, df], ignore_index=True)
            subset = [c for c in ["data","fonte","indicador"] if c in df.columns]
            if subset: df = df.drop_duplicates(subset=subset, keep="last")
    if "data" in df: df = df.sort_values("data")
    if path.suffix == ".parquet": df.to_parquet(path, index=False)
    else: df.to_csv(path, index=False)
    LOGGER.info("Cache salvo: %s (%d linhas)", path, len(df))


def standardize(df: pd.DataFrame, *, source: str, unit: str, indicator: str) -> pd.DataFrame:
    out = df.copy()
    if "data" not in out or "valor" not in out: raise ValueError("DataFrame deve conter colunas 'data' e 'valor'.")
    out["data"] = pd.to_datetime(out["data"], errors="coerce")
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")
    out["unidade"] = unit; out["fonte"] = source; out["indicador"] = indicator; out["data_extracao"] = extraction_timestamp()
    return out.dropna(subset=["data","valor"]).sort_values("data")


def request_json(session: requests.Session, url: str, *, params=None, headers=None, timeout: int = 60):
    LOGGER.info("GET %s", url); response = session.get(url, params=params, headers=headers, timeout=timeout); response.raise_for_status(); return response.json()


def request_text(session: requests.Session, url: str, *, params=None, data=None, headers=None, timeout: int = 90):
    method = session.post if data is not None else session.get
    LOGGER.info("%s %s", "POST" if data is not None else "GET", url)
    response = method(url, params=params, data=data, headers=headers, timeout=timeout); response.raise_for_status(); return response.text


def json_dumps_safe(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)

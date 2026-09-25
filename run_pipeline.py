#!/usr/bin/env python3
from __future__ import annotations
import argparse, logging
import pandas as pd
from analysis.descriptive import descriptive_by_government, wide_summary
from analysis.export import export_outputs
from analysis.relationships import correlation_matrix
from analysis.trends import detect_breaks_ruptures, external_shock_flags
from config import ANALYSIS_END, ANALYSIS_START, PROCESSED_DIR, RAW_DIR, PROJECT_ROOT
from etl.common import configure_logging
from etl.extract_bcb import extract_default_bcb
from etl.extract_ibge import extract_default_ibge
from etl.extract_ipeadata import extract_default_ipeadata
from etl.extract_worldbank import extract_default_worldbank
from etl.normalize import normalize_all
LOGGER=logging.getLogger("run_pipeline")

def extract_all(force:bool=False)->dict[str,pd.DataFrame]:
    series={}; series.update(extract_default_bcb(ANALYSIS_START,ANALYSIS_END,force=force)); series.update(extract_default_ibge(ANALYSIS_START,ANALYSIS_END,force=force)); series.update(extract_default_ipeadata(ANALYSIS_START,ANALYSIS_END,force=force)); series.update(extract_default_worldbank(1985,2024,force=force)); return series

def load_raw_series()->dict[str,pd.DataFrame]:
    series={}
    for path in sorted(RAW_DIR.glob("*.csv")):
        try:
            df=pd.read_csv(path)
            if "indicador" not in df.columns or df.empty:continue
            df["data"]=pd.to_datetime(df["data"],errors="coerce")
            for indicator,group in df.groupby("indicador"):
                series[indicator]=pd.concat([series.get(indicator,pd.DataFrame()),group],ignore_index=True).drop_duplicates(subset=["data","indicador"],keep="last")
        except Exception as exc: LOGGER.warning("Ignorando raw %s: %s",path,exc)
    return series

def normalize_stage(series:dict[str,pd.DataFrame]|None=None)->pd.DataFrame:
    panel=normalize_all(series or load_raw_series(),ANALYSIS_END); panel=external_shock_flags(panel); PROCESSED_DIR.mkdir(parents=True,exist_ok=True); panel.to_parquet(PROCESSED_DIR/"painel_governos.parquet",index=False); return panel

def analyze_stage(panel:pd.DataFrame|None=None)->None:
    if panel is None:panel=pd.read_parquet(PROCESSED_DIR/"painel_governos.parquet")
    out_dir=PROJECT_ROOT/"analysis"/"outputs"; out_dir.mkdir(parents=True,exist_ok=True); desc=descriptive_by_government(panel); desc.to_csv(out_dir/"descritiva_governo_indicador.csv",index=False); wide_summary(desc).to_csv(PROCESSED_DIR/"resumo_estatistico_por_governo.csv",index=False); correlation_matrix(panel).to_csv(out_dir/"correlacoes_mensais.csv")
    breaks=[]
    for indicator,g in panel.groupby("indicador"):
        b=detect_breaks_ruptures(g)
        if not b.empty:b.insert(0,"indicador",indicator);breaks.append(b)
    (pd.concat(breaks,ignore_index=True) if breaks else pd.DataFrame(columns=["indicador","break_index","break_date"])).to_csv(out_dir/"rupturas_detectadas.csv",index=False)

def main()->None:
    parser=argparse.ArgumentParser(description="Pipeline Brasil pós-redemocratização 1985-2024"); parser.add_argument("--stage",choices=["all","extract","normalize","analyze","export"],default="all"); parser.add_argument("--force",action="store_true",help="ignora caches de extração"); args=parser.parse_args(); configure_logging(); series=None; panel=None
    if args.stage in {"all","extract"}: LOGGER.info("Etapa: extração"); series=extract_all(force=args.force); 
    if args.stage=="extract": return
    if args.stage in {"all","normalize"}: LOGGER.info("Etapa: normalização"); panel=normalize_stage(series)
    if args.stage=="normalize": return
    if args.stage in {"all","analyze"}: LOGGER.info("Etapa: análise"); analyze_stage(panel)
    if args.stage=="analyze": return
    if args.stage in {"all","export"}:
        LOGGER.info("Etapa: export")
        if panel is None:panel=pd.read_parquet(PROCESSED_DIR/"painel_governos.parquet")
        for kind,path in export_outputs(panel).items(): LOGGER.info("%s -> %s",kind,path)

if __name__=="__main__": main()

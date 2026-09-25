from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from analysis.descriptive import descriptive_by_government, wide_summary
from config import PROCESSED_DIR

def export_outputs(panel:pd.DataFrame,output_dir:str|Path=PROCESSED_DIR)->dict[str,Path]:
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    parquet_path=out/"painel_governos.parquet"; csv_path=out/"resumo_estatistico_por_governo.csv"; json_path=out/"painel_governos.json"; long_summary_path=out/"resumo_estatistico_longo.csv"
    panel.to_parquet(parquet_path,index=False); desc=descriptive_by_government(panel); desc.to_csv(long_summary_path,index=False); wide_summary(desc).to_csv(csv_path,index=False)
    keep=[c for c in ["data","indicador","valor","unidade","fonte","governo","presidente","partido","mes_mandato","percentual_mandato_decorrido","indice_base100","quebra_metodologica","comparacao_direta_valida","governo_em_andamento","valor_ajustado_sazonal","choque_externo"] if c in panel.columns]
    records=panel[keep].copy(); records["data"]=pd.to_datetime(records["data"]).dt.strftime("%Y-%m-%d"); records=records.replace({np.nan:None,pd.NA:None}); json_path.write_text(json.dumps(records.to_dict("records"),ensure_ascii=False,separators=(",",":"),default=str),encoding="utf-8")
    return {"parquet":parquet_path,"summary":csv_path,"summary_long":long_summary_path,"json":json_path}

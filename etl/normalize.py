"""Normalização metodológica das séries.

1. Valores monetários nominais são deflacionados pelo IPCA.
2. Quebras metodológicas permanecem sinalizadas.
3. Observações recebem governo, mês do mandato e % do mandato.
4. Base 100 mede trajetória, não nível absoluto.
5. Ajuste sazonal usa STL quando há dados suficientes.
6. Indicadores anuais em anos de transição fora de 1º de janeiro são marcados como ambíguos.
"""
from __future__ import annotations
import logging
from typing import Iterable
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL
from metadata.governments import GOVERNMENTS, government_frame
from metadata.indicators import INDICATORS
LOGGER=logging.getLogger(__name__)

def build_ipca_index(ipca_monthly:pd.DataFrame,base_date:str|pd.Timestamp|None=None)->pd.DataFrame:
    x=ipca_monthly[["data","valor"]].dropna().copy(); x["data"]=pd.to_datetime(x["data"]).dt.to_period("M").dt.to_timestamp("M")
    x=x.groupby("data",as_index=False)["valor"].last().sort_values("data"); x["fator"]=1.0+x["valor"]/100.0; x["indice_preco"]=x["fator"].cumprod()
    if x.empty:return x
    base=pd.Timestamp(base_date).to_period("M").to_timestamp("M") if base_date is not None else x["data"].max(); base_rows=x[x["data"]<=base]
    if base_rows.empty: raise ValueError("Mês-base anterior à primeira observação do IPCA.")
    base_index=base_rows.iloc[-1]["indice_preco"]; x["indice_preco_base100"]=x["indice_preco"]/base_index*100.0; x["base_deflator"]=base_rows.iloc[-1]["data"]
    return x[["data","indice_preco","indice_preco_base100","base_deflator"]]

def deflate_nominal(nominal:pd.DataFrame,ipca_monthly:pd.DataFrame,*,base_date:str|pd.Timestamp|None=None,value_col:str="valor")->pd.DataFrame:
    """valor_real_t = valor_nominal_t * (P_base / P_t). Nunca compare R$ nominais entre décadas."""
    price=build_ipca_index(ipca_monthly,base_date)
    if price.empty: raise ValueError("IPCA vazio: não é possível deflacionar.")
    x=nominal.copy().sort_values("data"); x["data"]=pd.to_datetime(x["data"]); x["mes_ref"]=x["data"].dt.to_period("M").dt.to_timestamp("M")
    p=price.rename(columns={"data":"mes_ref"}).sort_values("mes_ref"); x=pd.merge_asof(x.sort_values("mes_ref"),p,on="mes_ref",direction="backward")
    base_month=price["base_deflator"].iloc[0]; p_base=price.loc[price["data"]==base_month,"indice_preco"].iloc[-1]
    x["valor_nominal"]=pd.to_numeric(x[value_col],errors="coerce"); x["valor_real"]=x["valor_nominal"]*p_base/x["indice_preco"]; x[value_col]=x["valor_real"]; x["deflacionado"]=True
    return x.drop(columns=["mes_ref"])

def harmonize_daily_to_monthly(df:pd.DataFrame,indicator:str)->pd.DataFrame:
    x=df.copy(); x["data"]=pd.to_datetime(x["data"]); x=x.set_index("data").sort_index(); agg="last" if indicator in {"selic_meta","reservas_internacionais"} else "mean"
    numeric=x[["valor"]].resample("ME").agg(agg); meta=x.drop(columns=["valor"]).resample("ME").last(); out=numeric.join(meta,how="left").reset_index(); out["frequencia_original"]="daily"; out["frequencia_analise"]="monthly"; return out

def mark_method_breaks(df:pd.DataFrame,break_dates:Iterable[str]|None)->pd.DataFrame:
    x=df.copy().sort_values("data"); x["quebra_metodologica"]=False
    if not break_dates or x.empty:return x
    dates=pd.to_datetime(x["data"])
    for b in pd.to_datetime(list(break_dates)):
        eligible=x.index[dates>=b]
        if len(eligible):x.loc[eligible[0],"quebra_metodologica"]=True
    return x

def assign_government(df:pd.DataFrame,analysis_end:str="2024-12-31")->pd.DataFrame:
    x=df.copy(); x["data"]=pd.to_datetime(x["data"]); x["governo"]=pd.NA; x["presidente"]=pd.NA; x["partido"]=pd.NA; x["mandato_completo"]=pd.NA; x["governo_em_andamento"]=False; cutoff=pd.Timestamp(analysis_end)
    for g in GOVERNMENTS:
        start=pd.Timestamp(g.data_inicio); end=pd.Timestamp(g.data_fim_exclusiva) if g.data_fim_exclusiva else cutoff+pd.Timedelta(days=1); mask=(x["data"]>=start)&(x["data"]<end)&(x["data"]<=cutoff)
        x.loc[mask,["governo","presidente","partido"]]=[g.governo,g.presidente,g.partido]; x.loc[mask,"mandato_completo"]=g.mandato_completo; x.loc[mask,"governo_em_andamento"]=g.data_fim_exclusiva is None
    return x

def add_mandate_axis(df:pd.DataFrame,analysis_end:str="2024-12-31")->pd.DataFrame:
    x=assign_government(df,analysis_end); gf=government_frame(analysis_end).set_index("governo"); x["mes_mandato"]=pd.NA; x["percentual_mandato_decorrido"]=np.nan
    for gov,idx in x.dropna(subset=["governo"]).groupby("governo").groups.items():
        start=gf.loc[gov,"data_inicio"]; dates=x.loc[idx,"data"]; months=(dates.dt.year-start.year)*12+(dates.dt.month-start.month)+1; x.loc[idx,"mes_mandato"]=months.astype("Int64")
        duration=float(gf.loc[gov,"duracao_dias"]); elapsed=(dates-start).dt.days.clip(lower=0); x.loc[idx,"percentual_mandato_decorrido"]=np.minimum(100.0,elapsed/max(duration,1.0)*100.0)
    return x

def base100_by_government(df:pd.DataFrame,value_col:str="valor")->pd.DataFrame:
    x=df.copy().sort_values(["governo","data"]); x["indice_base100"]=np.nan
    for (_, _),idx in x.dropna(subset=["governo"]).groupby(["governo","indicador"]).groups.items():
        vals=pd.to_numeric(x.loc[idx,value_col],errors="coerce"); valid=vals.replace([np.inf,-np.inf],np.nan).dropna()
        if valid.empty:continue
        base=valid.iloc[0]
        if base==0:continue
        x.loc[idx,"indice_base100"]=vals/base*100.0
    return x

def seasonal_adjust_stl(df:pd.DataFrame,value_col:str="valor",period:int=12)->pd.DataFrame:
    x=df.copy().sort_values("data"); x["valor_ajustado_sazonal"]=np.nan; x["tendencia_stl"]=np.nan; x["sazonal_stl"]=np.nan; y=pd.to_numeric(x[value_col],errors="coerce"); valid=y.dropna()
    if len(valid)<period*2:return x
    try:
        fit=STL(valid,period=period,robust=True).fit(); x.loc[valid.index,"valor_ajustado_sazonal"]=valid-fit.seasonal; x.loc[valid.index,"tendencia_stl"]=fit.trend; x.loc[valid.index,"sazonal_stl"]=fit.seasonal
    except Exception as exc:LOGGER.warning("STL falhou: %s",exc)
    return x

def flag_annual_transition_ambiguity(df:pd.DataFrame,frequency:str)->pd.DataFrame:
    x=df.copy(); x["atribuicao_governo_ambigua"]=False
    if frequency!="annual":return x
    transition_years={g.data_inicio.year for g in GOVERNMENTS if not(g.data_inicio.month==1 and g.data_inicio.day==1)}; x.loc[x["data"].dt.year.isin(transition_years),"atribuicao_governo_ambigua"]=True; return x

def normalize_indicator(df:pd.DataFrame,indicator:str,ipca:pd.DataFrame,analysis_end:str="2024-12-31")->pd.DataFrame:
    if df is None or df.empty:return pd.DataFrame()
    spec=INDICATORS.get(indicator,{}); x=df.copy(); x["indicador"]=indicator; freq=spec.get("frequency","unknown"); x["frequencia_original"]=freq; x["frequencia_analise"]=freq
    if freq=="daily":x=harmonize_daily_to_monthly(x,indicator)
    x=mark_method_breaks(x,spec.get("method_breaks")); x["deflacionado"]=False
    if spec.get("deflate"):x=deflate_nominal(x,ipca,base_date=analysis_end)
    x=add_mandate_axis(x,analysis_end); x=flag_annual_transition_ambiguity(x,"annual" if freq=="annual" else freq); x["comparacao_direta_valida"]=~x["quebra_metodologica"]&~x["atribuicao_governo_ambigua"]
    if spec.get("seasonal_adjust"):x=seasonal_adjust_stl(x,period=4 if freq=="quarterly" else 12)
    return base100_by_government(x)

def normalize_all(series:dict[str,pd.DataFrame],analysis_end:str="2024-12-31")->pd.DataFrame:
    if "ipca_mensal" not in series or series["ipca_mensal"].empty:raise ValueError("IPCA mensal (BCB/SGS 433) é obrigatório para a normalização.")
    ipca=series["ipca_mensal"]; normalized=[]
    for indicator,df in series.items():
        try:
            out=normalize_indicator(df,indicator,ipca,analysis_end)
            if not out.empty:normalized.append(out)
        except Exception as exc:LOGGER.exception("Falha de normalização em %s: %s",indicator,exc)
    if not normalized:return pd.DataFrame()
    panel=pd.concat(normalized,ignore_index=True,sort=False); return panel[panel["governo"].notna()].sort_values(["indicador","data"]).reset_index(drop=True)

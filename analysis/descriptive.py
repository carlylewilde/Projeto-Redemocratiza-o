from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm

def cagr(values:pd.Series,dates:pd.Series)->float:
    y=pd.to_numeric(values,errors="coerce"); x=pd.to_datetime(dates); valid=y.notna()&x.notna(); y,x=y[valid],x[valid]
    if len(y)<2 or y.iloc[0]<=0 or y.iloc[-1]<=0:return np.nan
    years=(x.iloc[-1]-x.iloc[0]).days/365.2425
    return (y.iloc[-1]/y.iloc[0])**(1.0/years)-1.0 if years>0 else np.nan

def monthly_volatility(values:pd.Series)->float:
    y=pd.to_numeric(values,errors="coerce").dropna()
    if len(y)<3:return np.nan
    r=np.log(y).diff().dropna() if (y>0).all() else y.diff().dropna()
    return float(r.std(ddof=1)) if len(r) else np.nan

def ols_slope(values:pd.Series)->tuple[float,float,float]:
    y=pd.to_numeric(values,errors="coerce").dropna()
    if len(y)<3:return np.nan,np.nan,np.nan
    t=np.arange(len(y),dtype=float); model=sm.OLS(y.to_numpy(),sm.add_constant(t)).fit(); return float(model.params[1]),float(model.pvalues[1]),float(model.rsquared)

def summarize_group(group:pd.DataFrame)->dict:
    g=group.sort_values("data"); v=pd.to_numeric(g["valor"],errors="coerce").dropna()
    if v.empty:return {}
    mean=float(v.mean()); std=float(v.std(ddof=1)) if len(v)>1 else np.nan; slope,slope_p,r2=ols_slope(g["valor"]); valid_direct=g.get("comparacao_direta_valida",pd.Series(True,index=g.index)).fillna(False)
    return {"n":int(v.size),"media":mean,"mediana":float(v.median()),"desvio_padrao":std,"coef_variacao":std/mean if mean!=0 and np.isfinite(std) else np.nan,"min":float(v.min()),"max":float(v.max()),"cagr":cagr(g.loc[v.index,"valor"],g.loc[v.index,"data"]),"volatilidade":monthly_volatility(v),"tendencia_ols_slope":slope,"tendencia_ols_pvalor":slope_p,"tendencia_ols_r2":r2,"pct_obs_comparacao_direta_valida":float(valid_direct.mean()),"periodo_parcial":bool(g.get("governo_em_andamento",pd.Series(False,index=g.index)).any())}

def descriptive_by_government(panel:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for (gov,indicator),group in panel.groupby(["governo","indicador"],dropna=False):
        stats=summarize_group(group)
        if stats:rows.append({"governo":gov,"indicador":indicator,**stats})
    return pd.DataFrame(rows)

def wide_summary(desc:pd.DataFrame)->pd.DataFrame:
    if desc.empty:return desc
    metric_cols=[c for c in desc.columns if c not in {"governo","indicador"}]; wide=desc.pivot(index="governo",columns="indicador",values=metric_cols); wide.columns=[f"{indicator}__{metric}" for metric,indicator in wide.columns]; return wide.reset_index()

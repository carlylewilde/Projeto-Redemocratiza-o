from __future__ import annotations
import numpy as np
import pandas as pd
import ruptures as rpt
import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose

def chow_test(y:pd.Series,breakpoint:int)->dict:
    y=pd.to_numeric(y,errors="coerce").dropna().reset_index(drop=True); n=len(y)
    if breakpoint<3 or n-breakpoint<3:return {"f_stat":np.nan,"p_value":np.nan,"valid":False}
    def rss(segment):
        X=sm.add_constant(np.arange(len(segment),dtype=float)); fit=sm.OLS(segment.to_numpy(),X).fit(); return float(np.sum(fit.resid**2)),len(segment)
    rss_full,_=rss(y); rss_1,n1=rss(y.iloc[:breakpoint]); rss_2,n2=rss(y.iloc[breakpoint:]); k=2
    numerator=(rss_full-(rss_1+rss_2))/k; denominator=(rss_1+rss_2)/(n1+n2-2*k); f_stat=numerator/denominator if denominator>0 else np.nan; p=1-stats.f.cdf(f_stat,k,n1+n2-2*k) if np.isfinite(f_stat) else np.nan
    return {"f_stat":float(f_stat),"p_value":float(p),"valid":True}

def detect_breaks_ruptures(df:pd.DataFrame,value_col:str="valor",model:str="rbf",penalty:float=5.0)->pd.DataFrame:
    x=df[["data",value_col]].dropna().sort_values("data").reset_index(drop=True)
    if len(x)<12:return pd.DataFrame(columns=["break_index","break_date"])
    signal=x[value_col].to_numpy(dtype=float).reshape(-1,1); algo=rpt.Pelt(model=model).fit(signal); breaks=[i for i in algo.predict(pen=penalty) if i<len(x)]
    return pd.DataFrame({"break_index":breaks,"break_date":[x.loc[i,"data"] for i in breaks]})

def decompose_series(df:pd.DataFrame,period:int,value_col:str="valor",model:str="additive")->pd.DataFrame:
    x=df[["data",value_col]].dropna().sort_values("data").copy()
    if len(x)<period*2:return pd.DataFrame()
    result=seasonal_decompose(x[value_col],model=model,period=period,extrapolate_trend="freq"); x["trend"]=result.trend.to_numpy(); x["seasonal"]=result.seasonal.to_numpy(); x["resid"]=result.resid.to_numpy(); return x

def external_shock_flags(df:pd.DataFrame)->pd.DataFrame:
    x=df.copy(); d=pd.to_datetime(x["data"]); x["choque_externo"]=""; x.loc[(d>="2008-09-01")&(d<="2009-12-31"),"choque_externo"]="crise_financeira_global"; x.loc[(d>="2015-01-01")&(d<="2016-12-31"),"choque_externo"]="recessao_brasil_2015_2016"; x.loc[(d>="2020-03-01")&(d<="2021-12-31"),"choque_externo"]="pandemia_covid19"; return x

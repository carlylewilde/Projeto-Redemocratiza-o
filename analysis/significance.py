from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats

def cohens_d(a,b)->float:
    a=pd.to_numeric(pd.Series(a),errors="coerce").dropna().to_numpy(); b=pd.to_numeric(pd.Series(b),errors="coerce").dropna().to_numpy()
    if len(a)<2 or len(b)<2:return np.nan
    pooled=np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2)); return float((a.mean()-b.mean())/pooled) if pooled>0 else np.nan

def compare_two_governments(panel:pd.DataFrame,indicator:str,gov_a:str,gov_b:str,paired:bool=False)->dict:
    mask=panel["indicador"].eq(indicator)
    if "comparacao_direta_valida" in panel: mask&=panel["comparacao_direta_valida"].fillna(False)
    x=panel[mask].copy(); a=pd.to_numeric(x.loc[x["governo"]==gov_a,"valor"],errors="coerce").dropna(); b=pd.to_numeric(x.loc[x["governo"]==gov_b,"valor"],errors="coerce").dropna()
    if paired:
        n=min(len(a),len(b)); test=stats.ttest_rel(a.iloc[:n],b.iloc[:n],nan_policy="omit") if n>=2 else None
    else:test=stats.ttest_ind(a,b,equal_var=False,nan_policy="omit") if len(a)>=2 and len(b)>=2 else None
    return {"indicador":indicator,"governo_a":gov_a,"governo_b":gov_b,"t_stat":float(test.statistic) if test else np.nan,"p_value":float(test.pvalue) if test else np.nan,"cohens_d":cohens_d(a,b),"n_a":len(a),"n_b":len(b)}

def omnibus_by_group(panel:pd.DataFrame,indicator:str,group_map:dict[str,str],method:str="kruskal")->dict:
    """Grupos são fornecidos externamente; nenhuma classificação política é embutida."""
    x=panel[panel["indicador"]==indicator].copy(); x["grupo"]=x["governo"].map(group_map); groups=[pd.to_numeric(g["valor"],errors="coerce").dropna().to_numpy() for _,g in x.dropna(subset=["grupo"]).groupby("grupo")]; groups=[g for g in groups if len(g)>=2]
    if len(groups)<2:return {"statistic":np.nan,"p_value":np.nan,"method":method}
    test=stats.f_oneway(*groups) if method=="anova" else stats.kruskal(*groups); return {"statistic":float(test.statistic),"p_value":float(test.pvalue),"method":method}

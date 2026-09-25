from __future__ import annotations
import warnings
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests

def monthly_matrix(panel:pd.DataFrame,value_col:str="valor")->pd.DataFrame:
    x=panel[["data","indicador",value_col]].dropna().copy(); x["mes"]=pd.to_datetime(x["data"]).dt.to_period("M").dt.to_timestamp("M"); return x.pivot_table(index="mes",columns="indicador",values=value_col,aggfunc="last").sort_index()

def correlation_matrix(panel:pd.DataFrame,value_col:str="valor",method:str="pearson")->pd.DataFrame:
    """Correlação exploratória. Correlação não implica causalidade."""
    return monthly_matrix(panel,value_col).corr(method=method)

def lag_correlation(panel:pd.DataFrame,x_indicator:str,y_indicator:str,max_lag:int=24)->pd.DataFrame:
    m=monthly_matrix(panel)[[x_indicator,y_indicator]].dropna(); rows=[]
    for lag in range(-max_lag,max_lag+1): rows.append({"lag_meses_x":lag,"correlacao":m[x_indicator].shift(lag).corr(m[y_indicator])})
    return pd.DataFrame(rows)

def granger_exploration(panel:pd.DataFrame,cause:str,effect:str,maxlag:int=12)->pd.DataFrame:
    """Teste de Granger exploratório; não prova causalidade estrutural."""
    m=monthly_matrix(panel)[[effect,cause]].dropna()
    if len(m)<maxlag*3:return pd.DataFrame()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore"); result=grangercausalitytests(m,maxlag=maxlag,verbose=False)
    rows=[]
    for lag,tests in result.items():
        stat,p,*_=tests[0]["ssr_ftest"]; rows.append({"lag":lag,"f_stat":stat,"p_value":p,"causa_testada":cause,"efeito_testado":effect})
    return pd.DataFrame(rows)

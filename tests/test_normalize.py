import numpy as np
import pandas as pd
from etl.normalize import add_mandate_axis, base100_by_government, deflate_nominal

def test_ipca_index_and_deflation_base_month():
    ipca=pd.DataFrame({"data":pd.to_datetime(["2024-01-31","2024-02-29"]),"valor":[0.0,10.0]})
    nominal=pd.DataFrame({"data":pd.to_datetime(["2024-01-31","2024-02-29"]),"valor":[100.0,110.0]})
    out=deflate_nominal(nominal,ipca,base_date="2024-02-29")
    assert np.isclose(out.iloc[0]["valor"],110.0)
    assert np.isclose(out.iloc[1]["valor"],110.0)

def test_base100_is_exact_on_first_observation():
    df=pd.DataFrame({"governo":["X","X","X"],"indicador":["a","a","a"],"data":pd.to_datetime(["2020-01-31","2020-02-29","2020-03-31"]),"valor":[50.0,55.0,45.0]})
    out=base100_by_government(df)
    assert np.isclose(out.iloc[0]["indice_base100"],100.0)
    assert np.isclose(out.iloc[1]["indice_base100"],110.0)
    assert np.isclose(out.iloc[2]["indice_base100"],90.0)

def test_month_of_mandate_lula_iii():
    df=pd.DataFrame({"data":pd.to_datetime(["2023-01-31","2023-02-28"]),"valor":[1,2],"indicador":["x","x"]})
    out=add_mandate_axis(df,"2024-12-31")
    assert out["governo"].tolist()==["Lula III","Lula III"]
    assert out["mes_mandato"].astype(int).tolist()==[1,2]

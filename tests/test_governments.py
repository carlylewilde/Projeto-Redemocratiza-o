import pandas as pd
from metadata.governments import government_frame

def test_government_periods_do_not_overlap():
    g=government_frame("2024-12-31").sort_values("data_inicio")
    for i in range(len(g)-1):
        assert g.iloc[i]["data_fim"] < g.iloc[i+1]["data_inicio"] or g.iloc[i]["data_fim"]+pd.Timedelta(days=1)==g.iloc[i+1]["data_inicio"]

def test_lula_iii_flagged_partial():
    g=government_frame("2024-12-31").set_index("governo")
    assert bool(g.loc["Lula III","em_andamento"])
    assert not bool(g.loc["Lula III","mandato_completo"])

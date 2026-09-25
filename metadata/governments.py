"""Metadados dos períodos presidenciais usados como unidade de análise.

A atribuição temporal segue o período em que cada governo efetivamente exercia a
Presidência. Em transições extraordinárias: Collor termina analiticamente em
02/10/1992, quando Itamar passa a exercer interinamente; Dilma II termina em
12/05/2016, quando Temer passa a exercer interinamente. As datas formais
posteriores do desfecho jurídico permanecem documentadas em notas.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Optional
import pandas as pd

@dataclass(frozen=True)
class GovernmentPeriod:
    governo: str
    presidente: str
    data_inicio: date
    data_fim_exclusiva: Optional[date]
    mandato_completo: bool
    forma_saida: str
    partido: str
    coligacao: str
    transicao_extraordinaria: bool = False
    nota: str = ""

GOVERNMENTS = [
    GovernmentPeriod("Sarney", "José Sarney", date(1985,3,15), date(1990,3,15), True, "sucessão constitucional / término do período", "PMDB", "Aliança Democrática (PMDB + Frente Liberal)", True, "Assumiu após a impossibilidade de posse de Tancredo Neves."),
    GovernmentPeriod("Collor", "Fernando Collor", date(1990,3,15), date(1992,10,2), False, "afastamento; renúncia durante processo de impeachment", "PRN", "Movimento Brasil Novo (PRN/PST/PSC/PTR)", True, "Janela analítica termina quando Itamar passa a exercer interinamente a Presidência."),
    GovernmentPeriod("Itamar", "Itamar Franco", date(1992,10,2), date(1995,1,1), False, "complementação de mandato", "PMDB", "Vice eleito na chapa Movimento Brasil Novo; posteriormente filiado ao PMDB", True, "Inclui período interino iniciado em 02/10/1992 e exercício formal após 29/12/1992."),
    GovernmentPeriod("FHC I", "Fernando Henrique Cardoso", date(1995,1,1), date(1999,1,1), True, "reeleição", "PSDB", "União, Trabalho e Progresso (PSDB/PFL/PTB)"),
    GovernmentPeriod("FHC II", "Fernando Henrique Cardoso", date(1999,1,1), date(2003,1,1), True, "término do mandato", "PSDB", "União, Trabalho e Progresso (PSDB/PFL/PTB/PPB/PSD)"),
    GovernmentPeriod("Lula I", "Luiz Inácio Lula da Silva", date(2003,1,1), date(2007,1,1), True, "reeleição", "PT", "Lula Presidente (PT/PL/PCdoB/PCB/PMN)"),
    GovernmentPeriod("Lula II", "Luiz Inácio Lula da Silva", date(2007,1,1), date(2011,1,1), True, "término do mandato", "PT", "A Força do Povo (PT/PRB/PCdoB)"),
    GovernmentPeriod("Dilma I", "Dilma Rousseff", date(2011,1,1), date(2015,1,1), True, "reeleição", "PT", "Para o Brasil Seguir Mudando (PT/PRB/PDT/PMDB/PTN/PSC/PR/PTC/PSB/PCdoB)"),
    GovernmentPeriod("Dilma II", "Dilma Rousseff", date(2015,1,1), date(2016,5,12), False, "afastamento; impeachment concluído em 31/08/2016", "PT", "Com a Força do Povo (PT/PMDB/PSD/PP/PR/PROS/PDT/PCdoB/PRB)", True, "Janela analítica termina quando Temer passa a exercer interinamente a Presidência."),
    GovernmentPeriod("Temer", "Michel Temer", date(2016,5,12), date(2019,1,1), False, "complementação de mandato", "PMDB/MDB", "Vice eleito pela coligação Com a Força do Povo", True, "Inclui exercício interino desde 12/05/2016 e posse definitiva em 31/08/2016."),
    GovernmentPeriod("Bolsonaro", "Jair Bolsonaro", date(2019,1,1), date(2023,1,1), True, "término do mandato", "PSL → sem partido → PL", "Brasil Acima de Tudo, Deus Acima de Todos (PSL/PRTB)"),
    GovernmentPeriod("Lula III", "Luiz Inácio Lula da Silva", date(2023,1,1), None, False, "em_andamento", "PT", "Brasil da Esperança (FE Brasil [PT/PCdoB/PV] + Solidariedade + Federação PSOL-REDE + PSB + Agir + Avante + PROS)", False, "Período parcial/em andamento. O recorte principal termina em 31/12/2024."),
]

def government_frame(analysis_end: str | pd.Timestamp = "2024-12-31") -> pd.DataFrame:
    cutoff = pd.Timestamp(analysis_end).date()
    rows = []
    for g in GOVERNMENTS:
        row = asdict(g)
        end_exclusive = g.data_fim_exclusiva or (cutoff + timedelta(days=1))
        effective_end_exclusive = min(end_exclusive, cutoff + timedelta(days=1))
        row["data_fim"] = effective_end_exclusive - timedelta(days=1)
        row["duracao_dias"] = max(0, (effective_end_exclusive - g.data_inicio).days)
        row["em_andamento"] = g.data_fim_exclusiva is None
        rows.append(row)
    df = pd.DataFrame(rows)
    for c in ["data_inicio", "data_fim_exclusiva", "data_fim"]:
        df[c] = pd.to_datetime(df[c])
    return df

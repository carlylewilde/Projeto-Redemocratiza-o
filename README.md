# Indicadores do Brasil por período presidencial — 1985–2024

Projeto de análise de dados sobre a evolução de indicadores econômicos e sociais do Brasil no período pós-redemocratização, com comparação descritiva entre períodos presidenciais.

> **Escopo analítico:** o projeto descreve diferenças observadas nas séries ao longo do tempo. Não presume causalidade entre governo e resultado econômico/social e não gera ranking político agregado.

## Projeto Final EBAC

A versão consolidada utilizada no projeto final da EBAC está disponível em [`ebac_final/`](ebac_final/).

Ela foi organizada a partir do pipeline mais amplo deste repositório, mantendo apenas os indicadores com cobertura histórica mais consistente para o recorte de 1985–2024 e concentrando a análise em duas dimensões: **economia** e **indicadores sociais**.

### Pergunta de análise

**Como evoluíram os principais indicadores econômicos e sociais do Brasil entre 1985 e 2024, e quais diferenças podem ser observadas entre os períodos presidenciais?**

### Indicadores utilizados na versão EBAC

- Crescimento real do PIB
- PIB per capita real
- IPCA acumulado no ano
- Taxa de desemprego harmonizada
- Índice de Desenvolvimento Humano (IDH)
- Expectativa de vida
- Mortalidade infantil

### Fontes utilizadas

A versão final combina dados públicos de:

- **World Bank / World Development Indicators** — crescimento do PIB, PIB per capita real, desemprego, expectativa de vida e mortalidade infantil;
- **Banco Central do Brasil / SGS** — série mensal do IPCA;
- **UNDP / Human Development Reports, via Our World in Data** — IDH.

### Preparação aplicada aos dados

Foram mantidas três tabelas analíticas principais: indicadores econômicos, indicadores sociais e dimensão de períodos presidenciais. O tratamento inclui padronização de datas e unidades, identificação de fonte e frequência, associação ao período presidencial, marcação de anos de transição e criação de colunas derivadas.

O IPCA anual foi calculado pela composição das taxas mensais, e não por média simples. Os anos de transição permanecem nas séries históricas, mas são excluídos das estatísticas agregadas por período presidencial.

### Pontos utilizados na análise exploratória

A versão EBAC foi estruturada em sete frentes de análise:

1. evolução temporal dos sete indicadores;
2. média e mediana por período presidencial;
3. distribuições e identificação de outliers pelo intervalo interquartil (IQR);
4. correlação de Pearson entre indicadores;
5. dispersão entre PIB per capita e indicadores sociais;
6. variação anual dos indicadores selecionados;
7. comparação consolidada por período presidencial.

### Dashboard final

O dashboard final foi desenvolvido em HTML com Plotly e possui navegação lateral, indicadores de destaque, séries históricas, comparação por período, cobertura amostral, matriz de correlação, scatterplots e seção metodológica.

Arquivos principais da versão final:

- [`ebac_final/README.md`](ebac_final/README.md)
- [`ebac_final/dashboard/dashboard_indicadores_redemocratizacao.html`](ebac_final/dashboard/dashboard_indicadores_redemocratizacao.html)
- [`ebac_final/docs/RELATORIO_FINAL.md`](ebac_final/docs/RELATORIO_FINAL.md)
- [`ebac_final/src/gerar_dashboard.py`](ebac_final/src/gerar_dashboard.py)
- [`ebac_final/dados/`](ebac_final/dados/)

---

## Estrutura do projeto original

```text
.
├── analysis/
├── dashboard/
├── data/
├── etl/
├── metadata/
├── notebooks/
├── tests/
├── ebac_final/
├── run_pipeline.py
└── requirements.txt
```

O projeto original preserva um pipeline mais amplo de extração, normalização e análise de indicadores macroeconômicos, sociais e fiscais. A pasta `ebac_final/` representa o recorte consolidado e documentado para a entrega acadêmica.

## Governos como unidade de análise

O catálogo contempla Sarney, Collor, Itamar, FHC I, FHC II, Lula I, Lula II, Dilma I, Dilma II, Temer, Bolsonaro e Lula III. O recorte principal termina em 31/12/2024.

## Instalação do pipeline original

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução do pipeline original

```bash
python run_pipeline.py --stage all
```

Etapas isoladas:

```bash
python run_pipeline.py --stage extract
python run_pipeline.py --stage normalize
python run_pipeline.py --stage analyze
python run_pipeline.py --stage export
```

## Testes

```bash
pytest -q
```

## Fontes do projeto ampliado

- Banco Central do Brasil — SGS
- IBGE — SIDRA
- IpeaData
- DataSUS / TabNet
- Portal da Transparência
- World Bank Indicators API
- Tribunal Superior Eleitoral e fontes oficiais para metadados históricos

Consulte a documentação de cada camada do repositório para detalhes metodológicos e de cobertura.

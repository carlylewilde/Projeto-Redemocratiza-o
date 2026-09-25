# Indicadores do Brasil por período presidencial — 1985–2024

Pipeline Python para extração, tratamento, normalização e análise estatística de indicadores macroeconômicos, sociais e fiscais do Brasil no período pós-redemocratização. O repositório produz uma camada `tidy` pronta para dashboard e um dashboard HTML autocontido em `dashboard/index.html`.

> **Escopo analítico:** comparação descritiva de períodos presidenciais. O projeto não presume causalidade entre governo e resultado econômico/social e não gera placar agregado ou ranking político.

## Estrutura

```text
.
├── analysis/
│   ├── descriptive.py
│   ├── export.py
│   ├── relationships.py
│   ├── significance.py
│   ├── trends.py
│   └── relatorio_metodologico.md
├── dashboard/
│   └── index.html
├── data/
│   ├── raw/
│   └── processed/
├── etl/
│   ├── common.py
│   ├── extract_bcb.py
│   ├── extract_datasus.py
│   ├── extract_ibge.py
│   ├── extract_ipeadata.py
│   ├── extract_transparencia.py
│   ├── extract_worldbank.py
│   └── normalize.py
├── metadata/
│   ├── governments.py
│   └── indicators.py
├── notebooks/
│   └── analise_exploratoria.ipynb
├── tests/
│   ├── test_governments.py
│   └── test_normalize.py
├── .github/workflows/tests.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── run_pipeline.py
```

## Governos como unidade de análise

O catálogo contém Sarney, Collor, Itamar, FHC I, FHC II, Lula I, Lula II, Dilma I, Dilma II, Temer, Bolsonaro e Lula III. Collor/Itamar e Dilma II/Temer usam a data de início do exercício interino do sucessor para atribuição das observações; a data formal posterior do desfecho é preservada em notas.

Lula III é sempre sinalizado como período parcial/em andamento; o recorte principal deste projeto termina em **31/12/2024**.

## Fontes

- Banco Central do Brasil — SGS: <https://www.bcb.gov.br/estabilidadefinanceira/seriestemporais>
- API SGS: <https://api.bcb.gov.br/>
- IBGE — SIDRA: <https://sidra.ibge.gov.br/>
- API SIDRA: <https://apisidra.ibge.gov.br/>
- IpeaData: <http://www.ipeadata.gov.br/>
- DataSUS/TabNet: <https://datasus.saude.gov.br/informacoes-de-saude-tabnet/>
- Portal da Transparência — API/Dados Abertos: <https://portaldatransparencia.gov.br/api-de-dados/> e <https://portaldatransparencia.gov.br/download-de-dados/>
- World Bank Indicators API v2: <https://datahelpdesk.worldbank.org/knowledgebase/articles/889392>
- Datas de exercício presidencial: <https://www.gov.br/cti/pt-br/trajetoria-historica/presidentes-da-republica-desde-a-criacao-do-cti>
- Coligações recentes: Tribunal Superior Eleitoral — <https://www.tse.jus.br/>

## Instalação

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Para despesas do Portal da Transparência:

```bash
cp .env.example .env
# Defina TRANSPARENCIA_API_KEY no ambiente.
```

## Execução

Pipeline completo:

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

Ignorar cache e consultar novamente as APIs:

```bash
python run_pipeline.py --stage extract --force
```

## Outputs gerados

- `data/processed/painel_governos.parquet` — formato tidy: data × indicador × governo.
- `data/processed/resumo_estatistico_por_governo.csv` — formato largo, uma linha por período presidencial.
- `data/processed/resumo_estatistico_longo.csv` — governo × indicador × estatística.
- `data/processed/painel_governos.json` — JSON compacto para front-end.
- `analysis/outputs/correlacoes_mensais.csv` — correlações exploratórias.
- `analysis/outputs/rupturas_detectadas.csv` — rupturas exploratórias detectadas por PELT.

## Normalização: decisões obrigatórias

### Deflação

Valores monetários nominais são convertidos para reais de dezembro de 2024 pelo IPCA. A regra é explícita no código:

```text
valor_real_t = valor_nominal_t × (P_base / P_t)
```

Não compare reais nominais entre décadas.

### Quebras metodológicas

A coluna `quebra_metodologica` é preservada. PNAD Contínua não é tratada como continuação automática da PNAD antiga. Para PIB, a série SIDRA corrente é uma série revisada/retropolada; por isso o projeto não inventa uma quebra dentro do vintage atual apenas pela data de publicação do novo sistema de contas.

### Mês de mandato

`mes_mandato` e `percentual_mandato_decorrido` permitem comparar trajetórias com durações diferentes.

### Base 100

`indice_base100` mede trajetória relativa ao primeiro ponto do mandato. Não representa nível absoluto nem “qualidade” do governo.

### Ajuste sazonal

STL é usado quando a série e o número de observações permitem. X-13 pode ser acrescentado em ambientes que tenham o binário instalado.

Consulte `analysis/relatorio_metodologico.md` antes de interpretar os resultados.

## Testes

```bash
pytest -q
```

Os testes verificam, entre outros pontos, a matemática da deflação, da indexação base 100 e a ausência de sobreposição entre períodos presidenciais.

## Dashboard

Abra `dashboard/index.html` diretamente no navegador. Ele usa dados demonstrativos embutidos para funcionar sem servidor e contém comentários indicando dois pontos de integração:

1. substituir o objeto JS de demonstração por dados reais;
2. em GitHub Pages/servidor HTTP, carregar `data/processed/painel_governos.json` via `fetch`.

O card tabular foi implementado como **Comparação por Indicador em ordem cronológica**, e não como ranking de governos.

## GitHub Pages

No GitHub, configure **Settings → Pages → Deploy from a branch** e aponte para a branch `main`. O mesmo dashboard já está copiado para `index.html` na raiz, então a página inicial fica pronta para publicação.

## Reprodutibilidade

- Todas as linhas carregam `fonte` e `data_extracao`.
- Cache local evita chamadas repetidas.
- APIs usam retry/backoff.
- Séries anuais em anos de transição fora de 1º de janeiro são marcadas como atribuição ambígua.
- Lula III permanece identificado como parcial.

# Dashboard Indicadores - Redemocratização

## Visão geral

Este projeto analisa a evolução de indicadores econômicos e sociais do Brasil entre 1985 e 2024, com recorte por períodos presidenciais. O objetivo é observar mudanças de longo prazo, diferenças entre períodos e relações estatísticas entre as séries, sem atribuir causalidade direta aos governos.

### Pergunta de análise

**Como evoluíram os principais indicadores econômicos e sociais do Brasil entre 1985 e 2024, e quais diferenças podem ser observadas entre os períodos presidenciais?**

## Indicadores utilizados

- Crescimento real do PIB
- PIB per capita real
- IPCA acumulado no ano
- Taxa de desemprego harmonizada
- IDH
- Expectativa de vida
- Mortalidade infantil

## Fontes públicas

- World Bank / World Development Indicators: crescimento do PIB, PIB per capita real, desemprego, expectativa de vida e mortalidade infantil.
- Banco Central do Brasil / SGS: IPCA mensal.
- UNDP / Human Development Reports, disponibilizado pela Our World in Data: IDH.
- A classificação dos períodos presidenciais é mantida no arquivo `dados/governos.csv` como dimensão temporal do projeto.

## Tratamento dos dados

A camada analítica padroniza as séries em frequência anual e inclui campos auxiliares como ano, grupo do indicador, fonte, unidade, período presidencial e marcação de anos de transição.

O IPCA anual foi obtido por composição das taxas mensais:

`IPCA_ano = [produto(1 + IPCA_mes/100) - 1] x 100`

Os anos de transição permanecem nas séries históricas, mas são excluídos das estatísticas agregadas por período presidencial. O PIB per capita real também possui índice base 100 e variação anual. IDH, expectativa de vida e mortalidade infantil possuem transformações anuais específicas para apoiar a análise.

## Análise exploratória

Foram desenvolvidas sete frentes de análise:

1. evolução temporal dos indicadores;
2. média e mediana por período presidencial;
3. distribuições e identificação de outliers pelo IQR;
4. correlação de Pearson entre indicadores;
5. dispersão entre PIB per capita e indicadores sociais;
6. variações anuais;
7. comparação consolidada por período.

## Principais resultados descritivos

- O PIB per capita real apresentou variação acumulada de aproximadamente **55.1%** entre 1985 e 2024.
- A expectativa de vida aumentou aproximadamente **12.04 anos** ao longo da série.
- A mortalidade infantil apresentou redução acumulada de aproximadamente **80.3%**.
- O IDH passou de **0.641** para **0.786** entre o primeiro e o último ano disponível.
- PIB per capita real e IDH apresentaram correlação de Pearson de aproximadamente **0.966**.
- PIB per capita real e desemprego apresentaram correlação de aproximadamente **0.092**, indicando baixa associação linear na série estudada.
- O IPCA é exibido em dois intervalos no dashboard, 1985–1994 e 1995–2024, porque a diferença de escala prejudicava a leitura do período posterior.

Esses resultados são descritivos. Correlação não implica causalidade, e a coincidência temporal entre um indicador e um período presidencial não é tratada como efeito direto do governo correspondente.

## Dashboard

O arquivo principal está em:

`dashboard/dashboard_indicadores_redemocratizacao.html`

Basta abrir o arquivo em um navegador. O painel contém navegação lateral e as seções:

- Visão Geral
- Economia
- Indicadores Sociais
- Comparação por Período
- Correlações
- Insights & Metodologia

O dashboard foi desenvolvido em HTML com gráficos interativos em Plotly.

O arquivo `src/gerar_dashboard.py` reconstrói o dashboard final a partir das bases da pasta `dados/`, mantendo a mesma estrutura, gráficos, controles e organização visual do arquivo entregue.

## Execução local

Com Python 3 instalado:

```bash
pip install -r requirements.txt
python src/preparar_dados.py
python src/gerar_dashboard.py
```

O dashboard será gerado em:

`dashboard/dashboard_indicadores_redemocratizacao.html`

## Estrutura do projeto

```text
Dashboard_Indicadores_Redemocratizacao_ENTREGA_FINAL/
├── README.md
├── requirements.txt
├── dados/
├── analises/
├── dashboard/
├── docs/
└── src/
```

## Limitações

As séries possuem janelas históricas diferentes. O desemprego harmonizado começa em 1991 e o IDH em 1990. Além disso, períodos presidenciais incompletos ou com poucas observações exigem cautela. O trabalho não controla fatores externos, defasagens, mudanças metodológicas das fontes ou relações causais entre política pública e indicadores.

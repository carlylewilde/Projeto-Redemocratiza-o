# Relatório Final — Indicadores Econômicos e Sociais do Brasil, 1985–2024

## 1. Objetivo

O projeto foi desenvolvido para analisar a evolução de sete indicadores econômicos e sociais no Brasil entre 1985 e 2024. A unidade de comparação temporal é o período presidencial, mas a análise permanece descritiva. O objetivo não é atribuir resultados diretamente a presidentes ou políticas específicas.

## 2. Bases de dados

A análise final utiliza três tabelas principais:

| Tabela | Linhas | Colunas | Finalidade |
|---|---:|---:|---|
| indicadores_economicos.csv | 120 | 16 | PIB, PIB per capita e IPCA |
| indicadores_sociais.csv | 148 | 16 | desemprego, IDH, expectativa de vida e mortalidade infantil |
| governos.csv | 12 | 10 | dimensão dos períodos presidenciais |

As duas tabelas de indicadores possuem mais de 100 registros e mais de 5 colunas, além de campos de data e ano.

## 3. Preparação

Os dados foram padronizados em frequência anual. Foram tratados formatos, unidades, identificação do indicador, fonte, frequência e associação com a dimensão de períodos presidenciais.

Foram adicionadas colunas derivadas para apoiar a exploração:

- `ano`;
- `grupo_indicador`;
- `governo`;
- `periodo_transicao`;
- `comparavel_governo`;
- `indice_base_100`, quando aplicável;
- `variacao_anual`, quando aplicável.

O IPCA anual é calculado por composição das taxas mensais, e não por média simples.

## 4. Regra para anos de transição

Os anos marcados como transição permanecem nos gráficos históricos, mas não entram nas médias, medianas e demais estatísticas agregadas por período presidencial. Essa regra evita atribuir integralmente um ano com mudança de governo a apenas um período.

## 5. Análise exploratória

### 5.1 Evolução temporal

As sete séries foram analisadas ao longo de suas respectivas janelas. Para o IPCA, a visualização foi separada em 1985–1994 e 1995–2024, pois os valores muito elevados do primeiro intervalo comprimiam a escala do segundo.

### 5.2 Tendência central por período

Foram calculadas média, mediana, desvio padrão, mínimo, máximo e número de anos válidos por período presidencial. Períodos com menos de três observações são sinalizados como amostra curta.

### 5.3 Distribuição e outliers

A distribuição foi observada por histogramas e boxplots. O critério de IQR foi utilizado para sinalizar valores extremos. Os outliers não foram removidos automaticamente, pois podem representar eventos históricos reais.

### 5.4 Correlações

A matriz de Pearson foi calculada par a par, utilizando somente anos comuns entre cada dupla de indicadores. Entre as associações observadas estão:

- PIB per capita real × IDH: **r = 0.966**;
- PIB per capita real × desemprego: **r = 0.092**;
- expectativa de vida × mortalidade infantil: associação negativa elevada.

Essas correlações não são interpretadas como causalidade. Séries com tendência temporal semelhante podem apresentar correlações elevadas mesmo sem relação causal direta.

### 5.5 Dispersões

Foram construídos scatterplots entre PIB per capita real e IDH, expectativa de vida, mortalidade infantil e desemprego. Cada ponto representa um ano comum entre as duas séries.

### 5.6 Variações anuais

As transformações foram aplicadas somente aos indicadores em que a leitura anual acrescenta informação:

- PIB per capita real: variação percentual;
- IDH: variação absoluta;
- expectativa de vida: variação absoluta;
- mortalidade infantil: variação percentual.

### 5.7 Comparação consolidada

O painel consolidado reúne média, mediana, dispersão e cobertura amostral por período. Não foi construído escore geral ou ranking de governos.

## 6. Resultados principais

No horizonte estudado, o PIB per capita real aumentou aproximadamente **55.1%** entre 1985 e 2024. A expectativa de vida aumentou **12.04 anos**, enquanto a mortalidade infantil caiu aproximadamente **80.3%**. O IDH aumentou de **0.641** para **0.786** no período coberto pela série.

O crescimento anual do PIB apresentou elevada volatilidade ao longo da série. O IPCA possui comportamento muito distinto antes e depois de 1994, razão pela qual as duas janelas são apresentadas separadamente no painel.

Os indicadores sociais estruturais apresentam associações fortes entre si e com o nível do PIB per capita, enquanto o desemprego apresenta relação linear fraca com o nível do PIB per capita na série analisada.

## 7. Dashboard

O dashboard final está no arquivo:

`dashboard/dashboard_indicadores_redemocratizacao.html`

O painel foi organizado com navegação lateral e apresenta visão geral, economia, indicadores sociais, comparação por período, correlações e notas metodológicas.

## 8. Limitações

A análise possui limitações importantes:

- as séries não começam no mesmo ano;
- períodos presidenciais incompletos possuem menos observações;
- mudanças metodológicas nas bases originais podem afetar comparações históricas;
- a análise não estima efeitos causais;
- choques externos e defasagens não são isolados;
- tendências temporais podem aumentar correlações entre séries.

## 9. Conclusão

O conjunto de dados permite acompanhar, em uma única estrutura, mudanças econômicas e sociais do Brasil ao longo de aproximadamente quatro décadas. A combinação de séries temporais, estatísticas descritivas, análise de dispersão, outliers e correlações fornece uma visão consistente da evolução dos indicadores, preservando as diferenças de cobertura e evitando atribuições causais que os dados utilizados não sustentam.

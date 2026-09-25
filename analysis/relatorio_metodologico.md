# Relatório metodológico — Brasil pós-redemocratização (1985–2024)

## 1. Objetivo e unidade de análise

O projeto organiza indicadores macroeconômicos, sociais e fiscais do Brasil por **período presidencial**, e não apenas por nome do presidente. FHC I/FHC II, Lula I/Lula II, Dilma I/Dilma II e Lula III são tratados separadamente; mandatos incompletos e complementações também.

A análise é **descritiva e estatística**, não causal. Uma observação ocorrida durante um governo não prova que o governo a causou. Política monetária, Congresso, entes subnacionais, defasagens de políticas anteriores, commodities, crises externas, demografia e choques sanitários podem afetar os mesmos indicadores.

## 2. Regra temporal dos governos

Nas sucessões extraordinárias, a janela acompanha quem efetivamente exercia a Presidência:

- Collor: janela termina em **02/10/1992**, quando Itamar Franco passou a exercer interinamente a Presidência; a renúncia ocorreu em 29/12/1992.
- Itamar: janela inicia em **02/10/1992**, incluindo o período interino.
- Dilma II: janela termina em **12/05/2016**, quando Michel Temer passou a exercer interinamente a Presidência; o impeachment foi concluído em 31/08/2016.
- Temer: janela inicia em **12/05/2016**, incluindo o período interino.
- Lula III: período **parcial/em andamento**; o recorte analítico deste projeto termina em 31/12/2024.

A implementação usa intervalos `[data_inicio, data_fim_exclusiva)`, evitando sobreposição.

## 3. Fontes

### Banco Central — SGS
Câmbio comercial venda (1), Selic meta (432), IPCA (433), IGP-M (189), dívida bruta/PIB (13762), reservas internacionais (13621).

### IBGE — SIDRA
Contas Nacionais Trimestrais (1846/6612) e PNAD Contínua (4099/6381). A cobertura varia por tabela; o pipeline não preenche anos ausentes por interpolação artificial.

### IpeaData
Usado para séries sociais longas, especialmente Gini, salário mínimo real e pobreza. O extrator faz descoberta por metadados e aceita override por variável de ambiente.

### DataSUS
`extract_datasus.py` aceita consultas TabNet parametrizadas e calcula mortalidade infantil a partir de SIM/SINASC. Como formulários/definições variam por base, o payload da consulta deve ficar explícito.

### Portal da Transparência
A API exige token. Para grandes volumes e histórico, arquivos de Dados Abertos são preferíveis à paginação de API. O projeto não inventa cobertura anterior à fonte.

### World Bank
Usado como cross-check/complemento anual para PIB per capita, crescimento, expectativa de vida, mortalidade infantil e Gini.

## 4. Deflação

**Nunca se compara R$ nominal de 1985 com R$ nominal de 2024.**

Para séries monetárias nominais, o pipeline constrói um índice de preços a partir do IPCA mensal e converte cada observação para preços do mês-base:

`valor_real_t = valor_nominal_t × (P_base / P_t)`

O mês-base padrão é dezembro de 2024. Quando aplicável, o dataset preserva `valor_nominal`, `valor_real`, `deflacionado` e `base_deflator`.

## 5. Quebras metodológicas

A coluna `quebra_metodologica` permanece no dataset.

- **PNAD → PNAD Contínua:** a PNAD Contínua inicia em 2012 e não é tratada como continuação mecânica da pesquisa anterior.
- **Contas Nacionais:** a série SIDRA corrente é revisada/retropolada sob o sistema vigente; portanto o pipeline não cria uma quebra artificial dentro do vintage atual apenas pela data de publicação de uma nova metodologia. Se vintages diferentes forem concatenados, a quebra deve ser registrada em `metadata/indicators.py`.

Taxas que cruzam uma quebra marcada devem ser tratadas como não comparáveis sem nota.

## 6. Frequência e ponderação implícita

Séries diárias são harmonizadas para mês para evitar peso estatístico desproporcional:

- câmbio: média mensal;
- Selic meta: último valor do mês;
- reservas: último valor do mês.

Séries mensais, trimestrais e anuais mantêm sua frequência natural.

## 7. Anos de transição

Indicadores anuais podem misturar dois governos quando a troca ocorre no meio do ano. O pipeline marca `atribuicao_governo_ambigua=True` e `comparacao_direta_valida=False` em anos desse tipo (por exemplo 1985, 1992 e 2016), evitando atribuir o ano inteiro a um único governo.

## 8. Mês de mandato e eixo relativo

Cada observação recebe:

- `mes_mandato`: mês 1, 2, 3... desde o início do período;
- `percentual_mandato_decorrido`: posição relativa na janela considerada.

Isso permite comparar trajetórias de mandatos com durações diferentes.

## 9. Base 100

Para comparar **trajetória**, não nível:

`indice_base100_t = valor_t / valor_inicial × 100`

Base 100 responde “quanto mudou desde o início?”, não “qual governo tinha o melhor nível”.

## 10. Ajuste sazonal

STL (`statsmodels.tsa.seasonal.STL`) é aplicado somente quando a série é marcada como sazonal e há observações suficientes. O dataset preserva valor original e `valor_ajustado_sazonal`. X-13ARIMA-SEATS pode ser acrescentado quando o binário externo estiver disponível.

## 11. Estatística descritiva por governo

Por indicador e período são calculados média, mediana, desvio-padrão, coeficiente de variação, mínimo, máximo, CAGR, volatilidade, inclinação OLS, p-valor e R² da tendência, além da proporção de observações diretamente comparáveis.

Mandatos parciais são sinalizados e não devem ser lidos como equivalentes a um mandato completo.

## 12. Ruptura, tendência e choques

O projeto inclui teste de Chow para pontos conhecidos, detecção exploratória de rupturas com `ruptures`/PELT, decomposição temporal e flags para crise financeira global, recessão brasileira de 2015–2016 e pandemia de COVID-19. Coincidência temporal entre ruptura e troca de governo **não identifica causa**.

## 13. Correlação e Granger

Correlação, correlação com defasagens e Granger são exploratórios. Granger significa ganho de poder preditivo temporal sob uma especificação; não prova mecanismo causal.

## 14. Significância

O módulo permite ANOVA/Kruskal-Wallis para grupos definidos explicitamente pelo pesquisador e teste t/Welch entre dois períodos. Sempre são reportados p-valor e Cohen's d. O projeto não embute classificação ideológica de governos.

## 15. Índices compostos

O repositório não gera um placar agregado de “melhor governo”. Combinar crescimento, inflação, desemprego e outros indicadores exige pesos normativos. Caso o usuário crie um índice composto, os pesos devem ser explícitos, editáveis e tratados como escolha subjetiva.

## 16. Limitações

1. Cobertura temporal varia por fonte.
2. Hiperinflação e mudanças monetárias tornam séries nominais antigas especialmente inadequadas sem deflação.
3. PIB e pesquisas domiciliares passam por revisões metodológicas.
4. Dados anuais têm baixa resolução para transições no meio do ano.
5. Políticas têm defasagens; atribuir todo resultado ao presidente em exercício é simplificação.
6. Choques externos e condições herdadas importam.
7. Lula III está incompleto no recorte 2023–2024.
8. Fontes oficiais podem revisar valores históricos; por isso `data_extracao` é preservada.

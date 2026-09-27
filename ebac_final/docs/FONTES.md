# Fontes e referências de dados

## World Bank / World Development Indicators

API utilizada no pipeline:
https://api.worldbank.org/v2/country/BRA/indicator/

Indicadores utilizados no recorte final:
- NY.GDP.MKTP.KD.ZG — crescimento real do PIB
- NY.GDP.PCAP.KD — PIB per capita real
- SL.UEM.TOTL.ZS — desemprego harmonizado
- SP.DYN.LE00.IN — expectativa de vida
- SP.DYN.IMRT.IN — mortalidade infantil

## Banco Central do Brasil / SGS

API:
https://api.bcb.gov.br/dados/serie/bcdata.sgs

Uso no projeto:
- série mensal do IPCA, posteriormente composta para frequência anual.

## UNDP / Human Development Reports / Our World in Data

Arquivo utilizado:
https://ourworldindata.org/grapher/human-development-index.csv

Uso no projeto:
- Índice de Desenvolvimento Humano (IDH).

## Períodos presidenciais

A dimensão temporal está registrada em `dados/governos.csv`. A classificação operacional foi usada apenas para agrupamento descritivo das observações.

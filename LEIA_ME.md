# Etapa 2 — análise exploratória de operações revisada em 07/10/2026

Abra relatorio_operacoes.html para consultar os resultados e gráficos. Os arquivos CSV de mensal, produtos, clientes e pedidos detalham os cálculos. indicadores.json contém os controles de conciliação. A pasta powerbi contém CSVs do modelo, medidas DAX e o roteiro do dashboard. A pasta graficos contém PNGs e SVGs para exportar.

Reprodução: `python analisar_operacoes.py operacoes.sqlite saida`. Dependências: pandas, numpy e matplotlib. A fonte é o banco da etapa 1, sem alterações. Dados identificáveis de clientes/transportadores não são incluídos nos CSVs exportados, mas produtos e dados operacionais reais continuam presentes.

Sete valores de quantidade continuam sem interpretação segura: cinco ausentes e dois textos com unidade (7200UN e 25.000 KG). Consulte quantidades_para_conferencia.csv. As taxas de corte por pedido são baseadas na presença de corte, não exigem somar unidades e incluem essas linhas quando pedido/data são consistentes. Taxas de quantidade excluem os valores indeterminados.


Revisão de 07/10/2026: 178 datas de carregamento de 2026 para 2025, preservando mês/dia e os valores originais. Nenhuma validade foi alterada. Os scripts foram recalculados a partir da tabela de valores originais preservada na etapa 1. O novo arquivo do início do projeto é descrito em historico e no relatório, sem concatenação. Correções individuais estão em correcoes_ano.csv.

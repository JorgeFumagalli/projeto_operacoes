# Revisão de 07/10/2026

- 178 datas de carregamento com ano 2026 corrigidas para 2025 por confirmação do responsável, preservando mês/dia.
- Valores originais de data e lote preservados. Datas de validade não alteradas.
- Análises recalculadas: agosto/2025 passa de 113 para 152 pedidos. Período analisável: 08/01/2025 a 13/10/2025.
- Total analisável permanece 1.826 pedidos, com 43 pedidos com corte (2,35%).
- Estimativas de lote recalculadas: 1.219 estimados e 453 ainda ausentes. Lotes originalmente registrados permanecem 4.756.
- Arquivo inicial contém 5.661 registros; datas válidas de 26/06/2024 a 06/01/2025. Mantido separado por diferenças de cadastro/estrutura e necessidade de validação dos pedidos.
- Planilha inicial e datas de validade não foram modificadas. A base tratada usa valores originais preservados na extração da etapa 1, sem reutilizar as estimativas anteriores como âncoras.
- Pendências e candidatos a duplicata mantidos. Marcas de erro do Excel em placa/motorista/descrição são preexistentes e não foram reparadas nesta correção de ano.

## Reprodução dos dados e gráficos

python tratar_carregamentos_revisado.py operacoes.sqlite nova_base
python analisar_operacoes_revisado.py nova_base/operacoes.sqlite nova_analise --inicio "Diário de Carregamento.xlsx"

O primeiro comando lê apenas as tabelas de valores originais e de estoque do banco. O destino deve ser uma pasta diferente. Também aceita o XLSX original de 2025 como fonte. A exportação XLSX é feita pelo builder JS, com @oai/artifact-tool; os cálculos de dados/SQL e gráficos são reproduzíveis em Python.

Este pacote é de trabalho privado: o banco/planilha inclui cadastros originais. CSVs para Power BI usam identificadores substitutos de cliente e pedido.

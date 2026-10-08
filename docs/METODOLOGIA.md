# Metodologia e limites

Uma linha é um lançamento de item, não um pedido. Contar pedidos distintos evita inflar o movimento quando há vários itens.

- Quantidade atendida: valor de Qtde. Quantidade faltante: Corte. Campo Corte vazio equivale a zero, por confirmação do responsável pelo registro.
- Solicitada = atendida + faltante. Atendimento em quantidade é calculado por produto e somente com valores válidos. Unidades de produtos diferentes não são somadas.
- Datas de carregamento com ano 2026 foram corrigidas para 2025, preservando mês/dia e valor original. Regra específica confirmada para este arquivo, não recomendação genérica. Datas de validade permanecem intactas.
- Pedidos devem ter um cliente consistente e data única. A data pode ser inferida por data única válida ou maioria estrita. Empates e clientes conflitantes ficam pendentes.
- Lotes originais são preservados. Quando autorizado, o lote ausente é estimado a partir do lote numérico original do mesmo produto na data anterior mais próxima, no mesmo ano, mais a diferença de dias. Estimativas são identificadas como não verificadas e não contam como rastreabilidade comprovada.
- Duplicatas candidatas são sinalizadas e mantidas. Quantidades ambíguas não são imputadas.
- Estoque manual sem data de referência confirmada não sustenta cálculo de ruptura histórica, validade atual ou utilização da capacidade.

A planilha do início do projeto permanece separada: layout, período e cadastro de produtos diferem. Ela não comprova uma melhoria antes/depois.

O relatório HTML mede cobertura de lote sobre todas as linhas de origem. As medidas do modelo Power BI usam apenas a base consistente; os valores têm denominadores diferentes.

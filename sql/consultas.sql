-- Apenas pedidos com data única; inferências identificadas na origem.
SELECT substr(data_tratada,1,7) AS mes, COUNT(DISTINCT pedido) AS pedidos,
       COUNT(*) AS linhas_itens
FROM base_pedido_data_unica GROUP BY mes ORDER BY mes;

-- Cobertura real de registro de lote, sem contar estimativas como evidência.
SELECT lote_status, COUNT(*) AS linhas FROM carregamentos_tratados GROUP BY lote_status;

-- Quantidade por produto; não somar embalagens diferentes indiscriminadamente.
SELECT codigo_produto, SUM(quantidade) AS quantidade_na_unidade_do_produto
FROM base_pedido_data_unica WHERE quantidade > 0 GROUP BY codigo_produto;

-- Pendências por motivo.
SELECT tipo, COUNT(*) AS ocorrencias FROM pendencias GROUP BY tipo ORDER BY ocorrencias DESC;

-- Quantidades faltantes por produto. Campo Corte vazio equivale a zero, conforme regra confirmada.
SELECT codigo_produto, SUM(quantidade_faltante) AS quantidade_faltante_registrada,
       COUNT(*) AS linhas_com_falta
FROM base_pedido_data_unica WHERE quantidade_faltante > 0 GROUP BY codigo_produto;

-- Atendimento ponderado por produto, em linhas com quantidades válidas e pedido/data consistentes.
-- Não combinar quantidades de produtos em embalagens distintas em uma taxa geral.
SELECT codigo_produto, COUNT(*) AS linhas_com_quantidade_valida,
       SUM(quantidade_atendida) AS atendida, SUM(quantidade_solicitada) AS solicitada,
       1.0 * SUM(quantidade_atendida) / NULLIF(SUM(quantidade_solicitada),0) AS fracao_atendimento
FROM base_pedido_data_unica WHERE atendimento_status = 'calculado'
GROUP BY codigo_produto;

# Construção do dashboard em Power BI

1. Importar fItens.csv, fPedidos.csv, dProdutos.csv, dClientes.csv e dCalendario.csv com UTF-8, delimitador vírgula e localidade Inglês (Estados Unidos) para números com ponto decimal. Campos de identificação como texto, datas como Date, flags como número inteiro e quantidades como decimal.
2. Criar relações unidirecionais 1:* de dCalendario[data] e dClientes[cliente_id] para ambas as tabelas fato. dProdutos[codigo_produto] filtra apenas fItens[codigo_produto]. Não relacionar as tabelas fato entre si. Marcar dCalendario como tabela de datas.
3. Criar as medidas do arquivo medidas.dax uma por vez e formatar taxas como percentual.
4. Página Expedição: cartões de pedidos e linhas de itens, pedidos por ano-mês, ranking de produtos por pedidos e clientes por pedidos. Seletores de data, produto e cliente. Mostrar ausência de registros como lacuna, sem concluir zero atividade.
5. Página Atendimento: pedidos com corte e taxa de pedidos com corte, evolução mensal e ranking por produto com numerador e denominador. Mostrar atendimento em quantidade apenas quando um produto for selecionado. Tooltip deve informar a unidade/embalagem do produto após validação do cadastro.
6. Página Rastreabilidade: cobertura original, linhas com lotes registrados/estimados/ausentes e linhas com datas inferidas/duplicatas candidatas. Nesta página os denominadores são a base consistente, e não a origem inteira. O relatório fornece ambas as coberturas para conciliação.
7. fPedidos serve à análise de pedidos e clientes sem filtro de produto. Use a medida Pedidos baseada em fItens nos visuais que precisam reagir ao filtro de produto; não use contagens de fPedidos nesses visuais.

## Significado do filtro de produto

Com produto selecionado, Pedidos com corte conta falta daquele produto. Sem filtro, conta pedido com falta em qualquer item. Não somar pedidos de cada produto. Não somar unidades de produtos distintos para obter um atendimento físico geral.

## Escopo

CSVs excluem pedidos/clientes/datas inconsistentes. Estimativas de lote continuam marcadas. Clientes e pedidos recebem identificadores substitutos; os arquivos gerados pela demonstração pública são inteiramente sintéticos. Estoque fica fora desta etapa porque sua data de referência ainda não foi confirmada. Não há arquivo PBIX nesta entrega.

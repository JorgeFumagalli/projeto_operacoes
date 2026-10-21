# Dashboard de inteligência de expedição

Relatório Power BI concluído, com três páginas e dados inteiramente sintéticos. O arquivo `inteligencia_expedicao_demo.pbix` apresenta a demonstração pública; os resultados reais agregados estão em [RESULTADOS_REAIS.md](../docs/RESULTADOS_REAIS.md).

## Abrir e atualizar

1. Baixar `inteligencia_expedicao_demo.pbix` desta pasta e abrir no Power BI Desktop. A visualização utiliza os dados importados e salvos no arquivo; a atualização depende das fontes locais.
2. Para reproduzir as fontes, executar na raiz do projeto:

```bash
python -m pip install -r requirements.txt
python src/executar_demo.py
python tests/validar_demo.py
```

3. Os cinco CSVs ficam em `outputs/demo/analise/powerbi/`: `fItens.csv`, `fPedidos.csv`, `dProdutos.csv`, `dClientes.csv` e `dCalendario.csv`.
4. No Power BI Desktop, abrir **Transformar dados**. Em cada uma das cinco consultas, selecionar a etapa **Fonte** e ajustar o caminho para o CSV correspondente no computador. Usar a engrenagem da etapa, quando disponível, ou editar apenas o caminho na expressão da Fonte. Preservar as etapas de transformação.
5. Usar **Fechar e aplicar**, atualizar e conferir os controles abaixo. Salvar com filtros em Todos, período completo e Visão Geral aberta.

A geração dos CSVs não cria nem altera o PBIX automaticamente. O arquivo PBIX é mantido no Power BI Desktop.

## Modelo de dados

Importação: UTF-8, delimitador vírgula. Identificadores como texto; datas como Data; flags como inteiro; quantidades como decimal. Interpretar números com ponto decimal usando localidade Inglês (Estados Unidos). A apresentação do relatório usa português brasileiro.

| Dimensão — lado 1 | Fato — lado muitos |
|---|---|
| `dCalendario[data]` | `fItens[data]` |
| `dCalendario[data]` | `fPedidos[data]` |
| `dClientes[cliente_id]` | `fItens[cliente_id]` |
| `dClientes[cliente_id]` | `fPedidos[cliente_id]` |
| `dProdutos[codigo_produto]` | `fItens[codigo_produto]` |

As cinco relações são ativas, 1:* e unidirecionais da dimensão para a fato. Não relacionar as fatos entre si. Marcar `dCalendario` como tabela de datas. Usar o campo de ano-mês em ordem cronológica nos eixos mensais.

Criar as medidas de [medidas.dax](medidas.dax) individualmente; criar `Situação do lote` como coluna calculada em `fItens`. O arquivo inclui uma medida de compatibilidade com o nome antigo da cobertura e uma medida complementar de atendimento em quantidade; não é necessário exibi-las nas páginas.

## Páginas publicadas

| Página | Cartões | Gráficos |
|---|---|---|
| Visão Geral | Pedidos; pedidos com corte; taxa de pedidos com corte; cobertura de lote original | Pedidos por mês; taxa de pedidos com corte por mês |
| Rastreabilidade | Linhas analisadas; lote estimado; sem lote; lote original | Situação do registro de lote por mês (%), em colunas 100% empilhadas; cobertura de lote original por produto |
| Atendimento | Pedidos; pedidos com corte; taxa de pedidos com corte; pedidos sem corte nos itens selecionados | Pedidos com corte por produto; pedidos com corte por cliente |

As três páginas têm segmentações por período, cliente e produto, usando as dimensões. A medida Pedidos usa `fItens`, inclusive para responder à seleção de produto. `fPedidos` permanece disponível para análises no grão do pedido sem filtro de produto.

Na composição mensal de lotes, usar `[Linhas de itens]`, calendário no eixo e `Situação do lote` na legenda. A cobertura por produto usa `[Cobertura de lote original]`.

## Regras de leitura

- Qtde é quantidade atendida; Corte é quantidade faltante. Corte vazio significa zero.
- Com produto selecionado, o indicador conta pedidos com falta nos produtos selecionados. Sem filtro de produto, conta pedidos com falta em qualquer item.
- Pedidos sem corte é o complemento dentro dos itens selecionados; não comprova atendimento integral de outros itens do mesmo pedido.
- Um pedido pode aparecer em vários produtos ou clientes conforme o agrupamento e os dados. Na base consistente cada pedido tem um único cliente; produtos podem compartilhar pedidos. Não somar contagens distintas por produto para obter o total.
- Lotes estimados não representam rastreabilidade comprovada. Cobertura original exclui estimativas e ausências.
- Os CSVs do modelo usam a base com pedido, cliente e data consistentes. A cobertura da origem inteira no HTML tem outro denominador.
- Quantidades de produtos com unidades diferentes não são somadas. A medida complementar de quantidade usa apenas linhas válidas de um produto selecionado.
- Ausência de registros não comprova ausência de atividade. Meses inicial e final podem ser parciais.

## Controles da demonstração

Sem filtros adicionais, período de 08/01/2025 a 15/04/2025:

| Controle | Esperado |
|---|---:|
| Pedidos | 98 |
| Pedidos com corte | 6 |
| Taxa de pedidos com corte | 6,12% |
| Pedidos sem corte nos itens selecionados | 92 |
| Linhas analisadas | 295 |
| Lote original | 220 |
| Lote estimado | 72 |
| Sem lote | 3 |
| Cobertura de lote original | 74,58% |

Conciliações: 220 + 72 + 3 = 295; 6 + 92 = 98. Pedidos mensais: janeiro 24, fevereiro 28, março 31 e abril 15. Em janeiro, 2 pedidos com corte em 24 = 8,33%. Selecionando apenas Produto fictício 1: 98 pedidos, nenhum com corte e taxa de 0%.

Estes valores pertencem ao gerador atual, não à operação real. Mudanças no gerador exigem nova conciliação e atualização do PBIX e das imagens.

## Padrão visual e evidências

Fundo claro `#F3F5F8`, visuais brancos, fonte Segoe UI. Azul `#16324F` para pedidos; laranja `#C06B27` para cortes e lotes estimados; verde-petróleo `#087F8C` para lote original; cinza `#8A949E` para ausência. Contagens inteiras e taxas com duas casas decimais.

Capturas em PNG, 1440 × 810 px, disponíveis em `docs/images/`: `dashboard_visao_geral.png`, `dashboard_rastreabilidade.png` e `dashboard_atendimento.png`.

## Limites

O PBIX é uma demonstração sintética do modelo analítico. Não contém as planilhas empresariais. Estoque sem data de referência confirmada permanece fora do painel. Os indicadores não medem atraso de entrega, perda financeira, causalidade ou melhoria antes/depois. A planilha histórica inicial não foi incorporada automaticamente ao diário de 2025.

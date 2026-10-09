# Inteligência de expedição e rastreabilidade

Análise de registros de carregamento para identificar faltas no atendimento dos pedidos e avaliar a qualidade dos dados de rastreabilidade.

**Tecnologias:** Python, Pandas, SQL, SQLite e Matplotlib.  
**Integração analítica:** modelo de dados e medidas DAX preparados para Power BI.

## Contexto

Uma operação logística utilizava planilhas para registrar carregamentos e atualizar saldos de estoque manualmente. Os registros apresentavam lotes ausentes, datas conflitantes por pedido e quantidades sem interpretação segura.

O projeto transforma esses registros em uma base auditável e indicadores de expedição, preservando os dados originais e identificando as alterações realizadas.

## Objetivos

- Medir a incidência de pedidos com falta no carregamento.
- Analisar a distribuição mensal dos pedidos.
- Avaliar a cobertura de lote originalmente registrado.
- Identificar registros que exigem conferência antes de integrar os indicadores.

## Resultados

Estudo real referente aos registros analisáveis de **08/01/2025 a 13/10/2025**.

| Indicador | Resultado |
|---|---:|
| Registros de itens na origem | 6.428 |
| Pedidos identificados | 1.900 |
| Pedidos com cliente e data consistentes | 1.826 |
| Pedidos com falta em pelo menos um item | 43 — 2,35% dos pedidos consistentes |
| Registros com lote original informado | 4.756 — 73,99% dos registros de origem |
| Pedidos separados para conferência | 74 |

![Pedidos por mês](docs/images/01_pedidos_mensais.png)

A análise evidencia duas frentes de atuação: investigar os produtos com faltas recorrentes e melhorar o preenchimento dos registros de expedição. Lotes estimados não são considerados evidência de rastreabilidade.

Os resultados completos, denominadores e gráficos estão em [Resultados do estudo](docs/RESULTADOS_REAIS.md).

## Tratamento dos dados

O processamento preserva os valores originais e registra as transformações em uma tabela de auditoria.

As principais regras são:

- **Quantidade atendida:** valor registrado em Qtde.
- **Quantidade faltante:** valor registrado em Corte; campo vazio equivale a zero, conforme regra operacional confirmada.
- **Quantidade solicitada:** quantidade atendida + quantidade faltante.
- **Pedido com corte:** pedido com quantidade faltante positiva em pelo menos um item.
- **Datas conflitantes:** resolução por data única válida ou maioria estrita, com cliente consistente. Casos sem decisão segura ficam separados.
- **Lotes ausentes:** estimativas identificadas como não verificadas; lotes originais permanecem intactos.
- **Duplicatas candidatas:** sinalizadas e preservadas.
- **Quantidades ambíguas:** mantidas como pendências, sem imputação automática.

A correção de carregamentos registrados com ano 2026 para 2025 foi confirmada pelo responsável pelos dados e aplica-se exclusivamente a este estudo. Datas de validade não foram alteradas.

Consulte [Metodologia](docs/METODOLOGIA.md) para os critérios completos.

## Executar o projeto

A versão pública utiliza **dados inteiramente sintéticos**, gerados independentemente das planilhas empresariais. A execução demonstra o processamento, mas não reproduz os indicadores do estudo real.

**Requisito:** Python 3.11 ou superior.

### Criar o ambiente

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### Instalar e executar

```bash
python -m pip install -r requirements.txt
python src/executar_demo.py
python tests/validar_demo.py
```

O relatório gerado pode ser aberto no navegador:

```text
outputs/demo/analise/relatorio_operacoes.html
```

### Saídas

- Banco SQLite com registros originais, tratados, pendências e auditoria.
- Indicadores e tabelas analíticas em CSV.
- Gráficos e relatório HTML.
- Tabelas para importação no Power BI.

As verificações validam a preservação dos registros, as regras de tratamento e os denominadores dos indicadores.

## Estrutura

| Diretório | Finalidade |
|---|---|
| `src/` | Geração dos dados sintéticos, tratamento e análise |
| `sql/` | Consultas analíticas |
| `docs/` | Metodologia e resultados agregados do estudo real |
| `powerbi/` | Medidas DAX e especificação do modelo |
| `data/` | Orientações sobre as fontes de dados |
| `tests/` | Verificações das regras de negócio |

## Power BI

O projeto inclui a especificação de um modelo estrela e medidas para análise de expedição, atendimento e rastreabilidade.

O roteiro está em [Modelo e dashboard](powerbi/ROTEIRO.md). O arquivo PBIX ainda não integra esta versão.

## Limitações

- Os dados empresariais não são distribuídos no repositório.
- Os indicadores de corte medem falta no carregamento, não atraso ou entrega ao cliente.
- Quantidades de produtos com unidades distintas não são agregadas em uma taxa física geral.
- Lotes estimados não comprovam rastreabilidade.
- O estoque não possui data de referência confirmada para análise histórica.
- Os resultados são descritivos e não comprovam impacto financeiro ou melhoria causal.
- Os meses inicial e final podem representar períodos parciais.

## Autor

**Jorge Fumagalli**  
MBA em Data Science & Analytics — USP/ESALQ, concluído em 2026.

[GitHub](https://github.com/JorgeFumagalli) · [LinkedIn](https://www.linkedin.com/in/jorge-fumagalli)
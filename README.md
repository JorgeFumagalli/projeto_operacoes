# Inteligência de expedição e rastreabilidade

**Como transformar registros manuais de carregamento em indicadores confiáveis de atendimento e qualidade de dados?**

Estudo de portfólio de **Jorge Fumagalli**, baseado em registros reais de uma operação logística. O trabalho trata inconsistências, preserva os valores de origem, documenta as regras de negócio e produz consultas SQL, gráficos e dados para Power BI.

**Python · Pandas · SQL/SQLite · Análise exploratória · Qualidade de dados · DAX**

## Problema de negócio

O diário e o estoque eram atualizados manualmente, sem conexão a um sistema. Datas conflitantes por pedido, lotes ausentes e quantidades ambíguas dificultavam uma leitura confiável da expedição. A análise busca responder: quantos pedidos foram registrados, quais tiveram falta no carregamento e qual parcela tem lote originalmente informado?

## Resultados do estudo real

| Indicador | Resultado |
|---|---:|
| Pedidos com cliente e data consistentes | 1.826 |
| Pedidos com ao menos um corte | 43 (2,35%) |
| Cobertura de lote original nas 6.428 linhas de origem | 73,99% |
| Pedidos separados para conferência | 74 |

![Pedidos por mês — estudo real de 2025](docs/images/01_pedidos_mensais.png)

Consulte [resultados e denominadores](docs/RESULTADOS_REAIS.md) e [metodologia](docs/METODOLOGIA.md). Lotes estimados não representam rastreabilidade comprovada. Os resultados são descritivos; não há impacto financeiro ou melhoria causal medida.

## Executar a demonstração pública

**Os registros da demonstração são inteiramente sintéticos.** O gerador não lê as planilhas empresariais. Seu relatório tem indicadores próprios, diferentes do estudo real. Os dados originais não são publicados.

Requer Python 3.11 ou superior. Na pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente: no Windows PowerShell, `.venv\Scripts\Activate.ps1`; no macOS/Linux, `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python src/executar_demo.py
python tests/validar_demo.py
```

Abra `outputs/demo/analise/relatorio_operacoes.html` no navegador. Essa execução gera um banco SQLite auditável, controles de qualidade, gráficos e CSVs para Power BI. Os arquivos de saída ficam fora do Git.

## Organização

| Pasta | Conteúdo |
|---|---|
| `src/` | Geração sintética, tratamento auditável e análise |
| `sql/` | Consultas sobre o banco tratado |
| `docs/` | Resultados reais agregados, gráficos e metodologia |
| `powerbi/` | Medidas DAX e roteiro do modelo estrela |
| `data/` | Política de dados e orientação para fontes privadas |
| `tests/` | Verificação de regras de negócio da demonstração |

## Decisões analíticas

- Qtde representa quantidade atendida; Corte representa quantidade faltante; Corte vazio significa zero.
- Pedidos com conflito sem resolução segura ficam separados; originais e alterações são auditados.
- Duplicatas candidatas são mantidas; lotes estimados recebem identificação própria.
- Taxas de atendimento em quantidade são calculadas por produto, evitando somar unidades diferentes.

## Estado do projeto

Tratamento, análise exploratória e demonstração executável concluídos. O modelo e as medidas para Power BI estão especificados; **o dashboard PBIX ainda não foi construído**. A planilha histórica inicial foi analisada separadamente e não integra automaticamente o diário de 2025.

## Autor

[Jorge Fumagalli](https://github.com/JorgeFumagalli) · MBA em Data Science & Analytics — USP/ESALQ, concluído em 2026.

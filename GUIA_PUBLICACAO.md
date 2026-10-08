# Publicação do projeto de expedição no GitHub

Perfil conferido: https://github.com/JorgeFumagalli/JorgeFumagalli. Seu README pessoal já apresenta o projeto Payment Fraud Detection System e o foco em Data Science / Machine Learning. O novo projeto deve ficar em um repositório próprio.

## 1. Criar o repositório

Acesse https://github.com/new, usando sua conta JorgeFumagalli.

- Nome: `inteligencia-expedicao`
- Descrição: `Análise de expedição e qualidade de dados com Python, SQL e preparação para Power BI. Estudo real com demonstração sintética reproduzível.`
- Visibilidade: Public.
- Deixe desmarcada a inicialização de README e não selecione .gitignore/licença nesta tela: o pacote já contém README e .gitignore; uma licença pode ser escolhida posteriormente.
- Clique em Create repository.

## 2. Enviar os arquivos

Extraia `inteligencia-expedicao-github.zip`. Abra a pasta `inteligencia-expedicao` extraída.

No novo repositório vazio, clique em `uploading an existing file`. Arraste o **conteúdo** da pasta para a área de upload, mantendo as subpastas `src`, `sql`, `docs`, `powerbi`, `data` e `tests`. O README deve ficar na raiz do repositório, e não dentro de outra pasta `inteligencia-expedicao`.

Inclua também `.gitignore`; alguns computadores ocultam esse arquivo. Antes de confirmar, verifique os caminhos exibidos. O pacote contém 17 arquivos, todos abaixo do limite do upload pelo navegador. Ele não contém planilhas ou bancos empresariais.

Mensagem do commit: `Adiciona estudo de expedição com demonstração reproduzível`.

Clique em Commit changes. O README será exibido na página principal do projeto.

## 3. Conferir a apresentação

- Abra os três gráficos no README/documentação e confira se carregam.
- Confirme que `src/executar_demo.py`, `requirements.txt` e `.gitignore` estão presentes.
- No About do repositório, adicione a descrição acima e tópicos como `python`, `sql`, `data-analysis`, `data-quality`, `logistics` e `power-bi`.
- Fixe o projeto no perfil em Customize your pins, mantendo o projeto de fraude em destaque também.

A URL prevista é `https://github.com/JorgeFumagalli/inteligencia-expedicao`; ela só existirá após a criação. Nenhum arquivo foi enviado à sua conta nesta entrega.

## 4. Complementar o perfil existente

Após publicar, você pode acrescentar o bloco abaixo à seção Featured Projects do seu README pessoal. O restante da apresentação já existente pode ser mantido.

```markdown
### 📦 [Shipping Analytics & Data Quality](https://github.com/JorgeFumagalli/inteligencia-expedicao)

A portfolio case study based on real operational records, with an independently generated synthetic demo for public reproducibility.

- Auditable data cleaning, business-rule validation and SQL analysis.
- 1,826 analyzable orders; 43 orders with loading shortages (2.35%).
- Original lot coverage: 73.99% of 6,428 source item records; estimates are explicitly flagged.
- Python pipeline, analytical charts and a Power BI model specification. PBIX dashboard in progress.

`Python` `Pandas` `SQL` `SQLite` `Data Quality` `DAX`
```

Seu perfil apresenta economia, ROI e redução de perdas no projeto de fraude. Se esses números vêm de simulação, identifique-os como projeções sob hipóteses no próprio perfil e no projeto. Resultados medidos em produção exigem evidência correspondente. Esta entrega não altera seu perfil pessoal.

## 5. Executar o código

As instruções completas estão no README. A demonstração gera dados inteiramente fictícios e um relatório HTML marcado como demonstração sintética. Ela não reproduz os indicadores das planilhas reais.

Verificado nesta entrega com Python 3.12.14, pandas 2.2.3, NumPy 2.3.5, Matplotlib 3.10.8 e openpyxl 3.1.5. As versões de dependências estão fixadas em requirements.txt. Os controles verificam preservação de linhas, conflitos, duplicatas, correção do ano, lotes originais, valores pendentes e denominadores.

Documentação de referência:
- https://docs.github.com/pt/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
- https://docs.github.com/pt/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile

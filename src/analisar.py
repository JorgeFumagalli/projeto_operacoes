"""Análise reproduzível. python src/analisar.py operacoes.sqlite pasta_saida
Dependências: pandas, numpy, matplotlib. Não altera a base de entrada.
"""
from pathlib import Path
import argparse, sqlite3, json, base64, html
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main(db, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/'graficos').mkdir(exist_ok=True)
    (out/'powerbi').mkdir(exist_ok=True)
    with sqlite3.connect(db) as con:
        allrows=pd.read_sql_query('SELECT * FROM carregamentos_tratados',con)
        original=pd.read_sql_query('SELECT * FROM originais_carregamentos',con)
    f=allrows[allrows.apto_pedido_data_unica.eq(1)].copy()
    f['mes']=f.data_tratada.str[:7]
    f['com_corte']=f.quantidade_faltante.gt(0)
    f['quantidade_valida']=f.percentual_atendimento.notna()
    names=allrows.cliente.fillna('SEM CLIENTE').str.upper().str.replace(r'\s+',' ',regex=True).str.strip()
    namecodes=allrows.assign(nome_normalizado=names).dropna(subset=['codigo_cliente']).groupby('nome_normalizado').codigo_cliente.agg(lambda v:set(v))
    def clientkey(r):
        name=' '.join(str(r.cliente or 'SEM CLIENTE').upper().split())
        codes=namecodes.get(name,set())
        code=r.codigo_cliente or (next(iter(codes)) if len(codes)==1 else None)
        return 'COD:'+str(code) if code else 'NOME:'+name
    f['cliente_chave']=f.apply(clientkey,axis=1)
    clientmap={v:f'Cliente {i:03d}' for i,v in enumerate(sorted(f.cliente_chave.unique()),1)}
    f['cliente_id']=f.cliente_chave.map(clientmap)
    ordermap={v:f'P{i:06d}' for i,v in enumerate(sorted(allrows.pedido.dropna().unique()),1)}
    f['pedido_id']=f.pedido.map(ordermap)
    orders=f.groupby('pedido_id').agg(data=('data_tratada','first'), cliente_id=('cliente_id','first'),
                                     linhas_itens=('linha_origem','size'), com_corte=('com_corte','max'),
                                     quantidade_completa=('quantidade_valida','all'),
                                     duplicata_candidata=('duplicata_candidata','max')).reset_index()
    orders['mes']=orders.data.str[:7]
    monthly=orders.groupby('mes').agg(pedidos=('pedido_id','size'),pedidos_com_corte=('com_corte','sum')).reset_index()
    monthly['taxa_pedidos_com_corte']=monthly.pedidos_com_corte/monthly.pedidos
    linecount=f.groupby('mes').size()
    monthly['linhas_itens']=monthly.mes.map(linecount)
    products=f.groupby('codigo_produto').agg(descricao=('descricao','first'), pedidos=('pedido_id','nunique'),
                                            linhas=('linha_origem','size'), linhas_com_corte=('com_corte','sum')).reset_index()
    cuts=f[f.com_corte].groupby('codigo_produto').pedido_id.nunique()
    products['pedidos_com_corte']=products.codigo_produto.map(cuts).fillna(0).astype(int)
    products['taxa_pedidos_com_corte']=products.pedidos_com_corte/products.pedidos
    v=f[f.quantidade_valida].groupby('codigo_produto').agg(atendida=('quantidade_atendida','sum'),
                                                        solicitada=('quantidade_solicitada','sum'), faltante=('quantidade_faltante','sum'))
    v['fracao_atendimento']=v.atendida/v.solicitada
    products=products.merge(v,left_on='codigo_produto',right_index=True,how='left')
    clients=orders.groupby('cliente_id').agg(pedidos=('pedido_id','size'),pedidos_com_corte=('com_corte','sum')).reset_index().sort_values('pedidos',ascending=False)
    clients['participacao_pedidos']=clients.pedidos/len(orders)
    lotcounts=allrows.lote_status.value_counts()
    # Sensibilidade às duplicatas candidatas, sem excluir arbitrariamente do conjunto principal.
    without=f[~f.duplicata_candidata.eq(1)].copy()
    wo_orders=without.groupby('pedido_id').com_corte.max()
    summary={
        'linhas_origem':len(allrows),'pedidos_identificados_origem':int(allrows.pedido.nunique()),
        'linhas_base_consistente':len(f),'pedidos_base_consistente':len(orders),
        'pedidos_excluidos_da_base_consistente':int(allrows.pedido.nunique()-len(orders)),
        'linhas_excluidas_da_base_consistente':len(allrows)-len(f),
        'pedidos_com_corte':int(orders.com_corte.sum()),
        'taxa_pedidos_com_corte':float(orders.com_corte.mean()),
        'pedidos_sem_corte_registrado':int((~orders.com_corte).sum()),
        'clientes_base_consistente':int(orders.cliente_id.nunique()),'produtos_base_consistente':len(products),
        'lotes_registrados_linhas':int(lotcounts.get('registrado',0)),
        'lotes_estimados_linhas':int(lotcounts.get('estimado_nao_verificado',0)),
        'lotes_ausentes_linhas':int(lotcounts.get('ausente',0)),
        'cobertura_lote_original':float(allrows.lote_original.notna().mean()),
        'cobertura_lote_original_base_consistente':float(f.lote_original.notna().mean()),
        'data_min':f.data_tratada.min(),'data_max':f.data_tratada.max(),
        'participacao_top10_clientes':float(clients.head(10).pedidos.sum()/len(orders)),
        'linhas_quantidade_indeterminada_origem':int(allrows.percentual_atendimento.isna().sum()),
        'linhas_quantidade_indeterminada_base_consistente':int((~f.quantidade_valida).sum()),
        'linhas_duplicatas_candidatas_base_consistente':int(f.duplicata_candidata.sum()),
        'pedidos_sem_linhas_duplicatas_candidatas':len(wo_orders),
        'taxa_corte_sem_linhas_duplicatas_candidatas':float(wo_orders.mean()),
    }
    # Reconciliações: incidência por pedido é contada uma única vez.
    assert monthly.pedidos.sum()==len(orders)
    assert monthly.pedidos_com_corte.sum()==orders.com_corte.sum()
    assert clients.pedidos.sum()==len(orders)
    assert orders.groupby('pedido_id').size().max()==1
    assert f.groupby('pedido_id').data_tratada.nunique().max()==1
    assert allrows.lote_status.value_counts().sum()==len(allrows)
    assert (products.pedidos_com_corte<=products.pedidos).all()
    assert np.allclose(f.loc[f.quantidade_valida,'quantidade_solicitada'],
                       f.loc[f.quantidade_valida,'quantidade_atendida']+f.loc[f.quantidade_valida,'quantidade_faltante'])
    (out/'indicadores.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    for name,df in [('mensal',monthly),('produtos',products),('clientes',clients),('pedidos',orders)]:
        df.to_csv(out/f'{name}.csv',index=False,encoding='utf-8-sig')
    problem=original[original.linha_origem.isin(allrows[allrows.percentual_atendimento.isna()].linha_origem)].copy()
    # Apenas campos necessários à conferência, sem identidade de clientes/transportadores.
    problem[['linha_origem','codigo_produto','quantidade']].to_csv(out/'quantidades_para_conferencia.csv',index=False,encoding='utf-8-sig')
    # CSVs para modelo estrela. São derivados; nenhuma identidade de cliente/placa/motorista é exportada.
    fact=f[['linha_origem','pedido_id','cliente_id','codigo_produto','data_tratada','quantidade_atendida',
            'quantidade_faltante','quantidade_solicitada','percentual_atendimento','com_corte','quantidade_valida',
            'lote_status','data_status','duplicata_candidata']].copy()
    fact.rename(columns={'data_tratada':'data'},inplace=True)
    for col in ['com_corte','quantidade_valida','duplicata_candidata']:fact[col]=fact[col].astype(int)
    fact.to_csv(out/'powerbi/fItens.csv',index=False,encoding='utf-8-sig')
    po=orders.drop(columns='mes').copy()
    for col in ['com_corte','quantidade_completa','duplicata_candidata']:po[col]=po[col].astype(int)
    po.to_csv(out/'powerbi/fPedidos.csv',index=False,encoding='utf-8-sig')
    products[['codigo_produto','descricao']].to_csv(out/'powerbi/dProdutos.csv',index=False,encoding='utf-8-sig')
    clients[['cliente_id']].sort_values('cliente_id').to_csv(out/'powerbi/dClientes.csv',index=False,encoding='utf-8-sig')
    calendar=pd.DataFrame({'data':pd.date_range(summary['data_min'],summary['data_max'])})
    calendar['ano']=calendar.data.dt.year;calendar['mes']=calendar.data.dt.month
    calendar['ano_mes']=calendar.data.dt.strftime('%Y-%m')
    calendar['mes_com_registros']=calendar.ano_mes.isin(monthly.mes).astype(int)
    calendar['data']=calendar.data.dt.strftime('%Y-%m-%d')
    calendar.to_csv(out/'powerbi/dCalendario.csv',index=False,encoding='utf-8-sig')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
                         'axes.spines.left':False,'axes.spines.bottom':False,'axes.titleweight':'bold',
                         'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
    navy='#16324f';teal='#087f8c';orange='#c06b27';grey='#c6cdd5'
    chartfiles=[]
    def save(fig,name):
        fig.tight_layout()
        fig.savefig(out/'graficos'/f'{name}.png',dpi=160,bbox_inches='tight')
        fig.savefig(out/'graficos'/f'{name}.svg',bbox_inches='tight')
        plt.close(fig);chartfiles.append(name)
    # Calendário completo: meses sem registros são lacunas, jamais zero atividade.
    months=pd.period_range(monthly.mes.min(),monthly.mes.max(),freq='M').astype(str)
    m=monthly.set_index('mes').reindex(months)
    fig,ax=plt.subplots(figsize=(12,4.8));x=np.arange(len(months));known=m.pedidos.notna()
    ax.plot(x,m.pedidos,color=navy,marker='o',linewidth=2)
    for i in x[known]:ax.annotate(str(int(m.pedidos.iloc[i])),(i,m.pedidos.iloc[i]),xytext=(0,8),textcoords='offset points',ha='center',fontsize=9)
    for i in x[~known]:ax.axvspan(i-.45,i+.45,color=grey,alpha=.25)
    ax.set_xticks(x);ax.set_xticklabels([s[5:]+'/'+s[:4] for s in months],rotation=55,ha='right')
    ax.set_ylim(0,max(m.pedidos)*1.2);ax.set_ylabel('Pedidos distintos');ax.set_title('Pedidos por mês registrado',loc='left')
    caption = ('Faixas cinza: meses sem registros disponíveis. ' if (~known).any() else '') + 'Meses inicial e final podem ser parciais.'
    ax.text(0,-.39,caption,transform=ax.transAxes,fontsize=9,color='#555')
    ax.grid(axis='y',alpha=.15);save(fig,'01_pedidos_mensais')
    fig,ax=plt.subplots(figsize=(11,4.6));x=np.arange(len(monthly))
    ax.bar(x,monthly.taxa_pedidos_com_corte*100,color=orange,width=.65)
    for i,r in monthly.iterrows():ax.text(i,r.taxa_pedidos_com_corte*100+.2,f'{r.taxa_pedidos_com_corte:.1%}\n({r.pedidos_com_corte}/{r.pedidos})',ha='center',fontsize=9)
    ax.set_xticks(x);ax.set_xticklabels(monthly.mes,rotation=45,ha='right');ax.set_ylabel('% dos pedidos do mês')
    ax.set_ylim(0,max(monthly.taxa_pedidos_com_corte)*100+3);ax.set_title('Pedidos com ao menos um corte',loc='left');save(fig,'02_cortes_mensais')
    top=products.sort_values(['pedidos_com_corte','pedidos'],ascending=False).head(10).iloc[::-1]
    labels=[f'{r.codigo_produto} · {str(r.descricao)[:35]}' for r in top.itertuples()]
    fig,ax=plt.subplots(figsize=(11,6));ax.barh(labels,top.pedidos_com_corte,color=orange)
    for i,r in enumerate(top.itertuples()):ax.text(r.pedidos_com_corte+.1,i,f'{r.pedidos_com_corte} / {r.pedidos} pedidos ({r.taxa_pedidos_com_corte:.1%})',va='center',fontsize=9)
    ax.set_xlim(0,max(top.pedidos_com_corte)*1.8);ax.set_xlabel('Pedidos com corte do produto');ax.set_title('Produtos com mais pedidos afetados por falta',loc='left');save(fig,'03_produtos_cortes')
    names=['Lote original registrado','Lote estimado','Lote ausente'];values=[summary['lotes_registrados_linhas'],summary['lotes_estimados_linhas'],summary['lotes_ausentes_linhas']]
    fig,ax=plt.subplots(figsize=(10,4));ax.barh(names[::-1],values[::-1],color=[grey,orange,teal])
    for i,vv in enumerate(values[::-1]):ax.text(vv+40,i,f'{vv:,} ({vv/len(allrows):.1%})',va='center')
    ax.set_xlim(0,max(values)*1.28);ax.set_xlabel('Linhas de itens na origem');ax.set_title('Cobertura de registro de lote',loc='left');save(fig,'04_rastreabilidade')
    topc=clients.head(10).iloc[::-1]
    fig,ax=plt.subplots(figsize=(9,5));ax.barh(topc.cliente_id,topc.pedidos,color=navy)
    for i,vv in enumerate(topc.pedidos):ax.text(vv+1,i,str(vv),va='center')
    ax.set_xlim(0,max(topc.pedidos)*1.18);ax.set_xlabel('Pedidos distintos');ax.set_title('Clientes com mais pedidos registrados',loc='left');save(fig,'05_clientes')
    # Relatório portátil, sem dependências externas, com gráficos incorporados.
    fmt=lambda v:f'{v:,}'.replace(',','.')
    cards=[('Pedidos analisáveis',fmt(len(orders))),('Pedidos com corte',f'{orders.com_corte.mean():.2%}'),
           ('Cobertura real de lote',f'{summary["cobertura_lote_original"]:.1%}'),('Pedidos separados',fmt(summary['pedidos_excluidos_da_base_consistente']))]
    charttitles=['Expedição ao longo do tempo','Frequência mensal de cortes','Prioridades de investigação','Registro real e estimativa de lote','Concentração de clientes']
    figs=''.join(f'<section><h2>{title}</h2><img alt="{title}" src="data:image/png;base64,{base64.b64encode((out/"graficos"/(name+".png")).read_bytes()).decode()}"></section>' for name,title in zip(chartfiles,charttitles))
    rank=products.sort_values(['pedidos_com_corte','pedidos'],ascending=False).head(10).copy()
    rank=rank[['codigo_produto','descricao','pedidos','pedidos_com_corte','taxa_pedidos_com_corte','fracao_atendimento']]
    for col in ['taxa_pedidos_com_corte','fracao_atendimento']:rank[col]=rank[col].map(lambda v:f'{v:.1%}' if pd.notna(v) else 'Indeterminado')
    rank.columns=['Produto','Descrição','Pedidos com produto','Pedidos com falta','Incidência de falta','Atendimento em quantidade¹']
    peak=monthly.loc[monthly.pedidos.idxmax()]
    issues_text=f'''<ul>
    <li>{fmt(len(orders))} dos {fmt(summary['pedidos_identificados_origem'])} pedidos identificados têm cliente e data consistentes. {summary['pedidos_excluidos_da_base_consistente']} pedidos e {summary['linhas_excluidas_da_base_consistente']} linhas ficam fora dessa base, incluindo linhas sem pedido.</li>
    <li>{summary['pedidos_com_corte']} pedidos apresentam falta em pelo menos um item ({summary['taxa_pedidos_com_corte']:.2%}). Isso mede corte na expedição, sem informar pontualidade ou entrega ao cliente.</li>
    <li>{peak['mes']} tem o maior número de pedidos no conjunto disponível: {int(peak['pedidos'])}. Os meses inicial e final não cobrem necessariamente meses completos.</li>
    <li>Os dez cadastros de cliente com mais pedidos representam {summary['participacao_top10_clientes']:.1%} dos pedidos analisáveis. Esta participação não mede receita, peso ou volume físico e depende da qualidade do cadastro.</li>
    <li>A cobertura de lote original é {summary['cobertura_lote_original']:.1%} das linhas da origem. Lotes estimados continuam separados e não comprovam rastreabilidade.</li>
    </ul>'''
    methodology='''<ul><li>Uma linha representa um lançamento de item. Várias linhas podem pertencer ao mesmo pedido e produto.</li>
    <li>Qtde = quantidade atendida. Corte = quantidade faltante. Corte vazio = zero, conforme confirmação do responsável. Solicitada = atendida + faltante.</li>
    <li>Pedido com corte = pedido com pelo menos uma linha com quantidade faltante positiva. O denominador é o total de pedidos distintos na base consistente.</li>
    <li>¹ Atendimento em quantidade por produto = soma atendida / soma solicitada, somente em linhas com quantidades válidas. Não combinar produtos com unidades/embalagens diferentes.</li>
    <li>Datas inferidas por pedido são mantidas e identificadas. Empates e clientes conflitantes permanecem pendentes. Duplicatas candidatas não foram removidas.</li>
    <li>A estimativa de lote soma dias corridos a um lote numérico original do mesmo produto na data anterior mais próxima, no mesmo ano. A estimativa não é lote verificado.</li>
    <li>Estoque atualizado manualmente e sem data de referência confirmada. Esta etapa não calcula validade atual, perdas por vencimento, ruptura histórica nem utilização de capacidade.</li>
    <li>Quantidades ausentes ou com unidades em texto exigem conferência. Não há imputação automática desses valores.</li>
    <li>Demonstração pública com dados inteiramente sintéticos. Os resultados desta execução não são os indicadores do estudo real.</li></ul>'''
    methodology=methodology.replace('</ul>','<li>Cliente: usar código cadastrado quando disponível ou nome associado a um único código. Sem código, usar nome normalizado. Nomes variantes sem código podem representar a mesma empresa e requerem revisão do cadastro.</li></ul>')
    sens=f'''<p>{summary['linhas_duplicatas_candidatas_base_consistente']} linhas da base consistente são candidatas a duplicata. A taxa de pedidos com corte é {summary['taxa_pedidos_com_corte']:.2%} incluindo essas linhas e {summary['taxa_corte_sem_linhas_duplicatas_candidatas']:.2%} ao retirar todas as candidatas ({summary['pedidos_sem_linhas_duplicatas_candidatas']} pedidos restantes). Este segundo cálculo é uma sensibilidade, não uma correção validada.</p>'''
    report=f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Inteligência de expedição — análise exploratória</title><style>
    body{{font:16px/1.6 system-ui,sans-serif;color:#243447;background:#f1f4f7;margin:0}}main{{max-width:1120px;margin:auto;padding:40px 24px}}h1{{font-size:36px;line-height:1.15;color:#16324f}}h2{{font-size:23px;color:#16324f}}h3{{font-size:19px}}section{{background:white;border-radius:12px;padding:26px;margin:22px 0}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}.card{{background:#16324f;color:white;padding:20px;border-radius:10px}}.card strong{{display:block;font-size:30px}}img{{max-width:100%;height:auto}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #dde3eb}}th{{background:#edf3f7}}.table{{overflow-x:auto}}.muted{{color:#536575}}@media(max-width:750px){{.cards{{grid-template-columns:repeat(2,1fr)}}h1{{font-size:28px}}main{{padding:20px 12px}}}}@media print{{body{{background:white}}section{{break-inside:avoid}}.card{{color:#16324f;background:#eef3f7}}}}</style><main>
    <p class="muted">Portfólio de Jorge Fumagalli · DEMONSTRAÇÃO SINTÉTICA</p><h1>Inteligência de expedição e rastreabilidade</h1><p>Período dos registros analisáveis: {summary['data_min']} a {summary['data_max']}. Fonte: registros fictícios gerados para demonstrar o tratamento. A regra de correção de 2026 para 2025 é específica deste estudo e aparece também nos exemplos sintéticos. Datas de validade não são alteradas.</p>
    <div class="cards">{''.join(f'<div class="card">{a}<strong>{b}</strong></div>' for a,b in cards)}</div>
    <section><h2>Resultados e implicações</h2>{issues_text}<h3>Ações sugeridas</h3><ol><li>Investigar a disponibilidade dos produtos com cortes recorrentes, conciliando pedidos, produção e estoque. Os dados não estabelecem a causa das faltas.</li><li>Tornar lote e quantidade campos obrigatórios no registro de expedição.</li><li>Conferir os pedidos com datas/clientes conflitantes e as quantidades pendentes antes de ampliar os indicadores.</li></ol></section>{figs}
    <section><h2>Produtos com mais pedidos afetados</h2><div class="table">{rank.to_html(index=False,escape=True,border=0)}</div><p>Os pedidos podem conter vários produtos. Não somar os pedidos por produto para obter o total da operação.</p></section>
    <section><h2>Sensibilidade às duplicatas</h2>{sens}</section><section><h2>Definições e limites</h2>{methodology}</section>
    <section><h2>Dashboard Power BI</h2><p>O repositório disponibiliza o relatório de demonstração em powerbi/inteligencia-expedicao_demo.pbix, com páginas de visão geral, rastreabilidade e atendimento. Esta execução gera os CSVs para atualização das fontes; não gera nem altera o PBIX automaticamente. As imagens e o relatório público utilizam dados sintéticos.</p></section></main></html>'''
    (out/'relatorio_operacoes.html').write_text(report,encoding='utf-8')
    (out/'powerbi/medidas.dax').write_text('''-- Criar cada medida separadamente. A última expressão é uma COLUNA de fItens.
-- Dimensões filtram fatos em sentido único; pedidos usam fItens para reagir a produto.
Pedidos = DISTINCTCOUNT(fItens[pedido_id])

Pedidos com corte =
COALESCE(CALCULATE(DISTINCTCOUNT(fItens[pedido_id]), fItens[com_corte] = 1), 0)

Taxa de pedidos com corte = DIVIDE([Pedidos com corte], [Pedidos])

Pedidos sem corte nos itens selecionados = [Pedidos] - [Pedidos com corte]

Linhas de itens = COUNTROWS(fItens)

Linhas com lote original =
COALESCE(CALCULATE([Linhas de itens], fItens[lote_status] = "registrado"), 0)

Cobertura de lote original = DIVIDE([Linhas com lote original], [Linhas de itens])

-- Compatibilidade com o nome utilizado na especificação inicial.
Cobertura real de lote = [Cobertura de lote original]

Linhas com lote estimado =
COALESCE(CALCULATE([Linhas de itens], fItens[lote_status] = "estimado_nao_verificado"), 0)

Linhas sem lote =
COALESCE(CALCULATE([Linhas de itens], fItens[lote_status] = "ausente"), 0)

-- Medida complementar: não integra as três páginas publicadas.
-- Seleção única de produto é necessária; cadastro/unidade precisam ser consistentes.
Atendimento em quantidade por produto =
IF(
    HASONEVALUE(dProdutos[codigo_produto]),
    DIVIDE(
        CALCULATE(SUM(fItens[quantidade_atendida]), fItens[quantidade_valida] = 1),
        CALCULATE(SUM(fItens[quantidade_solicitada]), fItens[quantidade_valida] = 1)
    ),
    BLANK()
)

-- COLUNA CALCULADA: selecionar fItens > Nova coluna. Não criar como medida.
Situação do lote =
SWITCH(
    fItens[lote_status],
    "ausente", "Sem lote",
    "estimado_nao_verificado", "Estimado — não verificado",
    "registrado", "Original registrado",
    "Não classificado"
)

-- Taxas: percentual com duas casas. Contagens: inteiro.
-- Cobertura usa somente linhas com pedido, cliente e data consistentes.
-- O HTML também apresenta cobertura na origem inteira: denominador diferente.
-- Sem registros no contexto, DIVIDE retorna BLANK: ausência não equivale a 0%.
''', encoding='utf-8')
    (out/'powerbi/ROTEIRO.md').write_text('''# Dashboard de inteligência de expedição

Relatório Power BI concluído, com três páginas e dados inteiramente sintéticos. O arquivo `inteligencia-expedicao_demo.pbix` apresenta a demonstração pública; os resultados reais agregados estão em [RESULTADOS_REAIS.md](../docs/RESULTADOS_REAIS.md).

## Abrir e atualizar

1. Baixar `inteligencia-expedicao_demo.pbix` desta pasta e abrir no Power BI Desktop. A visualização utiliza os dados importados e salvos no arquivo; a atualização depende das fontes locais.
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
''', encoding='utf-8')
    (out/'LEIA_ME.md').write_text('''# Etapa 2 — análise exploratória de operações revisada em 07/10/2026

Abra relatorio_operacoes.html para consultar os resultados e gráficos. Os arquivos CSV de mensal, produtos, clientes e pedidos detalham os cálculos. indicadores.json contém os controles de conciliação. A pasta powerbi contém CSVs do modelo, medidas DAX e o roteiro do dashboard. A pasta graficos contém PNGs e SVGs para exportar.

Reprodução: `python src/analisar.py operacoes.sqlite saida`. Dependências: pandas, numpy e matplotlib. A fonte é o banco da etapa 1, sem alterações. Dados identificáveis de clientes/transportadores não são incluídos nos CSVs exportados, mas produtos e dados operacionais reais continuam presentes.

Quantidades ausentes ou em texto ficam pendentes de conferência. Consulte quantidades_para_conferencia.csv. As taxas de corte por pedido são baseadas na presença de corte, não exigem somar unidades e incluem essas linhas quando pedido/data são consistentes. Taxas de quantidade excluem os valores indeterminados.
''',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print('TOP FALTAS',products.sort_values('pedidos_com_corte',ascending=False)[['codigo_produto','pedidos','pedidos_com_corte']].head(5).to_dict('records'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('banco',type=Path);p.add_argument('saida',type=Path)
    a=p.parse_args();main(a.banco,a.saida)

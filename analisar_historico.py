"""Leitura independente do início do projeto, sem concatenar com 2025.
python analisar_historico.py inicio.xlsx banco_2025.sqlite pasta_saida
"""
from pathlib import Path
import argparse,sqlite3,json
import openpyxl,pandas as pd

def run(source,db,out):
    w=openpyxl.load_workbook(source,read_only=True,data_only=True)
    rows=[]
    for i,r in enumerate(w['Carregamentos'].iter_rows(min_row=3,max_col=14,values_only=True),3):
        if r[3] is None:continue
        rows.append({'linha_origem':i,'pedido':str(r[2]) if r[2] is not None else None,
                     'codigo_produto':str(r[3]),'descricao':r[4],'unidade':r[5],'peso':r[6],
                     'quantidade':r[7],'lote':r[8],'data':r[9],'corte':r[12]})
    d=pd.DataFrame(rows);d['data_valida']=pd.to_datetime(d.data,errors='coerce')
    valid=d[d.data_valida.dt.year.isin([2024,2025])].copy()
    valid['mes']=valid.data_valida.dt.strftime('%Y-%m')
    monthly=valid.groupby('mes').agg(linhas_itens=('linha_origem','size'),pedidos_identificados=('pedido','nunique')).reset_index()
    with sqlite3.connect(db) as c:
        prods=set(pd.read_sql_query('SELECT DISTINCT codigo_produto FROM carregamentos_tratados',c).codigo_produto)
    summary={'registros_iniciais':len(d),'periodo_inicio':str(valid.data_valida.min().date()),
             'periodo_fim':str(valid.data_valida.max().date()),'registros_sem_pedido':int(d.pedido.isna().sum()),
             'pedidos_identificados_nao_validados':int(d.pedido.nunique()),
             'produtos_identificados':int(d.codigo_produto.nunique()),
             'codigos_produto_compartilhados_com_2025':len(set(d.codigo_produto)&prods),
             'campos_data_nao_validos':len(d)-len(valid)}
    out.mkdir(parents=True,exist_ok=True)
    monthly.to_csv(out/'mensal_inicio_projeto.csv',index=False,encoding='utf-8-sig')
    (out/'resumo_inicio.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    description='# Histórico inicial, leitura independente\n\n'+ '\n'.join(f'- {k}: {v}' for k,v in summary.items())
    description+='\n\nA base inicial contém unidade/peso em colunas próprias e um cadastro diferente. Não concatenada com 2025. Identificadores de pedido não foram validados pela regra de data única. As contagens mensais não comprovam evolução de perdas, cortes ou erros. Datas de validade não foram alteradas.\n'
    (out/'HISTORICO.md').write_text(description,encoding='utf-8')
    w.close()
    return summary,monthly

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('db',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();print(run(a.source,a.db,a.out)[0])

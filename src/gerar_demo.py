"""Gera registros fictícios independentes das planilhas empresariais."""
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import pandas as pd


def gerar(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    for i in range(100):
        day=datetime(2025,1,8)+timedelta(days=i)
        for j in range(3):
            r=dict(codigo_cliente=1000+i%12, cliente=f"Cliente fictício {i%12:02d}",
                   pedido=f"DEMO-{i:04d}", codigo_produto=f"DEMO-{j:03d}",
                   descricao=f"Produto fictício {j} CX 12X1KG", quantidade=20+i%15+j,
                   lote=str(5000+j*1000+i) if i%4 else None,
                   data=day.isoformat(), motorista=None, placa=None,
                   corte=2 if i%17==0 and j==0 else None,
                   observacoes=None, linha_origem=len(rows)+3)
            if i==12:r['data']=day.replace(year=2026).isoformat()
            if i==20 and j==2:r['data']=None
            if i==30 and j==0:r['quantidade']=None
            if i==31 and j==0:r['quantidade']='7200UN'
            if i==98 and j>0:r['cliente']='Outro cliente fictício'
            if i==99 and j==2:r['data']=(day+timedelta(days=1)).isoformat()
            if i==99 and j==1:r['data']=None
            rows.append(r)
    duplicate=rows[51].copy();duplicate['linha_origem']=len(rows)+3;rows.append(duplicate)
    stockcols=['linha_origem','codigo_produto','lote_original','descricao','referencia',
               'peso_original','quantidade','validade','local','venc_dias_original',
               'observacoes','data_snapshot','saldo_atualizacao']
    with sqlite3.connect(path) as con:
        pd.DataFrame(rows).to_sql('originais_carregamentos',con,index=False,if_exists='replace')
        pd.DataFrame(columns=stockcols).to_sql('estoque_snapshot',con,index=False,if_exists='replace')
    return path

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('saida',type=Path)
    gerar(p.parse_args().saida)

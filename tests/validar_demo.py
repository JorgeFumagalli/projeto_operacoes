"""Verificações de regras de negócio, executadas após o pipeline."""
from pathlib import Path
import sqlite3,json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'outputs/demo')
with sqlite3.connect(root/'base/operacoes.sqlite') as c:
    scalar=lambda sql:c.execute(sql).fetchone()[0]
    assert scalar('SELECT COUNT(*) FROM originais_carregamentos')==301
    assert scalar('SELECT COUNT(*) FROM carregamentos_tratados')==301
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE data_status='ano_corrigido_usuario'")==3
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE lote_original IS NOT NULL AND lote_original != lote_tratado")==0
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE lote_status='estimado_nao_verificado'")>0
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE pedido='DEMO-0098' AND apto_pedido_data_unica=1")==0
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE pedido='DEMO-0099' AND apto_pedido_data_unica=1")==0
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE duplicata_candidata=1")==2
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE quantidade_faltante < 0")==0
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE atendimento_status='calculado' AND ABS(quantidade_solicitada-quantidade_atendida-quantidade_faltante)>1e-9")==0
    assert scalar("SELECT COUNT(*) FROM carregamentos_tratados WHERE percentual_atendimento IS NULL")==2
s=json.loads((root/'analise/indicadores.json').read_text())
assert s['pedidos_base_consistente']==98
assert s['pedidos_com_corte']==6
assert s['pedidos_excluidos_da_base_consistente']==2
assert abs(s['taxa_pedidos_com_corte']-6/98)<1e-12
print('OK: preservação de registros, correção de ano, lotes, cortes, conflitos, duplicatas e denominadores.')

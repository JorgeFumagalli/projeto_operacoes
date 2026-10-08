"""Execução completa sem acesso a dados da empresa."""
from pathlib import Path
import argparse
from gerar_demo import gerar
from tratar import run
from analisar import main

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--saida',type=Path,default=Path('outputs/demo'))
    out=p.parse_args().saida
    source=gerar(out/'fonte_sintetica.sqlite')
    run(source,out/'base')
    main(out/'base/operacoes.sqlite',out/'analise')
    print('DEMONSTRAÇÃO SINTÉTICA: abra',out/'analise/relatorio_operacoes.html')

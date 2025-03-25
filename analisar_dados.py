"""
Script para analisar os dados dos CSVs antes da importação
"""
import os
import pandas as pd
from config import DIRETORIOS, ARQUIVOS

def analisar_operadoras():
    """
    Analisa o arquivo CSV das operadoras
    """
    arquivo = os.path.join(
        DIRETORIOS['dados']['operadoras_ativas'],
        ARQUIVOS['csv']['operadoras']
    )
    
    print("\n=== Análise do arquivo de operadoras ===")
    
    # Lê o arquivo
    df = pd.read_csv(arquivo, encoding='latin1', sep=';')
    
    # Mostra informações básicas
    print("\nInformações gerais:")
    print(df.info())
    
    # Mostra as primeiras linhas
    print("\nPrimeiras linhas:")
    print(df.head())
    
    # Mostra nomes das colunas
    print("\nColunas encontradas:")
    for col in df.columns:
        print(f"- {col}")

def analisar_demonstracoes():
    """
    Analisa os arquivos CSV das demonstrações contábeis
    """
    for ano in ['2023', '2024']:
        arquivo = os.path.join(
            DIRETORIOS['dados'][f'demo_{ano}'],
            f"demonstracoes_{ano}.csv"
        )
        
        if os.path.exists(arquivo):
            print(f"\n=== Análise do arquivo de demonstrações {ano} ===")
            
            # Lê o arquivo
            df = pd.read_csv(arquivo, encoding='latin1', sep=';')
            
            # Mostra informações básicas
            print("\nInformações gerais:")
            print(df.info())
            
            # Mostra as primeiras linhas
            print("\nPrimeiras linhas:")
            print(df.head())
            
            # Mostra nomes das colunas
            print("\nColunas encontradas:")
            for col in df.columns:
                print(f"- {col}")

if __name__ == "__main__":
    print("Iniciando análise dos dados...")
    analisar_operadoras()
    analisar_demonstracoes()
    print("\nAnálise concluída!") 
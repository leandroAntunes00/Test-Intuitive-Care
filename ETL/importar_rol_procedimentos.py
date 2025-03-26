import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'intuitive_care',
    'user': 'postgres',
    'password': 'postgres'
}

def criar_conexao():
    """Cria uma conexão com o banco de dados usando SQLAlchemy"""
    connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_string)

def importar_dados():
    """Importa os dados do CSV para o banco de dados"""
    try:
        # Ler o arquivo CSV
        print("Lendo arquivo CSV...")
        df = pd.read_csv('tabela_rol_procedimentos.csv', sep=';', encoding='latin1')
        
        # Criar conexão com o banco de dados
        print("Conectando ao banco de dados...")
        engine = criar_conexao()
        
        # Importar dados para o banco
        print("Importando dados para o banco...")
        df.to_sql('rol_procedimentos', 
                 engine, 
                 schema='public',
                 if_exists='append',
                 index=False,
                 method='multi',
                 chunksize=1000)
        
        print("Importação concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a importação: {str(e)}")
        raise

if __name__ == "__main__":
    importar_dados() 
import pandas as pd
from sqlalchemy import create_engine, text
import os
from config import (
    DB_NAME, DB_URL, ARQUIVOS,
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
)
from logger import logger
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

def create_database():
    logger.info("Iniciando criação do banco de dados...")
    try:
        # Conecta diretamente usando psycopg2 para criar o banco
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cur = conn.cursor()
        
        # Verifica se o banco já existe
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f'CREATE DATABASE {DB_NAME}')
            logger.info(f"Banco de dados {DB_NAME} criado com sucesso!")
        else:
            logger.info(f"Banco de dados {DB_NAME} já existe!")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {str(e)}")
        raise

def create_tables():
    logger.info("Iniciando criação das tabelas...")
    try:
        # Lê o arquivo SQL
        with open('create_tables.sql', 'r', encoding='utf-8') as file:
            sql_commands = file.read()
        
        # Conecta ao banco de dados
        engine = create_engine(f"{DB_URL}/{DB_NAME}")
        
        # Executa os comandos SQL
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS operadoras_ativas CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS demonstracoes_contabeis CASCADE"))
            conn.execute(text(sql_commands))
            conn.commit()
            logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")

def importar_operadoras():
    logger.info("Iniciando importação dos dados de operadoras...")
    try:
        arquivo_operadoras = os.path.join(ARQUIVOS['operadoras']['diretorio'], ARQUIVOS['operadoras']['arquivo'])
        df = pd.read_csv(arquivo_operadoras, sep=';', encoding=ARQUIVOS['operadoras']['encoding'])
        logger.info(f"Arquivo lido com sucesso. Total de registros: {len(df)}")

        # Renomear colunas para corresponder à tabela
        mapeamento_colunas = {
            'Registro_ANS': 'registro_ans',
            'CNPJ': 'cnpj',
            'Razao_Social': 'razao_social',
            'Nome_Fantasia': 'nome_fantasia',
            'Modalidade': 'modalidade',
            'Logradouro': 'logradouro',
            'Numero': 'numero',
            'Complemento': 'complemento',
            'Bairro': 'bairro',
            'Cidade': 'cidade',
            'UF': 'uf',
            'CEP': 'cep',
            'DDD': 'ddd',
            'Telefone': 'telefone',
            'Fax': 'fax',
            'Endereco_eletronico': 'email',
            'Representante': 'representante',
            'Cargo_Representante': 'cargo_representante',
            'Data_Registro_ANS': 'data_registro_ans'
        }

        df = df.rename(columns=mapeamento_colunas)
        df = df[list(mapeamento_colunas.values())]  # Seleciona apenas as colunas mapeadas

        # Converter data para o formato correto
        df['data_registro_ans'] = pd.to_datetime(df['data_registro_ans']).dt.strftime('%Y-%m-%d')

        # Importar dados para o banco
        engine = create_engine(DB_URL)
        df.to_sql('operadoras_ativas', engine, if_exists='append', index=False)
        logger.info("Dados das operadoras importados com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao importar dados das operadoras: {str(e)}")
        raise

def importar_demonstracoes():
    logger.info("Iniciando importação dos dados das demonstrações contábeis...")
    try:
        arquivo_demonstracoes = os.path.join(ARQUIVOS['demonstracoes']['diretorio'], ARQUIVOS['demonstracoes']['arquivo'])
        df = pd.read_csv(arquivo_demonstracoes, sep=';', encoding=ARQUIVOS['demonstracoes']['encoding'])
        logger.info(f"Arquivo lido com sucesso. Total de registros: {len(df)}")

        # Renomear colunas para corresponder à tabela
        mapeamento_colunas = {
            'DATA': 'data_base',
            'REG_ANS': 'registro_ans',
            'CD_CONTA_CONTABIL': 'cd_conta_contabil',
            'DESCRICAO': 'descricao',
            'VL_SALDO_INICIAL': 'saldo_inicial',
            'VL_SALDO_FINAL': 'saldo_final'
        }

        df = df.rename(columns=mapeamento_colunas)
        df = df[list(mapeamento_colunas.values())]  # Seleciona apenas as colunas mapeadas

        # Converter data para o formato correto
        df['data_base'] = pd.to_datetime(df['data_base'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

        # Converter valores monetários para decimal
        df['saldo_inicial'] = df['saldo_inicial'].str.replace(',', '.').astype(float)
        df['saldo_final'] = df['saldo_final'].str.replace(',', '.').astype(float)

        # Importar dados para o banco
        engine = create_engine(DB_URL)
        df.to_sql('demonstracoes_contabeis', engine, if_exists='append', index=False)
        logger.info("Dados das demonstrações contábeis importados com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao importar dados das demonstrações contábeis: {str(e)}")
        raise

def main():
    logger.info("Iniciando processo de importação de dados...")
    try:
        create_database()
        create_tables()
        importar_operadoras()
        importar_demonstracoes()
        logger.info("Processo de importação finalizado!")
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main() 
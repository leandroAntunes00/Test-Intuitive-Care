"""
Script para importação dos dados de operadoras e demonstrações contábeis para o PostgreSQL
"""
import os
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import zipfile
import io
from config import (
    DIRETORIOS, ARQUIVOS, LOGGING, DB_NAME, DB_USER, 
    DB_PASSWORD, DB_HOST, DB_PORT, ANO_ANTERIOR, ANO_ANTERIOR_2
)
import psycopg2
from psycopg2 import sql

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/import_operadoras.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurações
TEST_MODE = False  # Modo de teste processa apenas 50000 linhas por arquivo
LINHAS_TESTE = 10000  # Número de linhas a processar no modo de teste

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

def criar_diretorios():
    """Cria os diretórios necessários se não existirem."""
    try:
        for ano in [ANO_ANTERIOR_2, ANO_ANTERIOR]:
            diretorio = DIRETORIOS['dados'][f'demo_{ano}']
            if not os.path.exists(diretorio):
                os.makedirs(diretorio, exist_ok=True)
                logger.info(f"Diretório criado: {diretorio}")
    except Exception as e:
        logger.error(f"Erro ao criar diretórios: {str(e)}")
        raise

def criar_tabelas(conn):
    """Cria as tabelas necessárias no banco de dados."""
    try:
        with conn.cursor() as cursor:
            # Criar tabela de operadoras
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operadoras (
                    registro_ans VARCHAR(20) PRIMARY KEY,
                    cnpj VARCHAR(20),
                    razao_social VARCHAR(255),
                    nome_fantasia VARCHAR(255),
                    modalidade VARCHAR(100),
                    logradouro VARCHAR(255),
                    numero VARCHAR(20),
                    complemento VARCHAR(255),
                    bairro VARCHAR(100),
                    cidade VARCHAR(100),
                    uf CHAR(2),
                    cep VARCHAR(10)
                );
                
                CREATE INDEX IF NOT EXISTS idx_operadoras_cnpj ON operadoras(cnpj);
                CREATE INDEX IF NOT EXISTS idx_operadoras_razao_social ON operadoras(razao_social);
            """)

            # Criar tabela de demonstrações contábeis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
                    id SERIAL PRIMARY KEY,
                    data_demonstracao DATE,
                    registro_ans VARCHAR(20),
                    conta VARCHAR(20),
                    descricao TEXT,
                    saldo_inicial NUMERIC(15,2),
                    saldo_final NUMERIC(15,2),
                    CONSTRAINT uk_demonstracao
                        UNIQUE (data_demonstracao, registro_ans, conta)
                );
                
                CREATE INDEX IF NOT EXISTS idx_demonstracoes_data 
                    ON demonstracoes_contabeis(data_demonstracao);
                CREATE INDEX IF NOT EXISTS idx_demonstracoes_registro_ans 
                    ON demonstracoes_contabeis(registro_ans);
                CREATE INDEX IF NOT EXISTS idx_demonstracoes_conta 
                    ON demonstracoes_contabeis(conta);
            """)
            
            conn.commit()
            logging.info("Tabelas e índices criados com sucesso")
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao criar tabelas: {str(e)}")
        raise

def limpar_tabelas(conn):
    """Remove as tabelas existentes do banco de dados."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DROP TABLE IF EXISTS demonstracoes_contabeis CASCADE;
                DROP TABLE IF EXISTS operadoras CASCADE;
            """)
            conn.commit()
            logging.info("Tabelas removidas com sucesso")
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao remover tabelas: {str(e)}")
        raise

def validar_arquivo_zip(arquivo_zip, ano, trimestre):
    """Valida se o arquivo ZIP contém os arquivos necessários."""
    try:
        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
            arquivos = zip_ref.namelist()
            nome_demo = f"{trimestre}T{ano}_{trimestre-1 if trimestre > 1 else 4}T{ano if trimestre > 1 else ano-1}.csv"
            
            if "Relatorio_cadop.csv" not in arquivos:
                logger.error(f"Arquivo de operadoras não encontrado em {arquivo_zip}")
                return False
                
            arquivos_demo = [f for f in arquivos if f.endswith('.csv') and f != "Relatorio_cadop.csv"]
            if not arquivos_demo:
                logger.error(f"Arquivo de demonstrações não encontrado em {arquivo_zip}")
                return False
                
            return True
    except Exception as e:
        logger.error(f"Erro ao validar arquivo ZIP {arquivo_zip}: {str(e)}")
        return False

def extrair_operadoras_do_csv(arquivo_zip):
    """Extrai informações das operadoras do arquivo CSV dentro do ZIP."""
    try:
        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
            with zip_ref.open("Relatorio_cadop.csv") as csv_file:
                # No modo de teste, ler apenas as primeiras linhas
                if TEST_MODE:
                    df = pd.read_csv(
                        io.TextIOWrapper(csv_file, encoding='utf-8'),
                        sep=ARQUIVOS['csv']['separador'],
                        nrows=LINHAS_TESTE
                    )
                    logging.info(f"Modo de teste: Lendo {LINHAS_TESTE} linhas do arquivo de operadoras")
                else:
                    df = pd.read_csv(
                        io.TextIOWrapper(csv_file, encoding='utf-8'),
                        sep=ARQUIVOS['csv']['separador']
                    )
                
                # Renomear colunas conforme necessário
                colunas_mapeadas = {
                    'Registro ANS': 'registro_ans',
                    'CNPJ': 'cnpj',
                    'Razão Social': 'razao_social',
                    'Nome Fantasia': 'nome_fantasia',
                    'Modalidade': 'modalidade',
                    'Logradouro': 'logradouro',
                    'Número': 'numero',
                    'Complemento': 'complemento',
                    'Bairro': 'bairro',
                    'Cidade': 'cidade',
                    'UF': 'uf',
                    'CEP': 'cep',
                    'DDD': 'ddd',
                    'Telefone': 'telefone',
                    'Fax': 'fax',
                    'Endereço eletrônico': 'email',
                    'Representante': 'representante',
                    'Cargo Representante': 'cargo_representante',
                    'Data Registro ANS': 'data_registro_ans'
                }
                
                df = df.rename(columns=colunas_mapeadas)
                
                # Converter data_registro_ans para o formato correto
                df['data_registro_ans'] = pd.to_datetime(df['data_registro_ans'], format='%d/%m/%Y', errors='coerce')
                
                return df
    except Exception as e:
        logger.error(f"Erro ao extrair operadoras do CSV: {str(e)}")
        raise

def inserir_operadoras(conn, df):
    """Insere os dados das operadoras no banco de dados."""
    try:
        with conn.cursor() as cursor:
            values = []
            for _, row in df.iterrows():
                values.append((
                    str(row['Registro_ANS']),
                    str(row['CNPJ']),
                    str(row['Razao_Social']),
                    str(row['Nome_Fantasia']),
                    str(row['Modalidade']),
                    str(row['Logradouro']),
                    str(row['Numero']),
                    str(row['Complemento']),
                    str(row['Bairro']),
                    str(row['Cidade']),
                    str(row['UF']),
                    str(row['CEP'])
                ))

            cursor.executemany("""
                INSERT INTO operadoras (
                    registro_ans,
                    cnpj,
                    razao_social,
                    nome_fantasia,
                    modalidade,
                    logradouro,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    uf,
                    cep
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (registro_ans) DO UPDATE SET
                    cnpj = EXCLUDED.cnpj,
                    razao_social = EXCLUDED.razao_social,
                    nome_fantasia = EXCLUDED.nome_fantasia,
                    modalidade = EXCLUDED.modalidade,
                    logradouro = EXCLUDED.logradouro,
                    numero = EXCLUDED.numero,
                    complemento = EXCLUDED.complemento,
                    bairro = EXCLUDED.bairro,
                    cidade = EXCLUDED.cidade,
                    uf = EXCLUDED.uf,
                    cep = EXCLUDED.cep
            """, values)
            
            conn.commit()
            logging.info(f"Inseridas {len(values)} operadoras com sucesso")
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao inserir operadoras: {str(e)}")
        raise

def extrair_demonstracoes_do_csv(arquivo_zip, ano, trimestre):
    """Extrai demonstrações contábeis do arquivo CSV dentro do ZIP."""
    try:
        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
            arquivos_csv = [f for f in zip_ref.namelist() if f.endswith('.csv') and f != "Relatorio_cadop.csv"]
            if not arquivos_csv:
                raise ValueError("Arquivo de demonstrações não encontrado no ZIP")
                
            arquivo_demo = arquivos_csv[0]
            with zip_ref.open(arquivo_demo) as csv_file:
                # No modo de teste, ler apenas as primeiras linhas
                if TEST_MODE:
                    df = pd.read_csv(
                        io.TextIOWrapper(csv_file, encoding='utf-8'),
                        sep=ARQUIVOS['csv']['separador'],
                        nrows=LINHAS_TESTE
                    )
                    logging.info(f"Modo de teste: Lendo {LINHAS_TESTE} linhas do arquivo de demonstrações")
                else:
                    df = pd.read_csv(
                        io.TextIOWrapper(csv_file, encoding='utf-8'),
                        sep=ARQUIVOS['csv']['separador']
                    )
                
                # Renomear colunas conforme necessário
                colunas_mapeadas = {
                    'REGISTRO_ANS': 'registro_ans',
                    'DATA': 'data_demonstracao',
                    'CONTA': 'conta',
                    'DESCRICAO': 'descricao',
                    'VL_SALDO_INICIAL': 'saldo_inicial',
                    'VL_SALDO_FINAL': 'saldo_final'
                }
                
                df = df.rename(columns=colunas_mapeadas)
                
                # Converter valores monetários (substituir vírgula por ponto)
                df['saldo_inicial'] = df['saldo_inicial'].str.replace(',', '.').astype(float)
                df['saldo_final'] = df['saldo_final'].str.replace(',', '.').astype(float)
                
                # Converter data
                df['data_demonstracao'] = pd.to_datetime(df['data_demonstracao'], format='%d/%m/%Y')
                
                # Adicionar ano e trimestre
                df['ano'] = ano
                df['trimestre'] = trimestre
                
                return df
    except Exception as e:
        logging.error(f"Erro ao extrair demonstrações do CSV: {str(e)}")
        raise

def inserir_demonstracoes(conn, df_chunk):
    try:
        with conn.cursor() as cursor:
            # Preparar os dados para inserção
            values = []
            for _, row in df_chunk.iterrows():
                values.append((
                    pd.to_datetime(row['DATA']).date(),
                    str(row['REG_ANS']),
                    str(row['CD_CONTA_CONTABIL']),
                    str(row['DESCRICAO']),
                    float(str(row['VL_SALDO_INICIAL']).replace(',', '.')) if pd.notna(row['VL_SALDO_INICIAL']) else 0.0,
                    float(str(row['VL_SALDO_FINAL']).replace(',', '.')) if pd.notna(row['VL_SALDO_FINAL']) else 0.0
                ))

            # Inserir os dados em lote
            cursor.executemany("""
                INSERT INTO demonstracoes_contabeis (
                    data_demonstracao,
                    registro_ans,
                    conta,
                    descricao,
                    saldo_inicial,
                    saldo_final
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (data_demonstracao, registro_ans, conta) DO UPDATE SET
                    descricao = EXCLUDED.descricao,
                    saldo_inicial = EXCLUDED.saldo_inicial,
                    saldo_final = EXCLUDED.saldo_final
            """, values)
            
            conn.commit()
            logging.info(f"Inseridos {len(values)} registros de demonstrações financeiras com sucesso.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao inserir demonstrações financeiras: {str(e)}")
        raise

def processar_arquivo_zip(conn, zip_path, test_mode=False):
    try:
        # Extrair o arquivo ZIP para o diretório temporário
        temp_dir = os.path.join(os.path.dirname(zip_path), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Processar o arquivo CSV extraído
        csv_file = os.path.join(temp_dir, os.path.basename(zip_path).replace('.zip', '.csv'))
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"Arquivo CSV não encontrado em {csv_file}")
        
        # Ler o arquivo CSV em chunks
        chunk_size = LINHAS_TESTE if test_mode else 10000
        for chunk in pd.read_csv(csv_file, sep=';', encoding='utf-8', chunksize=chunk_size):
            inserir_demonstracoes(conn, chunk)
            if test_mode:
                logging.info("Modo de teste ativado - processando apenas o primeiro chunk")
                break
        
        logging.info(f"Arquivo {zip_path} processado com sucesso")
        return True
    except Exception as e:
        logging.error(f"Erro ao processar arquivo {zip_path}: {str(e)}")
        return False
    finally:
        # Limpar arquivos temporários
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)

def processar_todos_arquivos(conn):
    """Processa todos os arquivos dos dois anos anteriores."""
    try:
        total_sucesso = 0
        total_falhas = 0
        
        for ano in [ANO_ANTERIOR_2, ANO_ANTERIOR]:
            logging.info(f"\nProcessando arquivos do ano {ano}")
            for trimestre in range(1, 5):
                logging.info(f"\nProcessando {trimestre}º trimestre de {ano}")
                arquivo_zip = os.path.join(DIRETORIOS['dados'][f'demo_{ano}'], f"{trimestre}T{ano}.zip")
                arquivo_operadoras = 'dados_operadoras_ativas/Relatorio_cadop.csv'
                
                if os.path.exists(arquivo_zip):
                    logging.info(f"Processando arquivo: {arquivo_zip}")
                    sucesso = processar_arquivo_zip(conn, arquivo_zip, TEST_MODE)
                    if sucesso:
                        total_sucesso += 1
                    else:
                        total_falhas += 1
                else:
                    logging.error(f"Arquivo não encontrado: {arquivo_zip}")
                    total_falhas += 1
                    
        logging.info(f"\nProcessamento completo:")
        logging.info(f"Total de arquivos processados com sucesso: {total_sucesso}")
        logging.info(f"Total de falhas: {total_falhas}")
        
        return total_falhas == 0
        
    except Exception as e:
        logging.error(f"Erro ao processar todos os arquivos: {str(e)}")
        return False

def main():
    """Função principal"""
    try:
        # Criar conexão com o banco de dados
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Cria as tabelas se não existirem
        criar_tabelas(conn)

        # Limpa as tabelas existentes
        logging.info("Limpando tabelas existentes...")
        limpar_tabelas(conn)
        logging.info("Criando novas tabelas e índices...")
        criar_tabelas(conn)
        
        # Processar arquivo de operadoras
        arquivo_operadoras = 'dados_operadoras_ativas/Relatorio_cadop.csv'
        if not os.path.exists(arquivo_operadoras):
            raise FileNotFoundError(f"Arquivo de operadoras não encontrado: {arquivo_operadoras}")
        
        logging.info("Processando arquivo de operadoras...")
        df_operadoras = pd.read_csv(arquivo_operadoras, sep=';', encoding=ARQUIVOS['csv']['encoding'])
        inserir_operadoras(conn, df_operadoras)
        
        # Processar arquivos de demonstrações por ano e trimestre
        anos = ['2023', '2024']
        trimestres = ['1T', '2T', '3T', '4T']
        arquivos_processados = 0
        falhas = 0
        
        for ano in anos:
            dir_demo = f'demo_contabeis_{ano}'
            if not os.path.exists(dir_demo):
                logging.warning(f"Diretório não encontrado: {dir_demo}")
                continue
                
            for trimestre in trimestres:
                zip_path = os.path.join(dir_demo, f'{trimestre}{ano}.zip')
                if os.path.exists(zip_path):
                    logging.info(f"Processando arquivo: {zip_path}")
                    if processar_arquivo_zip(conn, zip_path, TEST_MODE):
                        arquivos_processados += 1
                    else:
                        falhas += 1
                else:
                    logging.warning(f"Arquivo não encontrado: {zip_path}")
                    falhas += 1
        
        logging.info(f"Processamento concluído. {arquivos_processados} arquivos processados com sucesso. {falhas} falhas.")
        
    except Exception as e:
        logging.error(f"Erro durante a execução: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main() 
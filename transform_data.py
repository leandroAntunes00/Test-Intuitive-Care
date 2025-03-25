"""
Script para transformação dos dados do PDF da ANS para CSV
"""
import os
import logging
import pandas as pd
import pdfplumber
import re
from config import DIRETORIOS, ARQUIVOS, LOGGING
import zipfile
from datetime import datetime
import psycopg2
from unidecode import unidecode

# Configuração de logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    datefmt=LOGGING['date_format']
)
logger = logging.getLogger(__name__)

def extrair_tabela_pdf(arquivo_pdf):
    """
    Extrai a tabela do PDF usando pdfplumber
    """
    logger.info(f"Extraindo dados do arquivo: {arquivo_pdf}")
    tabelas = []
    
    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            for pagina in pdf.pages:
                # Extrai tabelas da página
                tabelas_pagina = pagina.extract_tables()
                if tabelas_pagina:
                    tabelas.extend(tabelas_pagina)
        
        logger.info(f"Extraídas {len(tabelas)} tabelas do PDF")
        return tabelas
    except Exception as e:
        logger.error(f"Erro ao extrair tabelas do PDF: {e}")
        raise

def processar_tabelas(tabelas):
    """
    Processa as tabelas extraídas e converte para DataFrame
    """
    logger.info("Processando tabelas extraídas")
    
    # Lista para armazenar todas as linhas processadas
    dados_processados = []
    
    # Processa cada tabela
    for tabela in tabelas:
        for linha in tabela:
            # Remove células vazias e espaços extras
            linha_processada = [str(cell).strip() if cell else '' for cell in linha]
            
            # Verifica se a linha tem dados válidos
            if any(linha_processada):
                dados_processados.append(linha_processada)
    
    # Cria DataFrame
    df = pd.DataFrame(dados_processados)
    
    # Identifica a linha do cabeçalho (procura por 'PROCEDIMENTO' ou similar)
    for idx, row in df.iterrows():
        if any('PROCEDIMENTO' in str(cell).upper() for cell in row):
            # Define esta linha como cabeçalho
            df.columns = [str(col).upper().strip() for col in row]
            # Remove a linha do cabeçalho dos dados
            df = df.iloc[idx + 1:].reset_index(drop=True)
            break
    
    # Renomeia colunas se necessário
    rename_map = {
        'PROCEDIMENTO': 'procedimento',
        'ODONTOLÓGICO': 'od',
        'OD': 'od',
        'AMBULATORIAL': 'amb',
        'AMB': 'amb',
        'DESCRIÇÃO': 'descricao',
        'VIGÊNCIA': 'vigencia',
        'RN (ALTERAÇÃO)': 'rn_alteracao',
        'SUBGRUPO': 'subgrupo',
        'GRUPO': 'grupo',
        'CAPÍTULO': 'capitulo'
    }
    df = df.rename(columns=lambda x: rename_map.get(x.upper(), x.lower()))
    
    logger.info(f"Processadas {len(df)} linhas de dados")
    logger.info(f"Colunas encontradas: {', '.join(df.columns)}")
    return df

def substituir_abreviacoes(df):
    """
    Substitui as abreviações OD e AMB pelos termos completos
    """
    logger.info("Substituindo abreviações")
    
    # Mapeamento de abreviações
    mapa_abreviacoes = {
        'OD': 'Odontológico',
        'AMB': 'Ambulatorial'
    }
    
    # Substitui valores nas colunas
    for col in df.columns:
        if col in mapa_abreviacoes:
            df[col] = df[col].replace({'S': mapa_abreviacoes[col], 'N': f'Não {mapa_abreviacoes[col]}'})
    
    return df

def salvar_csv(df, nome_arquivo):
    """
    Salva o DataFrame como CSV com encoding correto
    """
    logger.info(f"Salvando arquivo CSV: {nome_arquivo}")
    
    try:
        # Salva com encoding UTF-8 e BOM para Excel
        df.to_csv(nome_arquivo, 
                 encoding='utf-8-sig',
                 sep=ARQUIVOS['csv']['separador'],
                 index=False)
        
        logger.info("Arquivo CSV salvo com sucesso")
        return nome_arquivo
    except Exception as e:
        logger.error(f"Erro ao salvar CSV: {e}")
        raise

def compactar_csv(arquivo_csv):
    """
    Compacta o arquivo CSV
    """
    logger.info("Compactando arquivo CSV")
    
    try:
        nome_zip = f"Teste_Leandro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(arquivo_csv, os.path.basename(arquivo_csv))
        
        logger.info(f"Arquivo ZIP criado: {nome_zip}")
        return nome_zip
    except Exception as e:
        logger.error(f"Erro ao criar arquivo ZIP: {e}")
        raise

def importar_para_banco(df):
    """
    Importa os dados para o PostgreSQL com tratamento de caracteres especiais
    """
    logger.info("Importando dados para o PostgreSQL")
    
    conn = None
    cur = None
    
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(
            dbname="intuitive_care",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        
        # Cria cursor
        cur = conn.cursor()
        
        # Cria tabela se não existir (sem especificar encoding)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS rol_procedimentos (
            id SERIAL PRIMARY KEY,
            procedimento TEXT,
            od TEXT,
            amb TEXT,
            vigencia TEXT,
            rn_alteracao TEXT,
            subgrupo TEXT,
            grupo TEXT,
            capitulo TEXT,
            data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Limpa dados anteriores
        cur.execute("TRUNCATE TABLE rol_procedimentos;")
        conn.commit()
        
        # Prepara a query de inserção
        insert_query = """
        INSERT INTO rol_procedimentos 
        (procedimento, od, amb, vigencia, rn_alteracao, subgrupo, grupo, capitulo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # Processa cada linha em uma transação separada
        for _, row in df.iterrows():
            try:
                # Prepara os dados
                dados = (
                    str(row.get('procedimento', '')).strip(),
                    str(row.get('od', '')).strip(),
                    str(row.get('amb', '')).strip(),
                    str(row.get('vigencia', '')).strip(),
                    str(row.get('rn\n(alteração)', '')).strip(),
                    str(row.get('subgrupo', '')).strip(),
                    str(row.get('grupo', '')).strip(),
                    str(row.get('capitulo', '')).strip()
                )
                
                # Executa a inserção
                cur.execute(insert_query, dados)
                conn.commit()
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Erro ao inserir linha: {e}")
                logger.error(f"Dados da linha: {row.to_dict()}")
                continue
        
        logger.info("Dados importados com sucesso para o PostgreSQL")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao importar para o banco: {e}")
        raise
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def main():
    try:
        # Encontra o arquivo PDF do Anexo I
        arquivos = [f for f in os.listdir() if f.endswith('.zip') and f.startswith('anexos_')]
        if not arquivos:
            raise FileNotFoundError("Arquivo ZIP dos anexos não encontrado")
        
        # Usa o arquivo ZIP mais recente
        arquivo_zip = max(arquivos)
        
        # Extrai o Anexo I
        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
            anexo_i = [f for f in zip_ref.namelist() if 'Anexo_I' in f][0]
            zip_ref.extract(anexo_i)
        
        # Processa o PDF
        tabelas = extrair_tabela_pdf(anexo_i)
        df = processar_tabelas(tabelas)
        df = substituir_abreviacoes(df)
        
        # Salva como CSV
        nome_csv = "rol_procedimentos.csv"
        salvar_csv(df, nome_csv)
        
        # Compacta o CSV
        nome_zip = compactar_csv(nome_csv)
        
        # Importa para o banco
        importar_para_banco(df)
        
        # Limpa arquivos temporários
        os.remove(anexo_i)
        os.remove(nome_csv)
        
        logger.info("Processo de transformação concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante o processo: {e}")
        raise

if __name__ == "__main__":
    main() 
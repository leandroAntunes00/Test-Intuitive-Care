"""
Script para download e processamento dos dados de operadoras da ANS
"""
import os
import logging
import requests
import pandas as pd
from config import DIRETORIOS, ARQUIVOS, LOGGING, URLS
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    datefmt=LOGGING['date_format']
)
logger = logging.getLogger(__name__)

def criar_diretorios():
    """
    Cria os diretórios necessários se não existirem
    """
    for dir_name in DIRETORIOS['dados'].values():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logger.info(f"Diretório criado: {dir_name}")

def baixar_arquivo(url, nome_arquivo, diretorio):
    """
    Baixa um arquivo da URL especificada
    """
    caminho_completo = os.path.join(diretorio, nome_arquivo)
    
    try:
        logger.info(f"Baixando arquivo de {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        tamanho_total = int(response.headers.get('content-length', 0))
        tamanho_baixado = 0
        
        with open(caminho_completo, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tamanho_baixado += len(chunk)
                    f.write(chunk)
                    if tamanho_total > 0:
                        progresso = (tamanho_baixado / tamanho_total) * 100
                        logger.info(f"Download em progresso: {progresso:.1f}%")
        
        logger.info(f"Arquivo baixado com sucesso: {nome_arquivo}")
        return caminho_completo
    
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo {nome_arquivo}: {e}")
        if os.path.exists(caminho_completo):
            os.remove(caminho_completo)
        raise

def processar_operadoras(arquivo_csv):
    """
    Processa o arquivo CSV de operadoras e retorna um DataFrame
    """
    try:
        logger.info(f"Processando arquivo de operadoras: {arquivo_csv}")
        
        # Lê o CSV
        df = pd.read_csv(arquivo_csv, 
                        encoding=ARQUIVOS['csv']['encoding'],
                        sep=ARQUIVOS['csv']['separador'],
                        low_memory=False)
        
        # Remove linhas duplicadas
        df = df.drop_duplicates().reset_index(drop=True)
        
        # Converte data de registro
        if 'Data Registro ANS' in df.columns:
            df['Data Registro ANS'] = pd.to_datetime(df['Data Registro ANS']).dt.date
        
        logger.info(f"Processamento concluído. {len(df)} operadoras encontradas.")
        return df
    
    except Exception as e:
        logger.error(f"Erro ao processar arquivo de operadoras: {e}")
        raise

def baixar_demonstracoes_trimestrais(ano):
    """
    Baixa os arquivos ZIP trimestrais de um determinado ano
    """
    try:
        arquivos_baixados = []
        url_base = URLS['demonstracoes'][str(ano)]
        diretorio = DIRETORIOS['dados'][f'demo_{ano}']
        
        for trimestre in range(1, 5):
            nome_arquivo = f"{trimestre}T{ano}.zip"
            url = f"{url_base}{nome_arquivo}"
            
            try:
                arquivo_baixado = baixar_arquivo(url, nome_arquivo, diretorio)
                arquivos_baixados.append(arquivo_baixado)
                logger.info(f"Download do {trimestre}º trimestre de {ano} concluído")
            except Exception as e:
                logger.error(f"Erro ao baixar {trimestre}º trimestre de {ano}: {e}")
                continue
        
        return arquivos_baixados
    
    except Exception as e:
        logger.error(f"Erro ao baixar demonstrações trimestrais de {ano}: {e}")
        raise

def main():
    try:
        # Cria diretórios necessários
        criar_diretorios()
        
        # Baixa dados das operadoras
        diretorio_operadoras = DIRETORIOS['dados']['operadoras_ativas']
        nome_arquivo = ARQUIVOS['csv']['operadoras']
        
        logger.info("Baixando dados das operadoras...")
        arquivo_operadoras = baixar_arquivo(
            URLS['operadoras'],
            nome_arquivo,
            diretorio_operadoras
        )
        
        # Processa dados das operadoras
        df_operadoras = processar_operadoras(arquivo_operadoras)
        
        # Baixa demonstrações contábeis trimestrais dos dois últimos anos
        anos = [datetime.now().year - 2, datetime.now().year - 1]
        for ano in anos:
            logger.info(f"\nBaixando demonstrações contábeis de {ano}...")
            arquivos_demo = baixar_demonstracoes_trimestrais(ano)
            logger.info(f"Arquivos baixados para {ano}: {len(arquivos_demo)}")
        
        logger.info("\nProcesso de download concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante o processo: {e}")
        raise

if __name__ == "__main__":
    main() 
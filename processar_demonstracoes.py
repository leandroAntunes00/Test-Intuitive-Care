import os
import pandas as pd
import zipfile
from config import ARQUIVOS
from logger import logger

def extrair_csv_do_zip(zip_path, diretorio_saida):
    """Extrai o arquivo CSV de dentro do ZIP"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Lista todos os arquivos no ZIP
            arquivos = zip_ref.namelist()
            
            # Procura por arquivos CSV
            csv_files = [f for f in arquivos if f.lower().endswith('.csv')]
            
            if not csv_files:
                logger.error(f"Nenhum arquivo CSV encontrado em {zip_path}")
                return None
                
            # Extrai o primeiro CSV encontrado
            csv_file = csv_files[0]
            zip_ref.extract(csv_file, diretorio_saida)
            
            return os.path.join(diretorio_saida, csv_file)
    except Exception as e:
        logger.error(f"Erro ao extrair {zip_path}: {str(e)}")
        return None

def processar_demonstracoes(ano):
    """Processa os arquivos de demonstrações contábeis de um ano específico"""
    diretorio = f'demo_contabeis_{ano}'
    
    if not os.path.exists(diretorio):
        logger.error(f"Diretório {diretorio} não encontrado")
        return None
        
    # Lista todos os arquivos ZIP no diretório
    arquivos_zip = [f for f in os.listdir(diretorio) if f.endswith('.zip')]
    
    if not arquivos_zip:
        logger.error(f"Nenhum arquivo ZIP encontrado em {diretorio}")
        return None
        
    # Diretório temporário para extrair os CSVs
    temp_dir = os.path.join(diretorio, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Lista para armazenar os DataFrames
    dfs = []
    
    # Processa cada arquivo ZIP
    for zip_file in sorted(arquivos_zip):
        zip_path = os.path.join(diretorio, zip_file)
        logger.info(f"Processando {zip_file}...")
        
        # Extrai o CSV do ZIP
        csv_path = extrair_csv_do_zip(zip_path, temp_dir)
        if csv_path:
            try:
                # Lê o CSV
                df = pd.read_csv(csv_path, 
                               encoding=ARQUIVOS['csv']['encoding'],
                               sep=ARQUIVOS['csv']['separador'])
                dfs.append(df)
                
                # Remove o arquivo extraído
                os.remove(csv_path)
            except Exception as e:
                logger.error(f"Erro ao ler {csv_path}: {str(e)}")
    
    # Remove o diretório temporário
    try:
        os.rmdir(temp_dir)
    except:
        pass
    
    if not dfs:
        logger.error("Nenhum dado foi processado")
        return None
        
    # Combina todos os DataFrames
    df_final = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicatas se houver
    df_final = df_final.drop_duplicates()
    
    return df_final

def gerar_csv_demonstracoes():
    """Gera o CSV final com todas as demonstrações"""
    logger.info("Iniciando processamento das demonstrações contábeis...")
    
    # Processa dados de 2023 e 2024
    df_2023 = processar_demonstracoes(2023)
    df_2024 = processar_demonstracoes(2024)
    
    if df_2023 is None and df_2024 is None:
        logger.error("Nenhum dado foi processado")
        return False
    
    # Combina os dados dos dois anos
    dfs = [df for df in [df_2023, df_2024] if df is not None]
    df_final = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicatas
    df_final = df_final.drop_duplicates()
    
    # Salva o arquivo final
    try:
        df_final.to_csv('demonstracoes.csv', 
                       index=False,
                       encoding=ARQUIVOS['csv']['encoding'],
                       sep=ARQUIVOS['csv']['separador'])
        logger.info("Arquivo demonstracoes.csv gerado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo final: {str(e)}")
        return False

if __name__ == "__main__":
    gerar_csv_demonstracoes() 
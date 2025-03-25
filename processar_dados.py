import os
import pandas as pd
import logging
from datetime import datetime
from config import DIRETORIOS, ARQUIVOS, LOGGING

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, LOGGING['level']),
    format=LOGGING['format'],
    filename=LOGGING['arquivo']
)
logger = logging.getLogger(__name__)

def processar_diretorio(diretorio, ano=None):
    """
    Processa os arquivos de um diretório específico e gera um CSV consolidado.
    
    Args:
        diretorio (str): Nome do diretório a ser processado
        ano (int, optional): Ano para filtrar os dados
    """
    try:
        logger.info(f"Processando diretório: {diretorio}")
        
        # Lista todos os arquivos CSV no diretório
        arquivos = [f for f in os.listdir(diretorio) if f.endswith('.csv')]
        
        if not arquivos:
            logger.warning(f"Nenhum arquivo CSV encontrado em {diretorio}")
            return
        
        # Lista para armazenar todos os DataFrames
        dfs = []
        
        for arquivo in arquivos:
            caminho_completo = os.path.join(diretorio, arquivo)
            logger.info(f"Processando arquivo: {arquivo}")
            
            # Lê o arquivo CSV
            df = pd.read_csv(
                caminho_completo,
                encoding=ARQUIVOS['csv']['encoding'],
                sep=ARQUIVOS['csv']['separador']
            )
            
            # Adiciona coluna de data_vigencia se não existir
            if 'data_vigencia' not in df.columns:
                if ano:
                    df['data_vigencia'] = f"{ano}-01-01"
                else:
                    # Tenta extrair o ano do nome do arquivo
                    try:
                        ano_arquivo = int(arquivo.split('_')[-1].split('.')[0])
                        df['data_vigencia'] = f"{ano_arquivo}-01-01"
                    except:
                        df['data_vigencia'] = datetime.now().strftime('%Y-%m-%d')
            
            dfs.append(df)
        
        # Concatena todos os DataFrames
        df_final = pd.concat(dfs, ignore_index=True)
        
        # Remove duplicatas
        df_final = df_final.drop_duplicates()
        
        # Ordena por código do procedimento e data de vigência
        df_final = df_final.sort_values(['codigo_procedimento', 'data_vigencia'])
        
        # Salva o arquivo CSV consolidado
        arquivo_saida = os.path.join(diretorio, ARQUIVOS['csv']['nome_saida'])
        df_final.to_csv(
            arquivo_saida,
            index=False,
            encoding=ARQUIVOS['csv']['encoding'],
            sep=ARQUIVOS['csv']['separador']
        )
        
        logger.info(f"Arquivo consolidado salvo: {arquivo_saida}")
        logger.info(f"Total de registros: {len(df_final)}")
        
        return df_final
        
    except Exception as e:
        logger.error(f"Erro ao processar diretório {diretorio}: {e}")
        raise

def main():
    """
    Função principal que processa todos os diretórios.
    """
    try:
        # Diretórios a serem processados
        diretorios = [
            DIRETORIOS['dados']['operadoras_ativas'],
            DIRETORIOS['dados']['demo_2023'],
            DIRETORIOS['dados']['demo_2024']
        ]
        
        # Processa cada diretório
        for diretorio in diretorios:
            if not os.path.exists(diretorio):
                logger.warning(f"Diretório não encontrado: {diretorio}")
                continue
                
            if '2023' in diretorio:
                processar_diretorio(diretorio, 2023)
            elif '2024' in diretorio:
                processar_diretorio(diretorio, 2024)
            else:
                processar_diretorio(diretorio)
        
        logger.info("Processamento concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante o processamento: {e}")
        raise

if __name__ == "__main__":
    main() 
import pandas as pd
import logging
from config import LOGGING

# Configuração de logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    datefmt=LOGGING['date_format']
)
logger = logging.getLogger(__name__)

def substituir_abreviacoes():
    """
    Substitui as abreviações OD e AMB pelos termos completos no arquivo CSV
    """
    try:
        # Nome do arquivo CSV
        arquivo_csv = "tabela_rol_procedimentos.csv"
        
        # Lê o arquivo CSV
        logger.info(f"Lendo arquivo: {arquivo_csv}")
        df = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8-sig')
        
        # Mapeamento de abreviações
        mapa_abreviacoes = {
            'OD': 'ODONTOLOGIA',
            'AMB': 'ATENDIMENTO AMBULATORIAL'
        }
        
        # Substitui os nomes das colunas
        df = df.rename(columns=mapa_abreviacoes)
        
        # Salva o arquivo CSV atualizado
        df.to_csv(arquivo_csv, sep=';', encoding='utf-8-sig', index=False)
        logger.info(f"Arquivo atualizado com sucesso: {arquivo_csv}")
        
        # Mostra as colunas atualizadas
        logger.info("Colunas atualizadas:")
        for col in df.columns:
            logger.info(f"- {col}")
            
    except Exception as e:
        logger.error(f"Erro ao substituir abreviações: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        substituir_abreviacoes()
        print("Processo concluído com sucesso!")
    except Exception as e:
        print(f"Erro: {e}") 
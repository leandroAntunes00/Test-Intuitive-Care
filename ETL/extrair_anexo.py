import zipfile
import os
from datetime import datetime
import logging
from config import LOGGING

# Configuração de logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    datefmt=LOGGING['date_format']
)
logger = logging.getLogger(__name__)

def extrair_anexo_i():
    """
    Extrai o Anexo I do arquivo ZIP mais recente
    """
    try:
        # Encontrar o arquivo ZIP mais recente
        arquivos_zip = [f for f in os.listdir('.') if f.startswith('anexos_') and f.endswith('.zip')]
        if not arquivos_zip:
            raise FileNotFoundError("Nenhum arquivo ZIP de anexos encontrado")
        
        arquivo_zip = max(arquivos_zip)  # Pega o mais recente
        logger.info(f"Arquivo ZIP encontrado: {arquivo_zip}")
        
        # Nome do arquivo PDF do Anexo I
        anexo_i = "Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"
        
        # Extrair o arquivo
        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
            if anexo_i not in zip_ref.namelist():
                raise FileNotFoundError(f"Arquivo {anexo_i} não encontrado no ZIP")
            
            zip_ref.extract(anexo_i)
            logger.info(f"Anexo I extraído com sucesso: {anexo_i}")
        
        return anexo_i
        
    except Exception as e:
        logger.error(f"Erro ao extrair Anexo I: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        pdf_path = extrair_anexo_i()
        print(f"Processo concluído com sucesso! Anexo I extraído: {pdf_path}")
    except Exception as e:
        print(f"Erro: {e}") 
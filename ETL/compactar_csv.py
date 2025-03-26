import zipfile
import os
import logging
from config import LOGGING

# Configuração de logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    datefmt=LOGGING['date_format']
)
logger = logging.getLogger(__name__)

def compactar_csv():
    """
    Compacta o arquivo CSV em um arquivo ZIP
    """
    try:
        # Nome do arquivo CSV
        arquivo_csv = "tabela_rol_procedimentos.csv"
        
        # Verificar se o arquivo CSV existe
        if not os.path.exists(arquivo_csv):
            raise FileNotFoundError(f"Arquivo {arquivo_csv} não encontrado")
        
        # Nome do arquivo ZIP
        nome_zip = "Teste_leandro.zip"
        
        # Compactar
        with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(arquivo_csv, os.path.basename(arquivo_csv))
        
        logger.info(f"Arquivo ZIP criado: {nome_zip}")
        return nome_zip
        
    except Exception as e:
        logger.error(f"Erro ao compactar arquivo: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        zip_file = compactar_csv()
        print(f"Processo concluído com sucesso! Arquivo ZIP criado: {zip_file}")
    except Exception as e:
        print(f"Erro: {e}") 
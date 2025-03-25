import requests
from bs4 import BeautifulSoup
import zipfile
import os
from datetime import datetime
import logging
from config import URLS, DIRETORIOS, ARQUIVOS, LOGGING

# Configuração de logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    datefmt=LOGGING['date_format']
)
logger = logging.getLogger(__name__)

def baixar_anexos():
    """
    Realiza o web scraping do site da ANS para baixar os anexos I e II
    e compacta em um arquivo ZIP.
    """
    try:
        url = URLS['ANS']['base']
        logger.info(f"Acessando URL: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar links dos PDFs
        pdfs = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href.endswith('.pdf') and ('Anexo_I' in href or 'Anexo_II' in href):
                pdfs.append(href)
                logger.info(f"PDF encontrado: {href}")
        
        if not pdfs:
            logger.error("Nenhum PDF encontrado na página")
            raise Exception("Não foi possível encontrar os anexos I e II na página da ANS")
        
        # Criar diretório para downloads
        os.makedirs(DIRETORIOS['dados']['downloads'], exist_ok=True)
        
        # Baixar PDFs
        for pdf_url in pdfs:
            logger.info(f"Baixando: {pdf_url}")
            response = requests.get(pdf_url)
            response.raise_for_status()
            
            filename = pdf_url.split('/')[-1]
            filepath = os.path.join(DIRETORIOS['dados']['downloads'], filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            logger.info(f"PDF salvo: {filepath}")
        
        # Compactar
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{ARQUIVOS['zip']['prefixo']}{timestamp}{ARQUIVOS['zip']['extensao']}"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pdf in pdfs:
                filename = pdf.split('/')[-1]
                filepath = os.path.join(DIRETORIOS['dados']['downloads'], filename)
                zipf.write(filepath, filename)
        
        logger.info(f"Arquivo ZIP criado: {zip_filename}")
        
        # Limpar arquivos temporários
        for pdf in pdfs:
            filename = pdf.split('/')[-1]
            filepath = os.path.join(DIRETORIOS['dados']['downloads'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        os.rmdir(DIRETORIOS['dados']['downloads'])
        logger.info("Arquivos temporários removidos")
        
        return zip_filename
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao acessar a URL: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro durante o processo: {e}")
        raise

if __name__ == "__main__":
    try:
        zip_file = baixar_anexos()
        print(f"Processo concluído com sucesso! Arquivo ZIP criado: {zip_file}")
    except Exception as e:
        print(f"Erro: {e}") 
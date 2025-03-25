import logging
import os
from datetime import datetime

def setup_logger():
    """Configura e retorna um logger personalizado"""
    
    # Cria o diretório de logs se não existir
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Nome do arquivo de log com data
    data_atual = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'processamento_{data_atual}.log')
    
    # Configura o logger
    logger = logging.getLogger('intuitive_care')
    logger.setLevel(logging.INFO)
    
    # Formata as mensagens de log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Remove handlers existentes
    logger.handlers = []
    
    # Adiciona os handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Cria uma instância global do logger
logger = setup_logger() 
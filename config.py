"""
Arquivo de configuração com constantes e configurações do projeto
"""
import logging
import os
from datetime import datetime

# Anos de referência (dois anos anteriores ao atual)
ANO_ATUAL = datetime.now().year
ANO_ANTERIOR = ANO_ATUAL - 1
ANO_ANTERIOR_2 = ANO_ATUAL - 2

# Configurações de diretórios
DIRETORIOS = {
    'dados': {
        'operadoras_ativas': 'dados_operadoras_ativas',
        f'demo_{ANO_ANTERIOR_2}': f'demo_contabeis_{ANO_ANTERIOR_2}',
        f'demo_{ANO_ANTERIOR}': f'demo_contabeis_{ANO_ANTERIOR}',
        'downloads': 'downloads'
    }
}

# Configurações de arquivos
ARQUIVOS = {
    'csv': {
        'encoding': 'utf-8',  # Encoding para arquivos da ANS
        'separador': ';',      # Separador padrão dos CSVs
        'operadoras': 'Relatorio_cadop.csv',
        'demonstracoes': 'demonstracoes.csv'
    }
}

# Configurações de logging
LOGGING = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Configurações do banco de dados
DB_NAME = "intuitive_care"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# URLs para download dos arquivos
URLS = {
    'operadoras': 'https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv',
    'demonstracoes': {
        str(ANO_ANTERIOR_2): f'https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/{ANO_ANTERIOR_2}/',
        str(ANO_ANTERIOR): f'https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/{ANO_ANTERIOR}/'
    }
}

# URL de conexão
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"

# Configurações da API
API = {
    'host': 'localhost',
    'port': 8000,
    'debug': True
}

# Configurações do frontend
FRONTEND = {
    'host': 'localhost',
    'port': 8080
} 
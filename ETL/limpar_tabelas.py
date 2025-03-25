import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def limpar_tabelas(conn):
    """Remove as tabelas existentes do banco de dados."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DROP TABLE IF EXISTS demonstracoes_contabeis CASCADE;
                DROP TABLE IF EXISTS operadoras CASCADE;
            """)
            conn.commit()
            logging.info("Tabelas removidas com sucesso")
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao remover tabelas: {str(e)}")
        raise

def main():
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Limpar tabelas
        limpar_tabelas(conn)
        
    except Exception as e:
        logging.error(f"Erro: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main() 
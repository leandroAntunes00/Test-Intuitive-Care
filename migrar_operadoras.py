import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrar_operadoras():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        with conn.cursor() as cursor:
            # Limpar tabela de destino
            cursor.execute("TRUNCATE TABLE operadoras_ativas")
            
            # Inserir dados da tabela operadoras
            cursor.execute("""
                INSERT INTO operadoras_ativas (
                    registro_ans,
                    cnpj,
                    razao_social,
                    nome_fantasia,
                    modalidade,
                    logradouro,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    uf,
                    cep
                )
                SELECT 
                    registro_ans,
                    cnpj,
                    razao_social,
                    nome_fantasia,
                    modalidade,
                    logradouro,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    uf,
                    cep
                FROM operadoras
            """)
            
            conn.commit()
            
            # Verificar quantidade de registros
            cursor.execute("SELECT COUNT(*) FROM operadoras_ativas")
            total = cursor.fetchone()[0]
            logger.info(f"Migração concluída. {total} registros inseridos.")
            
    except Exception as e:
        logger.error(f"Erro durante a migração: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    migrar_operadoras() 
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
import traceback

# Configuração de logging mais detalhada
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Log das variáveis de ambiente (sem senha)
logger.debug(f"DB_NAME: {os.getenv('DB_NAME')}")
logger.debug(f"DB_USER: {os.getenv('DB_USER')}")
logger.debug(f"DB_HOST: {os.getenv('DB_HOST')}")
logger.debug(f"DB_PORT: {os.getenv('DB_PORT')}")

app = FastAPI(
    title="API de Busca em Demonstrações Contábeis",
    description="""
    API para busca em demonstrações contábeis de operadoras de planos de saúde.
    
    ## Endpoints disponíveis:
    
    * `/` - Rota de teste para verificar a conexão com o banco de dados
    * `/busca` - Busca nas demonstrações contábeis
    * `/busca-operadora` - Busca nas operadoras
    
    ## Estrutura das tabelas:
    
    ### Demonstrações Contábeis
    * id: integer
    * data_demonstracao: date (YYYY-MM-DD)
    * registro_ans: varchar(20)
    * conta: varchar(20)
    * descricao: text
    * saldo_inicial: numeric(15,2)
    * saldo_final: numeric(15,2)
    
    ### Operadoras
    * id: integer
    * data_demonstracao: date (YYYY-MM-DD)
    * registro_ans: varchar(20)
    * conta: varchar(20)
    * descricao: text
    * saldo_inicial: numeric(15,2)
    * saldo_final: numeric(15,2)
    """,
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """
    Cria uma conexão com o banco de dados com as configurações corretas de encoding
    """
    try:
        logger.debug("Tentando conectar ao banco de dados...")
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "intuitive_care"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            options='-c client_encoding=LATIN1'
        )
        logger.debug("Conexão com banco de dados estabelecida com sucesso!")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        raise

@app.get("/")
async def testar_conexao():
    """
    Rota de teste para verificar a conexão com o banco de dados.
    
    Retorna:
    * status: status da operação (success/error)
    * message: mensagem descritiva
    * teste: resultado do teste de conexão
    """
    conn = None
    cur = None
    try:
        logger.debug("Iniciando teste de conexão...")
        
        # Tenta conectar ao banco
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Tenta executar uma query simples
        cur.execute("SELECT 1 as teste")
        resultado = cur.fetchone()
        
        logger.debug(f"Resultado do teste: {resultado}")
        
        return {
            "status": "success",
            "message": "Conexão com o banco de dados estabelecida com sucesso!",
            "teste": resultado
        }
        
    except Exception as e:
        logger.error(f"Erro durante o teste de conexão: {str(e)}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Erro ao conectar ao banco de dados: {str(e)}"
        }
    finally:
        if cur:
            try:
                cur.close()
                logger.debug("Cursor fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar cursor: {str(e)}")
        
        if conn:
            try:
                conn.close()
                logger.debug("Conexão fechada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar conexão: {str(e)}")

@app.get("/busca")
async def buscar_descricao(
    termo: str = Query(..., description="Termo para busca na coluna descricao da tabela demonstracoes_contabeis"),
    limite: int = Query(100, description="Número máximo de resultados a retornar (entre 1 e 1000)", ge=1, le=1000)
):
    """
    Busca registros na tabela demonstracoes_contabeis pelo termo na coluna descricao.
    
    Retorna uma lista de registros com:
    * id: identificador único
    * data_referencia: data da demonstração (YYYY-MM-DD)
    * registro_ans: registro ANS da operadora
    * conta: código da conta contábil
    * descricao: descrição da conta
    * saldo_inicial: saldo inicial do período
    * saldo_final: saldo final do período
    """
    conn = None
    cur = None
    try:
        logger.debug(f"Iniciando busca para termo: {termo}")
        logger.debug(f"Limite de resultados: {limite}")
        
        # Conecta ao banco de dados usando a função auxiliar
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            id::text as id,
            data_demonstracao::text as data_referencia,
            registro_ans::text as registro_ans,
            conta::text as conta,
            descricao::text as descricao,
            saldo_inicial::text as saldo_inicial,
            saldo_final::text as saldo_final
        FROM demonstracoes_contabeis
        WHERE descricao ILIKE %s
        ORDER BY data_demonstracao DESC
        LIMIT %s;
        """
        
        termo_busca = f"%{termo}%"
        logger.debug(f"Query a ser executada: {query}")
        logger.debug(f"Parâmetros: termo_busca={termo_busca}, limite={limite}")
        
        # Executa a query
        cur.execute(query, (termo_busca, limite))
        resultados = cur.fetchall()
        
        # Log dos resultados
        logger.debug(f"Total de resultados encontrados: {len(resultados)}")
        if len(resultados) > 0:
            logger.debug(f"Primeiro resultado: {resultados[0]}")
        
        # Converte os resultados para uma lista de dicionários
        return [dict(row) for row in resultados]
        
    except Exception as e:
        logger.error(f"Erro durante a execução da busca: {str(e)}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {str(e)}")
    finally:
        # Garante que as conexões sejam fechadas mesmo em caso de erro
        if cur:
            try:
                cur.close()
                logger.debug("Cursor fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar cursor: {str(e)}")
        
        if conn:
            try:
                conn.close()
                logger.debug("Conexão fechada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar conexão: {str(e)}")

@app.get("/busca-operadora")
async def buscar_operadora(
    termo: str = Query(..., description="Termo para busca na coluna descricao da tabela operadoras"),
    limite: int = Query(100, description="Número máximo de resultados a retornar (entre 1 e 1000)", ge=1, le=1000)
):
    """
    Busca registros na tabela operadoras pelo termo na coluna descricao.
    
    Retorna uma lista de registros com:
    * id: identificador único
    * data_referencia: data da demonstração (YYYY-MM-DD)
    * registro_ans: registro ANS da operadora
    * conta: código da conta contábil
    * descricao: descrição da conta
    * saldo_inicial: saldo inicial do período (formatado com 2 casas decimais)
    * saldo_final: saldo final do período (formatado com 2 casas decimais)
    """
    conn = None
    cur = None
    try:
        logger.debug(f"Iniciando busca na operadora para termo: {termo}")
        logger.debug(f"Limite de resultados: {limite}")
        
        # Conecta ao banco de dados usando a função auxiliar
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            id,
            to_char(data_demonstracao, 'YYYY-MM-DD') as data_referencia,
            registro_ans::varchar(20) as registro_ans,
            conta::varchar(20) as conta,
            descricao::text as descricao,
            to_char(saldo_inicial, '999999999999.99') as saldo_inicial,
            to_char(saldo_final, '999999999999.99') as saldo_final
        FROM operadoras
        WHERE descricao ILIKE %s
        ORDER BY data_demonstracao DESC
        LIMIT %s;
        """
        
        termo_busca = f"%{termo}%"
        logger.debug(f"Query a ser executada: {query}")
        logger.debug(f"Parâmetros: termo_busca={termo_busca}, limite={limite}")
        
        # Executa a query
        cur.execute(query, (termo_busca, limite))
        resultados = cur.fetchall()
        
        # Log dos resultados
        logger.debug(f"Total de resultados encontrados: {len(resultados)}")
        if len(resultados) > 0:
            logger.debug(f"Primeiro resultado: {resultados[0]}")
        
        # Converte os resultados para uma lista de dicionários
        return [dict(row) for row in resultados]
        
    except Exception as e:
        logger.error(f"Erro durante a execução da busca: {str(e)}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {str(e)}")
    finally:
        # Garante que as conexões sejam fechadas mesmo em caso de erro
        if cur:
            try:
                cur.close()
                logger.debug("Cursor fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar cursor: {str(e)}")
        
        if conn:
            try:
                conn.close()
                logger.debug("Conexão fechada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar conexão: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
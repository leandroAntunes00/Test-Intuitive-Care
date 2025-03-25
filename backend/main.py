from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
import traceback
from config import DB_CONFIG

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
    API para busca de informações em demonstrações contábeis de operadoras de saúde.
    
    ## Estrutura do Banco de Dados
    
    ### Tabelas Principais:
    
    1. **operadoras**
       - Tabela base com dados cadastrais das operadoras
       - Campos principais: registro_ans, cnpj, razao_social, nome_fantasia, modalidade
    
    2. **operadoras_ativas**
       - Subconjunto de operadoras atualmente ativas
       - Campos adicionais: telefone, email, representante
       - Relacionada com operadoras via registro_ans
    
    3. **demonstracoes_contabeis**
       - Dados financeiros das operadoras
       - Campos principais: data_demonstracao, registro_ans, conta, descricao, saldo_inicial, saldo_final
    
    4. **rol_procedimentos**
       - Catálogo de procedimentos médicos
       - Campos principais: procedimento, od, amb, vigencia, grupo, subgrupo
    
    ## Endpoints Disponíveis
    
    ### Buscas em Operadoras
    - `/operadoras/cnpj/{cnpj}` - Busca operadora por CNPJ
    - `/operadoras/cidade/{cidade}` - Busca operadoras por cidade
    - `/operadoras/modalidade/{modalidade}` - Busca operadoras por modalidade
    
    ### Buscas em Operadoras Ativas
    - `/operadoras-ativas/cidade/{cidade}` - Busca operadoras ativas por cidade
    - `/operadoras-ativas/uf/{uf}` - Busca operadoras ativas por UF
    
    ### Buscas em Demonstrações
    - `/demonstracoes/periodo/{data_inicio}/{data_fim}` - Busca demonstrações por período
    - `/demonstracoes/conta/{conta}` - Busca demonstrações por conta
    - `/demonstracoes/saldo-negativo` - Busca demonstrações com saldo negativo
    
    ### Buscas em Procedimentos
    - `/procedimentos/grupo/{grupo}` - Busca procedimentos por grupo
    - `/procedimentos/subgrupo/{subgrupo}` - Busca procedimentos por subgrupo
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
        conn = psycopg2.connect(**DB_CONFIG, options='-c client_encoding=LATIN1')
        logger.debug("Conexão com banco de dados estabelecida com sucesso!")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        raise

@app.get("/")
async def root():
    """Rota de teste para verificar se a API está funcionando"""
    return {"status": "online", "message": "API está funcionando"}

@app.get("/operadoras/cnpj/{cnpj}")
async def buscar_operadora_cnpj(cnpj: str):
    """Busca uma operadora pelo CNPJ"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT registro_ans, cnpj, razao_social, nome_fantasia, modalidade, 
                   logradouro, numero, complemento, bairro, cidade, uf, cep
            FROM operadoras 
            WHERE cnpj = %s
        """, (cnpj,))
        resultado = cur.fetchone()
        cur.close()
        conn.close()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        return resultado
    except Exception as e:
        logger.error(f"Erro ao buscar operadora: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operadoras/cidade/{cidade}")
async def buscar_operadoras_cidade(cidade: str):
    """Busca operadoras por cidade"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT registro_ans, cnpj, razao_social, nome_fantasia, modalidade, 
                   logradouro, numero, complemento, bairro, cidade, uf, cep
            FROM operadoras 
            WHERE cidade ILIKE %s
            LIMIT 100
        """, (f"%{cidade}%",))
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar operadoras: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operadoras-ativas/cidade/{cidade}")
async def buscar_operadoras_ativas_cidade(cidade: str):
    """Busca operadoras ativas por cidade"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT registro_ans, cnpj, razao_social, nome_fantasia, modalidade, 
                   logradouro, numero, complemento, bairro, cidade, uf, cep,
                   telefone, email, representante
            FROM operadoras_ativas 
            WHERE cidade ILIKE %s
            LIMIT 100
        """, (f"%{cidade}%",))
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar operadoras ativas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demonstracoes/periodo/{data_inicio}/{data_fim}")
async def buscar_demonstracoes_periodo(data_inicio: str, data_fim: str):
    """Busca demonstrações por período"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT data_demonstracao, registro_ans, conta, descricao, 
                   saldo_inicial, saldo_final
            FROM demonstracoes_contabeis 
            WHERE data_demonstracao BETWEEN %s AND %s
            ORDER BY data_demonstracao
            LIMIT 100
        """, (data_inicio, data_fim))
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar demonstrações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demonstracoes/saldo-negativo")
async def buscar_demonstracoes_saldo_negativo():
    """Busca demonstrações com saldo negativo"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT data_demonstracao, registro_ans, conta, descricao, 
                   saldo_inicial, saldo_final
            FROM demonstracoes_contabeis 
            WHERE saldo_final < 0
            ORDER BY data_demonstracao DESC
            LIMIT 100
        """)
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar demonstrações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/procedimentos/grupo/{grupo}")
async def buscar_procedimentos_grupo(grupo: str):
    """Busca procedimentos por grupo"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT procedimento, od, amb, vigencia, subgrupo, grupo, capitulo
            FROM rol_procedimentos 
            WHERE grupo ILIKE %s
            LIMIT 100
        """, (f"%{grupo}%",))
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar procedimentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
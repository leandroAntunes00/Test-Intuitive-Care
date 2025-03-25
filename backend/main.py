from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
import traceback
from config import DB_CONFIG
import unicodedata

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
    title="API de Busca de Operadoras de Saúde",
    description="""
    API para busca de informações sobre operadoras de saúde e suas demonstrações contábeis.
    
    ## Estrutura do Banco de Dados
    
    ### Tabelas Principais:
    
    1. **operadoras**
       - Tabela base com dados cadastrais das operadoras
       - Campos principais: registro_ans, cnpj, razao_social, nome_fantasia, modalidade, cidade, uf
    
    2. **demonstracoes_contabeis**
       - Dados financeiros das operadoras
       - Campos principais: data_demonstracao, registro_ans, conta, descricao, saldo_inicial, saldo_final
    
    ## Endpoints por Domínio

    ### 1. Operadoras
    Endpoints para busca na tabela `operadoras`:
    ```
    GET /operadoras/cnpj/{cnpj}
        - Busca operadora por CNPJ
        - Retorna dados completos da operadora

    GET /operadoras/cidade/{cidade}
        - Busca operadoras por cidade
        - Retorna lista de operadoras da cidade

    GET /operadoras/nome-fantasia/{nome}
        - Busca operadoras por nome fantasia
        - Suporta busca parcial (LIKE)

    GET /operadoras/razao-social/{nome}
        - Busca operadoras por razão social
        - Suporta busca parcial (LIKE)

    GET /operadoras/uf/{uf}
        - Busca operadoras por UF
        - Retorna todas as operadoras do estado
    ```

    ### 2. Demonstrações Contábeis
    Endpoints para busca na tabela `demonstracoes_contabeis`:
    ```
    GET /demonstracoes/periodo/{data_inicio}/{data_fim}
        - Busca demonstrações por período
        - Formato de data: YYYY-MM-DD

    GET /demonstracoes/saldo-negativo
        - Lista demonstrações com saldo final negativo
        - Ordenado por data (mais recente primeiro)
    ```

    ### 3. Procedimentos
    Endpoints para busca na tabela `rol_procedimentos`:
    ```
    GET /procedimentos/grupo/{grupo}
        - Busca procedimentos por grupo
        - Suporta busca parcial (LIKE)
    ```

    ## Notas Importantes
    - Todos os endpoints são paginados com limite de 100 registros
    - Buscas textuais ignoram acentuação e são case-insensitive
    - Resultados são ordenados por nome_fantasia ou data, conforme contexto
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

def normalize_text(text):
    """Remove acentos e converte para minúsculo"""
    if not text:
        return text
    # Normaliza para forma NFD e remove diacríticos
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return text.lower()

def get_db_connection():
    """
    Cria uma conexão com o banco de dados com as configurações corretas de encoding
    """
    try:
        logger.debug("Tentando conectar ao banco de dados...")
        conn = psycopg2.connect(
            **DB_CONFIG,
            options="-c client_encoding=UTF8"
        )
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
            SELECT 
                o.registro_ans, 
                o.cnpj, 
                o.razao_social, 
                o.nome_fantasia, 
                o.modalidade,
                o.logradouro,
                o.numero,
                o.complemento,
                o.bairro,
                o.cidade,
                o.uf,
                o.cep,
                oa.telefone,
                oa.email,
                oa.representante,
                oa.data_registro_ans,
                CASE 
                    WHEN oa.registro_ans IS NOT NULL THEN true
                    ELSE false
                END as is_ativa
            FROM operadoras o
            LEFT JOIN operadoras_ativas oa ON o.registro_ans = oa.registro_ans
            WHERE o.cnpj = %s
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
async def buscar_por_cidade(cidade: str):
    """
    Busca operadoras por cidade
    """
    try:
        logger.info(f"Recebida busca por cidade: {cidade}")
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Normaliza o termo de busca
        cidade_norm = normalize_text(cidade)
        logger.info(f"Termo de busca normalizado: {cidade_norm}")
        
        query = """
            SELECT 
                o.registro_ans,
                o.nome_fantasia,
                o.razao_social,
                o.cnpj,
                o.modalidade,
                o.logradouro,
                o.numero,
                o.complemento,
                o.bairro,
                o.cidade,
                o.uf,
                o.cep,
                oa.telefone,
                oa.email,
                oa.representante,
                oa.data_registro_ans,
                CASE 
                    WHEN oa.registro_ans IS NOT NULL THEN true
                    ELSE false
                END as is_ativa
            FROM operadoras o
            LEFT JOIN operadoras_ativas oa ON o.registro_ans = oa.registro_ans
            WHERE normalize_text(o.cidade) LIKE %s
            ORDER BY o.nome_fantasia
            LIMIT 100
        """
        
        # Criar função de normalização no PostgreSQL se não existir
        cur.execute("""
            CREATE OR REPLACE FUNCTION normalize_text(text)
            RETURNS text AS
            $$
            BEGIN
                RETURN translate(
                    lower($1),
                    'áàâãäéèêëíìîïóòôõöúùûüýÿçñ',
                    'aaaaaeeeeiiiioooouuuuyycn'
                );
            END;
            $$ LANGUAGE plpgsql IMMUTABLE;
        """)
        
        search_term = f'%{cidade}%'
        logger.info(f"Executando busca com termo: {search_term}")
        
        cur.execute(query, (search_term,))
        resultados = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar por cidade: {str(e)}")
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
            WHERE unaccent(LOWER(cidade)) LIKE unaccent(LOWER(%s))
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

@app.get("/operadoras/nome-fantasia/{nome}")
async def buscar_por_nome_fantasia(nome: str):
    """
    Busca operadoras por nome fantasia
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                o.registro_ans,
                o.nome_fantasia,
                o.razao_social,
                o.cnpj,
                o.modalidade,
                o.logradouro,
                o.numero,
                o.complemento,
                o.bairro,
                o.cidade,
                o.uf,
                o.cep,
                oa.telefone,
                oa.email,
                oa.representante,
                oa.data_registro_ans,
                CASE 
                    WHEN oa.registro_ans IS NOT NULL THEN true
                    ELSE false
                END as is_ativa
            FROM operadoras o
            LEFT JOIN operadoras_ativas oa ON o.registro_ans = oa.registro_ans
            WHERE normalize_text(o.nome_fantasia) LIKE %s
            ORDER BY o.nome_fantasia
            LIMIT 100
        """
        
        cur.execute(query, (f'%{nome}%',))
        resultados = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar por nome fantasia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operadoras/razao-social/{nome}")
async def buscar_por_razao_social(nome: str):
    """
    Busca operadoras por razão social
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                o.registro_ans,
                o.nome_fantasia,
                o.razao_social,
                o.cnpj,
                o.modalidade,
                o.cidade,
                o.uf,
                o.cep,
                oa.telefone,
                oa.email,
                oa.representante,
                oa.data_registro_ans,
                CASE 
                    WHEN oa.registro_ans IS NOT NULL THEN true
                    ELSE false
                END as is_ativa
            FROM operadoras o
            LEFT JOIN operadoras_ativas oa ON o.registro_ans = oa.registro_ans
            WHERE o.razao_social ILIKE %s
            ORDER BY o.razao_social
            LIMIT 100
        """
        
        cur.execute(query, (f'%{nome}%',))
        resultados = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar por razão social: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operadoras/uf/{uf}")
async def buscar_operadoras_por_uf(uf: str):
    """
    Busca operadoras por UF
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                o.registro_ans,
                o.nome_fantasia,
                o.razao_social,
                o.cnpj,
                o.modalidade,
                o.logradouro,
                o.numero,
                o.complemento,
                o.bairro,
                o.cidade,
                o.uf,
                o.cep,
                oa.telefone,
                oa.email,
                oa.representante,
                oa.data_registro_ans,
                CASE 
                    WHEN oa.registro_ans IS NOT NULL THEN true
                    ELSE false
                END as is_ativa
            FROM operadoras o
            LEFT JOIN operadoras_ativas oa ON o.registro_ans = oa.registro_ans
            WHERE o.uf ILIKE %s
            ORDER BY o.nome_fantasia
            LIMIT 100
        """
        
        cur.execute(query, (uf,))
        resultados = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar operadoras por UF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
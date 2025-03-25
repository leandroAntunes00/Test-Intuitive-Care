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
    API para busca de informações sobre operadoras de saúde. Esta API permite consultar dados cadastrais
    e informações detalhadas sobre operadoras de saúde no Brasil.
    
    ## Estrutura do Banco de Dados
    
    ### Tabelas Principais:
    
    1. **operadoras**
       - Tabela principal com dados cadastrais das operadoras
       - Campos:
         * registro_ans (chave primária)
         * cnpj
         * razao_social
         * nome_fantasia
         * modalidade
         * logradouro
         * numero
         * complemento
         * bairro
         * cidade
         * uf
         * cep
    
    2. **operadoras_ativas**
       - Tabela com informações adicionais das operadoras ativas
       - Campos:
         * registro_ans (chave estrangeira)
         * telefone
         * email
         * representante
         * data_registro_ans

    3. **demonstracoes_contabeis**
       - Tabela com dados financeiros das operadoras
       - Campos:
         * id (chave primária)
         * data_demonstracao
         * registro_ans
         * conta
         * descricao
         * saldo_inicial
         * saldo_final
    
    ## Endpoints Disponíveis

    ### Busca de Operadoras

    1. **Busca por CNPJ**
       ```
       GET /operadoras/cnpj/{cnpj}
       ```
       - Busca operadora pelo CNPJ exato
       - Retorna dados completos incluindo endereço e contato
       - Exemplo: /operadoras/cnpj/12345678901234

    2. **Busca por Cidade**
       ```
       GET /operadoras/cidade/{cidade}
       ```
       - Busca todas as operadoras de uma cidade
       - Case insensitive e ignora acentos
       - Exemplo: /operadoras/cidade/sao%20paulo

    3. **Busca por Nome Fantasia**
       ```
       GET /operadoras/nome-fantasia/{nome}
       ```
       - Busca por nome fantasia (busca parcial)
       - Case insensitive e ignora acentos
       - Exemplo: /operadoras/nome-fantasia/unimed

    4. **Busca por Razão Social**
       ```
       GET /operadoras/razao-social/{nome}
       ```
       - Busca por razão social (busca parcial)
       - Case insensitive e ignora acentos
       - Exemplo: /operadoras/razao-social/saude

    5. **Busca por UF**
       ```
       GET /operadoras/uf/{uf}
       ```
       - Lista todas as operadoras de um estado
       - Case insensitive
       - Exemplo: /operadoras/uf/SP

    ### Análises Financeiras

    1. **Maiores Despesas em Eventos/Sinistros**
       ```
       GET /demonstracoes/maiores-despesas-eventos
       ```
       - Retorna as 10 operadoras com maiores despesas em eventos/sinistros médico-hospitalares no último trimestre
       - Ordenado por valor de despesa (decrescente)
       - Retorna:
         * Nome da operadora
         * Registro ANS
         * Valor da despesa
         * Trimestre de referência
         * Ranking

    ## Formato de Retorno

    Todas as buscas retornam os seguintes campos quando disponíveis:
    ```json
    {
        "registro_ans": "123456",
        "cnpj": "12345678901234",
        "razao_social": "Nome da Empresa LTDA",
        "nome_fantasia": "Nome Fantasia",
        "modalidade": "Tipo de Operadora",
        "logradouro": "Rua/Avenida",
        "numero": "123",
        "complemento": "Sala 1",
        "bairro": "Nome do Bairro",
        "cidade": "Nome da Cidade",
        "uf": "UF",
        "cep": "12345678",
        "telefone": "(11) 1234-5678",
        "email": "contato@operadora.com",
        "representante": "Nome do Representante",
        "data_registro_ans": "2023-01-01",
        "is_ativa": true
    }
    ```

    Para o endpoint de análise financeira, o retorno tem o seguinte formato:
    ```json
    {
        "nome_operadora": "Nome da Operadora",
        "registro_ans": "123456",
        "valor_despesa": 1234567.89,
        "trimestre": "2024-1",
        "ranking": 1
    }
    ```

    ## Notas Importantes
    - Todas as buscas são paginadas com limite de 100 registros
    - Buscas textuais ignoram acentuação e são case-insensitive
    - O campo `is_ativa` indica se a operadora está na tabela `operadoras_ativas`
    - Campos podem retornar nulos quando não disponíveis
    - CEP e CNPJ são retornados sem formatação
    - Valores monetários são retornados como números decimais
    """,
    version="1.0.0",
    contact={
        "name": "Suporte API Operadoras",
        "email": "suporte@operadoras.com"
    }
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
            WHERE normalize_text(o.cidade) LIKE normalize_text(%s)
            ORDER BY o.nome_fantasia
            LIMIT 100
        """
        
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
            WHERE normalize_text(o.nome_fantasia) LIKE normalize_text(%s)
            ORDER BY o.nome_fantasia
            LIMIT 100
        """
        
        search_term = f'%{nome}%'
        cur.execute(query, (search_term,))
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
            WHERE normalize_text(o.razao_social) LIKE normalize_text(%s)
            ORDER BY o.razao_social
            LIMIT 100
        """
        
        search_term = f'%{nome}%'
        cur.execute(query, (search_term,))
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

@app.get("/demonstracoes/maiores-despesas-eventos", tags=["Análises Financeiras"])
async def get_maiores_despesas_eventos():
    """
    Retorna as 10 operadoras com maiores despesas em eventos/sinistros médico-hospitalares no último trimestre.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
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
        
        # Query para encontrar as 10 operadoras com maiores despesas
        query = """
        WITH ultima_data AS (
            SELECT MAX(data_demonstracao) as data_max
            FROM demonstracoes_contabeis
            WHERE data_demonstracao <= CURRENT_DATE
        ),
        ultimo_trimestre AS (
            SELECT DISTINCT ON (registro_ans) 
                registro_ans,
                data_demonstracao,
                EXTRACT(YEAR FROM data_demonstracao) AS ano,
                EXTRACT(QUARTER FROM data_demonstracao) AS trimestre
            FROM demonstracoes_contabeis d
            JOIN ultima_data ud ON d.data_demonstracao = ud.data_max
            ORDER BY registro_ans, data_demonstracao DESC
        ),
        despesas_eventos AS (
            SELECT 
                o.nome_fantasia,
                o.razao_social,
                o.registro_ans,
                SUM(ABS(d.saldo_final)) as valor_despesa,
                ut.ano,
                ut.trimestre
            FROM demonstracoes_contabeis d
            JOIN ultimo_trimestre ut ON d.registro_ans = ut.registro_ans 
                AND d.data_demonstracao = ut.data_demonstracao
            JOIN operadoras o ON d.registro_ans = o.registro_ans
            WHERE d.descricao ILIKE '%EVENTOS%SINISTROS%CONHECIDOS%AVISADOS%MEDICO%HOSPITALAR%'
            GROUP BY o.nome_fantasia, o.razao_social, o.registro_ans, ut.ano, ut.trimestre
        )
        SELECT 
            CASE 
                WHEN nome_fantasia = 'nan' OR nome_fantasia IS NULL OR nome_fantasia = '' 
                THEN COALESCE(NULLIF(razao_social, ''), 'Operadora ' || registro_ans)
                ELSE nome_fantasia
            END as nome_operadora,
            registro_ans,
            valor_despesa,
            ano || '-T' || trimestre as trimestre,
            ROW_NUMBER() OVER (ORDER BY valor_despesa DESC) as ranking
        FROM despesas_eventos
        ORDER BY valor_despesa DESC
        LIMIT 10;
        """
        
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        logger.error(f"Erro ao buscar maiores despesas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados de despesas")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
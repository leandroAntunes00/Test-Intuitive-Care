from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import pandas as pd
from typing import List
import os
from dotenv import load_dotenv
from schemas import ResultadoBusca, DespesaTrimestre, DespesaAno, TendenciaMensal
import psycopg2
from psycopg2.extras import RealDictCursor

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="API de Análise de Operadoras ANS",
    description="""
    API para análise de dados de operadoras de saúde e demonstrações contábeis da ANS.
    
    ### Dados Disponíveis
    * 1.107 operadoras de saúde
    * 6.204.491 registros de demonstrações contábeis
    * 8 trimestres (2023-2024)
    
    ### Estrutura do Banco
    * `operadoras`: Dados básicos das operadoras
    * `operadoras_ativas`: Informações detalhadas e contatos
    * `demonstracoes_contabeis`: Registros financeiros trimestrais
    
    ### Relacionamentos
    * `operadoras_ativas.registro_ans` → `operadoras.registro_ans` (FK)
    * `demonstracoes_contabeis.registro_ans` → `operadoras.registro_ans` (FK)
    """,
    version="1.0.0",
    contact={
        "name": "Suporte",
        "email": "suporte@exemplo.com"
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

# Configuração do banco de dados
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "database": os.getenv("DB_NAME", "intuitive_care")
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DATABASE_URL, connect_args={'client_encoding': 'utf8'})

@app.get("/", 
    tags=["Status"],
    summary="Status da API",
    description="Retorna uma mensagem indicando que a API está funcionando."
)
async def root():
    """
    Endpoint para verificar se a API está funcionando.
    """
    return {"message": "API de Análise de Operadoras"}

@app.get("/api/operadoras/busca",
    response_model=List[ResultadoBusca],
    tags=["Operadoras"],
    summary="Busca de Operadoras",
    description="""
    Busca operadoras por termo no nome ou razão social.
    
    ### Funcionalidades
    * Busca por nome fantasia ou razão social
    * Retorna dados básicos da operadora
    
    ### Exemplo de Uso
    ```bash
    curl "http://localhost:8000/api/operadoras/busca?termo=unimed&limite=5"
    ```
    """
)
async def buscar_operadoras(
    termo: str = Query(..., description="Termo para busca no nome da operadora"),
    limite: int = Query(10, description="Número máximo de resultados", ge=1, le=100)
):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            razao_social as operadora,
            1 as total_eventos,
            0.0 as total_despesas,
            1.0 as relevancia,
            100.0 as percentual_total
        FROM operadoras
        WHERE 
            razao_social ILIKE %s OR
            nome_fantasia ILIKE %s
        ORDER BY razao_social
        LIMIT %s
        """
        
        termo_busca = f"%{termo}%"
        cur.execute(query, (termo_busca, termo_busca, limite))
        resultados = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/despesas/ultimo-trimestre",
    response_model=List[DespesaTrimestre],
    tags=["Despesas"],
    summary="Despesas do Último Trimestre",
    description="""
    Retorna as 10 operadoras com maiores despesas no último trimestre.
    
    ### Detalhes
    * Considera apenas eventos/sinistros médico-hospitalares
    * Ordenado por valor total de despesas
    * Inclui percentual sobre o total do trimestre
    
    ### Exemplo de Uso
    ```bash
    curl "http://localhost:8000/api/despesas/ultimo-trimestre"
    ```
    """
)
async def get_despesas_ultimo_trimestre():
    try:
        query = """
        WITH ultimo_trimestre AS (
            SELECT 
                operadora,
                SUM(valor) as total_despesas,
                COUNT(*) as quantidade_eventos
            FROM public.despesas_operadoras
            WHERE categoria = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
            AND data_referencia >= CURRENT_DATE - INTERVAL '3 months'
            GROUP BY operadora
        )
        SELECT 
            operadora,
            ROUND(total_despesas::numeric, 2) as total_despesas,
            quantidade_eventos,
            ROUND((total_despesas / SUM(total_despesas) OVER()) * 100, 2) as percentual_total
        FROM ultimo_trimestre
        ORDER BY total_despesas DESC
        LIMIT 10
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/despesas/ultimo-ano",
    response_model=List[DespesaAno],
    tags=["Despesas"],
    summary="Despesas do Último Ano",
    description="""
    Retorna as 10 operadoras com maiores despesas no último ano.
    
    ### Métricas Calculadas
    * Total de despesas no período
    * Quantidade de eventos registrados
    * Média de valor por evento
    * Percentual em relação ao total
    
    ### Exemplo de Uso
    ```bash
    curl "http://localhost:8000/api/despesas/ultimo-ano"
    ```
    """
)
async def get_despesas_ultimo_ano():
    try:
        query = """
        WITH ultimo_ano AS (
            SELECT 
                operadora,
                SUM(valor) as total_despesas,
                COUNT(*) as quantidade_eventos,
                ROUND(AVG(valor), 2) as media_por_evento
            FROM public.despesas_operadoras
            WHERE categoria = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
            AND data_referencia >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY operadora
        )
        SELECT 
            operadora,
            ROUND(total_despesas::numeric, 2) as total_despesas,
            quantidade_eventos,
            media_por_evento,
            ROUND((total_despesas / SUM(total_despesas) OVER()) * 100, 2) as percentual_total
        FROM ultimo_ano
        ORDER BY total_despesas DESC
        LIMIT 10
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/despesas/tendencia-mensal",
    response_model=List[TendenciaMensal],
    tags=["Despesas"],
    summary="Tendência Mensal de Despesas",
    description="""
    Retorna a evolução mensal das despesas no último ano.
    
    ### Análise Temporal
    * Agrupamento por mês
    * Cálculo de totais mensais
    * Média por evento em cada mês
    
    ### Ordenação
    * Do mês mais recente para o mais antigo
    
    ### Exemplo de Uso
    ```bash
    curl "http://localhost:8000/api/despesas/tendencia-mensal"
    ```
    """
)
async def get_tendencia_mensal():
    try:
        query = """
        SELECT 
            DATE_TRUNC('month', data_referencia) as mes,
            COUNT(*) as total_eventos,
            ROUND(SUM(valor)::numeric, 2) as total_despesas,
            ROUND(AVG(valor)::numeric, 2) as media_por_evento
        FROM public.despesas_operadoras
        WHERE categoria = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
        AND data_referencia >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY DATE_TRUNC('month', data_referencia)
        ORDER BY mes DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
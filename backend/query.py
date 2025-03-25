import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def buscar_instalacoes():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            id,
            to_char(data_demonstracao, 'YYYY-MM-DD') as data_referencia,
            registro_ans::varchar(20),
            conta::varchar(20),
            descricao::text,
            to_char(saldo_inicial, '999999999999.99') as saldo_inicial,
            to_char(saldo_final, '999999999999.99') as saldo_final
        FROM operadoras 
        WHERE descricao = 'instalacoes'
        LIMIT 100;
        """
        
        cur.execute(query)
        resultados = cur.fetchall()
        
        for resultado in resultados:
            print(resultado)
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

if __name__ == "__main__":
    buscar_instalacoes() 
import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def verificar_contagem():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        with conn.cursor() as cursor:
            # Contar operadoras
            cursor.execute("SELECT COUNT(*) FROM operadoras")
            total_operadoras = cursor.fetchone()[0]
            print(f"\nTotal de operadoras: {total_operadoras}")
            
            # Contar demonstrações contábeis
            cursor.execute("SELECT COUNT(*) FROM demonstracoes_contabeis")
            total_demonstracoes = cursor.fetchone()[0]
            print(f"Total de demonstrações contábeis: {total_demonstracoes}")
            
            # Contar total por ano
            cursor.execute("""
                SELECT 
                    EXTRACT(YEAR FROM data_demonstracao) as ano,
                    COUNT(*) as total
                FROM demonstracoes_contabeis
                GROUP BY EXTRACT(YEAR FROM data_demonstracao)
                ORDER BY ano
            """)
            
            print("\nTotal por ano:")
            for row in cursor.fetchall():
                print(f"Ano {int(row[0])}: {row[1]} registros")
            
            # Contar demonstrações por trimestre
            cursor.execute("""
                SELECT 
                    EXTRACT(YEAR FROM data_demonstracao) as ano,
                    EXTRACT(QUARTER FROM data_demonstracao) as trimestre,
                    COUNT(*) as total
                FROM demonstracoes_contabeis
                GROUP BY 
                    EXTRACT(YEAR FROM data_demonstracao),
                    EXTRACT(QUARTER FROM data_demonstracao)
                ORDER BY ano, trimestre
            """)
            
            print("\nRegistros por trimestre:")
            for row in cursor.fetchall():
                print(f"Ano {int(row[0])}, {int(row[1])}º Trimestre: {row[2]} registros")
                
    except Exception as e:
        print(f"Erro ao verificar contagem: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    verificar_contagem() 
import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def verificar_dados():
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            options="-c client_encoding=UTF8"
        )
        
        with conn.cursor() as cursor:
            # Verificar operadoras primeiro
            print("\nRegistros da tabela operadoras:")
            print("=" * 80)
            cursor.execute("""
                SELECT registro_ans, cnpj, razao_social, nome_fantasia
                FROM operadoras
                LIMIT 10;
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                print(f"\nRegistro ANS: {row[0]}")
                print(f"CNPJ: {row[1]}")
                print(f"Razão Social: {row[2]}")
                print(f"Nome Fantasia: {row[3]}")
                print("-" * 80)

            # Procurar especificamente a operadora 2CARE
            print("\nBuscando operadora 2CARE:")
            print("=" * 80)
            cursor.execute("""
                SELECT registro_ans, cnpj, razao_social, nome_fantasia
                FROM operadoras
                WHERE razao_social LIKE '%2CARE%'
                   OR nome_fantasia LIKE '%2CARE%';
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                print(f"\nRegistro ANS: {row[0]}")
                print(f"CNPJ: {row[1]}")
                print(f"Razão Social: {row[2]}")
                print(f"Nome Fantasia: {row[3]}")
                print("-" * 80)

            # Verificar alguns registros da tabela demonstracoes_contabeis
            print("\nRegistros da tabela demonstracoes_contabeis:")
            print("=" * 80)
            cursor.execute("""
                SELECT data_demonstracao, registro_ans, conta, descricao, saldo_inicial, saldo_final
                FROM demonstracoes_contabeis
                LIMIT 5;
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                print(f"\nData: {row[0]}")
                print(f"Registro ANS: {row[1]}")
                print(f"Conta: {row[2]}")
                print(f"Descrição: {row[3]}")
                print(f"Saldo Inicial: {row[4]}")
                print(f"Saldo Final: {row[5]}")
                print("-" * 80)
                
    except Exception as e:
        print(f"Erro ao verificar dados: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verificar_dados() 
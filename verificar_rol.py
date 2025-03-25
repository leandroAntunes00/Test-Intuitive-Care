import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def verificar_rol_procedimentos():
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
            # Primeiro verificar se a tabela existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'rol_procedimentos'
                );
            """)
            
            tabela_existe = cursor.fetchone()[0]
            
            if not tabela_existe:
                print("A tabela rol_procedimentos não existe no banco de dados.")
                return
            
            # Verificar a estrutura da tabela
            print("\nEstrutura da tabela rol_procedimentos:")
            print("=" * 80)
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'rol_procedimentos'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"Coluna: {col[0]}")
                print(f"Tipo: {col[1]}")
                print(f"Tamanho máximo: {col[2]}")
                print("-" * 40)
            
            # Verificar alguns registros
            print("\nRegistros da tabela rol_procedimentos:")
            print("=" * 80)
            cursor.execute("""
                SELECT *
                FROM rol_procedimentos
                LIMIT 5;
            """)
            
            rows = cursor.fetchall()
            if not rows:
                print("Nenhum registro encontrado na tabela.")
            else:
                for row in rows:
                    print("\nRegistro:")
                    for col, value in zip([c[0] for c in columns], row):
                        print(f"{col}: {value}")
                    print("-" * 80)
                
    except Exception as e:
        print(f"Erro ao verificar rol de procedimentos: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verificar_rol_procedimentos() 
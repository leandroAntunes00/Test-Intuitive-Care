import pandas as pd

def verificar_csv():
    # Tentar diferentes encodings
    encodings = ['utf-8', 'iso-8859-1', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            print(f"\nTentando ler com encoding {encoding}:")
            print("=" * 80)
            
            df = pd.read_csv(
                'dados_operadoras_ativas/Relatorio_cadop.csv',
                sep=';',
                encoding=encoding,
                nrows=5  # Ler apenas 5 linhas para teste
            )
            
            print("\nColunas encontradas:")
            print(df.columns.tolist())
            
            print("\nPrimeiras linhas:")
            print(df[['Razao_Social', 'Nome_Fantasia']].to_string())
            
            # Procurar especificamente por registros com caracteres especiais
            special_chars = df[
                df['Razao_Social'].str.contains('Ç|Ã|É', na=False) |
                df['Nome_Fantasia'].str.contains('Ç|Ã|É', na=False)
            ]
            
            if not special_chars.empty:
                print("\nRegistros com caracteres especiais encontrados:")
                print(special_chars[['Razao_Social', 'Nome_Fantasia']].to_string())
            
            return  # Se chegou até aqui, deu certo
            
        except Exception as e:
            print(f"Erro com encoding {encoding}: {str(e)}")

if __name__ == "__main__":
    verificar_csv() 
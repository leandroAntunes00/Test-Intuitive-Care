import pandas as pd
import zipfile
import io

def mostrar_bytes_e_encodings(arquivo_zip):
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        # Pegar o primeiro arquivo CSV que não seja Relatorio_cadop.csv
        arquivos_csv = [f for f in zip_ref.namelist() if f.endswith('.csv') and f != "Relatorio_cadop.csv"]
        if not arquivos_csv:
            print("Nenhum arquivo CSV encontrado no ZIP!")
            return
            
        arquivo_csv = arquivos_csv[0]
        print(f"Lendo arquivo: {arquivo_csv}")
        
        # Ler os primeiros bytes do arquivo
        with zip_ref.open(arquivo_csv) as file:
            # Ler as primeiras linhas
            linhas = []
            for _ in range(10):  # Ler 10 linhas
                linha = file.readline()
                if not linha:
                    break
                linhas.append(linha)
        
        # Tentar decodificar com diferentes encodings
        encodings = ['cp1252', 'iso-8859-1', 'latin1', 'utf-8']
        
        for linha in linhas:
            print("\nBytes da linha:")
            print(linha)
            print("\nTentando decodificar com diferentes encodings:")
            for enc in encodings:
                try:
                    texto = linha.decode(enc)
                    print(f"{enc}: {texto}")
                except Exception as e:
                    print(f"Erro com {enc}: {str(e)}")

if __name__ == "__main__":
    arquivo_zip = "demo_contabeis_2023/1T2023.zip"
    mostrar_bytes_e_encodings(arquivo_zip) 
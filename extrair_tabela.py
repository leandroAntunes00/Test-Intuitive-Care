import pdfplumber
import pandas as pd
import re

def limpar_texto(texto):
    if texto is None:
        return ''
    # Remove espaços extras e quebras de linha
    texto = re.sub(r'\s+', ' ', str(texto).strip())
    return texto

def extrair_tabela_pdf(caminho_pdf):
    # Lista para armazenar todas as tabelas
    todas_tabelas = []
    
    # Abrir o PDF
    with pdfplumber.open(caminho_pdf) as pdf:
        # Iterar por todas as páginas
        for pagina in pdf.pages:
            # Extrair tabelas da página
            tabelas = pagina.extract_tables()
            
            # Se houver tabelas na página, adicionar à lista
            if tabelas:
                for tabela in tabelas:
                    # Processar cada célula da tabela
                    tabela_processada = []
                    for row in tabela:
                        # Limpar e processar cada célula
                        row_processada = [limpar_texto(cell) for cell in row]
                        # Adicionar apenas se a linha não estiver vazia
                        if any(cell for cell in row_processada):
                            tabela_processada.append(row_processada)
                    
                    if tabela_processada:
                        todas_tabelas.extend(tabela_processada)

    # Criar DataFrame
    df = pd.DataFrame(todas_tabelas[1:], columns=todas_tabelas[0])
    
    # Limpar nomes das colunas
    df.columns = [limpar_texto(col) for col in df.columns]
    
    # Substituir abreviações por descrições completas
    df = df.rename(columns={
        'OD': 'ODONTOLOGIA',
        'AMB': 'ATENDIMENTO AMBULATORIAL'
    })
    
    # Remover linhas duplicadas
    df = df.drop_duplicates()
    
    # Remover linhas onde todas as colunas são vazias
    df = df.dropna(how='all')
    
    # Resetar o índice
    df = df.reset_index(drop=True)
    
    # Salvar em CSV com codificação UTF-8 e separador ponto e vírgula
    df.to_csv('tabela_rol_procedimentos.csv', 
              index=False, 
              encoding='utf-8-sig',
              sep=';',
              quoting=1)  # quoting=1 para garantir que campos com vírgulas sejam corretamente escapados
    
    return df

if __name__ == "__main__":
    # Caminho do arquivo PDF
    pdf_path = "Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"
    
    print("Iniciando extração da tabela...")
    df = extrair_tabela_pdf(pdf_path)
    
    print("\nExtração concluída! Os dados foram salvos em 'tabela_rol_procedimentos.csv'")
    print(f"\nInformações sobre a tabela extraída:")
    print(f"Número de linhas: {len(df)}")
    print(f"Número de colunas: {len(df.columns)}")
    print("\nColunas encontradas:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nPrimeiras linhas da tabela:")
    print(df.head()) 
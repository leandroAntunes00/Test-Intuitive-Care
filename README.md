# Projeto de Processamento de Dados ANS

## 📋 Descrição do Projeto
Este projeto visa processar e estruturar dados da Agência Nacional de Saúde Suplementar (ANS), focando em três aspectos principais: coleta automatizada de documentos, transformação de dados e gestão de banco de dados.

## 🎯 Objetivos

O projeto está dividido em três partes principais:

### 1. Web Scraping
- Acesso automatizado ao site da ANS usando Python
- Download inteligente dos Anexos I e II mais recentes:
  - Rol de Procedimentos (Anexo I)
  - Diretrizes de Utilização (Anexo II)
- Compactação automática dos anexos em arquivo ZIP
- Recursos implementados:
  - Busca automática dos PDFs mais atuais
  - Sistema de logging para rastreamento
  - Limpeza automática de arquivos temporários
  - Tratamento de erros robusto

### 2. Transformação de Dados
- Extração de dados tabulares do Anexo I (Rol de Procedimentos)
- Conversão dos dados para formato CSV estruturado
- Processamento e normalização dos dados:
  - Expansão de abreviações (OD, AMB)
  - Estruturação em formato tabular
- Compactação do resultado em arquivo ZIP

### 3. Banco de Dados
- Coleta de dados de demonstrações contábeis (últimos 2 anos)
- Download de dados cadastrais de operadoras ativas
- Criação de estrutura de banco de dados
- Importação e organização dos dados coletados

## 🛠 Tecnologias Utilizadas

### Python
- **Web Scraping**: 
  - `requests`: Para requisições HTTP
  - `beautifulsoup4`: Para parsing do HTML
  - `zipfile`: Para compactação de arquivos
- **Processamento de PDFs**: [A ser implementado]
- **Manipulação de dados**: [A ser implementado]

### Banco de Dados
- PostgreSQL/MySQL para armazenamento
- Configuração flexível via arquivo `config.py`

## 📁 Estrutura de Diretórios

```
projeto/
├── dados/
│   ├── operadoras_ativas/
│   ├── demo_contabeis_2023/
│   ├── demo_contabeis_2024/
│   └── downloads/          # Diretório temporário para downloads
├── scripts/
│   ├── web_scraping.py    # Script de coleta de dados
│   └── [outros scripts]
├── config.py              # Configurações centralizadas
└── requirements.txt       # Dependências do projeto
```

## 🔧 Configuração

### Requisitos do Sistema
- Python 3.x
- PostgreSQL >= 10.0 ou MySQL 8.0
- Dependências Python (instale via pip):
  ```bash
  pip install requests beautifulsoup4
  ```

### Configuração do Banco de Dados
```python
DB_NAME = "intuitive_care"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
```

## 📊 Fontes de Dados

1. **Rol de Procedimentos e Eventos em Saúde**
   - URL Base: https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos
   - Anexo I: Lista de procedimentos cobertos (baixado automaticamente)
   - Anexo II: Diretrizes de Utilização (baixado automaticamente)

2. **Dados Financeiros e Cadastrais**
   - Demonstrações contábeis: https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/
   - Cadastro de operadoras: https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/

## 🚀 Como Executar

### 1. Web Scraping
```bash
# Execute o script de web scraping
python web_scraping.py
```
O script irá:
- Acessar o site da ANS automaticamente
- Localizar e baixar os PDFs mais recentes
- Criar um arquivo ZIP com timestamp (exemplo: anexos_20240324_230543.zip)
- Limpar arquivos temporários

### 2. Transformação de Dados
[Instruções serão adicionadas após implementação]

### 3. Banco de Dados
[Instruções serão adicionadas após implementação]

## 📝 Notas Importantes

- Os dados processados são públicos e disponibilizados pela ANS
- O processamento é otimizado para grandes volumes de dados
- Sistema de logging implementado para rastreamento de operações
- Tratamento de encoding específico para arquivos da ANS (Latin1)
- Limpeza automática de arquivos temporários

## 👥 Contribuição

[Instruções para contribuição serão adicionadas posteriormente]

## 📄 Licença

[Informações sobre licença serão adicionadas posteriormente]

# Importação de Dados ANS

## Sobre o Projeto
Este projeto realiza a importação e processamento de dados abertos da ANS (Agência Nacional de Saúde Suplementar), incluindo informações de operadoras de saúde e demonstrações contábeis trimestrais.

### Escopo e Complexidade
- Processamento de 6.204.491 registros de demonstrações contábeis
- Dados de 1.107 operadoras de saúde ativas
- 8 trimestres de demonstrações (2023-2024)
- Importação automatizada de múltiplos arquivos
- Sistema de logs para rastreamento de operações
- Validação e verificação de integridade dos dados

### Volume de Dados por Ano
- 2023: 3.904.869 registros (4 trimestres)
- 2024: 2.299.622 registros (3 trimestres)

## API REST

### Configuração
```bash
cd backend
pip install -r requirements.txt
python main.py
```
O servidor estará disponível em `http://localhost:8000`

### Endpoints Disponíveis

#### 1. Status da API
```
GET /
Retorna: {"message": "API de Análise de Operadoras"}
```

#### 2. Busca de Operadoras
```
GET /api/operadoras/busca
Parâmetros:
- termo (string): Termo para busca
- limite (int, opcional): Número máximo de resultados (1-100, default: 10)

Retorno:
[
    {
        "operadora": string,
        "total_eventos": int,
        "total_despesas": float,
        "relevancia": float,
        "percentual_total": float
    }
]
```

#### 3. Despesas do Último Trimestre
```
GET /api/despesas/ultimo-trimestre
Retorno:
[
    {
        "operadora": string,
        "total_despesas": float,
        "quantidade_eventos": int,
        "percentual_total": float
    }
]
```

#### 4. Despesas do Último Ano
```
GET /api/despesas/ultimo-ano
Retorno:
[
    {
        "operadora": string,
        "total_despesas": float,
        "quantidade_eventos": int,
        "media_por_evento": float,
        "percentual_total": float
    }
]
```

#### 5. Tendência Mensal
```
GET /api/despesas/tendencia-mensal
Retorno:
[
    {
        "mes": string (formato: "YYYY-MM-DD"),
        "total_eventos": int,
        "total_despesas": float,
        "media_por_evento": float
    }
]
```

### Exemplos de Uso

1. Buscar operadoras com "unimed" no nome:
```bash
curl "http://localhost:8000/api/operadoras/busca?termo=unimed&limite=5"
```

2. Ver despesas do último trimestre:
```bash
curl "http://localhost:8000/api/despesas/ultimo-trimestre"
```

## Competências Técnicas Demonstradas

### Banco de Dados
- PostgreSQL para armazenamento e consulta
- Modelagem de dados relacionais
- Criação e otimização de índices
- Constraints para garantia de integridade

### Processamento de Dados
- ETL (Extração, Transformação e Carga)
- Processamento de grandes volumes (+5M registros)
- Tratamento de encoding (UTF-8)
- Importação em lotes (chunking)
- Validação e limpeza de dados

### Desenvolvimento
- Python para scripts de automação
- Estruturação modular do código
- Tratamento de exceções
- Logging para rastreabilidade
- Controle de versão com Git

### Análise de Dados
- Pandas para manipulação de dados
- Verificação de consistência
- Análise de completude
- Estatísticas por período

## Dados Importados

O sistema importa:
- Dados de Operadoras Ativas
- Demonstrações Contábeis Trimestrais (2023 e 2024)
- Rol de Procedimentos

## Requisitos

- Python 3.x
- PostgreSQL
- Bibliotecas Python (requirements.txt):
  - pandas
  - psycopg2
  - sqlalchemy

## Configuração

1. Configure o banco de dados PostgreSQL no arquivo `config.py`:
```python
DB_NAME = "intuitive_care"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
```

2. Estrutura de diretórios necessária:
```
.
├── dados_operadoras_ativas/
│   └── Relatorio_cadop.csv
├── demo_contabeis_2023/
│   ├── 1T2023.zip
│   ├── 2T2023.zip
│   ├── 3T2023.zip
│   └── 4T2023.zip
└── demo_contabeis_2024/
    ├── 1T2024.zip
    ├── 2T2024.zip
    ├── 3T2024.zip
    └── 4T2024.zip
```

## Scripts Disponíveis

- `import_operadoras.py`: Script principal de importação
- `limpar_tabelas.py`: Remove todas as tabelas do banco
- `verificar_dados.py`: Verifica os dados importados
- `verificar_csv_operadoras.py`: Verifica o arquivo CSV de operadoras
- `verificar_rol.py`: Verifica a tabela de rol de procedimentos

## Como Usar

1. Limpar todas as tabelas:
```bash
python limpar_tabelas.py
```

2. Importar todos os dados:
```bash
python import_operadoras.py
```

## Modo de Teste

O script possui um modo de teste que pode ser configurado em `import_operadoras.py`:
```python
TEST_MODE = False  # Altere para True para processar apenas 50.000 registros por arquivo
```

## Encoding

- Todos os arquivos são processados em UTF-8
- A conexão com o banco de dados é configurada para UTF-8
- Os caracteres especiais (acentos, cedilha, etc.) são preservados

## Logs

Os logs são salvos em:
- Console (stdout)
- Arquivo: `logs/import_operadoras.log`

## Estrutura do Banco de Dados

### Tabela: operadoras
- registro_ans (PK)
- cnpj
- razao_social
- nome_fantasia
- modalidade
- logradouro
- numero
- complemento
- bairro
- cidade
- uf
- cep

### Tabela: demonstracoes_contabeis
- id (PK)
- data_demonstracao
- registro_ans
- conta
- descricao
- saldo_inicial
- saldo_final

## Índices

### operadoras
- idx_operadoras_cnpj
- idx_operadoras_razao_social

### demonstracoes_contabeis
- idx_demonstracoes_data
- idx_demonstracoes_registro_ans
- idx_demonstracoes_conta 
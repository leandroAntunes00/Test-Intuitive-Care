# API de Busca em Demonstrações Contábeis

## 📋 Descrição
API REST desenvolvida com FastAPI para busca e consulta de dados relacionados a operadoras de saúde, suas demonstrações contábeis e procedimentos médicos.

## 🎯 Funcionalidades

### 1. Buscas em Operadoras
- Busca por CNPJ
- Busca por cidade
- Busca por modalidade

### 2. Buscas em Operadoras Ativas
- Busca por cidade
- Busca por UF

### 3. Buscas em Demonstrações
- Busca por período
- Busca por conta
- Busca por saldo negativo

### 4. Buscas em Procedimentos
- Busca por grupo
- Busca por subgrupo

## 🛠 Tecnologias Utilizadas
- FastAPI
- PostgreSQL
- Python 3.x
- Uvicorn (servidor ASGI)

## 📁 Estrutura do Projeto
```
backend/
├── main.py              # Arquivo principal da API
├── config.py            # Configurações do banco de dados
├── requirements.txt     # Dependências do projeto
├── .env                 # Variáveis de ambiente
└── .env.example        # Exemplo de variáveis de ambiente
```

## 🔧 Configuração

### Requisitos do Sistema
- Python 3.x
- PostgreSQL
- Dependências Python:
  ```bash
  pip install -r requirements.txt
  ```

### Configuração do Banco de Dados
Crie um arquivo `.env` baseado no `.env.example`:
```env
DB_NAME=intuitive_care
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Iniciar o Servidor
```bash
python start.py
```

O servidor estará disponível em: `http://localhost:8000`

## 📚 Documentação da API

### Swagger UI
Acesse a documentação interativa em:
```
http://localhost:8000/docs
```

### Endpoints Disponíveis

#### Operadoras
- `GET /operadoras/cnpj/{cnpj}` - Busca operadora por CNPJ
- `GET /operadoras/cidade/{cidade}` - Busca operadoras por cidade
- `GET /operadoras/modalidade/{modalidade}` - Busca operadoras por modalidade

#### Operadoras Ativas
- `GET /operadoras-ativas/cidade/{cidade}` - Busca operadoras ativas por cidade
- `GET /operadoras-ativas/uf/{uf}` - Busca operadoras ativas por UF

#### Demonstrações
- `GET /demonstracoes/periodo/{data_inicio}/{data_fim}` - Busca demonstrações por período
- `GET /demonstracoes/conta/{conta}` - Busca demonstrações por conta
- `GET /demonstracoes/saldo-negativo` - Busca demonstrações com saldo negativo

#### Procedimentos
- `GET /procedimentos/grupo/{grupo}` - Busca procedimentos por grupo
- `GET /procedimentos/subgrupo/{subgrupo}` - Busca procedimentos por subgrupo

## 🔍 Exemplos de Uso

### Buscar Operadora por CNPJ
```bash
curl -X GET "http://localhost:8000/operadoras/cnpj/12345678901234"
```

### Buscar Demonstrações por Período
```bash
curl -X GET "http://localhost:8000/demonstracoes/periodo/2023-01-01/2023-12-31"
```

### Buscar Procedimentos por Grupo
```bash
curl -X GET "http://localhost:8000/procedimentos/grupo/CONSULTA%20ODONTOL%C3%93GICA"
```

## 📝 Notas
- Todas as rotas retornam no máximo 100 resultados
- As datas devem ser fornecidas no formato YYYY-MM-DD
- A API utiliza codificação UTF-8 para caracteres especiais 
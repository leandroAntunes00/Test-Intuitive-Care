# API de Busca de Operadoras de Saúde

![Image](https://github-production-user-asset-6210df.s3.amazonaws.com/131140028/427151891-1718fd21-65f7-4e3f-8dc0-0b5882ecb095.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250326%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250326T173914Z&X-Amz-Expires=300&X-Amz-Signature=9c02f1f7cf6436a940c13953d40628eecd00daee4c414f4630278a4a6ebcf8ea&X-Amz-SignedHeaders=host)
![Image2](https://github-production-user-asset-6210df.s3.amazonaws.com/131140028/427152128-b6a0be1c-88df-4c6b-af4a-92afdbf7baf7.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250326%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250326T174228Z&X-Amz-Expires=300&X-Amz-Signature=bc97ea4ad922dbf88a72d97d9db2e2e568d306d26efae64c69cd37a9f9e975cf&X-Amz-SignedHeaders=host)

## Sobre o Projeto

Esta API foi desenvolvida para fornecer informações detalhadas sobre operadoras de saúde no Brasil. Ela permite consultar dados cadastrais, informações de contato e análises financeiras das operadoras.

## Tecnologias Utilizadas

### Backend
- Python 3.x
- FastAPI
- PostgreSQL
- psycopg2
- uvicorn

### Frontend
- Vue.js
- JavaScript

## Funcionalidades Principais

### Busca de Operadoras
- Busca por CNPJ
- Busca por Cidade
- Busca por Nome Fantasia
- Busca por Razão Social
- Busca por UF

### Análises Financeiras
- Maiores despesas em eventos/sinistros por trimestre
- Maiores despesas em eventos/sinistros por ano
- Demonstrações contábeis por período
- Demonstrações com saldo negativo

## Como Executar

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente no arquivo `.env`:
```
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=seu_host
DB_PORT=sua_porta
```

4. Execute a aplicação:
```bash
python backend/main.py
```

A API estará disponível em `http://localhost:8000`

## Documentação da API

A documentação completa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Estrutura do Banco de Dados

### Tabelas Principais

1. **operadoras**
   - Dados cadastrais das operadoras
   - Campos: registro_ans, cnpj, razao_social, nome_fantasia, etc.

2. **operadoras_ativas**
   - Informações adicionais das operadoras ativas
   - Campos: telefone, email, representante, data_registro_ans

3. **demonstracoes_contabeis**
   - Dados financeiros das operadoras
   - Campos: data_demonstracao, conta, descricao, saldo_inicial, saldo_final

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter pull requests.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 
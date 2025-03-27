# API de Busca de Operadoras de Saúde

![Image](https://github-production-user-asset-6210df.s3.amazonaws.com/131140028/427665188-161a4de7-1c22-4f7a-a6bd-18dad25204af.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250327%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250327T163503Z&X-Amz-Expires=300&X-Amz-Signature=e7ea645e16059e43b67fba24ff77ef7714b4b207907e4980e694334c94323dfb&X-Amz-SignedHeaders=host)

![Image](https://github-production-user-asset-6210df.s3.amazonaws.com/131140028/427382684-901668a3-d26a-49b9-be32-b3b6a4d6b0a2.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250327%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250327T065905Z&X-Amz-Expires=300&X-Amz-Signature=9cb8e3a84a44b9a3c59234f06887ffde93f3207501277eedee8304fe2d12db88&X-Amz-SignedHeaders=host)

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

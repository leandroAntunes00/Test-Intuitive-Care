# Frontend - Sistema de Busca de Operadoras

## 📋 Descrição
Interface web desenvolvida em Vue.js para busca e visualização de dados relacionados a operadoras de saúde.

## 🎯 Funcionalidades

### Busca de Operadoras
- Pesquisa por nome da operadora
- Exibição de resultados com:
  - Total de eventos
  - Total de despesas
  - Relevância da busca
  - Percentual do total

## 🛠 Tecnologias Utilizadas
- Vue.js 3
- Vuetify 3
- Axios

## 📁 Estrutura do Projeto
```
frontend/
├── src/
│   ├── components/     # Componentes Vue
│   │   └── BuscaOperadoras.vue
│   ├── App.vue        # Componente principal
│   └── main.js        # Ponto de entrada
├── public/            # Arquivos estáticos
├── package.json       # Dependências e scripts
└── vue.config.js      # Configuração do Vue
```

## 🔧 Configuração

### Requisitos do Sistema
- Node.js 16.x ou superior
- npm ou yarn

### Instalação
```bash
# Instalar dependências
npm install
# ou
yarn install
```

### Configuração do Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
VUE_APP_API_URL=http://localhost:8000
```

## 🚀 Como Executar

### Desenvolvimento
```bash
npm run serve
# ou
yarn serve
```

### Build de Produção
```bash
npm run build
# ou
yarn build
```

### Preview do Build
```bash
npm run preview
# ou
yarn preview
```

## 📱 Componentes

### BuscaOperadoras
- Campo de busca por nome da operadora
- Tabela de resultados com paginação
- Formatação de valores monetários
- Indicadores de relevância

## 🔍 Integração com Backend
O frontend se comunica com a seguinte rota da API:

- `GET /api/operadoras/busca` - Busca de operadoras

## 📝 Notas
- A aplicação é responsiva e funciona em dispositivos móveis
- Utiliza Vuetify para componentes de UI
- Implementa cache de dados com Axios
- Suporta temas claro e escuro
- Inclui validação de formulários 
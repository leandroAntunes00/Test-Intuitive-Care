# Frontend - Sistema de Análise de Despesas das Operadoras

## 📋 Descrição
Interface web desenvolvida em Vue.js para visualização e análise de dados relacionados a operadoras de saúde e suas despesas.

## 🎯 Funcionalidades

### 1. Busca de Operadoras
- Pesquisa por nome da operadora
- Exibição de resultados com:
  - Total de eventos
  - Total de despesas
  - Relevância da busca
  - Percentual do total

### 2. Análise de Despesas
- Visualização do último trimestre
- Análise do último ano
- Tendência mensal em gráfico

## 🛠 Tecnologias Utilizadas
- Vue.js 3
- Vuetify 3
- Chart.js
- Vue Chart.js
- Axios

## 📁 Estrutura do Projeto
```
frontend/
├── src/
│   ├── components/     # Componentes Vue
│   │   ├── BuscaOperadoras.vue
│   │   └── LineChart.vue
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

### LineChart
- Gráfico de linha para tendências
- Formatação de valores no eixo Y
- Legendas e tooltips
- Responsividade

## 🔍 Integração com Backend
O frontend se comunica com as seguintes rotas da API:

- `GET /api/operadoras/busca` - Busca de operadoras
- `GET /api/despesas/ultimo-trimestre` - Dados do último trimestre
- `GET /api/despesas/ultimo-ano` - Dados do último ano
- `GET /api/despesas/tendencia-mensal` - Dados para o gráfico de tendência

## 📝 Notas
- A aplicação é responsiva e funciona em dispositivos móveis
- Utiliza Vuetify para componentes de UI
- Implementa cache de dados com Axios
- Suporta temas claro e escuro
- Inclui validação de formulários 
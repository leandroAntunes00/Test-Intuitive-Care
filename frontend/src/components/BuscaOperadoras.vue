<template>
  <v-card>
    <v-card-title>Busca de Operadoras</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="buscar">
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="tipoBusca"
              :items="tiposBusca"
              label="Tipo de Busca"
              @change="limparBusca"
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="termoBusca"
              :label="labelBusca"
              :placeholder="placeholderBusca"
              :loading="loading"
              @keyup.enter="buscar"
              clearable
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-btn
              color="primary"
              block
              :loading="loading"
              :disabled="!termoBusca.trim()"
              @click="buscar"
            >
              Buscar
            </v-btn>
          </v-col>
        </v-row>
      </v-form>

      <!-- Resultados em Cards -->
      <v-row v-if="resultados.length > 0" class="mt-4">
        <v-col 
          v-for="(operadora, index) in resultados" 
          :key="index"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card
            class="mx-auto"
            outlined
          >
            <v-card-title class="text-h6">
              {{ operadora.nome_fantasia || 'Nome não informado' }}
            </v-card-title>
            
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <strong>Registro ANS:</strong> {{ operadora.registro_ans }}
                </v-col>
                <v-col cols="12">
                  <strong>CNPJ:</strong> {{ formatarCNPJ(operadora.cnpj) }}
                </v-col>
                <v-col cols="12">
                  <strong>Razão Social:</strong> {{ operadora.razao_social }}
                </v-col>
                <v-col cols="12">
                  <strong>Modalidade:</strong> {{ operadora.modalidade }}
                </v-col>
                <v-col cols="12">
                  <strong>Localização:</strong> {{ operadora.cidade }} - {{ operadora.uf }}
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Tabela de Resultados -->
      <v-data-table
        v-if="resultados.length > 0"
        :headers="headers"
        :items="resultados"
        :loading="loading"
        class="elevation-1 mt-4"
        dense
        :items-per-page="10"
        :footer-props="{
          'items-per-page-options': [10, 20, 50, 100],
          'items-per-page-text': 'Itens por página'
        }"
      >
        <template #[`item.cnpj`]="{ item }">
          {{ formatarCNPJ(item.cnpj) }}
        </template>
      </v-data-table>

      <!-- Mensagens de Erro/Info -->
      <v-alert
        v-if="erro"
        type="error"
        class="mt-4"
      >
        {{ erro }}
      </v-alert>

      <v-alert
        v-if="!loading && buscaRealizada && resultados.length === 0"
        type="info"
        class="mt-4"
      >
        Nenhuma operadora encontrada com o termo "{{ termoBusca }}"
      </v-alert>

      <!-- Resumo dos Resultados -->
      <v-card
        v-if="resultados.length > 0"
        outlined
        class="mt-4"
      >
        <v-card-text>
          <div class="text-subtitle-1">
            Encontradas {{ resultados.length }} operadora(s)
          </div>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-card>
</template>

<script>
import axios from 'axios';

// Configuração base do Axios
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000
});

export default {
  name: 'BuscaOperadoras',
  data() {
    return {
      tipoBusca: 'cidade',  // Mudei o padrão para cidade
      tiposBusca: [
        { title: 'Cidade', value: 'cidade' },
        { title: 'CNPJ', value: 'cnpj' },
        { title: 'Nome Fantasia', value: 'nome-fantasia' },
        { title: 'Razão Social', value: 'razao-social' },
        { title: 'Modalidade', value: 'modalidade' },
        { title: 'Operadoras Ativas por Cidade', value: 'ativas-cidade' },
        { title: 'Operadoras Ativas por UF', value: 'ativas-uf' }
      ],
      termoBusca: '',
      loading: false,
      resultados: [],
      erro: null,
      buscaRealizada: false,
      headers: [
        { title: 'Registro ANS', key: 'registro_ans', sortable: true },
        { title: 'Nome Fantasia', key: 'nome_fantasia', sortable: true },
        { title: 'Razão Social', key: 'razao_social', sortable: true },
        { title: 'CNPJ', key: 'cnpj', sortable: true },
        { title: 'Modalidade', key: 'modalidade', sortable: true },
        { title: 'Cidade', key: 'cidade', sortable: true },
        { title: 'UF', key: 'uf', sortable: true }
      ]
    };
  },
  computed: {
    labelBusca() {
      const labels = {
        'cnpj': 'Digite o CNPJ',
        'nome-fantasia': 'Digite o nome fantasia',
        'razao-social': 'Digite a razão social',
        'cidade': 'Digite a cidade',
        'modalidade': 'Digite a modalidade',
        'ativas-cidade': 'Digite a cidade',
        'ativas-uf': 'Digite a UF'
      };
      return labels[this.tipoBusca] || 'Digite o termo de busca';
    },
    placeholderBusca() {
      const placeholders = {
        'cnpj': 'Ex: 12345678901234',
        'nome-fantasia': 'Ex: SulAmerica',
        'razao-social': 'Ex: SulAmerica Seguradora',
        'cidade': 'Ex: Sao Paulo',
        'modalidade': 'Ex: Cooperativa',
        'ativas-cidade': 'Ex: Rio de Janeiro',
        'ativas-uf': 'Ex: SP'
      };
      return placeholders[this.tipoBusca] || 'Digite sua busca';
    }
  },
  methods: {
    limparBusca() {
      this.termoBusca = '';
      this.resultados = [];
      this.erro = null;
      this.buscaRealizada = false;
    },
    async buscar() {
      if (!this.termoBusca.trim()) {
        this.erro = 'Por favor, digite um termo para busca';
        return;
      }

      this.loading = true;
      this.erro = null;
      this.resultados = [];
      this.buscaRealizada = true;

      try {
        let url;
        const termo = encodeURIComponent(this.termoBusca.trim());
        
        switch (this.tipoBusca) {
          case 'cnpj':
            url = `/operadoras/cnpj/${termo}`;
            break;
          case 'nome-fantasia':
            url = `/operadoras/nome-fantasia/${termo}`;
            break;
          case 'razao-social':
            url = `/operadoras/razao-social/${termo}`;
            break;
          case 'cidade':
            url = `/operadoras/cidade/${termo}`;
            break;
          case 'modalidade':
            url = `/operadoras/modalidade/${termo}`;
            break;
          case 'ativas-cidade':
            url = `/operadoras-ativas/cidade/${termo}`;
            break;
          case 'ativas-uf':
            url = `/operadoras-ativas/uf/${termo}`;
            break;
        }

        console.log('Fazendo requisição para:', url); // Debug
        const response = await api.get(url);
        console.log('Resposta:', response.data); // Debug
        
        if (Array.isArray(response.data)) {
          this.resultados = response.data;
        } else if (response.data) {
          this.resultados = [response.data];
        }

      } catch (error) {
        console.error('Erro na busca:', error);
        if (error.response) {
          if (error.response.status === 404) {
            this.erro = 'Nenhuma operadora encontrada com os critérios informados';
          } else {
            this.erro = `Erro ao buscar operadoras: ${error.response.data.detail || 'Tente novamente'}`;
          }
        } else {
          this.erro = 'Erro ao conectar com o servidor. Verifique sua conexão.';
        }
      } finally {
        this.loading = false;
      }
    },
    formatarCNPJ(cnpj) {
      if (!cnpj) return '';
      return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
    }
  }
};
</script>

<style scoped>
.v-data-table {
  margin-top: 1rem;
}

.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style> 
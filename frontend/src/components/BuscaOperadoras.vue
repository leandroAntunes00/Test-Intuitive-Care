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
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-btn
              color="primary"
              block
              :loading="loading"
              @click="buscar"
            >
              Buscar
            </v-btn>
          </v-col>
        </v-row>
      </v-form>

      <v-data-table
        v-if="resultados.length > 0"
        :headers="headers"
        :items="resultados"
        :loading="loading"
        class="elevation-1 mt-4"
      >
        <template #[`item.total_despesas`]="{ item }">
          R$ {{ formatarValor(item.total_despesas) }}
        </template>
        <template #[`item.percentual_total`]="{ item }">
          {{ item.percentual_total }}%
        </template>
        <template #[`item.relevancia`]="{ item }">
          {{ (item.relevancia * 100).toFixed(2) }}%
        </template>
        <template #[`item.cnpj`]="{ item }">
          {{ formatarCNPJ(item.cnpj) }}
        </template>
      </v-data-table>

      <v-alert
        v-if="erro"
        type="error"
        class="mt-4"
      >
        {{ erro }}
      </v-alert>

      <v-alert
        v-if="!loading && termoBusca && resultados.length === 0"
        type="info"
        class="mt-4"
      >
        Nenhuma operadora encontrada com o termo "{{ termoBusca }}"
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BuscaOperadoras',
  data() {
    return {
      tipoBusca: 'cnpj',
      tiposBusca: [
        { title: 'CNPJ', value: 'cnpj' },
        { title: 'Nome Fantasia', value: 'nome-fantasia' },
        { title: 'Razão Social', value: 'razao-social' },
        { title: 'Cidade', value: 'cidade' },
        { title: 'Modalidade', value: 'modalidade' },
        { title: 'Operadoras Ativas por Cidade', value: 'ativas-cidade' },
        { title: 'Operadoras Ativas por UF', value: 'ativas-uf' }
      ],
      termoBusca: '',
      loading: false,
      resultados: [],
      erro: null,
      headers: [
        { title: 'Registro ANS', key: 'registro_ans' },
        { title: 'Nome Fantasia', key: 'nome_fantasia' },
        { title: 'Razão Social', key: 'razao_social' },
        { title: 'CNPJ', key: 'cnpj' },
        { title: 'Modalidade', key: 'modalidade' },
        { title: 'Cidade', key: 'cidade' },
        { title: 'UF', key: 'uf' },
        { title: 'Total Eventos', key: 'total_eventos' },
        { title: 'Total Despesas', key: 'total_despesas' },
        { title: 'Relevância', key: 'relevancia' },
        { title: '% do Total', key: 'percentual_total' }
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
      return labels[this.tipoBusca];
    },
    placeholderBusca() {
      const placeholders = {
        'cnpj': 'Ex: 12345678901234',
        'nome-fantasia': 'Ex: SulAmérica',
        'razao-social': 'Ex: SulAmérica Seguradora de Vida e Previdência',
        'cidade': 'Ex: São Paulo',
        'modalidade': 'Ex: Cooperativa',
        'ativas-cidade': 'Ex: Rio de Janeiro',
        'ativas-uf': 'Ex: SP'
      };
      return placeholders[this.tipoBusca];
    }
  },
  methods: {
    limparBusca() {
      this.termoBusca = '';
      this.resultados = [];
      this.erro = null;
    },
    async buscar() {
      if (!this.termoBusca.trim()) return;

      this.loading = true;
      this.erro = null;

      try {
        let url;
        switch (this.tipoBusca) {
          case 'cnpj':
            url = `/api/operadoras/cnpj/${this.termoBusca}`;
            break;
          case 'nome-fantasia':
            url = `/api/operadoras/nome-fantasia/${this.termoBusca}`;
            break;
          case 'razao-social':
            url = `/api/operadoras/razao-social/${this.termoBusca}`;
            break;
          case 'cidade':
            url = `/api/operadoras/cidade/${this.termoBusca}`;
            break;
          case 'modalidade':
            url = `/api/operadoras/modalidade/${this.termoBusca}`;
            break;
          case 'ativas-cidade':
            url = `/api/operadoras-ativas/cidade/${this.termoBusca}`;
            break;
          case 'ativas-uf':
            url = `/api/operadoras-ativas/uf/${this.termoBusca}`;
            break;
        }

        const response = await axios.get(url);
        this.resultados = Array.isArray(response.data) ? response.data : [response.data];
      } catch (error) {
        this.erro = 'Erro ao buscar operadoras. Tente novamente.';
        console.error('Erro na busca:', error);
      } finally {
        this.loading = false;
      }
    },
    formatarValor(valor) {
      return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(valor);
    },
    formatarCNPJ(cnpj) {
      return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
    }
  }
};
</script>

<style scoped>
.v-data-table {
  margin-top: 1rem;
}
</style> 
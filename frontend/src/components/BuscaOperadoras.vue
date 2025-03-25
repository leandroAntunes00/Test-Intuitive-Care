<template>
  <v-card>
    <v-card-title>Busca de Operadoras</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="buscar">
        <v-row>
          <v-col cols="12" md="8">
            <v-text-field
              v-model="termoBusca"
              label="Digite o nome da operadora"
              placeholder="Ex: SulAmérica, Bradesco..."
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
      termoBusca: '',
      loading: false,
      resultados: [],
      erro: null,
      headers: [
        { title: 'Operadora', key: 'operadora' },
        { title: 'Total Eventos', key: 'total_eventos' },
        { title: 'Total Despesas', key: 'total_despesas' },
        { title: 'Relevância', key: 'relevancia' },
        { title: '% do Total', key: 'percentual_total' }
      ]
    };
  },
  methods: {
    async buscar() {
      if (!this.termoBusca.trim()) return;

      this.loading = true;
      this.erro = null;

      try {
        const response = await axios.get('/api/operadoras/busca', {
          params: {
            termo: this.termoBusca,
            limite: 10
          }
        });
        this.resultados = response.data;
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
    }
  }
};
</script>

<style scoped>
.v-data-table {
  margin-top: 1rem;
}
</style> 
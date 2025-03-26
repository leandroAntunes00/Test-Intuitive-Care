<template>
  <v-card>
    <v-card-title>Maiores Despesas com Sinistros</v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="despesas"
        :loading="loading"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item="{ item }">
          <tr>
            <td>
              <v-chip
                :color="getRankingColor(item.ranking)"
                small
              >
                {{ item.ranking }}º
              </v-chip>
            </td>
            <td>{{ item.nome_operadora }}</td>
            <td>{{ item.registro_ans }}</td>
            <td>{{ formatarValor(item.valor_despesa) }}</td>
            <td>{{ item.trimestre }}</td>
          </tr>
        </template>
      </v-data-table>

      <v-alert
        v-if="erro"
        type="error"
        class="mt-4"
      >
        {{ erro }}
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script>
import api from '../config/api';

export default {
  name: 'MaioresSinistros',
  data() {
    return {
      headers: [
        { title: 'Ranking', key: 'ranking', sortable: false },
        { title: 'Operadora', key: 'nome_operadora' },
        { title: 'Registro ANS', key: 'registro_ans' },
        { title: 'Valor Despesa', key: 'valor_despesa', sortable: true },
        { title: 'Trimestre', key: 'trimestre' }
      ],
      despesas: [],
      loading: false,
      erro: null
    };
  },
  methods: {
    async buscarDespesas() {
      this.loading = true;
      this.erro = null;
      
      try {
        const response = await api.get('/demonstracoes/maiores-despesas-eventos');
        this.despesas = response.data;
      } catch (error) {
        console.error('Erro ao buscar despesas:', error);
        this.erro = 'Erro ao carregar dados. Por favor, tente novamente.';
      } finally {
        this.loading = false;
      }
    },
    formatarValor(valor) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(valor);
    },
    getRankingColor(ranking) {
      const cores = {
        1: 'gold',
        2: 'grey lighten-1',
        3: 'brown lighten-1'
      };
      return cores[ranking] || 'grey';
    }
  },
  mounted() {
    this.buscarDespesas();
  }
};
</script> 
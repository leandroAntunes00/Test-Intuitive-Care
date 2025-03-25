<template>
  <v-card>
    <v-card-title>Maiores Despesas com Sinistros no Ano</v-card-title>
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
            <td>{{ item.quantidade_eventos }}</td>
            <td>{{ formatarValor(item.media_por_evento) }}</td>
            <td>{{ item.ano_referencia }}</td>
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
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'accept': 'application/json'
  }
});

export default {
  name: 'MaioresSinistrosAno',
  data() {
    return {
      headers: [
        { title: 'Ranking', key: 'ranking', sortable: false },
        { title: 'Operadora', key: 'nome_operadora' },
        { title: 'Registro ANS', key: 'registro_ans' },
        { title: 'Valor Total', key: 'valor_despesa', sortable: true },
        { title: 'Quantidade de Eventos', key: 'quantidade_eventos', sortable: true },
        { title: 'Média por Evento', key: 'media_por_evento', sortable: true },
        { title: 'Ano', key: 'ano_referencia' }
      ],
      despesas: [],
      loading: false,
      erro: null,
      buscando: false,
      tentativas: 0,
      maxTentativas: 3
    };
  },
  methods: {
    async buscarDespesas() {
      if (this.buscando) {
        console.log('Já existe uma busca em andamento, aguardando...');
        return;
      }

      this.loading = true;
      this.erro = null;
      this.buscando = true;
      this.tentativas = 0;
      
      await this.tentarBuscarDespesas();
    },

    async tentarBuscarDespesas() {
      try {
        console.log(`Iniciando busca de despesas anuais... (Tentativa ${this.tentativas + 1}/${this.maxTentativas})`);
        const response = await api.get('/demonstracoes/maiores-despesas-eventos-ano');
        console.log('Resposta recebida:', response.data);
        
        if (!response.data || !Array.isArray(response.data)) {
          throw new Error('Formato de dados inválido recebido do servidor');
        }
        
        this.despesas = response.data.map(item => ({
          ...item,
          valor_despesa: Number(item.valor_despesa),
          media_por_evento: Number(item.media_por_evento),
          quantidade_eventos: Number(item.quantidade_eventos)
        }));
        
        console.log('Dados processados:', this.despesas);
        this.buscando = false;
      } catch (error) {
        console.error(`Erro na tentativa ${this.tentativas + 1}:`, error.response || error);
        
        if (error.code === 'ECONNABORTED' && this.tentativas < this.maxTentativas) {
          this.tentativas++;
          console.log(`Tentando novamente em 2 segundos... (${this.tentativas}/${this.maxTentativas})`);
          setTimeout(() => this.tentarBuscarDespesas(), 2000);
        } else {
          this.erro = `Erro ao carregar dados: ${error.response?.data?.detail || error.message || 'Erro desconhecido'}`;
          this.buscando = false;
        }
      } finally {
        if (!this.buscando) {
          this.loading = false;
        }
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
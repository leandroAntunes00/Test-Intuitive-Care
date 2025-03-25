<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-title>Análise de Despesas das Operadoras</v-app-bar-title>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <BuscaOperadoras />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title>Despesas no Último Trimestre</v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="headersTrimestre"
                  :items="despesasTrimestre"
                  :loading="loading"
                  class="elevation-1"
                >
                  <template v-slot:item.total_despesas="{ item }">
                    R$ {{ formatarValor(item.total_despesas) }}
                  </template>
                  <template v-slot:item.percentual_total="{ item }">
                    {{ item.percentual_total }}%
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title>Despesas no Último Ano</v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="headersAno"
                  :items="despesasAno"
                  :loading="loading"
                  class="elevation-1"
                >
                  <template v-slot:item.total_despesas="{ item }">
                    R$ {{ formatarValor(item.total_despesas) }}
                  </template>
                  <template v-slot:item.media_por_evento="{ item }">
                    R$ {{ formatarValor(item.media_por_evento) }}
                  </template>
                  <template v-slot:item.percentual_total="{ item }">
                    {{ item.percentual_total }}%
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title>Tendência Mensal</v-card-title>
              <v-card-text>
                <LineChart :chart-data="chartData" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios';
import LineChart from './components/LineChart.vue';
import BuscaOperadoras from './components/BuscaOperadoras.vue';

export default {
  name: 'App',
  components: {
    LineChart,
    BuscaOperadoras
  },
  data() {
    return {
      loading: false,
      despesasTrimestre: [],
      despesasAno: [],
      tendenciaMensal: [],
      headersTrimestre: [
        { title: 'Operadora', key: 'operadora' },
        { title: 'Total Despesas', key: 'total_despesas' },
        { title: 'Quantidade Eventos', key: 'quantidade_eventos' },
        { title: '% do Total', key: 'percentual_total' }
      ],
      headersAno: [
        { title: 'Operadora', key: 'operadora' },
        { title: 'Total Despesas', key: 'total_despesas' },
        { title: 'Quantidade Eventos', key: 'quantidade_eventos' },
        { title: 'Média por Evento', key: 'media_por_evento' },
        { title: '% do Total', key: 'percentual_total' }
      ]
    };
  },
  computed: {
    chartData() {
      return {
        labels: this.tendenciaMensal.map(item => new Date(item.mes).toLocaleDateString('pt-BR')),
        datasets: [
          {
            label: 'Total Despesas',
            data: this.tendenciaMensal.map(item => item.total_despesas),
            borderColor: '#1976D2',
            fill: false
          },
          {
            label: 'Média por Evento',
            data: this.tendenciaMensal.map(item => item.media_por_evento),
            borderColor: '#4CAF50',
            fill: false
          }
        ]
      };
    }
  },
  methods: {
    async carregarDados() {
      this.loading = true;
      try {
        const [trimestreRes, anoRes, tendenciaRes] = await Promise.all([
          axios.get('http://localhost:8000/api/despesas/ultimo-trimestre'),
          axios.get('http://localhost:8000/api/despesas/ultimo-ano'),
          axios.get('http://localhost:8000/api/despesas/tendencia-mensal')
        ]);

        this.despesasTrimestre = trimestreRes.data;
        this.despesasAno = anoRes.data;
        this.tendenciaMensal = tendenciaRes.data;
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
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
  },
  mounted() {
    this.carregarDados();
  }
};
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}
</style> 
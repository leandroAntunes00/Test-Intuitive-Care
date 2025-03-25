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
            <v-row no-gutters>
              <v-col cols="6" class="pr-1">
                <v-btn
                  color="primary"
                  block
                  :loading="loading"
                  :disabled="campoVazio"
                  @click="buscar"
                >
                  Buscar
                </v-btn>
              </v-col>
              <v-col cols="6" class="pl-1">
                <v-btn
                  color="error"
                  block
                  :disabled="resultados.length === 0"
                  @click="limparResultados"
                >
                  Limpar
                </v-btn>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-form>

      <!-- Resultados em Cards com Paginação -->
      <div v-if="resultados.length > 0">
        <v-row>
          <v-col 
            v-for="(operadora, index) in resultadosPaginados" 
            :key="index"
            cols="12"
            sm="6"
            md="4"
          >
            <v-card
              class="mx-auto"
              outlined
              hover
            >
              <v-card-title class="text-h6 primary--text">
                {{ operadora.nome_fantasia === 'nan' ? operadora.razao_social : (operadora.nome_fantasia || 'Nome não informado') }}
              </v-card-title>
              
              <v-card-text>
                <v-row no-gutters>
                  <v-col cols="12" class="mb-2">
                    <strong>Registro ANS:</strong> {{ operadora.registro_ans }}
                  </v-col>
                  <v-col cols="12" class="mb-2">
                    <strong>CNPJ:</strong> {{ formatarCNPJ(operadora.cnpj) }}
                  </v-col>
                  <v-col cols="12" class="mb-2" v-if="operadora.nome_fantasia !== 'nan'">
                    <strong>Razão Social:</strong> {{ operadora.razao_social }}
                  </v-col>
                  <v-col cols="12" class="mb-2">
                    <strong>Modalidade:</strong> {{ operadora.modalidade }}
                  </v-col>
                  
                  <!-- Endereço -->
                  <v-col cols="12" class="mb-2">
                    <strong>Endereço:</strong><br>
                    <div v-if="operadora.logradouro || operadora.numero || operadora.complemento || operadora.bairro">
                      <template v-if="operadora.logradouro">{{ operadora.logradouro }}</template><!--
                      --><template v-if="operadora.numero">, {{ operadora.numero }}</template><!--
                      --><template v-if="operadora.complemento">, {{ operadora.complemento }}</template>
                      <template v-if="operadora.bairro"><br>Bairro: {{ operadora.bairro }}</template>
                      <br>{{ operadora.cidade }} - {{ operadora.uf }}
                      <template v-if="operadora.cep"><br>CEP: {{ formatarCEP(operadora.cep) }}</template>
                    </div>
                    <div v-if="!operadora.logradouro && !operadora.numero && !operadora.complemento && !operadora.bairro">
                      {{ operadora.cidade }} - {{ operadora.uf }}
                      <template v-if="operadora.cep"><br>CEP: {{ formatarCEP(operadora.cep) }}</template>
                    </div>
                  </v-col>

                  <!-- Informações de Contato -->
                  <v-col v-if="operadora.telefone" cols="12" class="mb-2">
                    <strong>Telefone:</strong> {{ operadora.telefone }}
                  </v-col>
                  <v-col v-if="operadora.email" cols="12" class="mb-2">
                    <strong>Email:</strong> {{ operadora.email }}
                  </v-col>
                  <v-col v-if="operadora.representante" cols="12" class="mb-2">
                    <strong>Representante:</strong> {{ operadora.representante }}
                  </v-col>
                  <v-col v-if="operadora.data_registro_ans" cols="12" class="mb-2">
                    <strong>Data de Registro ANS:</strong> {{ formatarData(operadora.data_registro_ans) }}
                  </v-col>

                  <!-- Indicador de Operadora Ativa -->
                  <v-col cols="12" class="mt-2">
                    <v-chip
                      :color="operadora.is_ativa ? 'success' : 'warning'"
                      small
                      class="mr-2"
                    >
                      {{ operadora.is_ativa ? 'Operadora Ativa' : 'Operadora Inativa' }}
                    </v-chip>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Paginação -->
        <v-row class="mt-4">
          <v-col cols="12" class="text-center">
            <v-pagination
              v-model="paginaAtual"
              :length="totalPaginas"
              :total-visible="7"
            ></v-pagination>
          </v-col>
          <v-col cols="12" sm="4" class="text-center">
            <v-select
              v-model="itensPorPagina"
              :items="opcoesItensPorPagina"
              label="Itens por página"
              dense
            ></v-select>
          </v-col>
          <v-col cols="12" sm="8" class="text-center">
            <div class="text-subtitle-1">
              Mostrando {{ inicio + 1 }}-{{ Math.min(fim, resultados.length) }} de {{ resultados.length }} operadora(s)
            </div>
          </v-col>
        </v-row>
      </div>

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
      tipoBusca: 'cidade',
      tiposBusca: [
        { title: 'Cidade', value: 'cidade' },
        { title: 'CNPJ', value: 'cnpj' },
        { title: 'Nome Fantasia', value: 'nome-fantasia' },
        { title: 'Razão Social', value: 'razao-social' },
        { title: 'Operadoras por UF', value: 'ativas-uf' }
      ],
      termoBusca: '',
      loading: false,
      resultados: [],
      erro: null,
      buscaRealizada: false,
      paginaAtual: 1,
      itensPorPagina: 12,
      opcoesItensPorPagina: [
        { text: '6 itens', value: 6 },
        { text: '12 itens', value: 12 },
        { text: '24 itens', value: 24 },
        { text: '48 itens', value: 48 }
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
        'ativas-uf': 'Ex: SP'
      };
      return placeholders[this.tipoBusca] || 'Digite sua busca';
    },
    campoVazio() {
      return !this.termoBusca || !this.termoBusca.trim();
    },
    totalPaginas() {
      return Math.ceil(this.resultados.length / this.itensPorPagina);
    },
    inicio() {
      return (this.paginaAtual - 1) * this.itensPorPagina;
    },
    fim() {
      return this.inicio + this.itensPorPagina;
    },
    resultadosPaginados() {
      return this.resultados.slice(this.inicio, this.fim);
    }
  },
  watch: {
    itensPorPagina() {
      this.paginaAtual = 1;
    },
    termoBusca(novoValor) {
      // Se o campo for limpo, reseta os resultados
      if (!novoValor || novoValor.trim() === '') {
        this.limparResultados();
      }
    }
  },
  methods: {
    limparBusca() {
      this.termoBusca = '';
      this.resultados = [];
      this.erro = null;
      this.buscaRealizada = false;
      this.paginaAtual = 1;
    },
    limparResultados() {
      this.resultados = [];
      this.erro = null;
      this.buscaRealizada = false;
      this.paginaAtual = 1;
    },
    normalizeText(text) {
      if (!text) return '';
      return text.normalize('NFD')
                .replace(/[\u0300-\u036f]/g, '') // remove acentos
                .toLowerCase();
    },
    async buscar() {
      if (!this.termoBusca || !this.termoBusca.trim()) {
        this.erro = 'Por favor, digite um termo para busca';
        return;
      }

      this.loading = true;
      this.erro = null;
      this.resultados = [];
      this.buscaRealizada = true;
      this.paginaAtual = 1;

      try {
        let url;
        const termoNormalizado = this.normalizeText(this.termoBusca.trim());
        const termo = encodeURIComponent(termoNormalizado);
        
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
          case 'ativas-uf':
            url = `/operadoras/uf/${termo.toUpperCase()}`;
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
    },
    formatarData(data) {
      if (!data) return '';
      const date = new Date(data);
      return date.toLocaleDateString('pt-BR');
    },
    formatarCEP(cep) {
      if (!cep) return '';
      return cep.replace(/^(\d{5})(\d{3})$/, "$1-$2");
    }
  }
};
</script>

<style scoped>
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.mb-2 {
  margin-bottom: 8px;
}
</style> 
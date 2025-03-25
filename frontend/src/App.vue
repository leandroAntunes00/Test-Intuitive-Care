<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-title>Busca de Operadoras</v-app-bar-title>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <BuscaOperadoras />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import BuscaOperadoras from './components/BuscaOperadoras.vue';

export default {
  name: 'App',
  components: {
    BuscaOperadoras
  }
};
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}
</style> 
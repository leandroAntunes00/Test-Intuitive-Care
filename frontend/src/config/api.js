import axios from 'axios';

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL,
  timeout: process.env.VUE_APP_API_TIMEOUT,
  headers: {
    'accept': 'application/json'
  }
});

export default api; 
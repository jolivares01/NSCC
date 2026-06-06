import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // La URL de tu Gateway
  timeout: 5000,
});

export default api;
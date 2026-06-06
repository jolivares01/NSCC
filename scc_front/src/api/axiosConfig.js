// src/api/axiosConfig.js
import axios from 'axios';

const api = axios.create({
  // Asegúrate de incluir /api/v1 si lo pusiste en el Backend
  baseURL: 'http://localhost:8000/api/v1', 
  headers: {
    'Content-Type': 'application/json'
  }
});

export default api;
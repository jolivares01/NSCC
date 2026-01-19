import api from '@/api/axiosConfig';

export default {
  // Recibe el tipo (ventas/postventa) y el rango de fechas
  getEstadisticas(tipo, inicio, fin) {
    return api.get('/dashboard/estadisticas', {
      params: {
        tipo: tipo,
        inicio: inicio,
        fin: fin
      }
    });
  }
};
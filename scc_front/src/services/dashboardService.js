import api from '@/api/axiosConfig';

export default {
  // Ahora solo recibe el periodo (Ej: '2026-02')
  getMetrics(periodo) {
    return api.get('/dashboard/metrics', {
      params: {
        periodo: periodo
      }
    });
  }
};
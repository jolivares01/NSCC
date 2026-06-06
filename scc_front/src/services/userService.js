import api from '@/api/axiosConfig';

export default {
  // Registro de usuario (POST) - Ahora enviará 8 parámetros según el backend
  registrar(data) {
    return api.post('/users/registrar-usuario', data);
  },

  // Obtener lista para la tabla principal (GET)
  getUsuarioVistaPrevia(username) {
    return api.get(`/users/usuarios-vista-previa`, {
      params: { username }
    });
  },

  // --- CATÁLOGOS MAESTROS ---

  getRegiones() {
    return api.get('/users/maestros/regiones');
  },
  
  getRoles() {
    return api.get('/users/maestros/roles');
  },

  getLocalidadesPorRegion(regionId) {
    return api.get('/users/maestros/localidades', {
      params: { region_id: regionId }
    });
  },

  // Obtener tipos de agente (A, B, E) para cálculo de comisión
  getTiposUsuario() {
    return api.get('/users/maestros/tipos-usuario'); //
  },

  // Obtener canales de venta (Corporativo, Agente, etc.)
  getCanales() {
    return api.get('/users/maestros/canales').then(res => {
      res.data = res.data.map(c => ({
        ...c,
        // Si c.description es undefined, pondrá un texto vacío en lugar de la palabra 'undefined'
        full_label: `${c.id_channel} - ${c.description || 'Sin nombre'}`
      }));
      return res;
    });
  },

  // --- GESTIÓN DE USUARIOS ---

  getUsuario(username) {
    return api.get(`/users/usuarios/${username}`);
  },

  actualizar(username, userData) {
    return api.put(`/users/usuarios/${username}`, userData);
  },

  consultarUsuario(username) {
    return api.get('/users/consultar-usuario', {
      params: { username }
    });
  },
};
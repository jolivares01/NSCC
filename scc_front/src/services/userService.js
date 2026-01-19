import api from '@/api/axiosConfig';

export default {
  // Registro de usuario (POST)
  registrar(data) {
    return api.post('/users/registrar-usuario', data);
  },

  // Obtener lista para la tabla principal (GET) - NUEVO: con búsqueda
  getUsuarioVistaPrevia(username) {
  return api.get(`/users/usuarios-vista-previa`, {
    params: { username }  // Cambia de 'search' a 'username'
  });
  },
  // Obtener catálogos para los selects del formulario (GET)
  getRegiones() {
    return api.get('/users/maestros/regiones');
  },
  
  getRoles() {
    return api.get('/users/maestros/roles');
  },

  // Obtener un usuario específico para editar (GET) - DETALLES COMPLETOS
  getUsuario(username) {
    return api.get(`/users/usuarios/${username}`);
  },

  // Actualizar usuario (PUT)
  actualizar(username, userData) {
    // userData debe cumplir con la clase ActualizarUsuario del backend
    return api.put(`/users/usuarios/${username}`, userData);
  },
    consultarUsuario(username) {
    return api.get('/users/consultar-usuario', {
      params: { username }
    });
  },
  // userService.js - Agregar este método:
getLocalidadesPorRegion(regionId) {
  return api.get('/users/maestros/localidades', {
    params: { region_id: regionId }
  });
},
};
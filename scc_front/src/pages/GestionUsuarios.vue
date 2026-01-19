<template>
  <div class="content">
    <div class="row">
      <div class="col-md-12">
        <card>
          <template slot="header">
            <div class="row align-items-center">
              <div class="col-md-12">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h4 class="card-title">Gestión de Usuarios</h4>
                    <p class="category">Consulta y edición de perfiles registrados</p>
                  </div>
                  <div class="d-flex align-items-center" style="width: 350px;">
                    <div class="input-group search-container">
                      <input 
                        type="text" 
                        class="form-control" 
                        placeholder="Buscar usuario por login..."
                        v-model="searchQuery"
                        @keyup.enter="ejecutarBusqueda"
                        :disabled="buscando"
                      >
                      <div class="input-group-append">
                        <button 
                          class="btn btn-primary" 
                          type="button"
                          @click="ejecutarBusqueda"
                          :disabled="buscando"
                        >
                          <i class="tim-icons icon-zoom-split"></i>
                          Buscar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <div class="table-responsive" style="overflow-y: hidden;">
            <!-- Indicador de carga -->
            <div v-if="buscando" class="text-center py-4">
              <div class="d-flex justify-content-center align-items-center">
                <i class="tim-icons icon-refresh-02 loading-spinner mr-2"></i>
                <span>Buscando usuarios...</span>
              </div>
            </div>

            <table v-else class="table tablesorter">
              <thead class="text-primary">
                <tr>
                  <th>Usuario</th>
                  <th>Región</th>
                  <th>Localidad</th>
                  <th>Roles</th>
                  <th class="text-center">Estado</th>
                  <th class="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in usuarios" :key="u.usuario">
                  <td>{{ u.usuario }}</td>
                  <td>{{ u.region }}</td>
                  <td>{{ u.localidad }}</td>
                  <td>{{ u.roles_asignados || 'Sin roles asignados' }}</td>
                  <td class="text-center">
                    <span :class="u.estado === 'Activo' ? 'badge badge-success' : 'badge badge-danger'">
                      {{ u.estado }}
                    </span>
                  </td>
                  <td class="text-right">
                    <base-button 
                      size="sm" 
                      type="info" 
                      icon 
                      @click="abrirEdicion(u.usuario)"
                      title="Editar"
                      :disabled="editando"
                    >
                      <i class="tim-icons icon-pencil"></i>
                    </base-button>
                  </td>
                </tr>
                <tr v-if="usuarios.length === 0 && !buscando">
                  <td colspan="6" class="text-center text-muted py-4">
                    <template v-if="searchQuery">
                      No se encontraron usuarios que coincidan con "{{ searchQuery }}"
                    </template>
                    <template v-else>
                      <i class="tim-icons icon-alert-circle-exc mr-2"></i>
                      Ingrese un usuario en el campo de búsqueda para comenzar
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </card>
      </div>
    </div>

    <!-- Modal de Edición -->
    <modal :show.sync="showEditModal" @close="cerrarModal">
      <template slot="header">
        <h5 class="modal-title">Editar Usuario</h5>
      </template>
      <div>
        <form @submit.prevent="guardarCambios">
          <div class="row">
            <div class="col-md-12">
              <div class="form-group">
                <label>Usuario</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="editUser.username" 
                  readonly
                >
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label>Región</label>
                <select 
                  class="form-control" 
                  v-model="editUser.id_region" 
                  @change="cargarLocalidades"
                  :disabled="cargandoLocalidades"
                  required
                >
                  <option value="">Seleccionar región</option>
                  <option 
                    v-for="region in regiones" 
                    :key="region.id_region" 
                    :value="region.id_region"
                  >
                    {{ region.display_value }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label>Localidad</label>
                <select 
                  class="form-control" 
                  v-model="editUser.location_name"
                  :disabled="!editUser.id_region || cargandoLocalidades || localidades.length === 0"
                  required
                >
                  <option value="">Seleccionar localidad</option>
                  <option 
                    v-for="loc in localidades" 
                    :key="loc.id_location" 
                    :value="loc.display_value"
                  >
                    {{ loc.display_value }}
                  </option>
                </select>
                <small 
                  v-if="!editUser.id_region" 
                  class="form-text text-muted"
                >
                  Seleccione una región primero
                </small>
                <small 
                  v-if="editUser.id_region && localidades.length === 0 && !cargandoLocalidades" 
                  class="form-text text-warning"
                >
                  No hay localidades disponibles para esta región
                </small>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-12">
              <div class="form-group">
                <label>Rol Principal</label>
                <select 
                  class="form-control" 
                  v-model="editUser.id_rol"
                  required
                >
                  <option value="">Seleccionar rol</option>
                  <option 
                    v-for="rol in roles" 
                    :key="rol.id_rol" 
                    :value="rol.id_rol"
                  >
                    {{ rol.rol_name }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-12">
              <div class="form-group">
                <div class="form-check">
                  <label class="form-check-label">
                    <input 
                      type="checkbox" 
                      class="form-check-input" 
                      v-model="editUser.is_active"
                    >
                    <span class="form-check-sign"></span>
                    Usuario Activo
                  </label>
                </div>
                <small class="form-text text-muted">
                  Desmarcar para deshabilitar el acceso del usuario
                </small>
              </div>
            </div>
          </div>
        </form>
      </div>
      <template slot="footer">
        <base-button type="secondary" @click="cerrarModal">
          Cancelar
        </base-button>
        <base-button 
          type="primary" 
          @click="guardarCambios"
          :disabled="guardando || !formularioValido"
        >
          <span v-if="guardando">
            <i class="tim-icons icon-refresh-02 loading-spinner mr-2"></i>
            Guardando...
          </span>
          <span v-else>
            <i class="tim-icons icon-check-2 mr-2"></i>
            Guardar Cambios
          </span>
        </base-button>
      </template>
    </modal>

    <!-- Notificación Toast -->
    <notification
      :show.sync="showNotification"
      :type="notificationType"
      :message="notificationMessage"
      @close="showNotification = false"
    >
    </notification>
  </div>
</template>

<script>
import userService from '@/services/userService';
import Modal from '@/components/Modal.vue';
import Notification from '@/components/Notification.vue';

export default {
  name: 'GestionUsuarios',
  components: {
    Modal,
    Notification
  },
  data() {
    return {
      usuarios: [],
      searchQuery: '',
      buscando: false,
      editando: false,
      guardando: false,
      
      // Modal de edición
      showEditModal: false,
      
      // Datos del usuario en edición
      editUser: {
        username: '',
        id_region: 0,
        location_name: '',
        id_rol: '',
        is_active: true,
        changedBy: 'ADMIN_TEST'
      },
      
      // Catálogos
      regiones: [],
      localidades: [],
      roles: [],
      cargandoLocalidades: false,
      
      // Notificación
      showNotification: false,
      notificationType: 'success',
      notificationMessage: ''
    };
  },
  computed: {
    formularioValido() {
      return (
        this.editUser.username &&
        this.editUser.id_region &&
        this.editUser.location_name &&
        this.editUser.id_rol
      );
    }
  },
  async mounted() {
    // Cargar catálogos al inicio
    await this.cargarCatalogos();
  },
  methods: {
    async ejecutarBusqueda() {
      if (!this.searchQuery || this.searchQuery.trim() === '') {
        this.mostrarNotificacion('Debe ingresar un usuario para buscar', 'warning');
        this.usuarios = [];
        return;
      }
      
      this.buscando = true;
      const usuarioBuscado = this.searchQuery.trim();
      
      try {
        const res = await userService.consultarUsuario(usuarioBuscado);
        
        if (res.data && res.data.length > 0) {
          this.usuarios = res.data;
          this.mostrarNotificacion(`Usuario "${usuarioBuscado}" encontrado`, 'success');
        } else {
          this.usuarios = [];
          this.mostrarNotificacion(`No se encontró el usuario "${usuarioBuscado}"`, 'warning');
        }
        
      } catch (error) {
        console.error("❌ Error en la búsqueda:", error);
        this.usuarios = [];
        
        let mensaje = 'Error al buscar usuario';
        if (error.response) {
          if (error.response.status === 400) {
            mensaje = error.response.data.detail?.mensaje || 'Usuario no válido';
          } else if (error.response.status === 422) {
            mensaje = 'El parámetro "username" es obligatorio';
          } else if (error.response.status === 500) {
            mensaje = 'Error del servidor. Por favor, intente más tarde.';
          }
        }
        
        this.mostrarNotificacion(mensaje, 'danger');
      } finally {
        this.buscando = false;
      }
    },
    
    async cargarCatalogos() {
      try {
        // Cargar regiones y roles en paralelo
        const [regionesRes, rolesRes] = await Promise.all([
          userService.getRegiones(),
          userService.getRoles()
        ]);
        
        this.regiones = regionesRes.data;
        this.roles = rolesRes.data;
        
      } catch (error) {
        console.error('❌ Error cargando catálogos:', error);
        this.mostrarNotificacion('Error al cargar catálogos', 'danger');
      }
    },
    
    async cargarLocalidades() {
  if (!this.editUser.id_region) {
    this.localidades = [];
    this.editUser.location_name = '';
    return;
  }
  
  this.cargandoLocalidades = true;
  
  try {
    // Llamar al endpoint real para obtener localidades por región
    const response = await userService.getLocalidadesPorRegion(this.editUser.id_region);
    this.localidades = response.data;
    
    console.log(`📍 Localidades cargadas para región ${this.editUser.id_region}:`, this.localidades);
    
    // Si el usuario ya tenía una localidad asignada, verificar si sigue siendo válida
    if (this.editUser.location_name && this.localidades.length > 0) {
      const localidadExiste = this.localidades.some(
        loc => loc.display_value === this.editUser.location_name
      );
      
      if (!localidadExiste) {
        // Si la localidad anterior no está en la nueva lista, limpiar la selección
        this.editUser.location_name = '';
        console.log('⚠️ Localidad anterior no disponible para esta región');
      }
    }
    
  } catch (error) {
    console.error('❌ Error cargando localidades:', error);
    
    // Si el endpoint no está implementado, mostrar un mensaje y usar datos de prueba
    if (error.response && error.response.status === 404) {
      console.log('⚠️ Endpoint de localidades no implementado, usando datos de prueba');
      this.mostrarNotificacion('Cargando modulo de edición de usuario', 'info');
      
      // Datos de prueba temporalmente
      const regionSeleccionada = this.regiones.find(r => r.id_region == this.editUser.id_region);
      if (regionSeleccionada) {
        this.localidades = [
          { id_location: 1, display_value: `${regionSeleccionada.display_value} - Localidad Principal` },
          { id_location: 2, display_value: `${regionSeleccionada.display_value} - Localidad Secundaria` },
          { id_location: 3, display_value: `${regionSeleccionada.display_value} - Localidad Alterna` }
        ];
      }
    } else {
      this.mostrarNotificacion('Error al cargar localidades', 'danger');
    }
  } finally {
    this.cargandoLocalidades = false;
  }
},
    
    async abrirEdicion(username) {
      try {
        this.editando = true;
        console.log(`✏️ Editando usuario: ${username}`);
        
        // Limpiar datos anteriores
        this.localidades = [];
        
        // Obtener datos completos del usuario
        const res = await userService.getUsuario(username);
        const usuarioData = res.data;
        
        // Preparar datos para el formulario
        this.editUser = {
          username: usuarioData.username,
          id_region: usuarioData.id_region,
          location_name: usuarioData.location_name,
          id_rol: usuarioData.roles_ids ? usuarioData.roles_ids.split(',')[0] : '',
          is_active: usuarioData.is_active,
          changedBy: 'ADMIN_TEST'
        };
        
        // Cargar localidades de la región seleccionada
        await this.cargarLocalidades();
        
        // Mostrar modal
        this.showEditModal = true;
        
        console.log('📝 Datos cargados para edición:', this.editUser);
        
      } catch (error) {
        console.error('❌ Error al obtener información del usuario:', error);
        this.mostrarNotificacion('Error al cargar datos del usuario para editar', 'danger');
      } finally {
        this.editando = false;
      }
    },
    
    async guardarCambios() {
      if (!this.formularioValido) {
        this.mostrarNotificacion('Por favor, complete todos los campos requeridos', 'warning');
        return;
      }
      
      this.guardando = true;
      
      try {
        console.log('💾 Guardando cambios para:', this.editUser.username);
        console.log('📤 Datos a enviar:', this.editUser);
        
        const response = await userService.actualizar(
          this.editUser.username,
          this.editUser
        );
        
        console.log('✅ Respuesta del servidor:', response.data);
        
        if (response.data.status === 'EXITO') {
          this.mostrarNotificacion('Usuario actualizado exitosamente', 'success');
          
          // Actualizar la tabla con los nuevos datos
          await this.ejecutarBusqueda();
          
          // Cerrar modal
          this.cerrarModal();
        } else {
          this.mostrarNotificacion(response.data.mensaje || 'Error al actualizar', 'danger');
        }
        
      } catch (error) {
        console.error('❌ Error guardando cambios:', error);
        
        let mensaje = 'Error al guardar cambios';
        if (error.response) {
          mensaje = error.response.data.detail?.mensaje || 
                    error.response.data.mensaje || 
                    `Error ${error.response.status}`;
        }
        
        this.mostrarNotificacion(mensaje, 'danger');
      } finally {
        this.guardando = false;
      }
    },
    
    cerrarModal() {
      this.showEditModal = false;
      // Resetear formulario
      this.editUser = {
        username: '',
        id_region: 0,
        location_name: '',
        id_rol: '',
        is_active: true,
        changedBy: 'ADMIN_TEST'
      };
      this.localidades = [];
    },
    
    mostrarNotificacion(mensaje, tipo = 'success') {
      this.notificationMessage = mensaje;
      this.notificationType = tipo;
      this.showNotification = true;
      
      // Auto-ocultar después de 5 segundos
      setTimeout(() => {
        this.showNotification = false;
      }, 5000);
    }
  }
}
</script>

<style scoped>

/* 1. TABLA - ESTILO ORIGINAL (más claro como antes) */
.table thead th {
  color: #9c27b0 !important; /* Color original morado claro */
  font-weight: 600 !important;
  font-size: 14px;
  border-bottom: 1px solid #dee2e6 !important;
}

.table tbody td {
  color: #666 !important; /* Gris claro como antes */
  font-weight: 400;
  padding: 12px 8px !important;
}

.table-responsive {
  max-height: 600px;
}

/* 2. BADGES - ESTILO ORIGINAL */
.badge-success {
  background-color: #28a745 !important;
  color: white !important;
  font-weight: 500;
  padding: 4px 8px !important;
  font-size: 0.85em;
  border-radius: 10rem;
}

.badge-danger {
  background-color: #dc3545 !important;
  color: white !important;
  font-weight: 500;
  padding: 4px 8px !important;
  font-size: 0.85em;
  border-radius: 10rem;
}

/* 3. TÍTULOS Y CATEGORÍAS - ESTILO ORIGINAL */
.card .card-header {
  padding: 1.5rem 1.5rem 0.5rem 1.5rem !important;
}

.card-title {
  color: #727070e4 !important; /* Gris oscuro, no tan fuerte */
  font-weight: 600;
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.category {
  color: #a29999 !important; /* Gris claro como antes */
  font-weight: 400;
  font-size: 0.95rem;
  margin-bottom: 0;
}

/* 4. BÚSQUEDA - ESTILO ORIGINAL */
.search-container {
  width: 100%;
  box-shadow: 0 1px 3px rgba(190, 179, 179, 0.459);
  border-radius: 0.4285rem;
  overflow: hidden;
}

.search-container .form-control {
  border-right: 0;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  color: #495057 !important;
  font-weight: 400;
  border: 1px solid #ced4da;
}

.search-container .form-control::placeholder {
  color: #6c757d !important;
}

.search-container .input-group-append .btn {
  border-left: 0;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: #9c27b0 !important; /* Color original */
  border-color: #9c27b0 !important;
  color: white !important;
  font-weight: 500;
}

.search-container .input-group-append .btn:hover {
  background-color: #7b1fa2 !important;
  border-color: #7b1fa2 !important;
}

/* 5. LOADING SPINNER */
.loading-spinner {
  animation: spin 1s linear infinite;
  font-size: 1.2rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ============================================
   MODAL DE EDICIÓN - ESTILOS MEJORADOS (BUEN CONTRASTE)
   ============================================ */

/* 6. MODAL - MEJOR CONTRASTE (esto queda bien) */
.modal-title {
  color: #2c3e50 !important;
  font-weight: 700;
  font-size: 1.3rem;
}

.modal .form-group label {
  color: #2c3e50 !important; /* Azul oscuro para buen contraste */
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 14px;
}

.modal .form-control {
  color: #2c3e50 !important; /* Texto oscuro en inputs */
  font-weight: 500;
  border: 1px solid #bdc3c7;
  padding: 10px 12px;
  border-radius: 6px;
}

.modal .form-control:focus {
  border-color: #4a6491;
  box-shadow: 0 0 0 2px rgba(74, 100, 145, 0.2);
}

.modal .form-control:disabled,
.modal .form-control[readonly] {
  background-color: #f8f9fa;
  color: #7b8a8b !important;
  font-weight: 600;
  opacity: 1;
}

/* 7. SELECTS DEL MODAL - MEJOR CONTRASTE */
select.form-control {
  appearance: auto;
  background-image: none;
  color: #2c3e50 !important;
  background-color: white;
  font-weight: 500;
}

select.form-control:disabled {
  background-color: #ecf0f1;
  color: #7f8c8d !important;
}

select.form-control option[value=""] {
  color: #95a5a6;
  font-style: italic;
}

/* 8. CHECKBOX DEL MODAL - MEJOR CONTRASTE */
.form-check {
  padding-left: 0;
}

.form-check-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #2c3e50 !important; /* Texto oscuro */
  font-weight: 600;
  font-size: 14px;
}

.form-check-input {
  margin-right: 10px;
  transform: scale(1.2);
}

.form-check-input:checked {
  background-color: #4a6491 !important;
  border-color: #4a6491 !important;
}

/* Texto de ayuda debajo del checkbox */
.modal .form-text.text-muted {
  color: #7f8c8d !important;
  font-size: 12px;
  font-style: italic;
  display: block;
  margin-top: 5px;
}

/* 9. ESPACIADO DEL MODAL */
.modal .row {
  margin-bottom: 1rem;
}

.modal .row:last-child {
  margin-bottom: 0;
}

/* 10. BOTONES DEL MODAL - MEJOR CONTRASTE */
.modal-footer .btn-primary {
  background-color: #4a6491 !important;
  border-color: #4a6491 !important;
  color: white !important;
  font-weight: 600;
}

.modal-footer .btn-primary:hover {
  background-color: #3a5481 !important;
  border-color: #3a5481 !important;
}

.modal-footer .btn-secondary {
  background-color: #95a5a6 !important;
  border-color: #95a5a6 !important;
  color: white !important;
  font-weight: 600;
}

.modal-footer .btn-secondary:hover {
  background-color: #7f8c8d !important;
  border-color: #7f8c8d !important;
}

/* 11. BOTÓN DE EDICIÓN EN TABLA - ESTILO ORIGINAL */
.btn-info {
  background-color: #00bcd4 !important; /* Color original cyan */
  border-color: #00bcd4 !important;
  color: white !important;
}

.btn-info:hover {
  background-color: #0097a7 !important;
  border-color: #0097a7 !important;
}

.btn-info .tim-icons {
  color: white !important;
}

/* 12. ESTADO DE CARGA */
.text-center.py-4 span {
  color: #9c27b0 !important; /* Color original morado */
  font-weight: 500;
}

/* 13. MENSAJES DE NO RESULTADOS */
.text-center.text-muted {
  color: #6c757d !important;
  font-weight: 400;
  font-size: 1rem;
}

/* 14. FILAS ALTERNAS PARA MEJOR LEGIBILIDAD (solo tabla) */
.table tbody tr:nth-child(even) {
  background-color: #f8f9fa;
}

.table tbody tr:hover {
  background-color: #e8f4fc;
}

/* 15. MODAL BACKDROP MÁS OSCURO */
.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5) !important;
}

/* 16. RESPONSIVE */
@media (max-width: 768px) {
  .table thead th,
  .table tbody td {
    font-size: 13px;
    padding: 8px 5px !important;
  }
  
  .card-title {
    font-size: 1.3rem;
  }
  
  .category {
    font-size: 0.85rem;
  }
  
  .modal .form-group label {
    font-size: 13px;
  }
  
  .modal .form-control {
    padding: 8px 10px;
    font-size: 14px;
  }
}

/* 17. ICONOS - ESTILO ORIGINAL */
.tim-icons {
  color: inherit !important;
}

/* 18. MEJORAR VISIBILIDAD DE BOTONES DESHABILITADOS */
button:disabled {
  opacity: 0.7;
}

button:disabled .tim-icons {
  opacity: 0.7;
}

/* 19. MEJORAR EL TEXTO EN INPUTS DESHABILITADOS */
input:disabled, 
select:disabled,
textarea:disabled {
  color: #6c757d !important;
  opacity: 1 !important;
}

/* 20. TEXTO DE ADVERTENCIA EN SELECTS VACÍOS */
small.form-text.text-warning {
  color: #dc3545 !important; /* Rojo original */
  font-weight: 500;
  font-size: 12px;
}
</style>
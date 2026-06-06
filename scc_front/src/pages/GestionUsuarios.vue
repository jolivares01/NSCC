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
                        placeholder="usuario"
                        v-model="searchQuery"
                        @input="searchQuery = searchQuery.toUpperCase()" 
                        @keyup.enter="ejecutarBusqueda"
                        :disabled="buscando"
                        style="text-transform: uppercase;"
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
                  <th>Región / Localidad</th>
                  <th>Roles</th>
                  <th class="text-center">Origen</th> <th class="text-center">Estado</th>
                  <th class="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in usuarios" :key="u.usuario">
                  <td>{{ u.usuario }}</td>
                  <td>{{ u.region }} - {{ u.localidad }}</td>
                  <td>{{ u.roles_asignados || 'Sin roles asignados' }}</td>
                  <td class="text-center">
                    <span v-if="u.origin_type === 'EXTERNO'" class="badge badge-info">
                      EXTERNO
                    </span>
                    <span v-else class="text-muted">INTERNO</span>
                  </td>
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
                <input type="text" class="form-control" v-model="editUser.username" readonly>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label>Región</label>
                <select class="form-control" v-model="editUser.id_region" @change="cargarLocalidades" required>
                  <option value="">Seleccionar región</option>
                  <option v-for="region in regiones" :key="region.id_region" :value="region.id_region">
                    {{ region.display_value }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label>Localidad</label>
                <select class="form-control" v-model="editUser.location_name" required>
                  <option value="">Seleccionar localidad</option>
                  <option v-for="loc in localidades" :key="loc.id_location" :value="loc.display_value">
                    {{ loc.display_value }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label>Canal de Ventas</label>
                <select class="form-control" v-model="editUser.id_channel" required>
                  <option value="" disabled>Seleccionar canal</option>
                  <option v-for="can in canales" :key="can.id_channel" :value="can.id_channel">
                    {{ can.full_label }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-6" v-if="editUser.origin_type === 'EXTERNO'">
              <div class="form-group">
                <label>Tipo de Agente</label>
                <select class="form-control" v-model="editUser.user_type" required>
                  <option value="" disabled>Seleccionar tipo (A, B, E)</option>
                  <option v-for="tipo in tiposUsuario" :key="tipo.id_type" :value="tipo.id_type">
                    {{ tipo.id_type }} - {{ tipo.description }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-12">
              <div class="form-group">
                <label>Rol Principal</label>
                <select class="form-control" v-model="editUser.id_rol" required>
                  <option value="">Seleccionar rol</option>
                  <option v-for="rol in roles" :key="rol.id_rol" :value="rol.id_rol">
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
                    <input type="checkbox" class="form-check-input" v-model="editUser.is_active">
                    <span class="form-check-sign"></span> Usuario Activo
                  </label>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
      <template slot="footer">
        <base-button type="secondary" @click="cerrarModal">Cancelar</base-button>
        <base-button 
          type="primary" 
          @click="guardarCambios"
          :disabled="guardando || !formularioValido"
        >
          Guardar Cambios
        </base-button>
      </template>
    </modal>

    <notification :show.sync="showNotification" :type="notificationType" :message="notificationMessage" />
  </div>
</template>

<script>
import userService from '@/services/userService';
import Modal from '@/components/Modal.vue';
import Notification from '@/components/Notification.vue';

export default {
  name: 'GestionUsuarios',
  components: { Modal, Notification },
  data() {
    return {
      usuarios: [],
      searchQuery: '',
      buscando: false,
      editando: false,
      guardando: false,
      showEditModal: false,
      editUser: {
        username: '', id_region: 0, location_name: '', id_rol: '', 
        is_active: true, changedBy: 'ADMIN_TEST',
        origin_type: '', user_type: null, id_channel: ''
      },
      regiones: [], localidades: [], roles: [], tiposUsuario: [], canales: [],
      cargandoLocalidades: false,
      showNotification: false, notificationType: 'success', notificationMessage: ''
    };
  },
  computed: {
    formularioValido() {
      const basicos = this.editUser.username && this.editUser.id_region && this.editUser.location_name && this.editUser.id_rol && this.editUser.id_channel;
      if (this.editUser.origin_type === 'EXTERNO') {
        return basicos && this.editUser.user_type;
      }
      return basicos;
    }
  },
  async mounted() {
    await this.cargarCatalogos();
  },
  methods: {
    async cargarCatalogos() {
      try {
        const [reg, rol, tip, can] = await Promise.all([
          userService.getRegiones(), userService.getRoles(), 
          userService.getTiposUsuario(), userService.getCanales()
        ]);
        this.regiones = reg.data;
        this.roles = rol.data;
        this.tiposUsuario = tip.data;
        this.canales = can.data.map(c => ({
          ...c,
          full_label: `${c.id_channel} - ${c.description || 'Sin descripción'}`
        }));
      } catch (e) { console.error('Error catálogos:', e); }
    },
    async ejecutarBusqueda() {
      if (!this.searchQuery || this.searchQuery.trim() === '') return;
      this.buscando = true;
      const usuarioBuscado = this.searchQuery.trim().toUpperCase();
      try {
        const res = await userService.consultarUsuario(usuarioBuscado);
        this.usuarios = res.data;
      } finally { this.buscando = false; }
    },
    async abrirEdicion(username) {
      try {
        this.editando = true;
        this.localidades = [];
        const res = await userService.getUsuario(username);
        const u = res.data;
        
        // CORRECCIÓN: Sincronización de campos de negocio para cargar el canal y tipo
        this.editUser = {
          username: u.username,
          id_region: u.id_region,
          location_name: u.location_name,
          id_rol: u.roles_ids ? u.roles_ids.split(',')[0] : '',
          is_active: u.is_active,
          changedBy: 'ADMIN_TEST',
          origin_type: u.origin_type, // Vital para el v-if
          user_type: u.user_type,     // Carga A, B o E
          id_channel: u.id_channel    // Carga ID del canal (ej: AI)
        };
        
        await this.cargarLocalidades();
        this.showEditModal = true;
      } catch (e) { this.mostrarNotificacion('Error al cargar datos', 'danger'); }
      finally { this.editando = false; }
    },
    async cargarLocalidades() {
      if (!this.editUser.id_region) return;
      this.cargandoLocalidades = true;
      try {
        const response = await userService.getLocalidadesPorRegion(this.editUser.id_region);
        this.localidades = response.data;
      } finally { this.cargandoLocalidades = false; }
    },
    async guardarCambios() {
      if (!this.formularioValido) return;
      this.guardando = true;
      try {
        if (this.editUser.origin_type === 'INTERNO') this.editUser.user_type = null;
        const res = await userService.actualizar(this.editUser.username, this.editUser);
        if (res.data.status === 'EXITO') {
          this.mostrarNotificacion('Usuario actualizado exitosamente', 'success');
          await this.ejecutarBusqueda();
          this.cerrarModal();
        }
      } finally { this.guardando = false; }
    },
    cerrarModal() {
      this.showEditModal = false;
      this.editUser = { username: '', id_region: 0, location_name: '', id_rol: '', is_active: true, changedBy: 'ADMIN_TEST', origin_type: '', user_type: null, id_channel: '' };
      this.localidades = [];
    },
    mostrarNotificacion(m, t = 'success') {
      this.notificationMessage = m; this.notificationType = t; this.showNotification = true;
      setTimeout(() => { this.showNotification = false; }, 5000);
    }
  }
}
</script>

<style scoped>


.badge-info {
  background-color: #11cdef !important;
  color: white !important;
}
.text-muted {
  font-style: italic;
  font-size: 13px;
}

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
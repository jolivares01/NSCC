<template>
  <card>
    <template slot="header">
      <h4 class="card-title">Registrar Usuario</h4>
      <p class="category">Complete los datos para pre-registro de credenciales de red</p>
    </template>

    <form @submit.prevent="handleRegistro">
      <div class="row">
        <div class="col-md-6">
          <base-input label="Región">
            <select v-model="user.region" class="form-control custom-select-scc" required>
              <option value="" disabled selected>Seleccione una región</option>
              <option v-for="reg in regiones" :key="reg.id_region" :value="reg.display_value">
                {{ reg.display_value }}
              </option>
            </select>
          </base-input>
        </div>
        <div class="col-md-6">
          <base-input label="Localidad" 
                      v-model="user.localidad" 
                      placeholder="Ingrese localidad"
                      required>
          </base-input>
        </div>
      </div>

      <div class="row">
        <div class="col-md-6">
          <base-input label="Username (LDAP)" 
                      v-model="user.username" 
                      placeholder="Ej: jdoe"
                      required>
          </base-input>
        </div>
        <div class="col-md-6">
          <base-input label="Rol">
            <select v-model="user.rol" class="form-control custom-select-scc" required>
              <option value="" disabled selected>Seleccione un rol</option>
              <option v-for="rol in roles" :key="rol.id_rol" :value="rol.id_rol">
                {{ rol.rol_name }}
              </option>
            </select>
          </base-input>
        </div>
      </div>
      
      <div class="text-right mt-3">
        <base-button type="success" native-type="submit" fill>
          Registrar Usuario
        </base-button>
      </div>
    </form>
  </card>
</template>

<script>
import userService from '@/services/userService';

export default {
  name: 'registrar-usuario',
  data() {
    return {
      user: { 
        region: '', 
        localidad: '', 
        username: '', 
        rol: '', 
        createdBy: 'ADMIN_TEST' // En el futuro, capturar del auth store
      },
      regiones: [],
      roles: []
    };
  },
  async mounted() {
    await this.cargarCatalogos();
  },
  methods: {
    async cargarCatalogos() {
      try {
        const [resReg, resRol] = await Promise.all([
          userService.getRegiones(),
          userService.getRoles()
        ]);
        this.regiones = resReg.data;
        this.roles = resRol.data;
      } catch (error) {
        console.error("Error cargando maestros:", error);
        this.notificarError("No se pudieron cargar las regiones o roles.");
      }
    },
    async handleRegistro() {
      try {
        const response = await userService.registrar(this.user);
        
        // El SP devuelve "EXITO: ..."
        alert(response.data.mensaje);
        
        // Limpiar el formulario tras éxito
        this.resetForm();
      } catch (error) {
        // Manejo de error estructurado según tu router.py
        const msg = error.response?.data?.detail?.mensaje || "Error desconocido";
        alert("Respuesta del Sistema: " + msg);
      }
    },
    resetForm() {
      this.user = { 
        region: '', 
        localidad: '', 
        username: '', 
        rol: '', 
        createdBy: 'ADMIN_TEST' 
      };
    }
  }
};
</script>

<style scoped>
/* Solución para la visibilidad del texto en los selects */
.custom-select-scc {
  color: #ffffff !important; /* Texto principal en blanco para el tema oscuro */
  background-color: #27293d !important; /* Color de fondo de la tarjeta de la plantilla */
}

/* Estilo para las opciones (cuando el menú se despliega) */
.custom-select-scc option {
  background-color: #ffffff !important; /* Fondo blanco para que destaque */
  color: #333333 !important; /* Letras oscuras para lectura fácil */
}

/* Quitar el resplandor azul por defecto y ajustar borde */
.custom-select-scc:focus {
  border-color: #e14eca;
  box-shadow: none;
}
</style>
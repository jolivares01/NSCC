<template>
  <card>
    <template slot="header">
      <h4 class="card-title">Registrar Usuario</h4>
    </template>

    <form @submit.prevent="handleRegistro">
      <div class="row">
        <div class="col-md-6">
          <base-input label="Región">
            <select 
              v-model="user.region" 
              class="form-control custom-select-scc" 
              @change="onRegionChange" 
              required
            >
              <option value="" disabled selected>Seleccione una región</option>
              <option v-for="reg in regiones" :key="reg.id_region" :value="reg.display_value">
                {{ reg.display_value }}
              </option>
            </select>
          </base-input>
        </div>

        <div class="col-md-6">
          <base-input label="Localidad">
            <select 
              v-model="user.localidad" 
              class="form-control custom-select-scc" 
              :disabled="!user.region || cargandoLocalidades"
              required
            >
              <option value="" disabled selected>
                {{ cargandoLocalidades ? 'Cargando localidades...' : 'Seleccione una localidad' }}
              </option>
              <option v-for="loc in localidades" :key="loc.id_location" :value="loc.display_value">
                {{ loc.display_value }}
              </option>
            </select>
          </base-input>
        </div>
      </div>

      <div class="row">
        <div class="col-md-6">
          <base-input label="Username (LDAP)" v-model="user.username" placeholder="Ej: jdoe" required />
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

      <div class="row">
        <div class="col-md-6">
          <base-input label="Origen del Usuario">
            <select v-model="user.origin_type" class="form-control custom-select-scc" required>
              <option value="INTERNO">INTERNO</option>
              <option value="EXTERNO">EXTERNO</option>
            </select>
          </base-input>
        </div>
        <div class="col-md-6">
          <base-input label="Canal de Ventas">
            <select v-model="user.id_channel" class="form-control custom-select-scc" required>
              <option value="" disabled selected>Seleccione un canal</option>
              <option v-for="can in canales" :key="can.id_channel" :value="can.id_channel">
                {{ can.full_label }}
              </option>
            </select>
          </base-input>
        </div>
      </div>

      <div class="row" v-if="user.origin_type === 'EXTERNO'">
        <div class="col-md-12">
          <base-input label="Tipo de Agente (Para Cálculo de Comisión)">
            <select v-model="user.user_type" class="form-control custom-select-scc" required>
              <option value="" disabled selected>Seleccione Categoría (A, B, E)</option>
              <option v-for="tipo in tiposUsuario" :key="tipo.id_type" :value="tipo.id_type">
                {{ tipo.id_type }} - {{ tipo.description }} (Monto Fijo: {{ tipo.monto_fijo }})
              </option>
            </select>
          </base-input>
        </div>
      </div>
      
      <div class="text-right mt-3">
        <base-button type="success" native-type="submit" fill :disabled="cargandoLocalidades">
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
        createdBy: 'ADMIN_TEST',
        origin_type: 'INTERNO',
        user_type: null,
        id_channel: ''
      },
      regiones: [],
      localidades: [], // Lista dinámica de localidades
      roles: [],
      tiposUsuario: [],
      canales: [],
      cargandoLocalidades: false
    };
  },
  async mounted() {
    await this.cargarCatalogos();
  },
  methods: {
    async cargarCatalogos() {
      try {
        const [resReg, resRol, resTip, resCan] = await Promise.all([
          userService.getRegiones(),
          userService.getRoles(),
          userService.getTiposUsuario(),
          userService.getCanales()
        ]);
        
        this.regiones = resReg.data;
        this.roles = resRol.data;
        this.tiposUsuario = resTip.data;

        this.canales = resCan.data.map(can => ({
          ...can,
          full_label: `${can.id_channel} - ${can.description || 'Sin descripción'}`
        }));

      } catch (error) {
        console.error("Error cargando maestros:", error);
      }
    },

    // Método para detectar cambio de región y cargar sus localidades
    async onRegionChange() {
      this.user.localidad = ''; // Limpiar selección anterior
      this.localidades = [];
      
      if (!this.user.region) return;

      // Buscamos el ID de la región basado en el display_value seleccionado
      const regionSeleccionada = this.regiones.find(r => r.display_value === this.user.region);
      if (!regionSeleccionada) return;

      this.cargandoLocalidades = true;
      try {
        // Llamada al nuevo endpoint que filtra por id_region
        const response = await userService.getLocalidadesPorRegion(regionSeleccionada.id_region);
        this.localidades = response.data;
      } catch (error) {
        console.error("Error al cargar localidades:", error);
      } finally {
        this.cargandoLocalidades = false;
      }
    },

    async handleRegistro() {
      try {
        this.user.username = this.user.username.toUpperCase();

        if (this.user.origin_type === 'INTERNO') {
          this.user.user_type = null;
        }

        const response = await userService.registrar(this.user);
        alert(response.data.mensaje);
        this.resetForm();
      } catch (error) {
        const msg = error.response?.data?.detail?.mensaje || "Error desconocido";
        alert("Respuesta del Sistema: " + msg);
      }
    },

    resetForm() {
      this.user = { 
        region: '', localidad: '', username: '', rol: '', 
        createdBy: 'ADMIN_TEST', origin_type: 'INTERNO', 
        user_type: null, id_channel: ''
      };
      this.localidades = [];
    }
  }
};
</script>


<style scoped>
.custom-select-scc {
  /* Eliminamos el color fijo para que herede del tema (blanco en dark, oscuro en light) */
  background-color: transparent !important; 
  border: 1px solid #2b3553;
  border-radius: 0.4285rem;
  padding: 0.5rem 0.7rem;
  width: 100%;
  transition: color 0.3s ease-in-out, border-color 0.3s ease-in-out;
}

/* Estilo para las opciones cuando el menú está abierto */
.custom-select-scc option {
  /* Forzamos fondo blanco y letra negra en el desplegable para máxima legibilidad en ambos temas */
  background-color: #ffffff !important;
  color: #333333 !important;
}

/* Color del texto del select dependiendo del tema del body */
.white-content .custom-select-scc {
  color: #222a42 !important; /* Texto oscuro para modo claro */
  border-color: #cad1d7;
}

.custom-select-scc {
  color: rgba(255, 255, 255, 0.8); /* Texto claro para modo oscuro */
}
</style>
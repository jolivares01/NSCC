<template>
  <div>
    <div class="row">
      <div class="col-12">
        <card>
          <div class="header-container d-flex justify-content-between align-items-center">
            <h4 class="card-title">Carga de Datos - Operaciones DigiData</h4>
            <div class="badge badge-info" v-if="loading">Procesando...</div>
          </div>

          <p class="card-category">
            Selecciona un rango de fechas para realizar la extracción de datos.
          </p>

          <div class="row mt-4">
            <div class="col-md-4">
              <div class="form-group">
                <label>Fecha Inicio</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="rango.inicio"
                  :disabled="loading"
                >
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-group">
                <label>Fecha Fin</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="rango.fin"
                  :disabled="loading"
                >
              </div>
            </div>

            <div class="col-md-4 d-flex align-items-end">
              <button 
                class="btn btn-primary btn-block" 
                @click="ejecutarSincronizacion"
                :disabled="loading || !rango.inicio || !rango.fin"
              >
                <i class="now-ui-icons arrows-1_refresh-69" :class="{'fa-spin': loading}"></i>
                {{ loading ? 'Sincronizando...' : 'Cargar de Datos' }}
              </button>
            </div>
          </div>

          <div v-if="resultado" class="mt-4">
            <div :class="['alert', 'alert-with-icon', resultado.error ? 'alert-danger' : 'alert-success']">
              <div class="container">
                <div class="alert-icon">
                  <i class="now-ui-icons" :class="resultado.error ? 'objects_support-17' : 'ui-2_like'"></i>
                </div>
                <strong>{{ resultado.error ? 'Error:' : '¡Éxito!' }}</strong> 
                <span> {{ resultado.mensaje }}</span>
                <button type="button" class="close" @click="resultado = null">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
            </div>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Activaciones',
  data() {
    return {
      loading: false,
      rango: {
        inicio: '',
        fin: ''
      },
      resultado: null
    };
  },
  methods: {
    formatDate(dateStr) {
      const [year, month, day] = dateStr.split('-');
      return `${day}.${month}.${year}`;
    },

    async ejecutarSincronizacion() {
      this.loading = true;
      this.resultado = null;

      const currentUser = localStorage.getItem('username') || 'admin';

      try {
        const payload = {
          fecha_inicio: this.formatDate(this.rango.inicio),
          fecha_fin: this.formatDate(this.rango.fin)
        };

        const response = await axios.post(
          'http://localhost:8000/api/v1/calculation/migrar-activaciones', 
          payload,
          { params: { username: currentUser } }
        );

        // RESPUESTA EXITOSA (VERDE)
        this.resultado = {
          error: false,
          mensaje: response.data.mensaje
        };
      } catch (error) {
        console.error("Error sincronizando:", error);
        // RESPUESTA DE ERROR (ROJO)
        this.resultado = {
          error: true,
          mensaje: error.response?.data?.detail?.mensaje || "Error de conexión con el servidor."
        };
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Forzamos el color verde para éxito y rojo para error */
.alert-success {
  background-color: #18ce0f !important; /* Verde Digitel/Éxito */
  color: #ffffff !important;
  font-weight: 500;
}

.alert-danger {
  background-color: #ff3636 !important; /* Rojo Error */
  color: #ffffff !important;
  font-weight: 500;
}

/* Alineación de iconos y texto dentro de la alerta */
.alert-with-icon .container {
  padding-left: 55px;
  position: relative;
}

.alert-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
}

.close {
  color: #fff;
  opacity: 0.8;
}

.fa-spin {
  animation: spin 2s infinite linear;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
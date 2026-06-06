<template>
  <div>
    <div class="row">
      <div class="col-12">
        <card>
          <!-- Header -->
          <div class="header-container d-flex justify-content-between align-items-center">
            <h4 class="card-title">Carga de Datos - Recargas</h4>
            <div class="badge badge-info" v-if="loading">Procesando...</div>
          </div>

          <p class="card-category">
            Selecciona un rango de fechas para ejecutar la migración de recargas desde Oracle a PostgreSQL.
          </p>

          <!-- Formulario -->
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
                @click="ejecutarMigracionRecargas"
                :disabled="loading || !rango.inicio || !rango.fin"
              >
                <i
                  class="now-ui-icons arrows-1_refresh-69"
                  :class="{ 'fa-spin': loading }"
                ></i>
                {{ loading ? 'Procesando...' : 'Cargar Recargas' }}
              </button>
            </div>
          </div>

          <!-- Resultado -->
          <div v-if="resultado" class="mt-4">
            <div :class="['alert', resultado.error ? 'alert-danger' : 'alert-success']">
              <span>{{ resultado.mensaje }}</span>
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
  name: 'ConsultaRecargas',

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
    // YYYY-MM-DD → DD.MM.YYYY
    formatDate(dateStr) {
      const [year, month, day] = dateStr.split('-');
      return `${day}.${month}.${year}`;
    },

    async ejecutarMigracionRecargas() {
      this.loading = true;
      this.resultado = null;

      const currentUser = localStorage.getItem('username') || 'admin';

      try {
        const payload = {
          fecha_inicio: this.formatDate(this.rango.inicio),
          fecha_fin: this.formatDate(this.rango.fin)
        };

        const response = await axios.post(
          'http://localhost:8000/api/v1/calculation/migrar-recargas',
          payload,
          { params: { username: currentUser } }
        );

        this.resultado = {
          error: false,
          mensaje: `Proceso completado exitosamente. Registros insertados: ${response.data.registros_insertados}`
        };

      } catch (error) {
        console.error('Error migrando recargas:', error);
        this.resultado = {
          error: true,
          mensaje:
            error.response?.data?.detail?.mensaje ||
            'Error de conexión con el servidor.'
        };
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.fa-spin {
  animation: spin 2s infinite linear;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
<template>
  <div>
    <div class="row">
      <div class="col-12">
        <card>
          <template slot="header">
            <h4 class="card-title">Parámetros de Cálculo - Digitel</h4>
          </template>
          
          <div class="row">
            <div class="col-md-4">
              <base-input label="ID del Periodo"
                          v-model="config.period_id"
                          placeholder="Ej: 2026-03">
              </base-input>
            </div>
            <div class="col-md-4">
              <base-input label="Unidad Digitel"
                          v-model="config.amount"
                          placeholder="Ej: 378,46">
              </base-input>
            </div>
            <div class="col-md-4 d-flex align-items-center">
              <base-button type="success" 
                           fill 
                           class="mt-2"
                           @click="ejecutarProceso"
                           :disabled="loading || !config.period_id || !config.amount">
                <i class="tim-icons icon-settings-gear-63"></i> 
                {{ loading ? 'Procesando...' : 'Ejecutar Motor de Cálculo' }}
              </base-button>
            </div>
          </div>
        </card>
      </div>

      <div class="col-12" v-if="reporte.length > 0">
        <card>
          <div class="d-flex justify-content-between align-items-center">
            <h4 class="card-title">Resumen de Operaciones Comisionables</h4>
            <base-button type="info" @click="descargarExcel" :disabled="downloading">
              <i class="tim-icons icon-cloud-download-93"></i> 
              {{ downloading ? 'Generando...' : 'Descargar Excel' }}
            </base-button>
          </div>
          
          <div class="table-responsive">
            <table class="table tablesorter">
              <thead class="text-primary">
                <tr>
                  <th>Tipo de Operación</th>
                  <th class="text-center">Total Registros</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in reporte" :key="index">
                  <td>{{ item.operation_type }}</td>
                  <td class="text-center">
                    <badge type="info">{{ item.total }}</badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </card>
      </div>

      <div class="col-12" v-if="listaAgentes.length > 0">
        <card>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="card-title">Publicación de Comisiones por Agente</h4>
            <base-button type="success" 
                         @click="confirmarPublicacion" 
                         :disabled="seleccionados.length === 0 || publishing">
              <i class="tim-icons icon-send"></i> 
              {{ publishing ? 'Publicando...' : `Publicar Selección (${seleccionados.length})` }}
            </base-button>
          </div>

          <div class="row mb-3">
            <div class="col-md-4">
              <base-input label="Filtrar por Región"
                          v-model="filtroRegion"
                          placeholder="Buscar región..."
                          addon-left-icon="tim-icons icon-zoom-split">
              </base-input>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th class="text-center">
                    <div class="form-check">
                      <label class="form-check-label">
                        <input class="form-check-input" type="checkbox" @change="seleccionarTodoVisibles($event)">
                        <span class="form-check-sign"></span>
                      </label>
                    </div>
                  </th>
                  <th>Región</th>
                  <th>Agente Origen</th>
                  <th>Localidad</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(agente, index) in agentesFiltrados" :key="index">
                  <td class="text-center">
                    <div class="form-check">
                      <label class="form-check-label">
                        <input class="form-check-input" type="checkbox" 
                               :value="agente.source_agent" 
                               v-model="seleccionados">
                        <span class="form-check-sign"></span>
                      </label>
                    </div>
                  </td>
                  <td>{{ agente.region }}</td>
                  <td>{{ agente.source_agent }}</td>
                  <td>{{ agente.locality }}</td>
                </tr>
                <tr v-if="agentesFiltrados.length === 0">
                   <td colspan="4" class="text-center text-muted">No se encontraron agentes en la región "{{ filtroRegion }}"</td>
                </tr>
              </tbody>
            </table>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Calculo',
  data() {
    return {
      loading: false,
      downloading: false,
      publishing: false,
      config: {
        period_id: '',
        amount: ''
      },
      filtroRegion: '',
      reporte: [],
      listaAgentes: [],
      seleccionados: []
    }
  },
  computed: {
    // Filtra la lista de agentes en tiempo real basado en el input de región
    agentesFiltrados() {
      return this.listaAgentes.filter(agente => {
        return agente.region.toLowerCase().includes(this.filtroRegion.toLowerCase());
      });
    }
  },
  methods: {
    async ejecutarProceso() {
      this.loading = true;
      this.reporte = [];
      this.listaAgentes = [];
      this.seleccionados = [];
      this.filtroRegion = '';
      try {
        const url = 'http://localhost:8000/api/v1/calculation/ejecutar-calculo';
        const response = await axios.post(url, this.config);
        
        if (response.data.status === 'EXITO') {
          this.reporte = response.data.reporte;
          this.$notify({
            type: 'success',
            message: response.data.mensaje,
            icon: 'tim-icons icon-check-2'
          });
          await this.cargarListaPublicacion();
        }
      } catch (error) {
        const errorMsg = error.response?.data?.detail?.mensaje || 'Error al ejecutar el cálculo';
        this.$notify({ type: 'danger', message: errorMsg, icon: 'tim-icons icon-alert-circle-exc' });
      } finally {
        this.loading = false;
      }
    },

    async cargarListaPublicacion() {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/calculation/lista-publicacion');
        this.listaAgentes = res.data;
      } catch (error) {
        console.error("Error cargando lista de publicación", error);
      }
    },

    // Selecciona/Deselecciona solo los agentes que están visibles bajo el filtro actual
    seleccionarTodoVisibles(event) {
      if (event.target.checked) {
        const idsVisibles = this.agentesFiltrados.map(a => a.source_agent);
        // Mantenemos los que ya estaban y añadimos los nuevos visibles sin duplicados
        this.seleccionados = [...new Set([...this.seleccionados, ...idsVisibles])];
      } else {
        const idsVisibles = this.agentesFiltrados.map(a => a.source_agent);
        // Removemos de la selección general solo aquellos que están visibles
        this.seleccionados = this.seleccionados.filter(id => !idsVisibles.includes(id));
      }
    },

    async confirmarPublicacion() {
      this.publishing = true;
      try {
        const res = await axios.post('http://localhost:8000/api/v1/calculation/publicar-comisiones', {
          agentes: this.seleccionados,
          period_id: this.config.period_id
        });
        if (res.data.status === 'EXITO') {
          this.$notify({
            type: 'success',
            message: res.data.mensaje,
            icon: 'tim-icons icon-check-2'
          });
          this.listaAgentes = []; 
          this.seleccionados = [];
          this.filtroRegion = '';
        }
      } catch (error) {
        this.$notify({ type: 'danger', message: 'Error en la publicación', icon: 'tim-icons icon-alert-circle-exc' });
      } finally {
        this.publishing = false;
      }
    },

    async descargarExcel() {
      this.downloading = true;
      try {
        const response = await axios({
          url: 'http://localhost:8000/api/v1/calculation/descargar-excel',
          method: 'GET',
          responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Reporte_Comisiones_${this.config.period_id}.xlsx`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        this.$notify({ type: 'danger', message: 'Error al generar Excel' });
      } finally {
        this.downloading = false;
      }
    }
  }
}
</script>

<style scoped>
.btn-success {
  background-color: #D50032 !important;
  border-color: #D50032 !important;
}

.btn-info {
  background-color: #5C068C !important;
  border-color: #5C068C !important;
}

.text-primary, .form-check-sign::before, .form-check-sign::after {
  color: #5C068C !important;
}

.badge-info {
  background-color: #5C068C !important;
}
</style>
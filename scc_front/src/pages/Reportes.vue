<template>
  <div class="content">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <card class="card-report">
          <template slot="header">
            <h4 class="card-title text-purple-digitel">
              <i class="tim-icons icon-notes text-primary mr-2"></i> 
              Centro de Reportes
            </h4>
          </template>

          <div class="p-4">
            <div class="form-group text-center mb-4">
              <label class="label-periodo">SELECCIONE EL PERIODO A CONSULTAR</label>
              <input 
                type="month" 
                v-model="periodo" 
                class="form-control date-input mx-auto"
                :disabled="loading"
              >
            </div>

            <div class="row">
              <div class="col-12 mb-4" v-if="isAdmin">
                <div class="report-option-box p-3 border-primary">
                  <div class="d-flex align-items-center justify-content-between">
                    <div>
                      <h5 class="mb-1 font-weight-bold">Detalle de Operations</h5>
                      <p class="small text-muted mb-0">Sábana completa de operaciones del periodo.</p>
                    </div>
                    <button 
                      class="btn btn-primary btn-round btn-icon-only" 
                      @click.stop="descargarReporte('comisiones')"
                      :disabled="loading"
                      title="Descargar Detalle General"
                    >
                      <i v-if="loadingType === 'comisiones'" class="fas fa-spinner fa-spin"></i>
                      <i v-else class="tim-icons icon-delivery-fast"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="row">
              <div class="col-12">
                <div v-if="isAdmin">
                  <label class="label-periodo text-center d-block mb-2">CONSULTA INDIVIDUAL DE AGENTE</label>
                  <div class="input-group mb-0">
                    <div class="input-group-prepend">
                      <div class="input-group-text bg-white border-right-0 search-icon-box">
                        <i class="tim-icons icon-zoom-split text-purple-digitel"></i>
                      </div>
                    </div>
                    <input 
                      type="text" 
                      class="form-control border-left-0 search-input" 
                      placeholder="Escriba el código exacto del agente (ej: CAR_64598_1)..." 
                      v-model="searchQuery"
                      @keyup.enter="buscarComisionesAgente"
                      :disabled="loading"
                    >
                    <div class="input-group-append">
                      <button 
                        class="btn btn-purple-digitel-bg m-0" 
                        type="button" 
                        @click="buscarComisionesAgente"
                        :disabled="loading || !searchQuery"
                      >
                        Buscar
                      </button>
                    </div>
                  </div>
                </div>

                <div v-else class="text-center p-2 bg-gray-light rounded border-purple-thin">
                  <span class="text-purple-digitel font-weight-bold small uppercase">
                    <i class="tim-icons icon-single-02 mr-2"></i>
                    Consultando Liquidaciones de su Cuenta Activa
                  </span>
                </div>
              </div>
            </div>

            <div v-if="loading" class="text-center mt-4">
              <div class="progress-container progress-primary">
                <span class="progress-badge">Consultando base de datos corporativa...</span>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                </div>
              </div>
            </div>
          </div>
        </card>
      </div>
    </div>

    <div class="row mt-4 animate__fadeIn" v-if="agenteData.length > 0">
      <div class="col-12">
        <card>
          <template slot="header">
            <div class="row align-items-center">
              <div class="col-md-12">
                <h4 class="card-title text-purple-digitel mb-0">
                  <i class="tim-icons icon-chart-bar-32 text-primary mr-2"></i> 
                  Resumen de Comisiones: Agente {{ agenteConsultado }} ({{ periodo }})
                </h4>
              </div>
            </div>
          </template>

          <div class="table-responsive">
            <table class="table table-sm custom-table">
              <thead>
                <tr>
                  <th class="text-left" style="width: 70%;">CONCEPTO</th>
                  <th class="text-right" style="width: 30%;">COMISIÓN</th>
                </tr>
              </thead>
              <tbody class="animate__fadeIn">
                <tr v-for="(item, index) in agenteData" :key="index">
                  <td class="text-left font-weight-bold text-dark">{{ item.concepto }}</td>
                  <td class="text-right text-purple-digitel font-weight-bold">
                    {{ item.comision }}
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="bg-gray-light font-weight-800">
                  <td class="text-right text-dark pr-3 font-weight-bold">TOTAL A LIQUIDAR:</td>
                  <td class="text-right text-purple-digitel font-weight-bold font-size-total">
                    {{ totalLiquidacionFormateado }}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </card>
      </div>
    </div>

    <div class="row mt-2" v-if="busquedaRealizada && agenteData.length === 0 && !loading">
       <div class="col-12 text-center p-5 card">
          <i class="tim-icons icon-alert-circle-exc text-warning d-block mb-2" style="font-size: 2rem;"></i>
          <p class="text-muted">No se encontraron liquidaciones para el agente <b>{{ agenteConsultado }}</b> en el periodo <b>{{ periodo }}</b>.</p>
       </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Reportes',
  data() {
    return {
      periodo: new Date().toISOString().slice(0, 7),
      loading: false,
      loadingType: null,
      isAdmin: localStorage.getItem('user_role') === 'ROL_0001', 
      // Mapeo seguro de redundancia por si requieres usar el alias local en algún punto
      userLogin: localStorage.getItem('user_login') || 
                 localStorage.getItem('username')   || 
                 localStorage.getItem('user')       || 
                 localStorage.getItem('login')      || 
                 '', 
      agenteData: [],
      searchQuery: '',
      agenteConsultado: '',
      busquedaRealizada: false
    };
  },
  watch: {
    periodo() {
      this.agenteData = [];
      this.busquedaRealizada = false;
      this.buscarComisionesAgente();
    }
  },
  computed: {
    totalLiquidacionFormateado() {
      if (!this.agenteData || this.agenteData.length === 0) return '0,00';
      const total = this.agenteData.reduce((acc, item) => {
        if (!item.comision) return acc;
        const numeroLimpio = item.comision.replace(/\s/g, '').replace(/,/g, '');
        return acc + parseFloat(numeroLimpio || 0);
      }, 0);
      return new Intl.NumberFormat('de-DE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(total);
    }
  },
  mounted() {
    this.buscarComisionesAgente();
  },
  methods: {
    async buscarComisionesAgente() {
      // Si es admin enviamos lo de la barra, si es agente mandamos cadena vacía (el backend resolverá mediante JWT)
      const agenteObjetivo = this.isAdmin ? this.searchQuery.trim() : '';

      // Si es admin pero aún no escribe nada en la barra, frenamos la ejecución temprana
      if (this.isAdmin && !agenteObjetivo) {
        return;
      }

      this.loading = true;
      this.busquedaRealizada = false;
      this.agenteData = [];
      
      // Asignación de etiqueta visual adaptativa en el header de la tabla
      this.agenteConsultado = this.isAdmin ? agenteObjetivo : (this.userLogin || 'Autorizado');

      try {
        const response = await this.$http.post('/api/v1/reports/comisiones-agente', {
          periodo: this.periodo,
          source_agent: agenteObjetivo // Si viaja vacío, el router.py inyecta de forma segura el sub del JWT
        });
        
        this.agenteData = Object.freeze(response.data);
        this.busquedaRealizada = true;
      } catch (error) {
        console.error("Error consultando comisiones del agente:", error);
        this.$notify({ type: 'danger', message: 'Error al consultar los datos del agente en el servidor.' });
      } finally {
        this.loading = false;
      }
    },

    async descargarReporte(tipo) {
      if (!this.periodo) {
        this.$notify({ type: 'warning', message: 'Seleccione un periodo.' });
        return;
      }
      this.loading = true;
      this.loadingType = tipo;
      try {
        const response = await this.$http.post('/api/v1/reports/export-comisiones', 
          { periodo: this.periodo }, 
          { responseType: 'blob' }
        );
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Reporte_Detalle_General_${this.periodo}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        this.$notify({ type: 'success', icon: 'tim-icons icon-check-2', message: 'Excel de operaciones descargado correctamente.' });
      } catch (error) {
        console.error("Error en descarga:", error);
        this.$notify({ type: 'danger', icon: 'tim-icons icon-alert-circle-exc', message: 'Error al generar el archivo masivo.' });
      } finally {
        this.loading = false;
        this.loadingType = null;
      }
    }
  }
}
</script>

<style scoped>
.text-purple-digitel { color: #5C068C !important; font-weight: bold; }
.btn-purple-digitel-bg { background-color: #5C068C !important; color: white !important; font-weight: bold; border-radius: 0 20px 20px 0 !important; }
.card-report { border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); position: relative; z-index: 5; }
.label-periodo { font-size: 0.75rem; font-weight: 800; color: #9A9A9A; letter-spacing: 1px; display: block; }
.report-option-box { background: rgba(255, 255, 255, 0.03); border-left: 5px solid; border-radius: 8px; transition: all 0.3s ease; }
.date-input { width: 220px; height: 45px; border: 2px solid #e3e3e3 !important; border-radius: 8px !important; font-weight: bold; color: #5C068C; }
.custom-table th { font-size: 0.75rem !important; text-transform: uppercase !important; color: #9A9A9A !important; font-weight: 800 !important; padding: 12px 10px !important; }
.custom-table td { padding: 15px 10px !important; vertical-align: middle; }
.bg-gray-light { background-color: rgba(0, 0, 0, 0.02) !important; }
.font-weight-800 { font-weight: 800 !important; }
.font-size-total { font-size: 1rem !important; }
tfoot tr td { border-top: 2px solid #5C068C !important; padding: 15px 10px !important; }
.border-primary { border-color: #e14eca !important; }
.btn-icon-only { width: 50px; height: 50px; padding: 0; line-height: 50px; }
.search-icon-box { border: 1px solid #d0d0d0; border-radius: 20px 0 0 20px !important; }
.search-input { border: 1px solid #d0d0d0; border-radius: 0 !important; height: 40px; font-weight: bold; color: #5C068C; }
.search-input:focus { border-color: #5C068C !important; box-shadow: none !important; }
.border-purple-thin { border: 1px dashed #5C068C; border-radius: 8px; }
.uppercase { text-transform: uppercase; }
.animate__fadeIn { animation: fadeIn 0.4s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>
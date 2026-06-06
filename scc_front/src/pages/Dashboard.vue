<template>
  <div class="content">
    <div class="row mb-5 justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card selector-container">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-sm-5 text-left text-sm-right border-right-custom">
                <label class="label-title">
                  <i class="tim-icons icon-calendar-60 text-digitel-purple mr-2"></i>
                  PERIODO DE CONSULTA
                </label>
              </div>
              <div class="col-sm-7">
                <input 
                  type="month" 
                  v-model="periodoSeleccionado" 
                  class="form-control date-input-minimal" 
                  @change="fetchDashboardData"
                >
              </div>
            </div>
            <hr class="my-3 divider-thin">
            <div class="text-center">
              <h2 class="dashboard-main-title">{{ nombreMesVista }}</h2>
              <p class="text-muted small text-uppercase tracking-wider">Métricas Operativas SCC</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-12 mb-4">
        <card type="chart" class="card-shadow">
          <template slot="header">
            <h5 class="card-category text-muted">Volumen Temporal</h5>
            <h3 class="card-title text-digitel-purple title-bold">
              <i class="tim-icons icon-delivery-fast text-info"></i> Operaciones por Día
            </h3>
          </template>
          <div class="chart-area-v-large">
            <bar-chart 
              :key="'diario-' + periodoSeleccionado"
              :chart-data="charts.diario.data" 
              :extra-options="charts.diario.opts" 
            />
          </div>
        </card>
      </div>

      <div class="col-lg-6 mb-4">
        <card type="chart" class="card-shadow">
          <template slot="header">
            <h5 class="card-category text-muted">Distribución de Red</h5>
            <h3 class="card-title text-digitel-purple title-bold">
              <i class="tim-icons icon-world text-danger"></i> Distribución por Red / Tecnología
            </h3>
          </template>
          <div class="chart-area-large d-flex justify-content-center align-items-center">
            <div style="width: 100%; max-width: 400px;">
              <pie-chart 
                :key="'tec-' + periodoSeleccionado"
                :chart-data="charts.tecnologia.data" 
                :extra-options="charts.tecnologia.opts"
              />
            </div>
          </div>
        </card>
      </div>

      <div class="col-lg-6 mb-4">
        <card type="chart" class="card-shadow">
          <template slot="header">
            <h5 class="card-category text-muted">Rendimiento Operativo</h5>
            <h3 class="card-title text-digitel-purple title-bold">
              <i class="tim-icons icon-coins text-warning"></i> Operaciones Comisionables
            </h3>
          </template>
          <div class="chart-area-large d-flex justify-content-center align-items-center">
            <div style="width: 100%; max-width: 400px;">
              <pie-chart 
                :key="'com-' + periodoSeleccionado"
                :chart-data="charts.comisionables.data" 
                :extra-options="charts.comisionables.opts"
              />
            </div>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>

<script>
import BarChart from "@/components/Charts/BarChart";
import PieChart from "@/components/Charts/PieChart"; 
import dashboardService from '@/services/dashboardService';

export default {
  components: { BarChart, PieChart },
  data() {
    return {
      periodoSeleccionado: new Date().toISOString().slice(0, 7),
      paleta: ['#5C068C', '#009FDF', '#E87722', '#008675', '#0072CE', '#6BA539'],
      charts: {
        diario: { 
          data: { labels: [], datasets: [] },
          opts: { 
            maintainAspectRatio: false, 
            legend: { display: false },
            scales: { 
              yAxes: [{ ticks: { beginAtZero: true } }], 
              xAxes: [{ barPercentage: 0.9 }] 
            } 
          }
        },
        tecnologia: { 
          data: { labels: [], datasets: [] },
          opts: { maintainAspectRatio: false, legend: { position: 'right' } }
        },
        comisionables: { 
          data: { labels: [], datasets: [] },
          opts: { 
            maintainAspectRatio: false, 
            legend: { position: 'right', labels: { boxWidth: 15, padding: 10 } },
            cutoutPercentage: 70 
          }
        }
      }
    };
  },
  computed: {
    nombreMesVista() {
      const meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
      const [year, month] = this.periodoSeleccionado.split('-');
      return `${meses[parseInt(month) - 1]} ${year}`;
    }
  },
  methods: {
    async fetchDashboardData() {
      try {
        const res = await dashboardService.getMetrics(this.periodoSeleccionado);
        if (res.data) this.processData(res.data);
      } catch (e) { console.error(e); }
    },
    processData(raw) {
      this.charts.diario.data = {
        labels: raw.operaciones_dia.map(i => i.etiqueta),
        datasets: [{ label: 'Total', backgroundColor: '#5C068C', data: raw.operaciones_dia.map(i => i.total) }]
      };
      
      this.charts.tecnologia.data = {
        labels: raw.tecnologia.map(i => i.etiqueta),
        datasets: [{ backgroundColor: ['#5C068C', '#009FDF', '#008675'], data: raw.tecnologia.map(i => i.total) }]
      };

      this.charts.comisionables.data = {
        labels: raw.comisionables.map(i => i.etiqueta),
        datasets: [{ 
          backgroundColor: this.paleta, 
          data: raw.comisionables.map(i => i.total),
          borderWidth: 0
        }]
      };
    }
  },
  mounted() { this.fetchDashboardData(); }
};
</script>

<style scoped>
/* --- ESTILOS INSTITUCIONALES --- */
.text-digitel-purple { color: #5C068C !important; }
.title-bold { font-weight: 800; }

/* --- SELECTOR DE MES ADAPTATIVO (CLARO/OSCURO) --- */
.selector-container {
  /* Al usar inherit, toma el color de fondo que tenga el dashboard en ese momento */
  background-color: inherit !important; 
  border-radius: 15px;
  /* Borde sutil que se ve en ambos temas */
  border: 1px solid rgba(128, 128, 128, 0.2); 
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
}

.label-title {
  color: #888;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 0;
}

.date-input-minimal {
  /* Border y fondo con transparencia para que se adapten al color de atrás */
  border: 1px solid rgba(128, 128, 128, 0.3) !important;
  border-radius: 8px !important;
  /* 'inherit' asegura que la letra sea negra en fondo claro y blanca en fondo oscuro */
  color: inherit !important; 
  font-weight: 600 !important;
  padding: 8px 15px !important;
  background-color: rgba(128, 128, 128, 0.1) !important;
}

.date-input-minimal:focus {
  border-color: #5C068C !important;
  background-color: transparent !important;
  outline: none;
}

.dashboard-main-title {
  color: #5C068C;
  font-weight: 800;
  margin-bottom: 0;
  text-transform: capitalize;
}

.border-right-custom {
  /* Separador adaptativo */
  border-right: 1px solid rgba(128, 128, 128, 0.2);
}

.divider-thin {
  opacity: 0.1;
  /* Usa el color de texto actual para la línea */
  background-color: currentColor; 
}

.tracking-wider {
  letter-spacing: 2px;
}

/* --- ESTILOS DE GRÁFICAS --- */
.chart-area-v-large { height: 450px; }
.chart-area-large { height: 380px; }

/* Tarjetas de gráficas también adaptativas */
.card-shadow { 
  background-color: inherit !important;
  box-shadow: 0 4px 20px 0 rgba(0,0,0,0.08); 
  border-radius: 12px; 
  border: 1px solid rgba(128, 128, 128, 0.1); 
}

@media (max-width: 576px) {
  .border-right-custom {
    border-right: none;
    border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    padding-bottom: 10px;
    margin-bottom: 10px;
  }
}
</style>
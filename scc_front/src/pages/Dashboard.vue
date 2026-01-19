<template>
  <div class="content">
    <div class="row">
      <div class="col-12">
        <card type="chart">
          <template slot="header">
            <div class="row">
              <div class="col-sm-6" :class="isRTL ? 'text-right' : 'text-left'">
                <h5 class="card-category">Resumen General</h5>
                <h2 class="card-title">Gráfica de Operaciones</h2>
              </div>
              <div class="col-sm-6 text-right">
                <div class="btn-group btn-group-toggle float-right" data-toggle="buttons">
                  <label
                    v-for="(option, index) in barChartCategories"
                    :key="option"
                    class="btn btn-sm btn-primary btn-simple"
                    :class="{ active: barChart.activeIndex === index }"
                    :id="index"
                  >
                    <input
                      type="radio"
                      @click="handleCategoryChange(index)"
                      name="options"
                      autocomplete="off"
                      :checked="barChart.activeIndex === index"
                    />
                    {{ option }}
                  </label>
                </div>
              </div>
            </div>

            <div class="row mt-3">
              <div class="col-md-3">
                <label class="text-muted small">Desde:</label>
                <input type="date" v-model="fechas.inicio" class="form-control date-input" @change="refreshData">
              </div>
              <div class="col-md-3">
                <label class="text-muted small">Hasta:</label>
                <input type="date" v-model="fechas.fin" class="form-control date-input" @change="refreshData">
              </div>
            </div>
          </template>

          <div class="chart-area">
            <bar-chart
              style="height: 100%"
              ref="barChart"
              :chart-id="'big-bar-chart'"
              :chart-data="barChart.chartData"
              :gradient-colors="barChart.gradientColors"
              :gradient-stops="barChart.gradientStops"
              :extra-options="barChart.extraOptions"
            >
            </bar-chart>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>

<script>
import BarChart from "@/components/Charts/BarChart";
import dashboardService from '@/services/dashboardService';
import themeService from '@/services/themeService';

export default {
  components: { BarChart },
  data() {
    return {
      fechas: {
        inicio: '2025-01-01',
        fin: '2025-12-31'
      },
      barChart: {
        activeIndex: 0,
        chartData: {
          labels: [],
          datasets: [{
            label: "Operaciones",
            data: [],
            backgroundColor: "#00bf9a",
            borderColor: "#00bf9a",
            borderWidth: 1,
            barPercentage: 0.8,
            categoryPercentage: 0.9,
          }],
        },
        extraOptions: {
          scales: {
            yAxes: [{ ticks: { beginAtZero: true, fontColor: "#9e9e9e", padding: 20 } }],
            xAxes: [{ ticks: { fontColor: "#9e9e9e", padding: 20 } }]
          },
          legend: { display: false },
          responsive: true,
          maintainAspectRatio: false,
        },
        gradientColors: ["#00bf9a", "#00a086", "#008573"],
        gradientStops: [1, 0.5, 0],
      },
    };
  },
  computed: {
    isRTL() { return this.$rtl.isRTL; },
    barChartCategories() { return ["Ventas", "Postventas", "Reportes"]; },
  },
  methods: {
    updateChartColors(isDark) {
      // Ajusta el color del texto según el tema
      const textColor = isDark ? "#9e9e9e" : "#333333";
      this.barChart.extraOptions.scales.yAxes[0].ticks.fontColor = textColor;
      this.barChart.extraOptions.scales.xAxes[0].ticks.fontColor = textColor;
      
      // Forzar actualización visual
      if (this.$refs.barChart && this.$refs.barChart.updateGradients) {
        this.$refs.barChart.updateGradients(this.barChart.chartData);
      }
    },
    async refreshData() {
      const tipo = this.barChart.activeIndex === 0 ? 'ventas' : 'postventas';
      if (this.barChart.activeIndex === 2) return;

      try {
        const res = await dashboardService.getEstadisticas(tipo, this.fechas.inicio, this.fechas.fin);
        const labels = res.data.map(item => item.mes_nombre);
        const totals = res.data.map(item => item.total);

        this.barChart.chartData = {
          labels: labels,
          datasets: [{
            ...this.barChart.chartData.datasets[0],
            data: totals
          }]
        };

        if (this.$refs.barChart && this.$refs.barChart.updateGradients) {
          this.$refs.barChart.updateGradients(this.barChart.chartData);
        }
      } catch (error) {
        console.error("Error al cargar datos del dashboard:", error);
      }
    },
    handleCategoryChange(index) {
      this.barChart.activeIndex = index;
      this.refreshData();
    }
  },
  mounted() {
    this.refreshData();
    
    // Inicializar colores según el tema actual
    const currentTheme = themeService.getStoredTheme();
    this.updateChartColors(currentTheme === 'dark');

    // Escuchar el evento global emitido por TopNavbar.vue
    this.$root.$on('theme-changed', (isDark) => {
      this.updateChartColors(isDark);
    });
  },
  beforeDestroy() {
    // Limpiar el evento al destruir el componente
    this.$root.$off('theme-changed');
  }
};
</script>

<style scoped>
.date-input {
  background-color: transparent !important;
  border: 1px solid #2b3553;
  color: inherit !important;
}

/* Invertir el icono del calendario solo en modo oscuro */
body:not(.white-content) .date-input::-webkit-calendar-picker-indicator {
    filter: invert(1);
}

/* Ajuste para que el texto sea legible en modo claro */
body.white-content .date-input {
    border-color: #d0d0d0;
    color: #333 !important;
}
</style>
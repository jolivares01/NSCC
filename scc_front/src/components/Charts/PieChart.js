import { Pie, mixins } from "vue-chartjs";

export default {
  name: "pie-chart",
  extends: Pie,
  mixins: [mixins.reactiveProp],
  props: {
    extraOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          display: true,
          position: 'bottom',
          labels: { fontColor: "#9e9e9e", padding: 20 }
        }
      })
    }
  },
  mounted() {
    // Watcher para asegurar que si chartData cambia, el gráfico se re-renderice
    this.$watch(
      "chartData",
      (newVal, oldVal) => {
        // Si es la primera vez o los datos cambiaron, renderizamos
        if (!oldVal || newVal !== oldVal) {
          this.renderChart(this.chartData, this.extraOptions);
        }
      },
      { immediate: true }
    );
  }
};
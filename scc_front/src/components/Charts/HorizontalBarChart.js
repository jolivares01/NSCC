import { HorizontalBar, mixins } from "vue-chartjs";

export default {
  name: "horizontal-bar-chart",
  extends: HorizontalBar, // <--- Aquí está el truco: HorizontalBar en lugar de Bar
  mixins: [mixins.reactiveProp],
  props: ["extraOptions"],
  mounted() {
    this.renderChart(this.chartData, this.extraOptions);
  }
};
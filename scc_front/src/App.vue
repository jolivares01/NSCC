<template>
  <div>
    <notifications></notifications>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
// Mantenemos el import por si otros componentes lo usan, 
// pero forzaremos la lógica aquí.
import themeService from '@/services/themeService';

export default {
  methods: {
    disableRTL() {
      if (!this.$rtl.isRTL) {
        this.$rtl.disableRTL();
      }
    },
    toggleNavOpen() {
      let root = document.getElementsByTagName("html")[0];
      root.classList.toggle("nav-open");
    },
    // Modificamos este método para que SIEMPRE fuerce el tema claro
    forceLightTheme() {
      // 1. Forzamos al servicio a usar modo 'light' (isDark = false)
      themeService.toggleTheme(false);
      
      // 2. Por seguridad, nos aseguramos de que el body tenga la clase necesaria
      // En Black Dashboard, 'white-content' es la clase para el modo claro.
      document.body.classList.add("white-content");
      
      // 3. Opcional: Limpiamos el localStorage para que no intente volver a oscuro
      localStorage.setItem('theme', 'light');
    }
  },
  mounted() {
    // 1. Forzar el tema claro apenas inicie
    this.forceLightTheme();
    
    this.$watch("$route", this.disableRTL, { immediate: true });
    this.$watch("$sidebar.showSidebar", this.toggleNavOpen);
  },
};
</script>

<style lang="scss">
/* Añadimos estas reglas globales aquí para asegurar que 
   NADA se quede con fondo oscuro 
*/

// Forzar el fondo de la página y paneles
body, .main-panel, .content {
    background-color: #f5f6fa !important;
}

// Forzar que todas las tarjetas sean blancas siempre
.card {
    background-color: #ffffff !important;
    
    // Forzar que los textos dentro de las cards sean oscuros
    .card-title, .card-category, p, td, th, label, span:not(.badge) {
        color: #32325d !important;
    }
}

// Normalizar inputs globales (lo que pediste anteriormente)
.form-control, select.form-control {
    background-color: #f4f5f7 !important;
    color: #32325d !important;
    border: 1px solid #d0d0d0 !important;

    &:focus {
        background-color: #ffffff !important;
        border-color: #5C068C !important;
    }
}
</style>
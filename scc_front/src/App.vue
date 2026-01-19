<template>
  <div>
    <notifications></notifications>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
// Importamos el servicio de tema para gestionar la persistencia
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
    // Método para aplicar el tema guardado en localStorage
    initializeTheme() {
      const savedTheme = themeService.getStoredTheme();
      const isDark = (savedTheme === 'dark');
      themeService.toggleTheme(isDark);
    }
  },
  mounted() {
    // 1. Inicializar el tema apenas se monte la aplicación
    this.initializeTheme();
    
    // 2. Mantener tus watches existentes para RTL y Sidebar
    this.$watch("$route", this.disableRTL, { immediate: true });
    this.$watch("$sidebar.showSidebar", this.toggleNavOpen);
  },
};
</script>

<style lang="scss"></style>
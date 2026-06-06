<template>
  <div class="wrapper">
    <side-bar>
      <template slot="links">
        <sidebar-link v-if="isAdmin" to="/dashboard" name="Dashboard" icon="tim-icons icon-chart-pie-36" />
        
        <sidebar-item v-if="isAdmin" title="Comisiones" icon="tim-icons icon-money-coins">
          <sidebar-link to="/activaciones" name="Activaciones" icon="tim-icons icon-chart-pie-36" />
          <sidebar-link to="/consulta-recargas" name="Consulta de Recargas" icon="tim-icons icon-zoom-split" />
          <sidebar-link to="/comisiones-especiales" name="Comisiones Especiales" icon="tim-icons icon-coins" />
          <sidebar-link to="/calculo" name="Cálculo" icon="tim-icons icon-coins" />
        </sidebar-item>
        
        <sidebar-item title="Módulo Reclamos" icon="tim-icons icon-alert-circle-exc">
          <sidebar-link to="/gestion-reclamos" name="Gestión de reclamos" icon="tim-icons icon-alert-circle-exc" />
        </sidebar-item>
        
        <sidebar-item title="Módulo de Reportes" icon="tim-icons icon-chart-bar-32">
          <sidebar-link to="/reportes" name="Reportes" icon="tim-icons icon-chart-bar-32" />
        </sidebar-item>
        
        <sidebar-item v-if="isAdmin" title="Gestión de Usuarios" icon="tim-icons icon-single-02">
          <sidebar-link to="/registrar-usuario" name="Registrar usuario" icon="tim-icons icon-single-02" />
          <sidebar-link to="/gestion-usuarios" name="Gestión de usuarios" icon="tim-icons icon-badge" />
        </sidebar-item>
        
        <sidebar-link v-if="isAdmin" to="/parametros-negocio" name="Parametros DE NEGOCIO" icon="tim-icons icon-settings" />
      </template>
    </side-bar>
    
    <div class="main-panel">
      <top-navbar></top-navbar>
      <dashboard-content @click.native="toggleSidebar"></dashboard-content>
      <content-footer></content-footer>
    </div>
  </div>
</template>

<script>
import TopNavbar from "./TopNavbar.vue";
import ContentFooter from "./ContentFooter.vue";
import DashboardContent from "./Content.vue";

export default {
  components: { TopNavbar, ContentFooter, DashboardContent },
  computed: {
    isAdmin() {
      // Verificamos si el rol guardado es el de Administrador
      return localStorage.getItem('user_role') === 'ROL_0001';
    }
  },
  methods: {
    toggleSidebar() {
      if (this.$sidebar.showSidebar) {
        this.$sidebar.displaySidebar(false);
      }
    },
  },
};
</script>
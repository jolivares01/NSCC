<template>
  <nav
    class="navbar navbar-expand-lg navbar-absolute"
    :class="{ 'bg-white': showMenu, 'navbar-transparent': !showMenu }"
  >
    <div class="container-fluid">
      <div class="navbar-wrapper">
        <div class="navbar-toggle d-inline" :class="{ toggled: $sidebar.showSidebar }">
          <button type="button" class="navbar-toggler" @click="toggleSidebar">
            <span class="navbar-toggler-bar bar1"></span>
            <span class="navbar-toggler-bar bar2"></span>
            <span class="navbar-toggler-bar bar3"></span>
          </button>
        </div>
        <a class="navbar-brand" href="javascript:void(0)">{{ routeName }}</a>
      </div>
      <button
        class="navbar-toggler"
        type="button"
        @click="toggleMenu"
        data-toggle="collapse"
        data-target="#navigation"
      >
        <span class="navbar-toggler-bar navbar-kebab"></span>
        <span class="navbar-toggler-bar navbar-kebab"></span>
        <span class="navbar-toggler-bar navbar-kebab"></span>
      </button>

      <collapse-transition>
        <div class="collapse navbar-collapse show" v-show="showMenu">
          <ul class="navbar-nav" :class="$rtl.isRTL ? 'mr-auto' : 'ml-auto'">
            
            <li class="nav-item">
              <button class="nav-link btn btn-link" @click="changeTheme" title="Cambiar Apariencia">
                <i :class="isDarkMode ? 'tim-icons icon-bulb-63' : 'tim-icons icon-light-3'"></i>
                <p class="d-lg-none">Cambiar Tema</p>
              </button>
            </li>

            <base-dropdown tag="li" :menu-on-right="!$rtl.isRTL" title-tag="a" class="nav-item">
              <a slot="title" href="#" class="dropdown-toggle nav-link" data-toggle="dropdown">
                <div class="notification d-none d-lg-block d-xl-block" v-if="notificationCount > 0"></div>
                <i class="tim-icons icon-sound-wave"></i>
                <span v-if="notificationCount > 0" class="badge badge-danger" 
                      style="position: absolute; top: 5px; right: 5px; font-size: 10px; background-color: #fd5d93;">
                  {{ notificationCount }}
                </span>
              </a>
              <li class="nav-link">
                <router-link to="/gestion-reclamos" class="nav-item dropdown-item">
                  {{ notificationMessage }}
                </router-link>
              </li>
            </base-dropdown>
            
            <base-dropdown tag="li" :menu-on-right="!$rtl.isRTL" title-tag="a" class="nav-item" menu-classes="dropdown-navbar">
              <a slot="title" href="#" class="dropdown-toggle nav-link" data-toggle="dropdown">
                <div class="photo">
                  <img src="img/digitel_logo_user.png" alt="Perfil" />
                </div>
                <b class="caret d-none d-lg-block d-xl-block"></b>
              </a>
              <li class="nav-link"><a href="#" class="nav-item dropdown-item">Perfil</a></li>
              <div class="dropdown-divider"></div>
              <li class="nav-link"><a href="#" @click="logout" class="nav-item dropdown-item">Cerrar Sesión</a></li>
            </base-dropdown>
          </ul>
        </div>
      </collapse-transition>
    </div>
  </nav>
</template>

<script>
import { CollapseTransition } from "vue2-transitions";
import themeService from '@/services/themeService';
import axios from 'axios';

export default {
  components: { CollapseTransition },
  computed: {
    routeName() {
      const { name } = this.$route;
      return this.capitalizeFirstLetter(name || "");
    },
    notificationMessage() {
      if (this.notificationCount === 0) return "No tienes notificaciones nuevas";
      return this.role === 'ROL_0001' 
        ? `Hay ${this.notificationCount} tickets esperando atención`
        : `Tienes ${this.notificationCount} respuestas nuevas`;
    }
  },
  data() {
    return {
      showMenu: false,
      isDarkMode: true,
      notificationCount: 0,
      role: localStorage.getItem('user_role'),
      username: localStorage.getItem('user_name'),
      polling: null
    };
  },
  methods: {
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    changeTheme() {
      this.isDarkMode = !this.isDarkMode;
      themeService.toggleTheme(this.isDarkMode);
      this.$root.$emit('theme-changed', this.isDarkMode);
    },
    toggleSidebar() {
      this.$sidebar.displaySidebar(!this.$sidebar.showSidebar);
    },
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    logout() {
      localStorage.clear(); // Limpia todo para seguridad
      this.$router.push('/login');
    },
 async fetchNotifications() {
  try {
    const res = await axios.get('http://localhost:8000/api/v1/claims/notifications-count', {
      params: { 
        id_rol: this.role,
        username: this.username 
      }
    });
    // Esto actualizará el número sobre la campana
    this.notificationCount = res.data.count; 
  } catch (error) {
    console.error("Error al obtener notificaciones", error);
  }
}
  },
  mounted() {
    this.isDarkMode = themeService.getStoredTheme() === 'dark';
    // Consulta inicial
    this.fetchNotifications();
    // Consultar cada 30 segundos
    this.polling = setInterval(this.fetchNotifications, 30000);
  },
  beforeDestroy() {
    // Importante limpiar el intervalo al salir
    clearInterval(this.polling);
  }
};
</script>
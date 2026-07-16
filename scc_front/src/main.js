/*
 =========================================================
 * Vue Black Dashboard - v1.1.3
 =========================================================
 * Product Page: https://www.creative-tim.com/product/black-dashboard
 * Copyright 2024 Creative Tim (http://www.creative-tim.com)
 =========================================================
 */
 import Vue from "vue";
 import VueRouter from "vue-router";
 import RouterPrefetch from "vue-router-prefetch";
 import App from "./App";
 import router from "./router/index";
 import axios from "axios"; // 1. Importar Axios
 
 import BlackDashboard from "./plugins/blackDashboard";
 import i18n from "./i18n";
 import "./registerServiceWorker";
 
 Vue.use(BlackDashboard);
 Vue.use(VueRouter);
 Vue.use(RouterPrefetch);
 
 // --- CONFIGURACIÓN GLOBAL DE AXIOS Y JWT ---
 
 // 2. URL Base del Gateway (Ajusta el puerto si es necesario)
 axios.defaults.baseURL = 'http://localhost:8080';
 
 // 3. Interceptor de Petición: Envía el token en cada llamada
 axios.interceptors.request.use(config => {
   const token = localStorage.getItem('user_token');
   if (token) {
     config.headers.Authorization = `Bearer ${token}`;
   }
   return config;
 }, error => {
   return Promise.reject(error);
 });
 
 // 4. Interceptor de Respuesta: Maneja el vencimiento del token (401)
 axios.interceptors.response.use(
   response => response,
   error => {
     // Si el error es 401 (Unauthorized), el token expiró o es inválido
     if (error.response && error.response.status === 401) {
       console.warn("Sesión expirada. Limpiando datos...");
       
       // Limpiamos la persistencia
       localStorage.removeItem('user_token');
       localStorage.removeItem('user_role');
       localStorage.removeItem('user_name');
       localStorage.removeItem('user_permissions');
 
       // Redirigir al login usando el hash de la URL (común en esta plantilla)
       window.location.href = '#/login';
       
       // Opcional: Recarga la página para limpiar cualquier estado de Vue en memoria
       window.location.reload(); 
     }
     return Promise.reject(error);
   }
 );
 
 // 5. Hacer axios accesible en todos los componentes como this.$http
 Vue.prototype.$http = axios;
 
 new Vue({
   router,
   i18n,
   render: (h) => h(App),
 }).$mount("#app");
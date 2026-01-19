import DashboardLayout from "@/layout/dashboard/DashboardLayout.vue";
// GeneralViews
import NotFound from "@/pages/NotFoundPage.vue";

// Admin pages
const Dashboard = () =>
  import(/* webpackChunkName: "dashboard" */ "@/pages/Dashboard.vue");

// Tus nuevas páginas
const Activaciones = () =>
  import(/* webpackChunkName: "comisiones" */ "@/pages/Activaciones.vue");
const ConsultaRecargas = () =>
  import(/* webpackChunkName: "comisiones" */ "@/pages/ConsultaRecargas.vue");
const ComisionesEspeciales = () =>
  import(/* webpackChunkName: "comisiones" */ "@/pages/ComisionesEspeciales.vue");
const Calculo = () =>
  import(/* webpackChunkName: "comisiones" */ "@/pages/Calculo.vue");
const GestionReclamos = () =>
  import(/* webpackChunkName: "reclamos" */ "@/pages/GestionReclamos.vue");
const Reportes = () =>
  import(/* webpackChunkName: "reportes" */ "@/pages/Reportes.vue");
const RegistrarUsuario = () =>
  import(/* webpackChunkName: "usuarios" */ "@/pages/RegistrarUsuario.vue");
const GestionUsuarios = () =>
  import(/* webpackChunkName: "usuarios" */ "@/pages/GestionUsuarios.vue");
const Parametros = () =>
  import(/* webpackChunkName: "usuarios" */ "@/pages/Parametros.vue");

const routes = [
  {
    path: "/",
    component: DashboardLayout,
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: Dashboard,
        meta: {
          icon: "tim-icons icon-chart-pie-36",
          title: "Dashboard"
        }
      },
      // Cálculo de Comisiones (Grupo)
      {
        path: "activaciones",
        name: "activaciones",
        component: Activaciones,
        meta: {
          icon: "tim-icons icon-chart-pie-36",
          title: "Activaciones",
          parent: "Cálculo de Comisiones"
        }
      },
      {
        path: "consulta-recargas",
        name: "consulta-recargas",
        component: ConsultaRecargas,
        meta: {
          icon: "tim-icons icon-zoom-split",
          title: "Consulta de Recargas",
          parent: "Cálculo de Comisiones"
        }
      },
      {
        path: "comisiones-especiales",
        name: "comisiones-especiales",
        component: ComisionesEspeciales,
        meta: {
          icon: "tim-icons icon-coins",
          title: "Comisiones Especiales",
          parent: "Cálculo de Comisiones"
        }
      },
      {
        path: "calculo",
        name: "calculo",
        component: Calculo,
        meta: {
          icon: "tim-icons icon-calculator",
          title: "Cálculo",
          parent: "Cálculo de Comisiones"
        }
      },
      // Módulo Reclamos
      {
        path: "gestion-reclamos",
        name: "gestion-reclamos",
        component: GestionReclamos,
        meta: {
          icon: "tim-icons icon-alert-circle-exc",
          title: "Gestión de reclamos"
        }
      },
      // Módulo de Reportes
      {
        path: "reportes",
        name: "reportes",
        component: Reportes,
        meta: {
          icon: "tim-icons icon-chart-bar-32",
          title: "Reportes"
        }
      },
      // Gestión de Usuarios (Grupo)
      {
        path: "registrar-usuario",
        name: "registrar-usuario",
        component: RegistrarUsuario,
        meta: {
          icon: "tim-icons icon-single-02",
          title: "Registrar usuario",
          parent: "Gestión de Usuarios"
        }
      },
      {
        path: "gestion-usuarios",
        name: "gestion-usuarios",
        component: GestionUsuarios,
        meta: {
          icon: "tim-icons icon-badge",
          title: "Gestión de usuarios",
          parent: "Gestión de Usuarios"
        }
      },
      {
        path: "parametros",
        name: "parametros",
        component: Parametros,
        meta: {
          icon: "tim-icons icon-settings",
          title: "Parametros",
          parent: "Gestión de Usuarios"
        }
      }
    ],
  },
  { path: "*", component: NotFound },
];

export default routes;
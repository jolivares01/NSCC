import VueRouter from "vue-router";
import DashboardLayout from "@/layout/dashboard/DashboardLayout.vue";
import NotFound from "@/pages/NotFoundPage.vue";

// Lazy loading de páginas
const Dashboard = () => import("@/pages/Dashboard.vue");
const Activaciones = () => import("@/pages/Activaciones.vue");
const ConsultaRecargas = () => import("@/pages/ConsultaRecargas.vue");
const ComisionesEspeciales = () => import("@/pages/ComisionesEspeciales.vue");
const Calculo = () => import("@/pages/Calculo.vue");
const GestionReclamos = () => import("@/pages/GestionReclamos.vue");
const Reportes = () => import("@/pages/Reportes.vue");
const RegistrarUsuario = () => import("@/pages/RegistrarUsuario.vue");
const GestionUsuarios = () => import("@/pages/GestionUsuarios.vue");
const Parametros = () => import("@/pages/Parametros.vue");

const routes = [
  {
    path: "/",
    component: DashboardLayout,
    // Se elimina el redirect estático para manejarlo dinámicamente
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: Dashboard,
        meta: { icon: "tim-icons icon-chart-pie-36", title: "Dashboard" }
      },
      {
        path: "activaciones",
        name: "activaciones",
        component: Activaciones,
        meta: { title: "Activaciones", parent: "Cálculo de Comisiones" }
      },
      {
        path: "consulta-recargas",
        name: "consulta-recargas",
        component: ConsultaRecargas,
        meta: { title: "Consulta de Recargas", parent: "Cálculo de Comisiones" }
      },
      {
        path: "comisiones-especiales",
        name: "comisiones-especiales",
        component: ComisionesEspeciales,
        meta: { title: "Comisiones Especiales", parent: "Cálculo de Comisiones" }
      },
      {
        path: "calculo",
        name: "calculo",
        component: Calculo,
        meta: { title: "Cálculo", parent: "Cálculo de Comisiones" }
      },
      {
        path: "gestion-reclamos",
        name: "gestion-reclamos",
        component: GestionReclamos,
        meta: { icon: "tim-icons icon-alert-circle-exc", title: "Gestión de reclamos" }
      },
      {
        path: "reportes",
        name: "reportes", // Nombre usado para la redirección
        component: Reportes,
        meta: { icon: "tim-icons icon-chart-bar-32", title: "Reportes" }
      },
      {
        path: "registrar-usuario",
        name: "registrar-usuario",
        component: RegistrarUsuario,
        meta: { title: "Registrar usuario", parent: "Gestión de Usuarios" }
      },
      {
        path: "gestion-usuarios",
        name: "gestion-usuarios",
        component: GestionUsuarios,
        meta: { title: "Gestión de usuarios", parent: "Gestión de Usuarios" }
      },
      {
        path: "parametros",
        name: "parametros",
        component: Parametros,
        meta: { title: "Parametros", parent: "Gestión de Usuarios" }
      }
    ]
  },
  { path: "*", component: NotFound }
];

const router = new VueRouter({
  routes,
  linkExactActiveClass: "active"
});

// LÓGICA DE REDIRECCIÓN POR ROL
router.beforeEach((to, from, next) => {
  const userRole = localStorage.getItem('user_role');

  if (to.path === "/") {
    if (userRole === 'ROL_0002') {
      next({ name: 'reportes' }); // Redirige a Reportes
    } else {
      next({ name: 'dashboard' }); // Redirige a Dashboard (Admin)
    }
  } else {
    next();
  }
});

export default router;
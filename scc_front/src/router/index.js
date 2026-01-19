import VueRouter from "vue-router";

// Importación de Layouts y Páginas Base
import DashboardLayout from "@/layout/dashboard/DashboardLayout.vue";
import Login from "@/pages/Login.vue";
import Dashboard from "@/pages/Dashboard.vue";

/**
 * NOTA: He corregido los nombres aquí para que coincidan con 
 * los archivos reales que hemos trabajado anteriormente.
 */
const UserManagement = () => import("@/pages/GestionUsuarios.vue"); 
const Reports = () => import("@/pages/Reportes.vue");
const Reclamos = () => import("@/pages/GestionReclamos.vue");

const routes = [
  { 
    path: "/login", 
    name: "Login", 
    component: Login,
    meta: { isPublic: true } 
  },
  {
    path: "/",
    component: DashboardLayout,
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: Dashboard,
        meta: { roles: ['ROL_0001'] }
      },
      {
        path: "registrar-usuario", // Debe coincidir con el 'to' de tu Sidebar
        name: "Registrar Usuario",
        component: () => import("@/pages/RegistrarUsuario.vue"),
        meta: { roles: ['ROL_0001'] } // Solo el Administrador puede ver esto
      },
      {
        path: "gestion-usuarios",
        name: "Usuarios",
        component: UserManagement,
        meta: { roles: ['ROL_0001'] }
      },
      {
        path: "reportes",
        name: "Reportes",
        component: Reports,
        meta: { roles: ['ROL_0001', 'ROL_0002'] }
      },
      {
        path: "gestion-reclamos",
        name: "Reclamos",
        component: Reclamos,
        meta: { roles: ['ROL_0001', 'ROL_0002'] }
      }
    ]
  },
  { path: "*", redirect: "/login" }
];

const router = new VueRouter({
  routes,
  linkExactActiveClass: "active",
});

// GUARD DE NAVEGACIÓN
router.beforeEach((to, from, next) => {
  const userRole = localStorage.getItem('user_role');
  const isLogged = !!userRole;

  if (to.meta.isPublic) {
    next();
  } 
  else if (!isLogged) {
    next({ name: 'Login' });
  } 
  else if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    const homePath = userRole === 'ROL_0001' ? '/dashboard' : '/reportes';
    next({ path: homePath });
  } 
  else {
    next();
  }
});

export default router;
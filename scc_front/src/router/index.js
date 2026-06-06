import VueRouter from "vue-router";

// Importación de Layouts y Páginas Base
import DashboardLayout from "@/layout/dashboard/DashboardLayout.vue";
import Login from "@/pages/Login.vue";
import Dashboard from "@/pages/Dashboard.vue";

// Páginas existentes
const UserManagement = () => import("@/pages/GestionUsuarios.vue"); 
const Reports = () => import("@/pages/Reportes.vue");
const Reclamos = () => import("@/pages/GestionReclamos.vue");

// Ayuda para carga segura
const safeImport = (path) => {
  return () => import(`@/pages/${path}`).catch(() => {
    console.warn(`Archivo ${path} no encontrado. Redirigiendo a Dashboard.`);
    return import("@/pages/Dashboard.vue");
  });
};

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
        component: Dashboard
      },
      {
        path: "comisiones",
        name: "Comisiones",
        component: safeImport("Comisiones.vue")
      },
      {
        path: "activaciones",
        name: "Activaciones",
        component: safeImport("Activaciones.vue")
      },
      {
        path: "consulta-recargas",
        name: "Recargas",
        component: safeImport("ConsultaRecargas.vue")
      },
      {
        path: "comisiones-especiales",
        name: "Comisiones Especiales",
        component: safeImport("ComisionesEspeciales.vue")
      },
      {
        path: "calculo",
        name: "Cálculo",
        component: safeImport("Calculo.vue")
      },
      {
        path: "parametros-negocio",
        name: "Parámetros de Negocio",
        component: safeImport("Parametros.vue")
      },
      {
        path: "registrar-usuario",
        name: "Registrar Usuario",
        component: () => import("@/pages/RegistrarUsuario.vue")
      },
      {
        path: "gestion-usuarios",
        name: "Usuarios",
        component: UserManagement
      },
      {
        path: "reportes",
        name: "Reportes",
        component: Reports
      },
      {
        path: "gestion-reclamos",
        name: "Reclamos",
        component: Reclamos
      }
    ]
  },
  { path: "*", redirect: "/login" }
];

const router = new VueRouter({
  routes,
  linkExactActiveClass: "active",
  // Esto ayuda a que el scroll vuelva arriba al cambiar de ruta
  scrollBehavior: () => ({ y: 0 }), 
});

// GUARD DE NAVEGACIÓN DINÁMICO Y DE SEGURIDAD
router.beforeEach((to, from, next) => {
  // 1. Validamos la sesión basándonos en el TOKEN (JWT)
  const token = localStorage.getItem('user_token');
  const userRole = localStorage.getItem('user_role');
  const isLogged = !!token; // Si hay token, está logueado
  
  // 2. Obtenemos permisos
  const storedPermissions = localStorage.getItem('user_permissions');
  const allowedPaths = storedPermissions ? JSON.parse(storedPermissions) : [];

  // --- CASO A: SI LA RUTA ES PÚBLICA (LOGIN) ---
  if (to.meta.isPublic) {
    if (isLogged) {
      // Si ya está logueado e intenta ir al Login (botón atrás), lo mandamos al Dashboard
      return next({ name: 'Dashboard' });
    }
    return next();
  } 

  // --- CASO B: SI NO ESTÁ LOGUEADO Y TRATA DE ENTRAR A RUTA PRIVADA ---
  if (!isLogged) {
    console.warn("Acceso denegado: No hay token activo.");
    return next({ name: 'Login' });
  } 

  // --- CASO C: ESTÁ LOGUEADO, VALIDAMOS PERMISOS DINÁMICOS ---
  // Normalizamos el path (ej: de "/comisiones" a "comisiones")
  const currentPath = to.path === '/' || to.path === '/dashboard' ? 'dashboard' : to.path.split('/').pop();

  // Siempre permitimos el dashboard como ruta base si hay login
  if (currentPath === 'dashboard' || allowedPaths.includes(currentPath)) {
    next();
  } 
  else {
    // Si no tiene permiso para ese path específico, lo mandamos a su "Home" según rol
    console.warn(`Sin permiso para: ${currentPath}. Redirigiendo a zona segura.`);
    const homePath = userRole === 'ROL_0001' ? '/dashboard' : '/gestion-reclamos';
    next({ path: homePath });
  }
});

export default router;
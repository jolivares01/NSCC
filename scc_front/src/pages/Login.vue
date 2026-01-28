<template>
  <div class="login-page bg-default" style="min-height: 100vh; display: flex; align-items: center;">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-4 col-md-6">
          <card class="card-login card-white">
            <template slot="header">
              <div class="text-center pt-3">
                <img src="img/digitel_logo_login.jpg" alt="Logo" style="width: 70px;" class="mb-3">
                <h1 class="card-title text-dark" style="font-size: 1.5rem; font-weight: 600;">Sistema de Calculo de Comisiones</h1>
              </div>
            </template>

            <form @submit.prevent="handleLogin">
              <base-input 
                label="" 
                v-model="user.username" 
                placeholder="Ingrese su usuario"
                addon-left-icon="tim-icons icon-single-02"
                class="text-dark"
              ></base-input>
              
              <base-input 
                label="" 
                v-model="user.password" 
                type="password" 
                placeholder="Contraseña"
                addon-left-icon="tim-icons icon-lock-circle"
              ></base-input>
              
              <div class="text-center">
                <button type="submit" class="btn btn-primary btn-block btn-lg mb-3" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
                  INGRESAR
                </button>
              </div>
            </form>
            
            <template slot="footer">
              <div class="text-center text-muted small">
                Sistema de Calculo de Comisiones v1.0
              </div>
            </template>
          </card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'login',
  data() {
    return {
      loading: false,
      user: {
        username: '',
        password: ''
      }
    };
  },
  methods: {
    async handleLogin() {
      if (!this.user.username || !this.user.password) {
        this.$notify({ type: 'danger', message: 'Por favor complete todos los campos' });
        return;
      }

      this.loading = true;
      try {
        // 1. Llamada a la Autenticación
        const authResponse = await axios.post('http://localhost:8000/api/v1/auth/login', this.user);
        const { id_rol, username } = authResponse.data;

        // 2. NUEVA LLAMADA: Obtener permisos dinámicos desde el rol_services
        // Esta llamada viaja a través del Gateway que configuramos anteriormente
        const permissionsResponse = await axios.get(`http://localhost:8000/api/v1/roles/permissions/${id_rol}`);
        const allowedPaths = permissionsResponse.data.paths;

        // 3. Persistencia de la sesión y los permisos
        localStorage.setItem('user_role', id_rol);
        localStorage.setItem('user_name', username);
        // Guardamos el array de paths como un string JSON
        localStorage.setItem('user_permissions', JSON.stringify(allowedPaths));

        this.$notify({ type: 'success', icon: 'tim-icons icon-check-2', message: `Bienvenido, ${username}` });

        // 4. Redirección basada en ROL
        // El Router Guard ahora verificará 'user_permissions' inmediatamente al intentar entrar
        if (id_rol === 'ROL_0001') {
          this.$router.push('/dashboard');
        } else {
          // Si es ROL_0002 o cualquier otro con permisos definidos
          this.$router.push('/gestion-reclamos');
        }
        
      } catch (error) {
        console.error("Error en login:", error);
        const errorMsg = error.response?.data?.detail || 'Error de conexión con el servidor';
        this.$notify({ type: 'danger', icon: 'tim-icons icon-alert-circle-exc', message: errorMsg });
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.card-login.card-white {
  background-color: #ffffff !important;
  border-radius: 8px;
  box-shadow: 0 15px 35px rgba(50,50,93,.1), 0 5px 15px rgba(0,0,0,.07);
}
.card-login .form-group label {
  color: #333 !important;
}
.login-page {
  background: linear-gradient(0deg, #1e1e2f 0%, #1e1e24 100%);
}
</style>
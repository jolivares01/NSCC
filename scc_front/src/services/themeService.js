export default {
  // Cambia el tema físicamente en el DOM y lo guarda en el navegador
  toggleTheme(isDark) {
    const body = document.body;
    if (isDark) {
      body.classList.remove('white-content');
      localStorage.setItem('theme_preference', 'dark');
    } else {
      body.classList.add('white-content');
      localStorage.setItem('theme_preference', 'light');
    }
  },
  // Obtiene la preferencia guardada (por defecto oscuro)
  getStoredTheme() {
    return localStorage.getItem('theme_preference') || 'dark';
  }
};
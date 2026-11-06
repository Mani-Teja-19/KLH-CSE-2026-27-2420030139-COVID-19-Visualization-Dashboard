/* ==========================================================================
   THEME MANAGER (LIGHT / DARK MODE PERSISTENCE)
   ========================================================================== */

(function () {
  const THEME_KEY = 'covid_dashboard_theme';
  
  function getPreferredTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    
    // Update theme toggle icons
    const themeIcons = document.querySelectorAll('.theme-toggle-icon');
    themeIcons.forEach(icon => {
      if (theme === 'dark') {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
      } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
      }
    });

    // Notify Chart.js charts to update colors if function exists
    if (window.updateChartsTheme) {
      window.updateChartsTheme(theme);
    }
  }

  // Initial application
  const currentTheme = getPreferredTheme();
  applyTheme(currentTheme);

  document.addEventListener('DOMContentLoaded', () => {
    const toggleBtns = document.querySelectorAll('.btn-theme-toggle');
    toggleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const activeTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
      });
    });
  });

  window.applyTheme = applyTheme;
})();

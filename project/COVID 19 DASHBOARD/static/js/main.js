/* ==========================================================================
   MAIN CORE APPLICATION SCRIPTS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Sidebar Collapse & Mobile Drawer Toggle
  const sidebar = document.getElementById('appSidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mobileToggle = document.getElementById('mobileSidebarToggle');
  
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
    });

    // Restore sidebar state
    if (localStorage.getItem('sidebar_collapsed') === 'true') {
      sidebar.classList.add('collapsed');
    }
  }

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });

    // Close when clicked outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 992 && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
          sidebar.classList.remove('show');
        }
      }
    });
  }

  // 2. Initialize Bootstrap Tooltips & Popovers
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 3. Mark Notification as Read dynamically
  document.querySelectorAll('.mark-read-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const notifId = this.getAttribute('data-id');
      fetch(`/notifications/${notifId}/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const item = document.getElementById(`notif-item-${notifId}`);
          if (item) {
            item.classList.remove('unread');
            item.style.opacity = '0.6';
          }
          // Decrement badge count
          const badges = document.querySelectorAll('.notif-badge-count');
          badges.forEach(b => {
            let current = parseInt(b.innerText) || 0;
            if (current > 0) b.innerText = current - 1;
            if (current - 1 <= 0) b.style.display = 'none';
          });
        }
      })
      .catch(err => console.error(err));
    });
  });

  // 4. Live Digital Clock in Navbar
  const clockEl = document.getElementById('liveClock');
  if (clockEl) {
    function updateClock() {
      const now = new Date();
      clockEl.innerText = now.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // 5. Password Show / Hide Toggle
  const togglePassBtns = document.querySelectorAll('.toggle-password-btn');
  togglePassBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      const icon = this.querySelector('i');
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          icon.classList.remove('fa-eye');
          icon.classList.add('fa-eye-slash');
        } else {
          input.type = 'password';
          icon.classList.remove('fa-eye-slash');
          icon.classList.add('fa-eye');
        }
      }
    });
  });

  // 6. Generic Table Client Search Filter
  const tableSearchInput = document.getElementById('clientTableSearch');
  if (tableSearchInput) {
    tableSearchInput.addEventListener('keyup', function () {
      const value = this.value.toLowerCase();
      const rows = document.querySelectorAll('.searchable-table tbody tr');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.indexOf(value) > -1 ? '' : 'none';
      });
    });
  }
});

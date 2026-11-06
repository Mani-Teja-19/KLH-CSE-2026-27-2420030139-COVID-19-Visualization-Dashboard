/* ==========================================================================
   DASHBOARD METRICS & NUMBER COUNTER ANIMATIONS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Smooth animated counter function
  function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const isFormatted = obj.getAttribute('data-format') === 'comma';
    
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const easeOutQuad = 1 - Math.pow(1 - progress, 3); // cubic easing
      const current = Math.floor(easeOutQuad * (end - start) + start);
      
      obj.innerHTML = isFormatted ? current.toLocaleString() : current;
      
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        obj.innerHTML = isFormatted ? end.toLocaleString() : end;
      }
    };
    window.requestAnimationFrame(step);
  }

  // Initialize all stat counters with data-count attribute
  const counterElements = document.querySelectorAll('.stat-counter');
  counterElements.forEach(counter => {
    const target = parseInt(counter.getAttribute('data-count'), 10) || 0;
    animateValue(counter, 0, target, 1200);
  });

  // Progress bar animated width fill
  const progressBars = document.querySelectorAll('.progress-bar-animated-fill');
  progressBars.forEach(bar => {
    const targetWidth = bar.getAttribute('data-width') || '0%';
    setTimeout(() => {
      bar.style.width = targetWidth;
      bar.style.transition = 'width 1.2s cubic-bezier(0.16, 1, 0.3, 1)';
    }, 200);
  });
});

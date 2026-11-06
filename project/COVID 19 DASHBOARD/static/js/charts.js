/* ==========================================================================
   CHART.JS ANALYTICS & VISUALIZATION ENGINE
   ========================================================================== */

let dashboardCharts = {};

function isDarkMode() {
  return document.documentElement.getAttribute('data-theme') === 'dark';
}

function getChartColors() {
  const dark = isDarkMode();
  return {
    textColor: dark ? '#94a3b8' : '#64748b',
    gridColor: dark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)',
    cardBg: dark ? '#131b2e' : '#ffffff',
    tooltipBg: dark ? '#1e293b' : '#0f172a',
    tooltipText: '#ffffff'
  };
}

function initDashboardCharts(data) {
  if (!data) return;
  const colors = getChartColors();
  
  // Set global Chart.js defaults
  Chart.defaults.font.family = "'Segoe UI', system-ui, -apple-system, sans-serif";
  Chart.defaults.color = colors.textColor;

  // 1. Affected vs Not Affected Places (Pie Chart)
  const placesPieEl = document.getElementById('placesPieChart');
  if (placesPieEl && data.places_pie) {
    if (dashboardCharts.placesPie) dashboardCharts.placesPie.destroy();
    dashboardCharts.placesPie = new Chart(placesPieEl, {
      type: 'pie',
      data: {
        labels: data.places_pie.labels,
        datasets: [{
          data: data.places_pie.data,
          backgroundColor: data.places_pie.colors,
          borderWidth: 2,
          borderColor: colors.cardBg,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 14, padding: 16 } },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            padding: 12,
            cornerRadius: 8
          }
        }
      }
    });
  }

  // 2. Vaccination Doughnut Chart
  const vaxDoughnutEl = document.getElementById('vaccinationDoughnutChart');
  if (vaxDoughnutEl && data.vaccination_doughnut) {
    if (dashboardCharts.vaxDoughnut) dashboardCharts.vaxDoughnut.destroy();
    dashboardCharts.vaxDoughnut = new Chart(vaxDoughnutEl, {
      type: 'doughnut',
      data: {
        labels: data.vaccination_doughnut.labels,
        datasets: [{
          data: data.vaccination_doughnut.data,
          backgroundColor: data.vaccination_doughnut.colors,
          borderWidth: 3,
          borderColor: colors.cardBg,
          cutout: '68%',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 14, padding: 16 } },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            padding: 12,
            cornerRadius: 8
          }
        }
      }
    });
  }

  // 3. District-wise Cases Multi-Bar Chart
  const districtBarEl = document.getElementById('districtBarChart');
  if (districtBarEl && data.district_bar) {
    if (dashboardCharts.districtBar) dashboardCharts.districtBar.destroy();
    dashboardCharts.districtBar = new Chart(districtBarEl, {
      type: 'bar',
      data: data.district_bar,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, padding: 14 } },
          tooltip: { backgroundColor: colors.tooltipBg, padding: 12, cornerRadius: 8 }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: colors.gridColor }, beginAtZero: true }
        }
      }
    });
  }

  // 4. Daily & Weekly Timeline Trends (Line Chart)
  const trendLineEl = document.getElementById('trendLineChart');
  if (trendLineEl && data.trend_line) {
    if (dashboardCharts.trendLine) dashboardCharts.trendLine.destroy();
    dashboardCharts.trendLine = new Chart(trendLineEl, {
      type: 'line',
      data: {
        labels: data.trend_line.labels,
        datasets: [
          {
            label: 'New Cases',
            data: data.trend_line.cases,
            borderColor: '#0d6efd',
            backgroundColor: 'rgba(13, 110, 253, 0.15)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 7
          },
          {
            label: 'Recoveries',
            data: data.trend_line.recoveries,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 7
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, padding: 14 } },
          tooltip: { backgroundColor: colors.tooltipBg, padding: 12, cornerRadius: 8 }
        },
        scales: {
          x: { grid: { color: colors.gridColor } },
          y: { grid: { color: colors.gridColor }, beginAtZero: true }
        }
      }
    });
  }

  // 5. Top Hotspots (Horizontal Bar)
  const hotspotsBarEl = document.getElementById('hotspotsBarChart');
  if (hotspotsBarEl && data.hotspots_bar) {
    if (dashboardCharts.hotspotsBar) dashboardCharts.hotspotsBar.destroy();
    dashboardCharts.hotspotsBar = new Chart(hotspotsBarEl, {
      type: 'bar',
      data: {
        labels: data.hotspots_bar.labels,
        datasets: [{
          label: 'Total Cases',
          data: data.hotspots_bar.data,
          backgroundColor: data.hotspots_bar.colors,
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { backgroundColor: colors.tooltipBg, padding: 12, cornerRadius: 8 }
        },
        scales: {
          x: { grid: { color: colors.gridColor }, beginAtZero: true },
          y: { grid: { display: false } }
        }
      }
    });
  }

  // 6. Age & Gender Demographics Chart
  const demographicsEl = document.getElementById('demographicsChart');
  if (demographicsEl && data.demographics) {
    if (dashboardCharts.demographics) dashboardCharts.demographics.destroy();
    dashboardCharts.demographics = new Chart(demographicsEl, {
      type: 'bar',
      data: {
        labels: data.demographics.labels,
        datasets: [
          { label: 'Male', data: data.demographics.male, backgroundColor: '#3b82f6', borderRadius: 4 },
          { label: 'Female', data: data.demographics.female, backgroundColor: '#ec4899', borderRadius: 4 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, padding: 14 } },
          tooltip: { backgroundColor: colors.tooltipBg, padding: 12, cornerRadius: 8 }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: colors.gridColor }, beginAtZero: true }
        }
      }
    });
  }

  // 7. Vaccine Brands Distribution Donut
  const vaxBrandsEl = document.getElementById('vaxBrandsChart');
  if (vaxBrandsEl && data.vax_brands) {
    if (dashboardCharts.vaxBrands) dashboardCharts.vaxBrands.destroy();
    dashboardCharts.vaxBrands = new Chart(vaxBrandsEl, {
      type: 'doughnut',
      data: {
        labels: data.vax_brands.labels,
        datasets: [{
          data: data.vax_brands.data,
          backgroundColor: data.vax_brands.colors,
          borderWidth: 2,
          borderColor: colors.cardBg,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 12, padding: 12 } },
          tooltip: { backgroundColor: colors.tooltipBg, padding: 12, cornerRadius: 8 }
        }
      }
    });
  }
}

// Function to download chart as image
function downloadChart(chartId, filename) {
  const canvas = document.getElementById(chartId);
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = `${filename || 'chart'}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

// Listen to theme changes and update chart palette
window.updateChartsTheme = function () {
  if (window.activeChartData) {
    initDashboardCharts(window.activeChartData);
  }
};

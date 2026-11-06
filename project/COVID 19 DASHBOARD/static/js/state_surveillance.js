/* ==========================================================================
   STATE-WISE COVID-19 SURVEILLANCE & VISUALIZATION ENGINE
   Interactive Charts, Filter, Sort, Pagination & Export
   ========================================================================== */

(function () {
  'use strict';

  // Global state for state-wise surveillance
  let stateDataStore = {
    allRows: [],
    filteredRows: [],
    currentState: 'All',
    deathSortOrder: 'default', // 'default', 'highest', 'lowest'
    tableSearch: '',
    tableSortCol: 'state_name',
    tableSortOrder: 'asc',
    currentPage: 1,
    pageSize: 10,
    charts: {
      chart1: null,
      chart2: null,
      chart3: null,
      chart4: null
    }
  };

  function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
      textColor: isDark ? '#94a3b8' : '#64748b',
      titleColor: isDark ? '#f1f5f9' : '#0f172a',
      gridColor: isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(0, 0, 0, 0.06)',
      cardBg: isDark ? '#131b2e' : '#ffffff',
      tooltipBg: isDark ? '#1e293b' : '#0f172a',
      tooltipText: '#ffffff'
    };
  }

  function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    if (typeof num === 'string' && isNaN(Number(num))) return num;
    return Number(num).toLocaleString();
  }

  // Smooth counter animation
  function animateCardNumber(elementId, targetValue) {
    const el = document.getElementById(elementId);
    if (!el) return;

    if (typeof targetValue === 'string') {
      el.textContent = targetValue;
      return;
    }

    const startVal = parseInt(el.getAttribute('data-current') || '0', 10);
    const endVal = Number(targetValue) || 0;
    el.setAttribute('data-current', endVal);

    if (startVal === endVal) {
      el.textContent = endVal.toLocaleString();
      return;
    }

    const duration = 600;
    let startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(ease * (endVal - startVal) + startVal);
      el.textContent = current.toLocaleString();
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        el.textContent = endVal.toLocaleString();
      }
    }
    window.requestAnimationFrame(step);
  }

  // =========================================================================
  // 1. UPDATE SUMMARY CARDS DYNAMICALLY
  // =========================================================================
  function updateSummaryCards(summary) {
    if (!summary) return;

    animateCardNumber('cardStatePopulation', summary.total_population);
    animateCardNumber('cardStateAffected', summary.affected);
    animateCardNumber('cardStateNonAffected', summary.non_affected);
    animateCardNumber('cardStateActive', summary.active);
    animateCardNumber('cardStateRecovered', summary.recovered);
    animateCardNumber('cardStateDeaths', summary.deaths);

    // Vaccination Cards (handle unavailable data gracefully)
    const vaxEl = document.getElementById('cardStateVaccinated');
    const nonVaxEl = document.getElementById('cardStateNonVaccinated');
    
    if (summary.vaccination_data_available && summary.vaccinated !== null) {
      animateCardNumber('cardStateVaccinated', summary.vaccinated);
      animateCardNumber('cardStateNonVaccinated', summary.non_vaccinated);
    } else {
      if (vaxEl) {
        vaxEl.innerHTML = '<span class="badge bg-secondary-subtle text-secondary border px-2 py-1 fs-6">Not Available</span>';
      }
      if (nonVaxEl) {
        nonVaxEl.innerHTML = '<span class="badge bg-secondary-subtle text-secondary border px-2 py-1 fs-6">Not Available</span>';
      }
    }

    // Update scope pill
    const scopeEl = document.getElementById('activeStateScopeBadge');
    if (scopeEl) {
      scopeEl.textContent = summary.is_all_states ? 'All 36 States & UTs' : summary.state_name;
    }

    // Update rates in KPI badges if present
    const recRateEl = document.getElementById('badgeRecoveryRate');
    if (recRateEl && summary.recovery_rate !== undefined) {
      recRateEl.textContent = `${summary.recovery_rate}% Recovery`;
    }
    const deathRateEl = document.getElementById('badgeDeathRate');
    if (deathRateEl && summary.death_rate !== undefined) {
      deathRateEl.textContent = `${summary.death_rate}% Fatality`;
    }
  }

  // =========================================================================
  // 2. CHART RENDERING & UPDATING
  // =========================================================================

  // Chart 1: State-wise Affected vs Non-Affected (Bar Chart)
  function renderChart1(data) {
    const ctx = document.getElementById('stateAffectedVsNonAffectedChart');
    if (!ctx || !data) return;

    const colors = getThemeColors();
    if (stateDataStore.charts.chart1) {
      stateDataStore.charts.chart1.destroy();
    }

    stateDataStore.charts.chart1 = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: data.datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 14, color: colors.textColor, font: { weight: '600' } }
          },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function (context) {
                return ` ${context.dataset.label}: ${context.parsed.y.toLocaleString()} people`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: colors.textColor,
              maxRotation: 45,
              minRotation: data.labels.length > 5 ? 45 : 0,
              font: { size: data.labels.length > 15 ? 10 : 12 }
            }
          },
          y: {
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textColor,
              callback: function (val) {
                if (val >= 1e7) return (val / 1e6).toFixed(0) + 'M';
                if (val >= 1e5) return (val / 1e3).toFixed(0) + 'K';
                return val.toLocaleString();
              }
            },
            title: {
              display: true,
              text: 'Number of People',
              color: colors.textColor,
              font: { weight: '600' }
            }
          }
        }
      }
    });
  }

  // Chart 2: State-wise Deaths (Bar Chart, with sorting)
  function renderChart2(data) {
    const ctx = document.getElementById('stateDeathsChart');
    if (!ctx || !data) return;

    const colors = getThemeColors();
    if (stateDataStore.charts.chart2) {
      stateDataStore.charts.chart2.destroy();
    }

    stateDataStore.charts.chart2 = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: data.datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 14, color: colors.textColor, font: { weight: '600' } }
          },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function (context) {
                return ` Fatalities: ${context.parsed.y.toLocaleString()} deaths`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: colors.textColor,
              maxRotation: 45,
              minRotation: data.labels.length > 5 ? 45 : 0,
              font: { size: data.labels.length > 15 ? 10 : 12 }
            }
          },
          y: {
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textColor,
              callback: function (val) {
                if (val >= 1e5) return (val / 1e3).toFixed(0) + 'K';
                return val.toLocaleString();
              }
            },
            title: {
              display: true,
              text: 'Total Deaths',
              color: colors.textColor,
              font: { weight: '600' }
            }
          }
        }
      }
    });
  }

  // Chart 3: State-wise Active vs Recovered (Grouped Bar Chart)
  function renderChart3(data) {
    const ctx = document.getElementById('stateActiveVsRecoveredChart');
    if (!ctx || !data) return;

    const colors = getThemeColors();
    if (stateDataStore.charts.chart3) {
      stateDataStore.charts.chart3.destroy();
    }

    stateDataStore.charts.chart3 = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: data.datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 14, color: colors.textColor, font: { weight: '600' } }
          },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function (context) {
                return ` ${context.dataset.label}: ${context.parsed.y.toLocaleString()} cases`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: colors.textColor,
              maxRotation: 45,
              minRotation: data.labels.length > 5 ? 45 : 0,
              font: { size: data.labels.length > 15 ? 10 : 12 }
            }
          },
          y: {
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textColor,
              callback: function (val) {
                if (val >= 1e6) return (val / 1e6).toFixed(1) + 'M';
                if (val >= 1e3) return (val / 1e3).toFixed(0) + 'K';
                return val.toLocaleString();
              }
            },
            title: {
              display: true,
              text: 'Cases Count',
              color: colors.textColor,
              font: { weight: '600' }
            }
          }
        }
      }
    });
  }

  // Chart 4: Vaccinated vs Non-Vaccinated (Doughnut Chart or Unavailable Notice)
  function renderChart4(data) {
    const containerEl = document.getElementById('stateVaccinationChartContainer');
    const canvasEl = document.getElementById('stateVaccinationDoughnutChart');
    const emptyNoticeEl = document.getElementById('stateVaccinationEmptyNotice');
    if (!containerEl) return;

    if (stateDataStore.charts.chart4) {
      stateDataStore.charts.chart4.destroy();
      stateDataStore.charts.chart4 = null;
    }

    if (data && data.available) {
      // Genuine data available -> show canvas, hide notice
      if (emptyNoticeEl) emptyNoticeEl.style.display = 'none';
      if (canvasEl) {
        canvasEl.style.display = 'block';
        const colors = getThemeColors();
        stateDataStore.charts.chart4 = new Chart(canvasEl, {
          type: 'doughnut',
          data: {
            labels: data.labels,
            datasets: data.datasets
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
                labels: { boxWidth: 14, color: colors.textColor }
              },
              tooltip: {
                backgroundColor: colors.tooltipBg,
                padding: 12,
                cornerRadius: 8,
                callbacks: {
                  label: function (context) {
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const pct = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                    return ` ${context.label}: ${context.raw.toLocaleString()} (${pct}%)`;
                  }
                }
              }
            },
            cutout: '65%'
          }
        });
      }
    } else {
      // Vaccination data NOT available -> show genuine informative notice
      if (canvasEl) canvasEl.style.display = 'none';
      if (emptyNoticeEl) emptyNoticeEl.style.display = 'flex';
    }
  }

  function updateAllCharts(chartsData) {
    if (!chartsData) return;
    renderChart1(chartsData.chart1_affected_vs_non_affected);
    renderChart2(chartsData.chart2_deaths);
    renderChart3(chartsData.chart3_active_vs_recovered);
    renderChart4(chartsData.chart4_vaccination);
  }

  // =========================================================================
  // 3. RESPONSIVE DATA TABLE WITH SEARCH, SORT, PAGINATION & TOTALS
  // =========================================================================

  function renderTable() {
    const tbody = document.getElementById('stateDataTableBody');
    const tfoot = document.getElementById('stateDataTableFoot');
    const infoEl = document.getElementById('stateTablePaginationInfo');
    const navEl = document.getElementById('stateTablePaginationNav');
    if (!tbody) return;

    // Filter by search string
    let filtered = stateDataStore.allRows;
    if (stateDataStore.currentState && stateDataStore.currentState !== 'All') {
      filtered = filtered.filter(
        r => r.state_name.toLowerCase() === stateDataStore.currentState.toLowerCase()
      );
    }
    if (stateDataStore.tableSearch.trim()) {
      const q = stateDataStore.tableSearch.trim().toLowerCase();
      filtered = filtered.filter(r => r.state_name.toLowerCase().includes(q));
    }

    // Sort
    const col = stateDataStore.tableSortCol;
    const rev = stateDataStore.tableSortOrder === 'desc';
    filtered.sort((a, b) => {
      const valA = a[col];
      const valB = b[col];
      if (typeof valA === 'string') {
        return rev ? valB.localeCompare(valA) : valA.localeCompare(valB);
      }
      return rev ? (valB - valA) : (valA - valB);
    });

    stateDataStore.filteredRows = filtered;

    // Pagination
    const totalItems = filtered.length;
    const pageSize = stateDataStore.pageSize === 'all' ? totalItems : parseInt(stateDataStore.pageSize, 10);
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
    if (stateDataStore.currentPage > totalPages) stateDataStore.currentPage = totalPages;
    const startIdx = (stateDataStore.currentPage - 1) * pageSize;
    const pageRows = filtered.slice(startIdx, startIdx + pageSize);

    // Build Table Body
    if (pageRows.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="9" class="text-center py-5 text-muted">
            <i class="fa-solid fa-folder-open fs-2 mb-2 d-block"></i>
            No matching states or union territories found.
          </td>
        </tr>
      `;
    } else {
      let html = '';
      pageRows.forEach((r, idx) => {
        const vaxContent = r.vaccination_data_available && r.vaccinated !== null
          ? Number(r.vaccinated).toLocaleString()
          : '<span class="badge bg-secondary-subtle text-secondary border">Not Available</span>';

        const nonVaxContent = r.vaccination_data_available && r.non_vaccinated !== null
          ? Number(r.non_vaccinated).toLocaleString()
          : '<span class="badge bg-secondary-subtle text-secondary border">Not Available</span>';

        html += `
          <tr>
            <td class="fw-bold">
              <span class="text-primary-emphasis">${escapeHtml(r.state_name)}</span>
              <span class="badge bg-body-tertiary text-muted ms-1 small" style="font-size: 0.7rem;">${escapeHtml(r.zone || '')}</span>
            </td>
            <td class="text-end fw-semibold">${Number(r.population).toLocaleString()}</td>
            <td class="text-end text-danger fw-semibold">${Number(r.affected).toLocaleString()}</td>
            <td class="text-end text-info fw-semibold">${Number(r.non_affected).toLocaleString()}</td>
            <td class="text-end text-warning fw-semibold">${Number(r.active).toLocaleString()}</td>
            <td class="text-end text-success fw-semibold">${Number(r.recovered).toLocaleString()}</td>
            <td class="text-end text-danger fw-bold">${Number(r.deaths).toLocaleString()}</td>
            <td class="text-center">${vaxContent}</td>
            <td class="text-center">${nonVaxContent}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // Build Totals Footer Row
    if (tfoot) {
      const sumPop = filtered.reduce((s, r) => s + (Number(r.population) || 0), 0);
      const sumAff = filtered.reduce((s, r) => s + (Number(r.affected) || 0), 0);
      const sumNonAff = filtered.reduce((s, r) => s + (Number(r.non_affected) || 0), 0);
      const sumAct = filtered.reduce((s, r) => s + (Number(r.active) || 0), 0);
      const sumRec = filtered.reduce((s, r) => s + (Number(r.recovered) || 0), 0);
      const sumDth = filtered.reduce((s, r) => s + (Number(r.deaths) || 0), 0);

      tfoot.innerHTML = `
        <tr class="table-group-divider fw-bold bg-body-tertiary">
          <td>
            <div class="d-flex align-items-center gap-2">
              <i class="fa-solid fa-calculator text-primary"></i>
              <span>${filtered.length > 1 ? 'Total / National Summary' : 'State Total'}</span>
            </div>
          </td>
          <td class="text-end text-dark">${sumPop.toLocaleString()}</td>
          <td class="text-end text-danger">${sumAff.toLocaleString()}</td>
          <td class="text-end text-info">${sumNonAff.toLocaleString()}</td>
          <td class="text-end text-warning">${sumAct.toLocaleString()}</td>
          <td class="text-end text-success">${sumRec.toLocaleString()}</td>
          <td class="text-end text-danger">${sumDth.toLocaleString()}</td>
          <td class="text-center text-muted small"><span class="badge bg-secondary-subtle text-secondary border">Not Available</span></td>
          <td class="text-center text-muted small"><span class="badge bg-secondary-subtle text-secondary border">Not Available</span></td>
        </tr>
      `;
    }

    // Update Pagination Info
    if (infoEl) {
      if (totalItems === 0) {
        infoEl.textContent = 'Showing 0 of 0 entries';
      } else {
        const endIdx = Math.min(startIdx + pageSize, totalItems);
        infoEl.textContent = `Showing ${startIdx + 1} to ${endIdx} of ${totalItems} entries`;
      }
    }

    // Build Pagination Buttons
    if (navEl) {
      if (totalPages <= 1) {
        navEl.innerHTML = '';
      } else {
        let pBtnHtml = '';
        // Previous
        pBtnHtml += `
          <li class="page-item ${stateDataStore.currentPage === 1 ? 'disabled' : ''}">
            <button class="page-link" onclick="window.stateSurveillance.setPage(${stateDataStore.currentPage - 1})">&laquo; Prev</button>
          </li>
        `;
        // Page numbers
        for (let p = 1; p <= totalPages; p++) {
          pBtnHtml += `
            <li class="page-item ${stateDataStore.currentPage === p ? 'active' : ''}">
              <button class="page-link" onclick="window.stateSurveillance.setPage(${p})">${p}</button>
            </li>
          `;
        }
        // Next
        pBtnHtml += `
          <li class="page-item ${stateDataStore.currentPage === totalPages ? 'disabled' : ''}">
            <button class="page-link" onclick="window.stateSurveillance.setPage(${stateDataStore.currentPage + 1})">Next &raquo;</button>
          </li>
        `;
        navEl.innerHTML = pBtnHtml;
      }
    }

    // Update sort header icons
    updateSortIcons();
  }

  function updateSortIcons() {
    const headers = document.querySelectorAll('.state-sortable-th');
    headers.forEach(th => {
      const col = th.getAttribute('data-col');
      const icon = th.querySelector('.sort-icon');
      if (icon) {
        if (col === stateDataStore.tableSortCol) {
          icon.className = stateDataStore.tableSortOrder === 'asc'
            ? 'fa-solid fa-sort-up sort-icon text-primary'
            : 'fa-solid fa-sort-down sort-icon text-primary';
        } else {
          icon.className = 'fa-solid fa-sort sort-icon text-muted opacity-50';
        }
      }
    });
  }

  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // =========================================================================
  // 4. MAIN STATE SELECTION CONTROLLER
  // =========================================================================
  async function selectState(stateName) {
    stateDataStore.currentState = stateName || 'All';

    // Show subtle loading state if needed
    const selectEl = document.getElementById('stateFilterSelect');
    if (selectEl && selectEl.value !== stateDataStore.currentState) {
      selectEl.value = stateDataStore.currentState;
    }

    try {
      const url = `/api/states/data?state=${encodeURIComponent(stateDataStore.currentState)}&sort_deaths=${stateDataStore.deathSortOrder}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Network response was not ok');
      const payload = await response.json();

      // 1. Update Cards
      updateSummaryCards(payload.summary);

      // 2. Update Charts
      updateAllCharts(payload.charts);

      // 3. Update Table
      if (payload.table && payload.table.rows) {
        if (stateDataStore.currentState === 'All') {
          stateDataStore.allRows = payload.table.rows;
        }
        stateDataStore.currentPage = 1;
        renderTable();
      }
    } catch (err) {
      console.error('Error fetching state data:', err);
    }
  }

  // Sort Chart 2 Deaths
  async function toggleDeathSort(order) {
    stateDataStore.deathSortOrder = order;
    
    // Update active button indicator
    const btnGroup = document.getElementById('deathSortBtnGroup');
    if (btnGroup) {
      btnGroup.querySelectorAll('button').forEach(btn => {
        if (btn.getAttribute('data-sort') === order) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    try {
      const url = `/api/states/charts?state=${encodeURIComponent(stateDataStore.currentState)}&sort_deaths=${order}`;
      const res = await fetch(url);
      const charts = await res.json();
      renderChart2(charts.chart2_deaths);
    } catch (e) {
      console.error('Error sorting deaths chart:', e);
    }
  }

  // Sync Dataset
  async function syncDataset() {
    const btn = document.getElementById('syncDatasetBtn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Syncing...';
    }

    try {
      const res = await fetch('/api/states/import', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast(`Dataset synced successfully! ${data.total_states} states verified from ${data.source_file}.`, 'success');
        // Refresh view
        await selectState(stateDataStore.currentState);
      } else {
        showToast(`Sync failed: ${data.error}`, 'danger');
      }
    } catch (e) {
      showToast('Error connecting to server for sync.', 'danger');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-arrows-rotate me-1"></i> Sync Dataset';
      }
    }
  }

  function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('appToastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} shadow-lg rounded-3 py-2 px-3 mb-2 d-flex align-items-center gap-2 animate-fade-in`;
    toast.style.minWidth = '280px';
    toast.innerHTML = `
      <i class="fa-solid ${type === 'success' ? 'fa-circle-check text-success' : 'fa-circle-exclamation text-danger'}"></i>
      <span class="flex-grow-1 small">${escapeHtml(message)}</span>
      <button type="button" class="btn-close btn-close-sm" onclick="this.parentElement.remove()"></button>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      if (toast.parentElement) toast.remove();
    }, 4500);
  }

  function createToastContainer() {
    const cont = document.createElement('div');
    cont.id = 'appToastContainer';
    cont.style.position = 'fixed';
    cont.style.top = '20px';
    cont.style.right = '20px';
    cont.style.zIndex = '9999';
    document.body.appendChild(cont);
    return cont;
  }

  // =========================================================================
  // 5. INITIALIZATION
  // =========================================================================
  function initStateSurveillance(initData) {
    if (!initData) return;

    if (initData.table && initData.table.rows) {
      stateDataStore.allRows = initData.table.rows;
    }

    // Render initial charts
    if (initData.charts) {
      updateAllCharts(initData.charts);
    }

    // Render initial table
    renderTable();

    // Bind State Filter Dropdown
    const stateFilterSelect = document.getElementById('stateFilterSelect');
    if (stateFilterSelect) {
      stateFilterSelect.addEventListener('change', (e) => {
        selectState(e.target.value);
      });
    }

    // Bind Table Search Input
    const tableSearchInput = document.getElementById('stateTableSearch');
    if (tableSearchInput) {
      tableSearchInput.addEventListener('input', (e) => {
        stateDataStore.tableSearch = e.target.value;
        stateDataStore.currentPage = 1;
        renderTable();
      });
    }

    // Bind Page Size Selector
    const pageSizeSelect = document.getElementById('statePageSizeSelect');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', (e) => {
        stateDataStore.pageSize = e.target.value;
        stateDataStore.currentPage = 1;
        renderTable();
      });
    }

    // Bind Sortable Column Headers
    const sortHeaders = document.querySelectorAll('.state-sortable-th');
    sortHeaders.forEach(th => {
      th.addEventListener('click', () => {
        const col = th.getAttribute('data-col');
        if (stateDataStore.tableSortCol === col) {
          stateDataStore.tableSortOrder = stateDataStore.tableSortOrder === 'asc' ? 'desc' : 'asc';
        } else {
          stateDataStore.tableSortCol = col;
          stateDataStore.tableSortOrder = 'asc';
        }
        renderTable();
      });
    });

    // Re-render charts on theme change
    window.addEventListener('themeChanged', () => {
      if (initData.charts) {
        selectState(stateDataStore.currentState);
      }
    });
  }

  // Expose public API to window for inline onclick handlers
  window.stateSurveillance = {
    init: initStateSurveillance,
    selectState: selectState,
    toggleDeathSort: toggleDeathSort,
    syncDataset: syncDataset,
    setPage: function (page) {
      stateDataStore.currentPage = page;
      renderTable();
    },
    exportExcel: function () {
      const state = stateDataStore.currentState;
      window.location.href = `/api/states/export/excel?state=${encodeURIComponent(state)}`;
    },
    exportCSV: function () {
      const state = stateDataStore.currentState;
      window.location.href = `/api/states/export/csv?state=${encodeURIComponent(state)}`;
    }
  };

})();


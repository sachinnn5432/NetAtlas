/**
 * NetAtlas Main Application Coordinator
 * Handles tab navigation, KPI metrics bar updates, and lifecycle initializations.
 */

const NetAtlasApp = {
  currentView: 'map-view',

  init() {
    this.bindNavigation();
    this.fetchOverviewKPIs();

    // Initialize sub-controllers
    MapController.init();
    CatalogController.init();
    AnalyticsController.init();
  },

  bindNavigation() {
    const tabs = document.querySelectorAll('.nav-tab-btn');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetViewId = tab.dataset.view;
        if (!targetViewId) return;

        // Update active tab button
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Toggle views
        document.querySelectorAll('.content-view').forEach(v => v.classList.remove('active-view'));
        const mapCanvas = document.querySelector('.map-canvas-container');

        if (targetViewId === 'map-view') {
          mapCanvas.style.display = 'block';
          MapController.map.invalidateSize();
        } else {
          mapCanvas.style.display = 'none';
          const targetEl = document.getElementById(targetViewId);
          if (targetEl) targetEl.classList.add('active-view');
        }

        this.currentView = targetViewId;
      });
    });
  },

  fetchOverviewKPIs() {
    fetch('/api/v1/overview')
      .then(r => r.json())
      .then(res => {
        const d = res.data || {};
        document.getElementById('kpi-cables').innerText = (d.total_submarine_cables || 0).toLocaleString();
        document.getElementById('kpi-landings').innerText = (d.total_landing_stations || 0).toLocaleString();
        document.getElementById('kpi-ixps').innerText = (d.total_ixps || 0).toLocaleString();
        document.getElementById('kpi-facilities').innerText = (d.total_facilities || 0).toLocaleString();
      })
      .catch(err => console.error('Failed fetching overview KPIs:', err));
  }
};

document.addEventListener('DOMContentLoaded', () => {
  NetAtlasApp.init();
});


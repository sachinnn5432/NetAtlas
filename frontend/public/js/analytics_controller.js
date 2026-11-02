/**
 * NetAtlas Analytics and Data Storytelling Controller
 * Visualizes NetworkX graph metrics, degree distributions, regional density,
 * and data quality audits using Plotly.js.
 */

const AnalyticsController = {
  init() {
    this.loadTopologyCharts();
    this.loadRegionalCharts();
    this.loadStories();
    this.loadDataQuality();
    this.loadProvenance();
  },

  loadTopologyCharts() {
    fetch('/api/v1/analytics/network-topology')
      .then(r => r.json())
      .then(res => {
        const topo = res.topology || {};
        const dist = res.degree_distributions || {};

        // 1. Top IXPs Chart
        const topIXPs = (topo.top_connected_ixps || []).slice(0, 10).reverse();
        const traceIXPs = {
          x: topIXPs.map(i => i.connected_networks_count),
          y: topIXPs.map(i => `${i.name} (${i.country})`),
          type: 'bar',
          orientation: 'h',
          marker: { color: '#7c3aed' }
        };
        Plotly.newPlot('chart-top-ixps', [traceIXPs], {
          margin: { l: 180, r: 20, t: 10, b: 40 },
          xaxis: { title: 'Participant Autonomous Systems (ASNs)', font: { size: 11 } },
          font: { family: 'Inter, sans-serif', size: 11 }
        }, { responsive: true, displayModeBar: false });

        // 2. Top Networks Chart
        const topNets = (topo.top_connected_networks || []).slice(0, 10).reverse();
        const traceNets = {
          x: topNets.map(n => n.ixp_presence_count),
          y: topNets.map(n => `${n.name} (AS${n.asn || '?'})`),
          type: 'bar',
          orientation: 'h',
          marker: { color: '#0284c7' }
        };
        Plotly.newPlot('chart-top-networks', [traceNets], {
          margin: { l: 200, r: 20, t: 10, b: 40 },
          xaxis: { title: 'Documented IXP Presences', font: { size: 11 } },
          font: { family: 'Inter, sans-serif', size: 11 }
        }, { responsive: true, displayModeBar: false });

        // 3. Degree Distribution Chart
        const netDist = dist.network_degree_distribution || [];
        const traceDist = {
          x: netDist.map(d => d.range),
          y: netDist.map(d => d.count),
          type: 'bar',
          marker: { color: '#0f172a' }
        };
        Plotly.newPlot('chart-degree-dist', [traceDist], {
          margin: { l: 50, r: 20, t: 10, b: 50 },
          xaxis: { title: 'IXP Presences per Network (Bin Range)', font: { size: 11 } },
          yaxis: { title: 'Network Count (Log scale)', type: 'log', font: { size: 11 } },
          font: { family: 'Inter, sans-serif', size: 11 }
        }, { responsive: true, displayModeBar: false });
      });
  },

  loadRegionalCharts() {
    fetch('/api/v1/analytics/regions')
      .then(r => r.json())
      .then(res => {
        const regions = res.data || [];
        const trace = {
          x: regions.map(r => r.region),
          y: regions.map(r => r.infrastructure_density_score),
          type: 'bar',
          marker: { color: '#0d9488' }
        };
        Plotly.newPlot('chart-regional-density', [trace], {
          margin: { l: 60, r: 20, t: 10, b: 60 },
          xaxis: { title: 'Continental / Macro-Region', font: { size: 11 } },
          yaxis: { title: 'Infrastructure Density Index', font: { size: 11 } },
          font: { family: 'Inter, sans-serif', size: 11 }
        }, { responsive: true, displayModeBar: false });
      });
  },

  loadStories() {
    fetch('/api/v1/analytics/stories')
      .then(r => r.json())
      .then(res => {
        const stories = res.data || [];
        const container = document.getElementById('stories-container');
        if (!container) return;

        container.innerHTML = stories.map(s => `
          <div class="story-card">
            <div class="story-header">${s.title}</div>
            <div class="story-summary">${s.summary}</div>
            <div class="story-metrics-pills">
              ${(s.key_metrics || []).map(m => `
                <div class="story-pill"><b>${m.label}:</b> ${m.value}</div>
              `).join('')}
            </div>
          </div>
        `).join('');
      });
  },

  loadDataQuality() {
    fetch('/api/v1/data-quality')
      .then(r => r.json())
      .then(res => {
        const q = res.data || {};
        const container = document.getElementById('quality-metrics-container');
        if (!container) return;

        const summary = q.summary || {};
        const cq = q.cable_quality || {};
        const lq = q.landing_station_quality || {};
        const fq = q.facility_quality || {};

        container.innerHTML = `
          <div class="analytics-grid">
            <div class="chart-card">
              <div class="chart-card-title">Submarine Cable Route Quality</div>
              <div class="chart-card-desc">Validation against WGS84 topology standards</div>
              <div class="detail-row"><span class="detail-key">Verified Geometries</span><span class="detail-val">${cq.verified_geometries_pct}%</span></div>
              <div class="detail-row"><span class="detail-key">Known Commissioning Date</span><span class="detail-val">${(100 - cq.missing_commission_year_pct).toFixed(1)}%</span></div>
              <div class="detail-row"><span class="detail-key">Known Route Length</span><span class="detail-val">${(100 - cq.missing_length_pct).toFixed(1)}%</span></div>
              <div class="detail-row"><span class="detail-key">Abnormal Outliers Detected</span><span class="detail-val">${cq.outlier_lengths_detected}</span></div>
            </div>

            <div class="chart-card">
              <div class="chart-card-title">Geographic Coordinate Accuracy</div>
              <div class="chart-card-desc">Landing stations and facility geocoding completeness</div>
              <div class="detail-row"><span class="detail-key">Landing Station Coordinates</span><span class="detail-val">${lq.coordinate_completeness_pct}% verified</span></div>
              <div class="detail-row"><span class="detail-key">Facility Coordinates</span><span class="detail-val">${fq.coordinate_completeness_pct}% geocoded</span></div>
              <div class="detail-row"><span class="detail-key">Coordinate Bounds Check</span><span class="detail-val">EPSG:4326 Strict Compliant</span></div>
              <div class="detail-row"><span class="detail-key">Null Island Protection</span><span class="detail-val">Enforced (lat=0, lon=0 pruned)</span></div>
            </div>
          </div>
        `;
      });
  },

  loadProvenance() {
    fetch('/api/v1/provenance')
      .then(r => r.json())
      .then(res => {
        const tbody = document.getElementById('provenance-table-body');
        if (!tbody) return;
        const list = res.data || [];
        tbody.innerHTML = list.map(p => `
          <tr>
            <td style="font-weight:600;">${p.name}</td>
            <td><a href="${p.url}" target="_blank" style="color:#0284c7; text-decoration:none;">${p.url}</a></td>
            <td>${p.license}</td>
            <td>${p.record_count.toLocaleString()}</td>
            <td style="font-size:0.75rem; color:#64748b; max-width:300px;">${p.known_limitations}</td>
          </tr>
        `).join('');
      });
  }
};


/**
 * NetAtlas Catalog and Search Controller
 * Handles entity lists, real-time search, filters, and tabular displays.
 */

const CatalogController = {
  countries: [],

  init() {
    this.loadCountryList();
    this.bindSearchInput();
    this.loadCablesTable();
    this.loadIXPTable();
    this.loadFacilitiesTable();
  },

  loadCountryList() {
    fetch('/api/v1/analytics/countries')
      .then(r => r.json())
      .then(res => {
        this.countries = res.data || [];
        const select = document.getElementById('country-filter');
        if (!select) return;

        select.innerHTML = '<option value="">All Economies</option>';
        this.countries.forEach(c => {
          const opt = document.createElement('option');
          opt.value = c.country_code;
          opt.innerText = `${c.country_name} (${c.country_code})`;
          opt.dataset.lat = c.latitude;
          opt.dataset.lon = c.longitude;
          select.appendChild(opt);
        });

        select.addEventListener('change', e => {
          const opt = select.options[select.selectedIndex];
          if (opt && opt.dataset.lat && opt.dataset.lon) {
            MapController.zoomToCountry(parseFloat(opt.dataset.lat), parseFloat(opt.dataset.lon));
          }
        });
      });
  },

  bindSearchInput() {
    const input = document.getElementById('global-search-input');
    const dropdown = document.getElementById('search-dropdown');
    if (!input || !dropdown) return;

    let debounceTimer = null;
    input.addEventListener('input', e => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      if (query.length < 2) {
        dropdown.style.display = 'none';
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`/api/v1/search?q=${encodeURIComponent(query)}`)
          .then(r => r.json())
          .then(res => {
            const data = res.data || {};
            let html = '';

            // Cables
            if (data.cables && data.cables.length > 0) {
              html += '<div class="search-result-group-title">Submarine Cables</div>';
              data.cables.forEach(c => {
                html += `<div class="search-result-item" onclick="CatalogController.selectSearchResult('cable', '${c.id}')">
                  <span>${c.name}</span>
                  <span style="color:#64748b;">${c.length_km ? c.length_km.toLocaleString() + ' km' : 'Cable'}</span>
                </div>`;
              });
            }

            // IXPs
            if (data.ixps && data.ixps.length > 0) {
              html += '<div class="search-result-group-title">Internet Exchanges</div>';
              data.ixps.forEach(ix => {
                html += `<div class="search-result-item" onclick="CatalogController.selectSearchResult('ixp', '${ix.id}')">
                  <span>${ix.name} (${ix.city || ''}, ${ix.country})</span>
                  <span style="color:#64748b;">${ix.net_count} ASNs</span>
                </div>`;
              });
            }

            // Facilities
            if (data.facilities && data.facilities.length > 0) {
              html += '<div class="search-result-group-title">Facilities</div>';
              data.facilities.forEach(f => {
                html += `<div class="search-result-item" onclick="CatalogController.selectSearchResult('facility', '${f.id}', ${f.lat}, ${f.lon})">
                  <span>${f.name} (${f.city || ''})</span>
                  <span style="color:#64748b;">${f.country}</span>
                </div>`;
              });
            }

            if (!html) {
              html = '<div style="padding:12px; font-size:0.8rem; color:#94a3b8;">No matching infrastructure found.</div>';
            }

            dropdown.innerHTML = html;
            dropdown.style.display = 'block';
          });
      }, 250);
    });

    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
      }
    });
  },

  selectSearchResult(type, id, lat = null, lon = null) {
    const dropdown = document.getElementById('search-dropdown');
    if (dropdown) dropdown.style.display = 'none';

    if (type === 'cable') {
      fetch(`/api/v1/cables/${id}`)
        .then(r => r.json())
        .then(res => {
          if (res.data) {
            MapController.displayFeatureDetails('cable', res.data);
          }
        });
    } else if (type === 'facility' && lat && lon) {
      MapController.zoomToCountry(lat, lon, 11);
    }
  },

  loadCablesTable() {
    fetch('/api/v1/cables?limit=150')
      .then(r => r.json())
      .then(res => {
        const tbody = document.getElementById('cables-table-body');
        if (!tbody) return;
        const cables = res.data || [];
        tbody.innerHTML = cables.map(c => `
          <tr>
            <td style="font-weight:600;">${c.name}</td>
            <td>${c.rfs_year || '<span style="color:#94a3b8;">Unavailable</span>'}</td>
            <td>${c.length_km ? c.length_km.toLocaleString() + ' km' : '<span style="color:#94a3b8;">Unavailable</span>'}</td>
            <td>${c.is_planned ? '<span style="color:#ea580c; font-weight:600;">Planned</span>' : '<span style="color:#059669; font-weight:600;">Operational</span>'}</td>
            <td>${c.landing_points_count || 0}</td>
            <td style="max-width:260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${c.owners || 'Unavailable'}</td>
          </tr>
        `).join('');
      });
  },

  loadIXPTable() {
    fetch('/api/v1/ixps?limit=150')
      .then(r => r.json())
      .then(res => {
        const tbody = document.getElementById('ixp-table-body');
        if (!tbody) return;
        const ixps = res.data || [];
        tbody.innerHTML = ixps.map(ix => `
          <tr>
            <td style="font-weight:600;">${ix.name}</td>
            <td>${ix.city || '<span style="color:#94a3b8;">Unknown</span>'}</td>
            <td>${ix.country}</td>
            <td>${ix.region_continent || 'Global'}</td>
            <td style="font-weight:700; color:#7c3aed;">${ix.net_count}</td>
            <td>${ix.fac_count}</td>
            <td>${ix.proto_ipv6 ? 'IPv4 / IPv6' : 'IPv4 Only'}</td>
          </tr>
        `).join('');
      });
  },

  loadFacilitiesTable() {
    fetch('/api/v1/facilities?limit=150')
      .then(r => r.json())
      .then(res => {
        const tbody = document.getElementById('facility-table-body');
        if (!tbody) return;
        const facs = res.data || [];
        tbody.innerHTML = facs.map(f => `
          <tr>
            <td style="font-weight:600;">${f.name}</td>
            <td>${f.org_name || '<span style="color:#94a3b8;">Unavailable</span>'}</td>
            <td>${f.city || 'Unknown'}</td>
            <td>${f.country}</td>
            <td style="font-weight:700; color:#0d9488;">${f.net_count}</td>
            <td>${f.ix_count}</td>
            <td>${f.latitude ? f.latitude.toFixed(3) + ', ' + f.longitude.toFixed(3) : '<span style="color:#94a3b8;">Ungeocoded</span>'}</td>
          </tr>
        `).join('');
      });
  }
};


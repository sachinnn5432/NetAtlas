/**
 * NetAtlas Map Controller
 * Manages Leaflet GIS canvas, vector submarine cable layers, landing stations,
 * IXP points, and facility clusters.
 */

const MapController = {
  map: null,
  cableLayer: null,
  landingLayer: null,
  ixpLayer: null,
  facilityLayer: null,
  markerClusterGroup: null,

  init() {
    // Center on zero-meridian oceanic view
    this.map = L.map('map', {
      center: [20.0, 10.0],
      zoom: 3,
      minZoom: 2,
      maxZoom: 18,
      worldCopyJump: true,
      preferCanvas: true
    });

    // OpenStreetMap Standard Basemap (Reliable, publicly accessible, no API key required)
    const baseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
    });

    baseLayer.on('tileerror', (error) => {
      console.warn('Map tile failed to load:', error);
    });

    baseLayer.addTo(this.map);

    // Responsive container resize listener
    window.addEventListener('resize', () => {
      if (this.map) {
        this.map.invalidateSize();
      }
    });

    this.markerClusterGroup = L.markerClusterGroup({
      maxClusterRadius: 40,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false
    });
    this.map.addLayer(this.markerClusterGroup);

    this.loadCableRoutes();
    this.loadLandingStations();
    this.loadIXPPoints();
    this.loadFacilityPoints();
    this.bindLayerControls();
  },

  loadCableRoutes() {
    fetch('/api/v1/geojson/cables')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}: Failed to fetch cable routes`);
        return r.json();
      })
      .then(geo => {
        if (!geo || !geo.features || !Array.isArray(geo.features)) {
          console.warn('Empty or invalid cable GeoJSON received.');
          return;
        }
        this.cableLayer = L.geoJSON(geo, {
          style: feature => {
            const isPlanned = feature.properties ? feature.properties.is_planned : false;
            return {
              color: isPlanned ? '#ea580c' : ((feature.properties && feature.properties.color) || '#0284c7'),
              weight: 2,
              opacity: 0.85,
              dashArray: isPlanned ? '4, 4' : null
            };
          },
          onEachFeature: (feature, layer) => {
            layer.on({
              mouseover: e => {
                const l = e.target;
                l.setStyle({ weight: 4, opacity: 1.0 });
              },
              mouseout: e => {
                if (this.cableLayer) this.cableLayer.resetStyle(e.target);
              },
              click: () => {
                if (feature.properties) {
                  this.displayFeatureDetails('cable', feature.properties);
                }
              }
            });
            const name = (feature.properties && feature.properties.name) ? feature.properties.name : 'Unknown Cable';
            layer.bindTooltip(`<b>${name}</b>`, { sticky: true });
          }
        });
        this.map.addLayer(this.cableLayer);
      })
      .catch(err => {
        console.error('Failed loading cable GeoJSON:', err);
      });
  },

  loadLandingStations() {
    fetch('/api/v1/geojson/landing-stations')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}: Failed to fetch landing stations`);
        return r.json();
      })
      .then(geo => {
        if (!geo || !geo.features || !Array.isArray(geo.features)) {
          console.warn('Empty or invalid landing stations GeoJSON received.');
          return;
        }
        this.landingLayer = L.geoJSON(geo, {
          pointToLayer: (feature, latlng) => {
            return L.circleMarker(latlng, {
              radius: 4,
              fillColor: '#2563eb',
              color: '#ffffff',
              weight: 1,
              opacity: 1,
              fillOpacity: 0.9
            });
          },
          onEachFeature: (feature, layer) => {
            layer.on('click', () => {
              if (feature.properties) {
                this.displayFeatureDetails('landing', feature.properties);
              }
            });
            const name = (feature.properties && feature.properties.name) ? feature.properties.name : 'Landing Station';
            layer.bindTooltip(`<b>Landing Station:</b> ${name}`, { sticky: true });
          }
        });
        this.map.addLayer(this.landingLayer);
      })
      .catch(err => {
        console.error('Failed loading landing stations GeoJSON:', err);
      });
  },

  loadIXPPoints() {
    fetch('/api/v1/ixps?limit=800')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}: Failed to fetch IXPs`);
        return r.json();
      })
      .then(res => {
        const ixps = res.data || [];
        this.ixpLayer = L.layerGroup();
        // Layer available for optional point display
      })
      .catch(err => {
        console.error('Failed loading IXP points:', err);
      });
  },

  loadFacilityPoints() {
    fetch('/api/v1/facilities?limit=1500')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}: Failed to fetch facilities`);
        return r.json();
      })
      .then(res => {
        const facs = res.data || [];
        facs.forEach(f => {
          if (f.latitude != null && f.longitude != null && !isNaN(f.latitude) && !isNaN(f.longitude)) {
            if (f.latitude >= -90 && f.latitude <= 90 && f.longitude >= -180 && f.longitude <= 180) {
              const marker = L.circleMarker([f.latitude, f.longitude], {
                radius: 4,
                fillColor: '#0d9488',
                color: '#ffffff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.85
              });
              marker.bindTooltip(`<b>${f.name || 'Facility'}</b><br>${f.city || ''}, ${f.country || ''}`, { sticky: true });
              marker.on('click', () => {
                this.displayFeatureDetails('facility', f);
              });
              this.markerClusterGroup.addLayer(marker);
            }
          }
        });
      })
      .catch(err => {
        console.error('Failed loading facility points:', err);
      });
  },

  bindLayerControls() {
    document.getElementById('toggle-cables')?.addEventListener('change', e => {
      if (e.target.checked) this.map.addLayer(this.cableLayer);
      else this.map.removeLayer(this.cableLayer);
    });

    document.getElementById('toggle-landings')?.addEventListener('change', e => {
      if (e.target.checked) this.map.addLayer(this.landingLayer);
      else this.map.removeLayer(this.landingLayer);
    });

    document.getElementById('toggle-facilities')?.addEventListener('change', e => {
      if (e.target.checked) this.map.addLayer(this.markerClusterGroup);
      else this.map.removeLayer(this.markerClusterGroup);
    });
  },

  displayFeatureDetails(type, props) {
    const panel = document.getElementById('detail-inspector');
    const titleEl = document.getElementById('inspector-title');
    const typeEl = document.getElementById('inspector-type');
    const bodyEl = document.getElementById('inspector-body');

    if (!panel || !titleEl || !typeEl || !bodyEl) return;

    panel.style.display = 'block';

    if (type === 'cable') {
      titleEl.innerText = props.name || props.id;
      typeEl.innerText = 'Submarine Fiber-Optic Cable';
      const countries = Array.isArray(props.countries_connected) ? props.countries_connected : [];
      bodyEl.innerHTML = `
        <div class="detail-row"><span class="detail-key">RFS (Commission Year)</span><span class="detail-val">${props.rfs_year || 'Unavailable'}</span></div>
        <div class="detail-row"><span class="detail-key">Route Length</span><span class="detail-val">${props.length_km ? props.length_km.toLocaleString() + ' km' : 'Unavailable'}</span></div>
        <div class="detail-row"><span class="detail-key">Status</span><span class="detail-val">${props.is_planned ? 'Announced / Planned' : 'Active / Operational'}</span></div>
        <div class="detail-row"><span class="detail-key">Landing Stations</span><span class="detail-val">${props.landing_points_count || 'Recorded'}</span></div>
        <div class="detail-row"><span class="detail-key">Owners / Consortium</span><span class="detail-val">${props.owners || 'Unavailable'}</span></div>
        <div style="margin-top: 10px;">
          <span class="detail-key">Connected Economies:</span>
          <div class="detail-tag-list">
            ${countries.map(c => `<span class="detail-tag">${c}</span>`).join('') || '<span class="detail-tag">Multi-regional transit</span>'}
          </div>
        </div>
      `;
    } else if (type === 'landing') {
      titleEl.innerText = props.name;
      typeEl.innerText = 'Submarine Cable Landing Point';
      bodyEl.innerHTML = `
        <div class="detail-row"><span class="detail-key">Country</span><span class="detail-val">${props.country} (${props.country_code || 'N/A'})</span></div>
        <div class="detail-row"><span class="detail-key">Coordinates</span><span class="detail-val">${props.geometry ? props.geometry.coordinates[1].toFixed(4) + ', ' + props.geometry.coordinates[0].toFixed(4) : 'WGS84'}</span></div>
        <div class="detail-row"><span class="detail-key">Status</span><span class="detail-val">${props.is_tbd ? 'To Be Determined' : 'Confirmed Landing'}</span></div>
        <div class="detail-row"><span class="detail-key">Data Authority</span><span class="detail-val">TeleGeography Public Data</span></div>
      `;
    } else if (type === 'facility') {
      titleEl.innerText = props.name;
      typeEl.innerText = 'Interconnection & Data Facility';
      bodyEl.innerHTML = `
        <div class="detail-row"><span class="detail-key">Operator</span><span class="detail-val">${props.org_name || 'Unavailable'}</span></div>
        <div class="detail-row"><span class="detail-key">Location</span><span class="detail-val">${props.city || ''}, ${props.country}</span></div>
        <div class="detail-row"><span class="detail-key">Connected Networks</span><span class="detail-val">${props.net_count || 0} ASNs</span></div>
        <div class="detail-row"><span class="detail-key">Present IXPs</span><span class="detail-val">${props.ix_count || 0}</span></div>
        <div class="detail-row"><span class="detail-key">Coordinates</span><span class="detail-val">${props.latitude?.toFixed(4)}, ${props.longitude?.toFixed(4)}</span></div>
        <div class="detail-row"><span class="detail-key">Registry</span><span class="detail-val">PeeringDB Verified</span></div>
      `;
    }
  },

  zoomToCountry(lat, lon, zoom = 5) {
    if (this.map && lat && lon) {
      this.map.flyTo([lat, lon], zoom, { duration: 1.2 });
    }
  }
};


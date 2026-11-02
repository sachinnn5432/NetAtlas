# NetAtlas Analytical Methodology & Data Science Framework

## 1. Data Cleaning & Spatial Normalization

### Coordinate Standardisation & Anomaly Elimination
All geographical coordinates undergo automated validation:
1. **Coordinate Reference System (CRS):** Standardized to WGS84 (EPSG:4326).
2. **Boundary Validation:**
   $$-180.0 \le \text{Longitude} \le 180.0$$
   $$-90.0 \le \text{Latitude} \le 90.0$$
3. **Null Island Elimination:** Geocoding bugs frequently default missing coordinates to $(0.0, 0.0)$. Any observation where $|\text{lat}| < 10^{-4}$ and $|\text{lon}| < 10^{-4}$ is flagged and removed from geospatial layers.
4. **Shapely Geometry Sanitization:** MultiLineString routes are tested via `geom.is_valid`. Any self-intersecting or broken line geometries are repaired using topological zero-buffer routines (`geom.buffer(0)`).

---

## 2. Bipartite Network Graph Modeling

The internet peering ecosystem is modeled as an undirected bipartite graph $G = (V_{net} \cup V_{ix}, E)$:
- $V_{net}$: Set of Autonomous Systems / network operators.
- $V_{ix}$: Set of Internet Exchange Points.
- $E$: Edge $(u, v)$ indicating that network $u$ participates in the shared switching fabric of exchange $v$.

### Topological Metric Definitions
1. **Network Degree $k_i$:** The number of distinct IXPs where network $i$ has established an active peering presence:
   $$k_i = \sum_{j \in V_{ix}} A_{ij}$$
2. **IXP Degree $d_j$:** The number of distinct networks connected to exchange point $j$:
   $$d_j = \sum_{i \in V_{net}} A_{ij}$$
3. **Giant Connected Component (GCC) Ratio:** The proportion of nodes belonging to the largest connected subcomponent:
   $$\text{Ratio}_{GCC} = \frac{|V_{GCC}|}{|V|}$$
   NetAtlas observes an empirical ratio of $97\%$, demonstrating the unified global reachability of the core peering mesh.

---

## 3. Infrastructure Density Index Formulation

To benchmark digital infrastructure depth across sovereign nations without conflating raw record counts with physical capacity, NetAtlas computes a composite Infrastructure Density Index ($IDI_c$) for each country $c$:

$$IDI_c = 4.0 \cdot N_{cables, c} + 3.0 \cdot N_{landings, c} + 2.0 \cdot N_{ixp, c} + 0.5 \cdot N_{fac, c}$$

### Weighting Rationale
- **Submarine Cables ($4.0\times$):** International oceanic capacity is capital-intensive and constitutes the foundational intercontinental backbone.
- **Landing Stations ($3.0\times$):** Coastal points of entry require terrestrial security, power, and backhaul transmission.
- **Internet Exchanges ($2.0\times$):** Sovereign peering fabrics enable local traffic keeping and latency minimization.
- **Colocation Facilities ($0.5\times$):** Commercial data centers are more numerous and exhibit commercial clustering.


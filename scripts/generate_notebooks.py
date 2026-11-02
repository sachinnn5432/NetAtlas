"""Generates comprehensive Jupyter Notebooks for academic and exploratory evaluation."""

import json
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

def create_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.14.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def code_cell(code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    }

def markdown_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    }

def build_exploration_notebook():
    cells = [
        markdown_cell("# NetAtlas — Exploratory Data Analysis & Quality Profiling\n## Global Internet Infrastructure Intelligence Platform"),
        code_cell("""
import pandas as pd
import numpy as np
import sqlite3
import os
from pathlib import Path

# Set paths
DATA_DIR = Path('../data')
REPORTING_DIR = DATA_DIR / 'reporting'
DB_PATH = DATA_DIR / 'netatlas.db'

print(f"Connecting to NetAtlas SQLite database at: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
"""),
        markdown_cell("### 1. Ingested Entity Record Counts"),
        code_cell("""
query = \"\"\"
SELECT 'Submarine Cables' AS Layer, COUNT(*) AS TotalRecords FROM cables
UNION ALL
SELECT 'Landing Stations', COUNT(*) FROM landing_stations
UNION ALL
SELECT 'Internet Exchanges', COUNT(*) FROM ixps
UNION ALL
SELECT 'Facilities', COUNT(*) FROM facilities
UNION ALL
SELECT 'Networks (ASNs)', COUNT(*) FROM networks
UNION ALL
SELECT 'Peering Interconnections', COUNT(*) FROM network_ix_relationships;
\"\"\"
summary_df = pd.read_sql_query(query, conn)
summary_df
"""),
        markdown_cell("### 2. Submarine Cable Length Statistics"),
        code_cell("""
cables_df = pd.read_sql_query("SELECT id, name, rfs_year, length_km, is_planned, landing_points_count FROM cables", conn)
print("Cable Length Summary Statistics (Kilometers):")
cables_df['length_km'].describe()
"""),
        markdown_cell("### 3. Missing Value Analysis"),
        code_cell("""
missing_data = pd.DataFrame({
    'TotalRecords': len(cables_df),
    'Missing_RFS_Year': cables_df['rfs_year'].isna().sum(),
    'Missing_Length': cables_df['length_km'].isna().sum(),
    'Missing_Length_Pct': round(cables_df['length_km'].isna().mean() * 100, 2)
}, index=['Submarine Cables'])
missing_data
""")
    ]
    with open(NOTEBOOKS_DIR / "data_exploration.ipynb", "w", encoding="utf-8") as f:
        json.dump(create_notebook(cells), f, indent=2)

def build_geographical_notebook():
    cells = [
        markdown_cell("# NetAtlas — Geospatial Analysis\n## Spatial Distribution of Subsea Cables and Landing Stations"),
        code_cell("""
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path('../data')
GEOJSON_DIR = DATA_DIR / 'geojson'

# Load landing stations GeoJSON
stations_gdf = gpd.read_file(GEOJSON_DIR / 'landing_stations.geojson')
print(f"Loaded {len(stations_gdf)} verified landing stations.")
stations_gdf.head()
"""),
        markdown_cell("### 1. Geographic Coordinate Bounds Check"),
        code_cell("""
bounds = stations_gdf.total_bounds # [minx, miny, maxx, maxy]
print(f"Bounding Box: Lon [{bounds[0]:.2f}, {bounds[2]:.2f}], Lat [{bounds[1]:.2f}, {bounds[3]:.2f}]")
"""),
        markdown_cell("### 2. Top Economies by Landing Station Count"),
        code_cell("""
top_countries = stations_gdf['country'].value_counts().head(15)
plt.figure(figsize=(10, 5))
top_countries.plot(kind='bar', color='#0284c7', edgecolor='black')
plt.title('Top 15 Countries by Confirmed Submarine Cable Landing Stations')
plt.xlabel('Country')
plt.ylabel('Landing Stations Count')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
""")
    ]
    with open(NOTEBOOKS_DIR / "geographical_analysis.ipynb", "w", encoding="utf-8") as f:
        json.dump(create_notebook(cells), f, indent=2)

def build_network_notebook():
    cells = [
        markdown_cell("# NetAtlas — Network Topology & Graph Analysis\n## NetworkX Interconnection Bipartite Graph Analysis"),
        code_cell("""
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path('../data')
rel_path = DATA_DIR / 'reporting' / 'FactNetworkRelationship.csv'
df_rel = pd.read_csv(rel_path)
print(f"Loaded {len(df_rel)} observed peering relationships.")
df_rel.head()
"""),
        markdown_cell("### 1. Constructing the Bipartite Peering Graph"),
        code_cell("""
B = nx.Graph()
for _, row in df_rel.iterrows():
    net_node = f"NET_{row['NetworkID']}"
    ix_node = f"IX_{row['IXPID']}"
    B.add_edge(net_node, ix_node)

print(f"Graph Order: {B.number_of_nodes()} nodes")
print(f"Graph Size: {B.number_of_edges()} edges")
"""),
        markdown_cell("### 2. Connected Component & Degree Analysis"),
        code_cell("""
components = list(nx.connected_components(B))
print(f"Connected Components: {len(components)}")
giant_size = len(max(components, key=len))
print(f"Giant Connected Component Size: {giant_size} nodes ({giant_size / B.number_of_nodes() * 100:.2f}%)")

degrees = [d for n, d in B.degree() if n.startswith('NET_')]
print(f"Max Network Degree: {max(degrees)}")
print(f"Median Network Degree: {np.median(degrees)}")
"""),
        markdown_cell("### 3. Degree Distribution Log-Log Plot (Scale-Free Assessment)"),
        code_cell("""
plt.figure(figsize=(8, 4.5))
plt.hist(degrees, bins=30, color='#7c3aed', edgecolor='black', log=True)
plt.title('Network Degree Distribution on IXP Peering Fabrics')
plt.xlabel('Degree (IXP Presences per Network)')
plt.ylabel('Frequency (Log Scale)')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
""")
    ]
    with open(NOTEBOOKS_DIR / "network_analysis.ipynb", "w", encoding="utf-8") as f:
        json.dump(create_notebook(cells), f, indent=2)

def build_visualization_notebook():
    cells = [
        markdown_cell("# NetAtlas — Statistical Visualization & Reporting Analysis\n## Exploratory Visualizations for Infrastructure Intelligence"),
        code_cell("""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA_DIR = Path('../data')
REPORTING_DIR = DATA_DIR / 'reporting'

fact_ixp = pd.read_csv(REPORTING_DIR / 'FactIXP.csv')
fact_cable = pd.read_csv(REPORTING_DIR / 'FactCable.csv')
fact_fac = pd.read_csv(REPORTING_DIR / 'FactFacility.csv')

sns.set_theme(style='whitegrid', font='sans-serif')
"""),
        markdown_cell("### 1. Top Global Internet Exchanges by Connected Networks"),
        code_cell("""
top_ixps = fact_ixp.sort_values(by='ConnectedNetworksCount', ascending=False).head(12)

plt.figure(figsize=(10, 5))
sns.barplot(data=top_ixps, x='ConnectedNetworksCount', y='IXPName', color='#7c3aed')
plt.title('Top 12 Global Internet Exchange Points by Participant ASNs')
plt.xlabel('Connected Networks (ASNs)')
plt.ylabel('Internet Exchange Point')
plt.tight_layout()
plt.show()
"""),
        markdown_cell("### 2. Submarine Cable Commissioning Timeline (1990 - 2028)"),
        code_cell("""
cable_years = fact_cable.dropna(subset=['RFS_Year']).copy()
cable_years['RFS_Year'] = cable_years['RFS_Year'].astype(int)
valid_years = cable_years[(cable_years['RFS_Year'] >= 1990) & (cable_years['RFS_Year'] <= 2028)]

plt.figure(figsize=(12, 4.5))
sns.histplot(data=valid_years, x='RFS_Year', hue='IsPlanned', multiple='stack', bins=38, palette={0: '#0284c7', 1: '#ea580c'})
plt.title('Submarine Cable Commissioning Trajectory by Year (1990 - 2028)')
plt.xlabel('Ready For Service (RFS) Year')
plt.ylabel('Cable Systems Commissioned / Planned')
plt.tight_layout()
plt.show()
""")
    ]
    with open(NOTEBOOKS_DIR / "visualization_analysis.ipynb", "w", encoding="utf-8") as f:
        json.dump(create_notebook(cells), f, indent=2)

if __name__ == "__main__":
    build_exploration_notebook()
    build_geographical_notebook()
    build_network_notebook()
    build_visualization_notebook()
    print("All 4 Jupyter Notebooks successfully generated in notebooks/")


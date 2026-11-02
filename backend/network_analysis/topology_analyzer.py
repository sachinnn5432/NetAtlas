"""Topology and Connectivity Analysis for NetAtlas Interconnection Graphs."""

from typing import Dict, Any, List
import networkx as nx
from backend.network_analysis.graph_builder import InterconnectionGraphBuilder
from backend.models.database import SessionLocal
from backend.models.db_models import NetworkModel, IXPModel
from backend.config.logging_config import logger

class TopologyAnalyzer:
    """Computes rigorous topological graph metrics on observed peering fabrics."""

    @classmethod
    def analyze_global_peering_topology(cls) -> Dict[str, Any]:
        """Calculates macro-topological metrics of the bipartite peering graph."""
        B = InterconnectionGraphBuilder.build_bipartite_ixp_graph()
        if B.number_of_nodes() == 0:
            return {
                "total_nodes": 0, "total_edges": 0, "status": "no_data_available"
            }

        session = SessionLocal()
        try:
            # Component analysis
            components = list(nx.connected_components(B))
            component_count = len(components)
            giant_component_size = len(max(components, key=len)) if components else 0
            giant_component_ratio = round(giant_component_size / B.number_of_nodes(), 4)

            # Degree analysis
            degrees = dict(B.degree())
            net_degrees = {n: d for n, d in degrees.items() if n.startswith("NET_")}
            ix_degrees = {n: d for n, d in degrees.items() if n.startswith("IX_")}

            top_net_nodes = sorted(net_degrees.items(), key=lambda x: x[1], reverse=True)[:15]
            top_ix_nodes = sorted(ix_degrees.items(), key=lambda x: x[1], reverse=True)[:15]

            # Resolve network names
            top_networks = []
            for n_id, deg in top_net_nodes:
                raw_id = int(n_id.replace("NET_", ""))
                net = session.query(NetworkModel).filter_by(id=raw_id).first()
                top_networks.append({
                    "id": raw_id,
                    "name": net.name if net else f"Network {raw_id}",
                    "asn": net.asn if net else None,
                    "ixp_presence_count": deg
                })

            # Resolve IXP names
            top_ixps = []
            for i_id, deg in top_ix_nodes:
                raw_id = int(i_id.replace("IX_", ""))
                ix = session.query(IXPModel).filter_by(id=raw_id).first()
                top_ixps.append({
                    "id": raw_id,
                    "name": ix.name if ix else f"IXP {raw_id}",
                    "city": ix.city if ix else "Unknown",
                    "country": ix.country if ix else "Unknown",
                    "connected_networks_count": deg
                })

            metrics = {
                "total_nodes": B.number_of_nodes(),
                "total_edges": B.number_of_edges(),
                "total_networks_participating": len(net_degrees),
                "total_active_ixps": len(ix_degrees),
                "connected_components_count": component_count,
                "giant_component_node_count": giant_component_size,
                "giant_component_ratio": giant_component_ratio,
                "top_connected_networks": top_networks,
                "top_connected_ixps": top_ixps,
                "interpretation": (
                    "This graph models observed presence on public IXP switching fabrics recorded in PeeringDB. "
                    "A high degree indicates extensive multi-exchange presence, characteristic of major content "
                    "distribution networks (CDNs), Tier-1 transit providers, and cloud hyperscalers."
                )
            }
            return metrics
        finally:
            session.close()


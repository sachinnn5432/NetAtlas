"""NetworkX Graph Construction Module for Interconnection Topologies.

Constructs bipartite graphs representing Network-to-IX and Network-to-Facility
interconnections from authenticated PeeringDB records.
"""

from typing import Dict, Any, Tuple, Optional
import networkx as nx
from backend.models.database import SessionLocal
from backend.models.db_models import (
    NetworkModel, IXPModel, FacilityModel, NetworkIXRelationshipModel, NetworkFacilityRelationshipModel
)
from backend.config.logging_config import logger

class InterconnectionGraphBuilder:
    """Builds NetworkX graph representations of global internet peering relationships."""

    @classmethod
    def build_bipartite_ixp_graph(cls, limit_edges: Optional[int] = 50000) -> nx.Graph:
        """Constructs bipartite graph of Networks and IXPs.

        Nodes have attribute 'bipartite': 0 for Networks, 1 for IXPs.
        Edges represent presence on an IXP exchange fabric.
        """
        B = nx.Graph()
        session = SessionLocal()
        try:
            # Query relationships
            query = session.query(
                NetworkIXRelationshipModel.net_id,
                NetworkIXRelationshipModel.ix_id,
                NetworkIXRelationshipModel.speed,
                NetworkIXRelationshipModel.asn
            )
            if limit_edges:
                query = query.limit(limit_edges)

            edges = query.all()
            if not edges:
                logger.warning("No Network-IX relationships found in database.")
                return B

            net_ids = set()
            ix_ids = set()
            for net_id, ix_id, speed, asn in edges:
                net_node = f"NET_{net_id}"
                ix_node = f"IX_{ix_id}"
                net_ids.add((net_node, asn))
                ix_ids.add(ix_node)

                B.add_edge(net_node, ix_node, speed=speed)

            # Add node attributes
            for net_node, asn in net_ids:
                B.nodes[net_node]["bipartite"] = 0
                B.nodes[net_node]["type"] = "network"
                B.nodes[net_node]["asn"] = asn

            for ix_node in ix_ids:
                B.nodes[ix_node]["bipartite"] = 1
                B.nodes[ix_node]["type"] = "ixp"

            logger.info("Constructed Bipartite Peering Graph: %d nodes (%d nets, %d IXPs), %d edges.",
                        B.number_of_nodes(), len(net_ids), len(ix_ids), B.number_of_edges())
            return B
        finally:
            session.close()

    @classmethod
    def get_ixp_projection(cls, B: nx.Graph) -> nx.Graph:
        """Projects bipartite graph onto IXP nodes to reveal co-presence overlap."""
        ix_nodes = {n for n, d in B.nodes(data=True) if d.get("bipartite") == 1}
        if not ix_nodes:
            return nx.Graph()
        try:
            return nx.bipartite.projected_graph(B, ix_nodes)
        except Exception as e:
            logger.error("Error creating IXP projection: %s", e)
            return nx.Graph()


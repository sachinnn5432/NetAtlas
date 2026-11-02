"""Unit Tests for NetAtlas NetworkX Topologies and Degree Analysis."""

import pytest
import networkx as nx
from backend.network_analysis.graph_builder import InterconnectionGraphBuilder
from backend.network_analysis.topology_analyzer import TopologyAnalyzer
from backend.network_analysis.degree_metrics import DegreeMetricsCalculator

def test_bipartite_graph_construction():
    B = InterconnectionGraphBuilder.build_bipartite_ixp_graph(limit_edges=100)
    assert isinstance(B, nx.Graph)
    assert B.number_of_nodes() > 0
    assert B.number_of_edges() > 0

    # Test bipartite attribute assignment
    for n, d in B.nodes(data=True):
        assert "bipartite" in d
        assert d["bipartite"] in (0, 1)

def test_topology_metrics():
    metrics = TopologyAnalyzer.analyze_global_peering_topology()
    assert "total_nodes" in metrics
    assert "giant_component_node_count" in metrics
    assert "top_connected_networks" in metrics
    assert "top_connected_ixps" in metrics
    assert metrics["giant_component_ratio"] > 0.5  # Internet graph giant component is dominant

def test_degree_metrics_bins():
    deg_res = DegreeMetricsCalculator.calculate_degree_distributions()
    assert "network_degree_distribution" in deg_res
    assert "ixp_degree_distribution" in deg_res
    assert len(deg_res["network_degree_distribution"]) > 0


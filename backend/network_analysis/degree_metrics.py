"""Degree Distribution and Connectivity Histogram Module for NetAtlas."""

from typing import Dict, Any, List
import numpy as np
from backend.network_analysis.graph_builder import InterconnectionGraphBuilder

class DegreeMetricsCalculator:
    """Calculates empirical degree distribution histograms for internet topologies."""

    @classmethod
    def calculate_degree_distributions(cls) -> Dict[str, Any]:
        """Calculates degree bins and distributions for Networks and IXPs."""
        B = InterconnectionGraphBuilder.build_bipartite_ixp_graph()
        if B.number_of_nodes() == 0:
            return {"network_degrees": [], "ixp_degrees": []}

        degrees = dict(B.degree())
        net_degrees = [d for n, d in degrees.items() if n.startswith("NET_")]
        ix_degrees = [d for n, d in degrees.items() if n.startswith("IX_")]

        def bin_degrees(vals: List[int]) -> List[Dict[str, Any]]:
            if not vals:
                return []
            bins = [1, 2, 5, 10, 25, 50, 100, 250, 500, 1000]
            labels = ["1", "2-4", "5-9", "10-24", "25-49", "50-99", "100-249", "250-499", "500+"]
            hist, _ = np.histogram(vals, bins=bins + [max(max(vals) + 1, 1001)])
            return [{"range": labels[i], "count": int(hist[i])} for i in range(len(labels))]

        return {
            "network_degree_distribution": bin_degrees(net_degrees),
            "ixp_degree_distribution": bin_degrees(ix_degrees),
            "network_stats": {
                "max": int(max(net_degrees)) if net_degrees else 0,
                "median": float(np.median(net_degrees)) if net_degrees else 0.0,
                "mean": round(float(np.mean(net_degrees)), 2) if net_degrees else 0.0
            },
            "ixp_stats": {
                "max": int(max(ix_degrees)) if ix_degrees else 0,
                "median": float(np.median(ix_degrees)) if ix_degrees else 0.0,
                "mean": round(float(np.mean(ix_degrees)), 2) if ix_degrees else 0.0
            }
        }


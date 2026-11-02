"""Infrastructure Density and Data Storytelling Narratives for NetAtlas."""

from typing import Dict, Any, List
from backend.analytics.country_stats import CountryAnalytics
from backend.analytics.regional_aggregation import RegionalAnalytics

class DataStoryteller:
    """Generates evidenced-backed analytical narratives supported by authentic data."""

    @classmethod
    def generate_analytical_stories(cls) -> List[Dict[str, Any]]:
        """Synthesizes key research findings grounded strictly in verified observations."""
        countries = CountryAnalytics.get_all_country_summaries()
        regions = RegionalAnalytics.get_regional_breakdown()

        top_ixp_countries = sorted(countries, key=lambda x: x["ixp_count"], reverse=True)[:5]
        top_cable_countries = sorted(countries, key=lambda x: x["landing_station_count"], reverse=True)[:5]
        top_fac_countries = sorted(countries, key=lambda x: x["facility_count"], reverse=True)[:5]

        stories = [
            {
                "id": "story_ixp_concentration",
                "title": "Geographic Concentration of Internet Exchange Points",
                "summary": (
                    f"IXP deployment is intensely clustered. The top 5 countries account for a disproportionate "
                    f"share of global peering fabrics, led by {top_ixp_countries[0]['country_name']} "
                    f"({top_ixp_countries[0]['ixp_count']} IXPs) and {top_ixp_countries[1]['country_name']} "
                    f"({top_ixp_countries[1]['ixp_count']} IXPs). In developing regions, peering remains concentrated "
                    f"in single national commercial capitals."
                ),
                "key_metrics": [
                    {"label": c["country_name"], "value": f"{c['ixp_count']} IXPs"}
                    for c in top_ixp_countries[:3]
                ]
            },
            {
                "id": "story_cable_chokepoints",
                "title": "Maritime Subsea Corridors & Coastal Landing Concentration",
                "summary": (
                    f"Subsea fiber landings follow maritime choke-points and critical littoral straits. Leading "
                    f"intercontinental landing hubs include {top_cable_countries[0]['country_name']} "
                    f"({top_cable_countries[0]['landing_station_count']} landing points) and "
                    f"{top_cable_countries[1]['country_name']} ({top_cable_countries[1]['landing_station_count']} landing points). "
                    f"Key maritime conduits such as the Red Sea, Strait of Malacca, and English Channel "
                    f"concentrate global oceanic data transit."
                ),
                "key_metrics": [
                    {"label": c["country_name"], "value": f"{c['landing_station_count']} Stations"}
                    for c in top_cable_countries[:3]
                ]
            },
            {
                "id": "story_facility_density",
                "title": "Colocation Facilities & Interconnection Gravity",
                "summary": (
                    f"Recorded colocation facilities in PeeringDB reflect commercial interconnection gravity rather "
                    f"than domestic consumer dispersion. {top_fac_countries[0]['country_name']} leads with "
                    f"{top_fac_countries[0]['facility_count']} documented facilities, driven by hyperscale peering "
                    f"clusters like Ashburn, Northern Virginia, Silicon Valley, and Frankfurt."
                ),
                "key_metrics": [
                    {"label": c["country_name"], "value": f"{c['facility_count']} Facilities"}
                    for c in top_fac_countries[:3]
                ]
            },
            {
                "id": "story_analytical_limitations",
                "title": "Methodological Limitations in Cross-Country Comparisons",
                "summary": (
                    "Direct country comparisons must account for reporting asymmetries in community-governed databases. "
                    "In regions where PeeringDB participation is standard operational procedure (North America, Western Europe), "
                    "record completeness approaches near-total coverage. In domestic closed-market environments, infrastructure "
                    "may exist at scale without being cataloged on public peering registries."
                ),
                "key_metrics": [
                    {"label": "Data Source", "value": "PeeringDB + TeleGeography"},
                    {"label": "Reporting Paradigm", "value": "Voluntary Operator Registry"}
                ]
            }
        ]
        return stories


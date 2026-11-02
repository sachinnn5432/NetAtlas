"""Regional Aggregation and Macro-Geographic Comparison Engine for NetAtlas."""

from typing import Dict, Any, List
import pandas as pd
from backend.analytics.country_stats import CountryAnalytics

class RegionalAnalytics:
    """Computes regional comparisons and macro-geographic concentration indexes."""

    @classmethod
    def get_regional_breakdown(cls) -> List[Dict[str, Any]]:
        """Aggregates all country data into continental and subcontinental regions."""
        countries = CountryAnalytics.get_all_country_summaries()
        df = pd.DataFrame(countries)
        if df.empty:
            return []

        regional_groups = df.groupby("region").agg({
            "country_code": "count",
            "ixp_count": "sum",
            "facility_count": "sum",
            "landing_station_count": "sum",
            "cable_count": "sum",
            "infrastructure_density_score": "sum"
        }).reset_index()

        regional_groups.rename(columns={"country_code": "economies_tracked"}, inplace=True)
        regional_groups.sort_values(by="infrastructure_density_score", ascending=False, inplace=True)

        return regional_groups.to_dict(orient="records")


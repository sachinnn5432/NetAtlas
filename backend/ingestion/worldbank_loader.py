"""World Bank Digital Infrastructure and Development Indicator Loader.

Ingests country-level digital development metrics (Internet adoption %,
secure servers per capita, broadband penetration) to provide contextual infrastructure
analysis in compliance with World Bank Open Data (CC BY 4.0).
"""

from typing import Dict, Any, List, Optional
import json
import requests
from pathlib import Path
from backend.config.settings import REQUEST_TIMEOUT_SEC, RAW_DATA_DIR, USER_AGENT
from backend.config.logging_config import logger

WORLD_BANK_API_BASE = "https://api.worldbank.org/v2"

# Key World Development Report / Digital Development Indicators
INDICATORS = {
    "internet_users_pct": "IT.NET.USER.ZS",      # Individuals using the Internet (% of population)
    "secure_servers_p6": "IT.NET.SECR.P6",       # Secure Internet servers (per 1 million people)
    "broadband_subscriptions": "IT.NET.BBND"     # Fixed broadband subscriptions
}

class WorldBankLoader:
    """Loader for World Bank open indicators."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        })

    def fetch_country_indicator(self, indicator_code: str, year: int = 2023) -> Dict[str, float]:
        """Fetches the latest values for an indicator across all countries."""
        cache_file = RAW_DATA_DIR / f"wb_{indicator_code}.json"
        if cache_file.exists() and cache_file.stat().st_size > 1000:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        url = f"{WORLD_BANK_API_BASE}/country/all/indicator/{indicator_code}?date={year-2}:{year}&format=json&per_page=300"
        logger.info("Fetching World Bank indicator: %s", indicator_code)
        results = {}

        try:
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT_SEC)
            if resp.status_code == 200:
                payload = resp.json()
                if len(payload) > 1 and isinstance(payload[1], list):
                    for entry in payload[1]:
                        cid = entry.get("countryiso3code")
                        val = entry.get("value")
                        if cid and val is not None and cid not in results:
                            results[cid] = float(val)

                    # Cache
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(results, f)
            else:
                logger.warning("World Bank API returned status %d", resp.status_code)
        except Exception as exc:
            logger.warning("World Bank API fetch error: %s", exc)

        return results

    def get_contextual_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Aggregates all digital development indicators per country ISO3."""
        internet_users = self.fetch_country_indicator(INDICATORS["internet_users_pct"])
        secure_servers = self.fetch_country_indicator(INDICATORS["secure_servers_p6"])

        all_countries = set(internet_users.keys()) | set(secure_servers.keys())
        context_data = {}
        for c in all_countries:
            context_data[c] = {
                "internet_users_pct": internet_users.get(c),
                "secure_servers_per_million": secure_servers.get(c)
            }
        return context_data


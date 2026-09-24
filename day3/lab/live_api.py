"""Day 3 IN03 helper: live external APIs shared by the REST agent and MCP server.

Kept inside Day 3 so the day is self-contained (the class redefines these live
functions in each notebook that needs them).
"""

from __future__ import annotations

import requests

from common.config import settings

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
TAVILY_URL = "https://api.tavily.com/search"


def _geocode(city: str, api_key: str) -> dict:
    response = requests.get(
        GEOCODE_URL, params={"q": city, "limit": 1, "appid": api_key}, timeout=10
    )
    response.raise_for_status()
    matches = response.json()
    if matches:
        return {"lat": matches[0]["lat"], "lon": matches[0]["lon"], "name": matches[0]["name"]}
    response = requests.get(
        NOMINATIM_URL,
        params={"q": city, "format": "json", "limit": 1},
        headers={"User-Agent": "advanced-agentic-ai-lab/1.0"},
        timeout=10,
    )
    response.raise_for_status()
    hits = response.json()
    if not hits:
        raise ValueError(f"No geocoding match for '{city}'")
    return {"lat": float(hits[0]["lat"]), "lon": float(hits[0]["lon"]), "name": city}


def get_store_weather(city: str, country_code: str = "IN") -> dict:
    """Live OpenWeatherMap current weather for a Walmart store city."""
    if not settings.openweathermap_api_key:
        return {"error": "OPENWEATHERMAP_API_KEY missing"}
    api_key = settings.openweathermap_api_key.get_secret_value()
    location = _geocode(f"{city},{country_code}" if country_code else city, api_key)
    response = requests.get(
        WEATHER_URL,
        params={"lat": location["lat"], "lon": location["lon"], "appid": api_key, "units": "metric"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "city": location["name"],
        "temperature_c": round(data["main"]["temp"], 1),
        "condition": data["weather"][0]["description"],
        "humidity_pct": data["main"]["humidity"],
    }


def search_demand_trends(query: str, max_results: int = 3) -> dict:
    """Live Tavily search for current market/demand signals."""
    if not settings.tavily_api_key:
        return {"error": "TAVILY_API_KEY missing"}
    response = requests.post(
        TAVILY_URL,
        json={
            "api_key": settings.tavily_api_key.get_secret_value(),
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": True,
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "answer": data.get("answer", ""),
        "results": [
            {"title": item["title"], "content": item["content"][:250]}
            for item in data.get("results", [])
        ],
    }

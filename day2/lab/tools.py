from __future__ import annotations

import requests

from day1.lab.app.config import Settings


def get_weather(city: str, settings: Settings) -> str:
    if not settings.openweathermap_api_key:
        return "Weather lookup is unavailable because OPENWEATHERMAP_API_KEY is missing."
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": settings.openweathermap_api_key.get_secret_value(),
                "units": "metric",
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"Weather lookup failed: {exc}"
    data = response.json()
    description = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    return f"{city}: {description}, {temperature:.1f} C."


def search_web(query: str, settings: Settings) -> str:
    if not settings.tavily_api_key:
        return "Web search is unavailable because TAVILY_API_KEY is missing."
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.tavily_api_key.get_secret_value(),
                "query": query,
                "search_depth": "basic",
                "max_results": 3,
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"Web search failed: {exc}"
    results = response.json().get("results", [])
    if not results:
        return "No web results were found."
    return "\n".join(
        f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:300]}"
        for item in results
    )
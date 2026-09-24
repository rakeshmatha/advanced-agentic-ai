"""Day 2: API / MCP / Frameworks / Build vs Buy intro (IN03 intro notebook).

Matches `Day2/IN03_API_MCP_Frameworks_Build_vs_Buy - Intro.ipynb`.

The store manager at WMT-2847 (Bengaluru) asks: based on today's weather and
demand, what should we stock? Live OpenWeatherMap + Tavily, then a Python-only
LLM recommendation.

Then the three architect questions the notebook poses:
  1. Protocol: REST vs MCP
  2. Framework: Python-only vs LangChain vs LangGraph
  3. Build vs Buy for each component

REST tools + a real MCP server + LangGraph agents are Day 3.

    source ./activate
    build-vs-buy
    build-vs-buy "What should we stock if it rains all week?"
"""

from __future__ import annotations

import argparse
import json
import textwrap
import time

import requests

from common.client import build_client
from common.config import settings

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
TAVILY_URL = "https://api.tavily.com/search"
STORE_ID = "WMT-2847"
STORE_CITY = "Bengaluru"
STORE_QUERY = (
    "Based on today's actual conditions, what should we prioritise stocking today?"
)


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


def fetch_weather(city: str = STORE_CITY) -> dict:
    """Live OpenWeatherMap. Day 2 notebook Core API Functions."""
    if not settings.openweathermap_api_key:
        return {"error": "OPENWEATHERMAP_API_KEY missing"}
    api_key = settings.openweathermap_api_key.get_secret_value()
    location = _geocode(city, api_key)
    response = requests.get(
        WEATHER_URL,
        params={
            "lat": location["lat"],
            "lon": location["lon"],
            "appid": api_key,
            "units": "metric",
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "city": location["name"],
        "temperature_c": round(data["main"]["temp"], 1),
        "feels_like_c": round(data["main"]["feels_like"], 1),
        "humidity_pct": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed_ms": data["wind"]["speed"],
    }


def fetch_demand_trends(query: str, max_results: int = 3) -> dict:
    """Live Tavily. Day 2 notebook Core API Functions."""
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
            {"title": item["title"], "content": item["content"][:300]}
            for item in data.get("results", [])
        ],
    }


def python_only_agent(query: str, city: str = STORE_CITY) -> dict:
    """Notebook Python-only path: developer pre-fetches, then the LLM reasons."""
    started = time.perf_counter()
    weather = fetch_weather(city)
    demand = fetch_demand_trends(f"retail product demand {city} India this week", max_results=2)
    client = build_client()
    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are an AI assistant for Walmart India store {STORE_ID} in {city}. "
                    "Recommend 3-5 product categories to stock today. Use only the live data. "
                    "Be concise. Bullet the products and one reason each.\n"
                    f"Live weather: {json.dumps(weather)}\n"
                    f"Demand signals: {demand.get('answer', '')}"
                ),
            },
            {"role": "user", "content": query},
        ],
        temperature=0,
        max_tokens=400,
    )
    usage = response.usage
    in_cost = (usage.prompt_tokens / 1_000_000) * 0.150
    out_cost = (usage.completion_tokens / 1_000_000) * 0.600
    return {
        "weather": weather,
        "demand": demand,
        "answer": response.choices[0].message.content.strip(),
        "latency_sec": round(time.perf_counter() - started, 2),
        "cost_usd": round(in_cost + out_cost, 6),
        "framework": "Python-only",
    }


def render_table(
    headers: list[str],
    rows: list[list[str]],
    max_widths: list[int | None] | None = None,
    center: set[int] | None = None,
) -> str:
    ncols = len(headers)
    max_widths = max_widths or [None] * ncols
    center = center or set()

    def wrap(text: str, width: int | None) -> list[str]:
        raw = str(text).splitlines() or [""]
        if width is None:
            return raw
        lines: list[str] = []
        for para in raw:
            if para.startswith("• "):
                lines.extend(textwrap.wrap(para, width, subsequent_indent="  ") or ["• "])
            else:
                lines.extend(textwrap.wrap(para, width) or [""])
        return lines or [""]

    wrapped = [[wrap(str(cell), max_widths[i]) for i, cell in enumerate(row)] for row in rows]
    widths = [len(header) for header in headers]
    for cells in wrapped:
        for i, lines in enumerate(cells):
            for line in lines:
                widths[i] = max(widths[i], len(line))

    def pad(text: str, i: int) -> str:
        return text.center(widths[i]) if i in center else text.ljust(widths[i])

    def row_line(cells_line: list[str]) -> str:
        return "│ " + " │ ".join(pad(cells_line[i], i) for i in range(ncols)) + " │"

    def bar(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (width + 2) for width in widths) + right

    out = [bar("┌", "┬", "┐"), row_line(headers), bar("├", "┼", "┤")]
    for idx, cells in enumerate(wrapped):
        if idx:
            out.append(bar("├", "┼", "┤"))
        height = max(len(cell) for cell in cells)
        for row in range(height):
            out.append(
                row_line([cells[i][row] if row < len(cells[i]) else "" for i in range(ncols)])
            )
    out.append(bar("└", "┴", "┘"))
    return "\n".join(out)


def print_decisions() -> None:
    print("1. PROTOCOL  (REST vs MCP)")
    print(
        render_table(
            ["Option", "Who owns the schema", "Use when", "Day 2 pick"],
            [
                [
                    "REST",
                    "You write it in the agent",
                    "One app, few tools, existing HTTP APIs",
                    "YES - weather + Tavily are HTTP",
                ],
                [
                    "MCP",
                    "The server; clients discover it",
                    "Many agents must share the same tools",
                    "Day 3 - real FastMCP server",
                ],
            ],
            max_widths=[8, 28, 32, 28],
        )
    )
    print()
    print("2. FRAMEWORK  (TCO, not features)")
    print(
        render_table(
            ["Option", "What you get", "Cost", "Day 2 pick"],
            [
                [
                    "Python-only",
                    "You pre-fetch, then call the LLM. Full control.",
                    "Least abstraction, you write the loop",
                    "YES - this lab",
                ],
                [
                    "LangChain",
                    "Tool loop + integrations for you",
                    "Dependency + debugging overhead",
                    "Day 3 compares it live",
                ],
                [
                    "LangGraph",
                    "Explicit state and branching",
                    "More setup, better for multi-step agents",
                    "Day 3 orchestration",
                ],
            ],
            max_widths=[12, 36, 28, 24],
        )
    )
    print()
    print("3. BUILD vs BUY  (per component)")
    print(
        render_table(
            ["Component", "Build or buy", "Why"],
            [
                [
                    "Weather",
                    "BUY OpenWeatherMap",
                    "Commodity data. Not a Walmart differentiator.",
                ],
                [
                    "Demand / news",
                    "BUY Tavily",
                    "Search infra is a vendor product.",
                ],
                [
                    "LLM reasoning",
                    "BUY OpenAI",
                    "Do not train a weather/demand model for this.",
                ],
                [
                    "Orchestration",
                    "BUILD Python-only (now)",
                    "Two live calls + one prompt. Buy a framework later if loops grow.",
                ],
                [
                    "Shared tool catalog",
                    "BUILD MCP later",
                    "Buy REST today. Build MCP when a 2nd host needs the same tools.",
                ],
            ],
            max_widths=[20, 24, 48],
        )
    )
    print()


def run_query(query: str, city: str = STORE_CITY) -> None:
    print()
    print(f"STORE   {STORE_ID} | {city}, India")
    print(f"QUESTION\n  {query}\n")
    print("Fetching live weather + demand...")
    result = python_only_agent(query, city=city)
    weather = result["weather"]
    demand = result["demand"]

    print()
    print("LIVE DATA")
    if "error" in weather:
        print(f"  weather: {weather['error']}")
        weather_row = [["Weather", "—", str(weather["error"])]]
    else:
        weather_row = [[
            "Weather",
            weather.get("city", city),
            (
                f"{weather.get('temperature_c')} C, {weather.get('condition')}, "
                f"humidity {weather.get('humidity_pct')}%"
            ),
        ]]
    demand_answer = demand.get("error") or demand.get("answer") or "(no Tavily answer)"
    print(
        render_table(
            ["Source", "Where", "Signal"],
            weather_row + [["Demand (Tavily)", city, demand_answer]],
            max_widths=[16, 16, 56],
        )
    )
    print()
    print(f"RECOMMENDATION  ({result['framework']} | {result['latency_sec']}s | ${result['cost_usd']})")
    for line in result["answer"].splitlines():
        print(f"  {line}")
    print()
    print_decisions()


def print_legend() -> None:
    print("=" * 70)
    print("Day 2 Build vs Buy  (IN03 intro)")
    print("=" * 70)
    print("Walmart India Retail Assistant @ 4,700 stores.")
    print(f"Store manager at {STORE_ID} {STORE_CITY} asks what to stock today.")
    print("This lab: live weather + demand, then Python-only reasoning.")
    print("Then three decisions: REST vs MCP, framework, build vs buy.")
    print("MCP server + LangGraph agents are Day 3.")
    print()
    print("Try this:")
    print(f'  "{STORE_QUERY}"')
    print('  "It will rain all week. What should we stock?"')
    print("Commands: /exit quits, /decisions reprints the tables.")
    print("-" * 70)


def chat_repl() -> None:
    print_legend()
    run_query(STORE_QUERY)
    while True:
        try:
            text = input("manager> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/exit":
            break
        if text == "/decisions":
            print()
            print_decisions()
            continue
        run_query(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Day 2 IN03 intro: live APIs + protocol/framework/build-vs-buy"
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="store-manager question (skip chat; still prints decision tables)",
    )
    args = parser.parse_args()
    question = " ".join(args.question).strip()
    if question:
        run_query(question)
        return
    chat_repl()


if __name__ == "__main__":
    main()

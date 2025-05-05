#!/usr/bin/env python3
"""
Weather by City CLI — prints today's temperature and an icon.
Free: uses Open‑Meteo (no API keys) + Rich for a nice terminal output.
Usage:
  python weather.py "Gaborone"
  python weather.py "New York" --units imperial
"""

from __future__ import annotations
import argparse
import sys
import requests
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL  = "https://api.open-meteo.com/v1/forecast"

# Minimal WMO weather code mapping → (emoji, description)
WMO_MAP = {
    0:  ("☀️", "Clear sky"),
    1:  ("🌤️", "Mainly clear"),
    2:  ("⛅", "Partly cloudy"),
    3:  ("☁️", "Overcast"),
    45: ("🌫️", "Fog"),
    48: ("🌫️", "Depositing rime fog"),
    51: ("🌦️", "Light drizzle"),
    53: ("🌦️", "Moderate drizzle"),
    55: ("🌧️", "Dense drizzle"),
    56: ("🌧️", "Light freezing drizzle"),
    57: ("🌧️", "Dense freezing drizzle"),
    61: ("🌦️", "Slight rain"),
    63: ("🌧️", "Moderate rain"),
    65: ("🌧️", "Heavy rain"),
    66: ("🌧️", "Light freezing rain"),
    67: ("🌧️", "Heavy freezing rain"),
    71: ("🌨️", "Slight snowfall"),
    73: ("🌨️", "Moderate snowfall"),
    75: ("❄️",  "Heavy snowfall"),
    77: ("🌨️", "Snow grains"),
    80: ("🌦️", "Rain showers (slight)"),
    81: ("🌧️", "Rain showers (moderate)"),
    82: ("🌧️", "Rain showers (violent)"),
    85: ("🌨️", "Snow showers (slight)"),
    86: ("🌨️", "Snow showers (heavy)"),
    95: ("⛈️", "Thunderstorm (slight/moderate)"),
    96: ("⛈️", "Thunderstorm with slight hail"),
    99: ("⛈️", "Thunderstorm with heavy hail"),
}

def flag_emoji(country_code: Optional[str]) -> str:
    """Return a flag emoji from a 2-letter ISO country code, else empty string."""
    if not country_code or len(country_code) != 2:
        return ""
    return "".join(chr(127397 + ord(c)) for c in country_code.upper())

def geocode(city: str) -> Tuple[float, float, str, Optional[str], Optional[str]]:
    """Look up latitude/longitude for a city using Open-Meteo geocoding (no key)."""
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    r = requests.get(GEO_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        raise SystemExit(f"[error] No results found for '{city}'. Try a larger city or add country (e.g., 'Paris, FR').")
    it = results[0]
    return float(it["latitude"]), float(it["longitude"]), it.get("name",""), it.get("country_code"), it.get("admin1")

def fetch_current_weather(lat: float, lon: float, units: str) -> dict:
    # Map units to Open-Meteo parameters
    temp_unit = "fahrenheit" if units == "imperial" else "celsius"
    wind_unit = "mph" if units == "imperial" else "kmh"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "temperature_unit": temp_unit,
        "windspeed_unit": wind_unit,
        "timezone": "auto",
    }
    r = requests.get(WX_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("current_weather") or {}

def main(argv=None):
    parser = argparse.ArgumentParser(description="Weather by City (Open‑Meteo, no key)")
    parser.add_argument("city", help="City name (e.g., 'Gaborone' or 'Paris, FR')")
    parser.add_argument("--units", choices=["metric", "imperial"], default="metric",
                        help="Units for temperature/wind (default: metric)")
    args = parser.parse_args(argv)

    try:
        lat, lon, pretty_name, country_code, admin1 = geocode(args.city)
        current = fetch_current_weather(lat, lon, args.units)
    except requests.RequestException as e:
        console.print(f"[bold red]Network error:[/bold red] {e}")
        sys.exit(1)
    except SystemExit as e:
        console.print(f"[bold red]{e}[/bold red]")
        sys.exit(2)

    temp = current.get("temperature")
    wind = current.get("windspeed")
    code = int(current.get("weathercode", -1))
    icon, desc = WMO_MAP.get(code, ("❔", "Unknown conditions"))
    unit = "°F" if args.units == "imperial" else "°C"
    wind_unit = "mph" if args.units == "imperial" else "km/h"

    place_bits = [pretty_name]
    if admin1: place_bits.append(admin1)
    flag = flag_emoji(country_code)
    if flag: place_bits.append(flag)
    place = ", ".join(place_bits)

    header = f"{place} — {icon}  {desc}"
    table = Table(show_header=False, box=box.SIMPLE, pad_edge=False)
    table.add_row("Temperature", f"[bold cyan]{temp}{unit}[/bold cyan]")
    if wind is not None:
        table.add_row("Wind", f"{wind} {wind_unit}")
    table.add_row("Coordinates", f"{lat:.3f}, {lon:.3f}")

    console.print(Panel(table, title=header, border_style="cyan", expand=False))

if __name__ == "__main__":
    main()

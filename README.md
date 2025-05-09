# Weather by City CLI

Tiny Python CLI that prints today's weather for a city using the **Open‑Meteo** API (no API key) with a nice Rich output.

## Quick start (Windows / VS Code)

```powershell
# in a folder you like
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python weather.py "Gaborone"
python weather.py "New York" --units imperial
```

## Files

- `weather.py` – the CLI
- `requirements.txt` – dependencies (`requests`, `rich`)

## Example

```
Gaborone — 🌤️  Mainly clear
Temperature  23°C
Wind         11 km/h
Coordinates  -24.654, 25.908
```

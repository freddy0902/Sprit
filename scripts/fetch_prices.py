#!/usr/bin/env python3
"""
Holt den aktuellen Super-E5-Preis fuer zwei feste Tankstellen ueber die
offizielle Tankerkoenig-API (basiert auf den MTS-K-Daten des Bundeskartellamts)
und schreibt das Ergebnis nach data/prices.json.

Die Tankstellen-UUIDs werden beim ersten Lauf automatisch ueber die
Umkreissuche (list.php) anhand von Strasse/Hausnummer/PLZ ermittelt und in
data/station_ids.json zwischengespeichert, damit spaetere Laeufe nur noch
den guenstigen prices.php-Endpunkt brauchen.
"""

import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("TANKERKOENIG_API_KEY")
BASE_URL = "https://creativecommons.tankerkoenig.de/json/"

STATIONS = [
    {
        "key": "dietzenbach",
        "label": "Esso",
        "place": "Dietzenbach",
        "address": "Hauptstr. 7, 63128 Dietzenbach",
        "search_lat": 50.0173,
        "search_lng": 8.7870,
        "match_street": "hauptstr",
        "match_house_number": "7",
        "match_post_code": "63128",
    },
    {
        "key": "bielefeld",
        "label": "12. Mann",
        "place": "Bielefeld",
        "address": "Jakob-Kaiser-Str. 28, 33615 Bielefeld",
        "search_lat": 52.0378,
        "search_lng": 8.51171,
        "match_street": "jakob-kaiser",
        "match_house_number": "28",
        "match_post_code": "33615",
    },
]

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
IDS_FILE = DATA_DIR / "station_ids.json"
PRICES_FILE = DATA_DIR / "prices.json"


def api_get(path, **params):
    params["apikey"] = API_KEY
    url = BASE_URL + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "spritpreise-privat/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def load_ids():
    if IDS_FILE.exists():
        return json.loads(IDS_FILE.read_text(encoding="utf-8"))
    return {}


def save_ids(ids):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IDS_FILE.write_text(json.dumps(ids, indent=2, ensure_ascii=False), encoding="utf-8")


def resolve_station_id(station):
    data = api_get(
        "list.php",
        lat=station["search_lat"],
        lng=station["search_lng"],
        rad=6,
        type="e5",
        sort="dist",
    )
    if not data.get("ok"):
        raise RuntimeError(f"list.php fehlgeschlagen ({station['key']}): {data}")

    for s in data.get("stations", []):
        street_low = (s.get("street") or "").lower()
        house = str(s.get("houseNumber") or "").strip().lower()
        post = str(s.get("postCode") or "")

        street_match = station["match_street"] in street_low
        # Hausnummer steht manchmal im houseNumber-Feld, manchmal direkt in der Strasse
        house_match = house == station["match_house_number"] or station["match_house_number"] in street_low
        post_match = post == station["match_post_code"]

        if street_match and house_match and post_match:
            return s["id"]

    raise RuntimeError(
        f"Keine passende Tankstelle fuer '{station['address']}' in den list.php-Ergebnissen gefunden. "
        "Adresse/Suchradius in fetch_prices.py pruefen."
    )


def main():
    if not API_KEY:
        print("Fehler: Umgebungsvariable TANKERKOENIG_API_KEY ist nicht gesetzt.", file=sys.stderr)
        sys.exit(1)

    # kleine zufaellige Verzoegerung, wie von Tankerkoenig fuer automatisierte
    # Systeme empfohlen (keine Anfragen exakt zu runden Zeiten)
    time.sleep(random.uniform(1, 20))

    ids = load_ids()
    ids_changed = False
    for station in STATIONS:
        if station["key"] not in ids:
            sid = resolve_station_id(station)
            ids[station["key"]] = sid
            ids_changed = True
            print(f"Tankstelle aufgeloest: {station['key']} -> {sid}")
    if ids_changed:
        save_ids(ids)

    all_ids = [ids[s["key"]] for s in STATIONS]
    prices_data = api_get("prices.php", ids=",".join(all_ids))
    if not prices_data.get("ok"):
        raise RuntimeError(f"prices.php fehlgeschlagen: {prices_data}")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result = {"generatedAt": now, "stations": {}}

    for station in STATIONS:
        sid = ids[station["key"]]
        p = prices_data["prices"].get(sid, {})
        result["stations"][station["key"]] = {
            "label": station["label"],
            "place": station["place"],
            "address": station["address"],
            "status": p.get("status"),
            "e5": p.get("e5"),
        }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PRICES_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

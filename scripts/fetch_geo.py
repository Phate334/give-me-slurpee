"""deprecated
"""

import json
import time

import requests

from slurpee.stores import Store711


def fetch_geo(address) -> tuple[float, float]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()

    return res.json()[0]["lat"], res.json()[0]["lon"]


with open("slurpee_stores.json", "r", encoding="utf-8") as f:
    stores_json = json.load(f)
    slurpee_stores = [Store711(**store) for store in stores_json]

for store in slurpee_stores:
    address = store.address
    while address and not store.lat and not store.lon:
        try:
            lat, lon = fetch_geo(address)
            store.lat = float(lat)
            store.lon = float(lon)
            time.sleep(2)
        except IndexError:
            address = address[:-2]

with open("slurpee_stores.json", "w", encoding="utf-8") as f:
    f.write(
        json.dumps([store.model_dump() for store in slurpee_stores], ensure_ascii=False)
    )

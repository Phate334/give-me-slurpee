import json
import re
from urllib.parse import urljoin

from requests_html import HTMLSession

from slurpee.stores import Store711

session = HTMLSession()

url = "https://emap.pcsc.com.tw/"
res = session.get(url)

# 取出縣市代號
scripts = res.html.find("script")
areacode_src = [
    urljoin(res.url, script.attrs.get("src", ""))
    for script in scripts
    if "areacode.js" in script.attrs.get("src", "")
][0]
areacode_script = session.get(areacode_src)
pattern = r"""new AreaNode\('(.*?)', new bu\(.*?\), '(.*?)'\)"""
matches = re.findall(pattern, areacode_script.text)
city_code = {location: code for location, code in matches}

# TODO: 取出側邊欄的思樂冰代號
# slurpee_menu = res.html.find("table#menu_tb", first=True).find(
#     "div", containing="思樂冰", first=True
# )
# slurpee_menu_code = slurpee_menu.attrs.get("id", "").split("_")[-1]
slurpee_menu_code = "06"

# 搜尋結果>縣市
url = "https://emap.pcsc.com.tw/EMapSDK.aspx"
res = session.post(
    url,
    data={"commandid": "SearchArea", "leftMenuChecked": "06", "address": ""},
)

slurpee_stores = []
for areaName in res.html.find("areaname"):
    # 搜尋縣市>地區
    city_id = city_code.get(areaName.text, "")
    if city_id:
        town_res = session.post(
            url,
            data={
                "commandid": "GetTown",
                "cityid": city_id,
                "leftMenuChecked": slurpee_menu_code,
            },
        )
        # 搜尋地區>店家
        for town in town_res.html.find("TownName"):
            store_res = session.post(
                url,
                data={
                    "commandid": "SearchStore",
                    "city": areaName.text,
                    "town": town.text,
                    "leftMenuChecked": slurpee_menu_code,
                    "roadname": "",
                    "ID": "",
                    "StoreName": "",
                    "SpecialStore_Kind": "",
                    "address": "",
                },
            )
            store_res.raise_for_status()
            stores = store_res.html.find("GeoPosition")
            for store in stores:
                store_name = store.find("POIName", first=True).text
                store_address = store.find("Address", first=True).text
                store_lat = float(store.find("Y", first=True).text) / 1000000
                store_lon = float(store.find("X", first=True).text) / 1000000
                slurpee_stores.append(
                    Store711(
                        name=store_name,
                        address=store_address,
                        lat=store_lat,
                        lon=store_lon,
                    )
                )

with open("slurpee_stores.json", "w", encoding="utf-8") as f:
    f.write(
        json.dumps([store.model_dump() for store in slurpee_stores], ensure_ascii=False)
    )

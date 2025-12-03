import requests
import json
import sqlite3
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
params = {
    "Authorization": "CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F",
    "downloadType": "WEB",
    "format": "JSON"
}

response = requests.get(url, params=params, verify=False)
data = response.json()

weather_data = data["cwaopendata"]["resources"]["resource"]["data"] \
                ["agrWeatherForecasts"]["weatherForecasts"]["location"]

records = []

for loc in weather_data:
    area = loc["locationName"]

    maxT = loc["weatherElements"]["MaxT"]["daily"]
    minT = loc["weatherElements"]["MinT"]["daily"]

    for i in range(len(maxT)):
        date = maxT[i]["dataDate"]
        maxt = maxT[i]["temperature"]
        mint = minT[i]["temperature"]
        records.append((area, date, maxt, mint))

conn = sqlite3.connect("sqlitedata.db")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS temperature_daily(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area TEXT,
        date TEXT,
        maxT TEXT,
        minT TEXT
    )
""")

cur.executemany("""
    INSERT INTO temperature_daily(area, date, maxT, minT)
    VALUES (?, ?, ?, ?)
""", records)

conn.commit()
conn.close()

print("Saved", len(records), "rows into sqlitedata.db")

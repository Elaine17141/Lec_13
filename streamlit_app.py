import sqlite3
import json
import requests
import urllib3
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from datetime import datetime
import pandas as pd
import streamlit as st
import altair as alt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "sqlitedata.db"
CWA_API_URL = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
CWA_PARAMS = {
    "Authorization": "CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F",
    "downloadType": "WEB",
    "format": "JSON",
}

app = Flask(__name__, static_folder=str(APP_DIR / "static"), static_url_path="")


def load_db():
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT area, date, maxT, minT FROM temperature_daily")
    rows = cur.fetchall()
    conn.close()
    records = []
    for area, date_s, maxT, minT in rows:
        # normalize
        try:
            dt = datetime.fromisoformat(date_s)
            date_iso = dt.isoformat()
        except Exception:
            date_iso = date_s
        try:
            maxv = float(maxT) if maxT is not None else None
        except Exception:
            maxv = None
        try:
            minv = float(minT) if minT is not None else None
        except Exception:
            minv = None
        records.append({"area": area, "date": date_iso, "maxT": maxv, "minT": minv})
    return records


# simple cache for coords to avoid repeated remote calls
_COORDS_CACHE = None


def fetch_coords():
    global _COORDS_CACHE
    if _COORDS_CACHE is not None:
        return _COORDS_CACHE
    try:
        r = requests.get(CWA_API_URL, params=CWA_PARAMS, verify=False, timeout=10)
        r.raise_for_status()
        payload = r.json()
    except Exception:
        _COORDS_CACHE = {}
        return _COORDS_CACHE

    # defensive traversal for "location" list
    def find_locations(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "location" and isinstance(v, list):
                    return v
                res = find_locations(v)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = find_locations(item)
                if res:
                    return res
        return None

    locations = find_locations(payload) or []
    mapping = {}
    for loc in locations:
        name = loc.get("locationName")
        lat = loc.get("lat") or loc.get("latitude") or None
        lon = loc.get("lon") or loc.get("longitude") or None
        # try nested
        if (lat is None or lon is None):
            for v in loc.values():
                if isinstance(v, dict):
                    if v.get("lat") and v.get("lon"):
                        lat = v.get("lat"); lon = v.get("lon")
        try:
            if name and lat is not None and lon is not None:
                mapping[name] = {"lat": float(lat), "lon": float(lon)}
        except Exception:
            continue
    _COORDS_CACHE = mapping
    return mapping


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/locations")
def api_locations():
    records = load_db()
    coords = fetch_coords()
    # compute latest per area
    latest = {}
    for r in records:
        a = r["area"]
        d = r["date"]
        if a not in latest or (d and latest[a]["date"] and d > latest[a]["date"]):
            latest[a] = r
    out = []
    for area, rec in latest.items():
        coord = coords.get(area, {})
        out.append(
            {
                "area": area,
                "date": rec.get("date"),
                "maxT": rec.get("maxT"),
                "minT": rec.get("minT"),
                "lat": coord.get("lat"),
                "lon": coord.get("lon"),
            }
        )
    return jsonify(out)


@app.route("/api/area")
def api_area():
    area = request.args.get("area")
    if not area:
        return jsonify({"error": "missing area parameter"}), 400
    records = [r for r in load_db() if r["area"] == area]
    # sort by date ascending
    try:
        records.sort(key=lambda x: x["date"])
    except Exception:
        pass
    return jsonify(records)


@st.cache_data
def load_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    if not db_path.exists():
        return pd.DataFrame(columns=["area", "date", "maxT", "minT"])
    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql_query(
        "SELECT area, date, maxT, minT FROM temperature_daily", conn
    )
    conn.close()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["maxT"] = pd.to_numeric(df["maxT"], errors="coerce")
    df["minT"] = pd.to_numeric(df["minT"], errors="coerce")
    return df


def main():
    st.set_page_config(page_title="Taiwan Temperature", layout="wide")
    st.title("Taiwan Temperature Dashboard")
    
    df = load_data()
    if df.empty:
        st.warning("No data. Run `python sqlite.py` first.")
        return
    
    locations = ["All"] + sorted(df["area"].dropna().unique().tolist())
    selected = st.sidebar.selectbox("Select location", locations)
    
    if selected == "All":
        view = df.copy()
    else:
        view = df[df["area"] == selected].copy()
    
    st.subheader(f"Records: {len(view)} — {selected}")
    st.dataframe(view.sort_values("date", ascending=False), use_container_width=True)
    
    if not view.empty:
        ts_melt = view.melt(id_vars=["date"], value_vars=["maxT", "minT"], var_name="type", value_name="temperature")
        chart = (
            alt.Chart(ts_melt)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("temperature:Q", title="Temperature (°C)"),
                color="type:N",
                tooltip=["date:T", "type:N", "temperature:Q"],
            )
            .interactive()
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    main()
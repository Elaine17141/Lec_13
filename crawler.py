import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
params = {
    "Authorization": "CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F",
    "downloadType": "WEB",
    "format": "JSON"
}

try:
    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()

    data = response.json()

    print(json.dumps(data, indent=2))

    with open("cwa_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Data saved to cwa_data.json successfully.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")

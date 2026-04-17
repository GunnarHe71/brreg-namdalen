import requests

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

r = requests.get(BASE_URL, params={"size": 10})
data = r.json()

for e in data.get("_embedded", {}).get("enheter", []):
    print(e.get("navn"), e.get("registreringsdato"))

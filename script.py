import requests

URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

params = {
    "size": 20,
    "sort": "registreringsdato,desc"
}

r = requests.get(URL, params=params)
data = r.json()

enheter = data.get("_embedded", {}).get("enheter", [])

print("---- SISTE REGISTRERTE ----")

for e in enheter:
    navn = e.get("navn", "Ukjent")
    dato = e.get("registreringsdato", "Ingen dato")
    print(navn, "-", dato)

print("---------------------------")

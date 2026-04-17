import requests
from datetime import datetime, timedelta

URL = "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter"

def hent():
    r = requests.get(URL + "?size=50")
    data = r.json()
    return data.get("_embedded", {}).get("oppdaterteEnheter", [])


if __name__ == "__main__":
    now = datetime.now()
    grense = now - timedelta(days=30)

    enheter = hent()

    print("---- SISTE ENDRINGER ----")

    treff = 0
    for e in enheter:
        dato_str = e.get("oppdateringsdato")
        if not dato_str:
            continue

        dato = datetime.fromisoformat(dato_str.replace("Z", "+00:00"))

        if dato > grense:
            print(e.get("navn"), "-", dato_str)
            treff += 1

    if treff == 0:
        print("Ingen funnet (uvanlig)")

    print("-------------------------")

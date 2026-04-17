import requests
from datetime import datetime, timedelta

URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

def hent_alle():
    liste = []
    url = URL + "?size=100"

    while url:
        r = requests.get(url)
        data = r.json()

        enheter = data.get("_embedded", {}).get("enheter", [])
        if not enheter:
            break

        for e in enheter:
            liste.append(e)

        url = data.get("_links", {}).get("next", {}).get("href")

    return liste


if __name__ == "__main__":
    now = datetime.now()
    grense = now - timedelta(days=30)

    alle = hent_alle()

    print("---- RESULTAT ----")

    treff = 0
    for e in alle:
        dato_str = e.get("registreringsdato")
        if not dato_str:
            continue

        dato = datetime.fromisoformat(dato_str.replace("Z", "+00:00"))

        if dato > grense:
            print(e.get("navn"), "-", dato_str)
            treff += 1

    if treff == 0:
        print("Ingen funnet (men scriptet fungerer)")

    print("------------------")

import requests
from datetime import datetime, timedelta

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

NAMDAL_KOMMUNER = {
    "NAMSOS", "NAMSSKOGAN", "GRONG", "HØYLANDET",
    "OVERHALLA", "FLATANGER", "LIERNE", "RØYRVIK",
    "NÆRØYSUND"
}

def hent(sist):
    liste = []
    url = BASE_URL
    params = {
        "size": 100,
        "sort": "registreringsdatoEnhetsregisteret,desc"
    }

    while url:
        r = requests.get(url, params=params)
        data = r.json()

        if "_embedded" not in data:
            print("DEBUG:", data)
            break

        for enhet in data["_embedded"]["enheter"]:

            dato_str = enhet.get("registreringsdatoEnhetsregisteret")
            if not dato_str:
                continue

            dato = datetime.fromisoformat(dato_str.replace("Z", "+00:00"))

            # ENESTE ENDRING:
            if dato.replace(tzinfo=None) < sist:
                return liste

            adr = enhet.get("forretningsadresse", {})
            kommune = adr.get("kommune", "").upper()

            if kommune not in NAMDAL_KOMMUNER:
                continue

            adresse = " ".join(adr.get("adresse", [])) if adr else "Ukjent"

            liste.append({
                "navn": enhet.get("navn"),
                "dato": dato_str,
                "adresse": adresse,
                "kommune": kommune
            })

        next_link = data["_links"].get("next", {}).get("href")
        if next_link:
            url = next_link
            params = None
        else:
            url = None

    return liste


if __name__ == "__main__":
    now = datetime.now()
    sist = now - timedelta(days=30)

    nye = hent(sist)

    nye.sort(key=lambda x: x["dato"], reverse=True)
    nye.sort(key=lambda x: x["kommune"])

    print("---- NYE FORETAK (30 DAGER) ----")

    if nye:
        current_kommune = None
        for x in nye:
            if x["kommune"] != current_kommune:
                current_kommune = x["kommune"]
                print(f"\n{current_kommune}")

            print(f"{x['dato']} | {x['navn']} | {x['adresse']}")
    else:
        print("Ingen nye foretak funnet")

    print("--------------------------------")

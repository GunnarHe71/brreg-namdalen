import requests
from datetime import datetime, timedelta

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

NAMDAL_KOMMUNER = {
    "NAMSOS", "NAMSSKOGAN", "GRONG", "HØYLANDET",
    "OVERHALLA", "FLATANGER", "LIERNE", "RØYRVIK", "NÆRØYSUND"
}

def hent():
    grense = datetime.now() - timedelta(days=30)

    url = BASE_URL
    params = {
        "size": 100,
        "sort": "registreringsdato,desc"
    }

    resultater = []

    while url:
        r = requests.get(url, params=params)
        data = r.json()

        enheter = data.get("_embedded", {}).get("enheter", [])
        if not enheter:
            break

        for e in enheter:
            dato_str = e.get("registreringsdato")
            if not dato_str:
                continue

            dato = datetime.fromisoformat(dato_str.replace("Z", "+00:00"))

            # stopp når vi er utenfor 30 dager
            if dato < grense:
                return resultater

            adr = e.get("forretningsadresse") or e.get("postadresse")
            if not adr:
                continue

            kommune = adr.get("kommune", "").upper()
            if kommune not in NAMDAL_KOMMUNER:
                continue

            adresse = adr.get("adresse", [""])[0]

            resultater.append({
                "navn": e.get("navn"),
                "dato": dato_str[:10],
                "adresse": adresse,
                "kommune": kommune
            })

        # paging
        url = data.get("_links", {}).get("next", {}).get("href")
        params = None

    return resultater


if __name__ == "__main__":
    nye = hent()

    print("---- NYE FORETAK (30 DAGER) ----")

    if nye:
        for e in nye:
            print(f"{e['dato']} | {e['navn']} | {e['adresse']} | {e['kommune']}")
    else:
        print("Ingen nye foretak funnet")

    print("--------------------------------")

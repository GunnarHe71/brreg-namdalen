import requests
from datetime import datetime, timedelta

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

NAMDAL_KOMMUNER = [
    "NAMSOS", "NAMSSKOGAN", "GRONG", "HØYLANDET",
    "OVERHALLA", "FLATANGER", "LIERNE", "RØYRVIK", "NÆRØYSUND"
]

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

            # stopp når vi er eldre enn 30 dager
            if dato < grense:
                return resultater

            adr = e.get("forretningsadresse") or e.get("postadresse")
            if not adr:
                continue

            kommune_raw = adr.get("kommune", "")
            kommune = kommune_raw.upper()

            # robust matching (tåler "Namsos kommune" osv.)
            if not any(k in kommune for k in NAMDAL_KOMMUNER):
                continue

            adresse_liste = adr.get("adresse", [])
            adresse = adresse_liste[0] if adresse_liste else ""

            resultater.append({
                "dato": dato_str[:10],
                "navn": e.get("navn", ""),
                "adresse": adresse,
                "kommune": kommune_raw
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

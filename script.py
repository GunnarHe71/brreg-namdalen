import requests
from datetime import datetime, timedelta

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

NAMDAL_KOMMUNER = [
    "NAMSOS", "NAMSSKOGAN", "GRONG", "HØYLANDET",
    "OVERHALLA", "FLATANGER", "LIERNE", "RØYRVIK", "NÆRØYSUND"
]

def parse_dato(e):
    # prøv riktige felt i prioritert rekkefølge
    for felt in [
        "registreringsdatoEnhetsregisteret",
        "stiftelsesdato",
        "registreringsdato"
    ]:
        d = e.get(felt)
        if d:
            try:
                return datetime.fromisoformat(d.replace("Z", "+00:00"))
            except:
                pass
    return None


def hent():
    grense = datetime.now() - timedelta(days=30)

    url = BASE_URL
    params = {
        "size": 100,
        "sort": "registreringsdatoEnhetsregisteret,desc"
    }

    resultater = []

    while url:
        r = requests.get(url, params=params)
        data = r.json()

        enheter = data.get("_embedded", {}).get("enheter", [])
        if not enheter:
            break

        for e in enheter:
            dato = parse_dato(e)
            if not dato:
                continue

            # stopp når vi går for langt tilbake
            if dato < grense:
                return resultater

            adr = e.get("forretningsadresse") or e.get("postadresse")
            if not adr:
                continue

            kommune_raw = adr.get("kommune", "")
            kommune = kommune_raw.upper()

            if not any(k in kommune for k in NAMDAL_KOMMUNER):
                continue

            adresse = ""
            if adr.get("adresse"):
                adresse = adr["adresse"][0]

            resultater.append({
                "dato": dato.strftime("%Y-%m-%d"),
                "navn": e.get("navn", ""),
                "adresse": adresse,
                "kommune": kommune_raw
            })

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

    print("--------------------------------")Husker akta
a

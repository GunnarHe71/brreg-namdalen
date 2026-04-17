import requests
from datetime import datetime, timedelta

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

NAMDAL_KOMMUNER = {
    "NAMSOS", "NAMSSKOGAN", "GRONG", "HØYLANDET",
    "OVERHALLA", "FLATANGER", "LIERNE", "RØYRVIK", "NÆRØYSUND"
}

def hent():
    fra_dato = (datetime.now() - timedelta(days=30)).date().isoformat()

    params = {
        "registreringsdatoFra": fra_dato,
        "size": 100
    }

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    liste = []

    for enhet in data.get("_embedded", {}).get("enheter", []):
        adr = enhet.get("forretningsadresse")
        if not adr:
            continue

        kommune = adr.get("kommune", "").upper()
        if kommune in NAMDAL_KOMMUNER:
            liste.append(enhet["navn"])

    return liste


if __name__ == "__main__":
    nye = hent()

    print("---- RESULTAT ----")
    if nye:
        for navn in nye:
            print(navn)
    else:
        print("Ingen nye foretak siste 30 dager")
    print("------------------")

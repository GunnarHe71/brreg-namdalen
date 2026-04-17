import requests
from datetime import datetime, timedelta

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

NAMDAL_KOMMUNER = {
    "NAMSOS", "NAMSSKOGAN", "GRONG", "HØYLANDET",
    "OVERHALLA", "FLATANGER", "LIERNE", "RØYRVIK", "NÆRØYSUND"
}


def hent(sist):
    liste = []
    url = BASE_URL
    params = {
        "size": 100,
        "sort": "registreringsdato,desc"
    }

    while url:
        r = requests.get(url, params=params)
        data = r.json()

        enheter = data.get("_embedded", {}).get("enheter", [])
        if not enheter:
            break

        for enhet in enheter:
            adresse = enhet.get("forretningsadresse") or enhet.get("postadresse")
            if not adresse:
                continue

            kommune = adresse.get("kommune", "").upper()
            if kommune not in NAMDAL_KOMMUNER:
                continue

            dato_str = enhet.get("registreringsdato")
            if not dato_str:
                continue

            dato = datetime.fromisoformat(dato_str.replace("Z", "+00:00"))

            if dato > sist:
                liste.append({
                    "navn": enhet["navn"],
                    "dato": dato_str
                })
            else:
                return liste

        next_link = data.get("_links", {}).get("next", {}).get("href")
        if next_link:
            url = next_link
            params = None
        else:
            url = None

    return liste


if __name__ == "__main__":
    now = datetime.now()
    sist = now - timedelta(days=7)

    nye = hent(sist)

    print("---- RESULTAT ----")
    if nye:
        for x in nye:
            print(x["navn"], "-", x["dato"])
    else:
        print("Ingen nye foretak siste 7 dager")
    print("------------------")

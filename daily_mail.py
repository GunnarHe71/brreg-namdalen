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
    sett = set()
    url = BASE_URL
    params = {
        "size": 100,
        "sort": "registreringsdatoEnhetsregisteret,desc"
    }

    while url:
        r = requests.get(url, params=params)
        data = r.json()

        if "_embedded" not in data:
            break

        for enhet in data["_embedded"]["enheter"]:

            orgnr = enhet.get("organisasjonsnummer")
            if not orgnr or orgnr in sett:
                continue
            sett.add(orgnr)

            dato_str = enhet.get("registreringsdatoEnhetsregisteret")
            if not dato_str:
                continue

            dato = datetime.fromisoformat(dato_str.replace("Z", "+00:00"))

            if dato.replace(tzinfo=None) < sist:
                return liste

            adr = enhet.get("forretningsadresse", {})
            kommune = adr.get("kommune", "").upper()

            if kommune not in NAMDAL_KOMMUNER:
                continue

            adresse_linje = " ".join(adr.get("adresse", []))
            postnr = adr.get("postnummer", "")
            poststed = adr.get("poststed", "")

            adresse = f"{adresse_linje}, {postnr} {poststed}".strip(", ")

            liste.append({
                "navn": enhet.get("navn"),
                "orgnr": orgnr,
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


def main():
    now = datetime.now()
    sist = now - timedelta(days=1)

    nye = hent(sist)

    nye.sort(key=lambda x: x["kommune"])

    print("---- NYE FORETAK (SISTE DØGN) ----")

    if nye:
        current_kommune = None
        for x in nye:
            if x["kommune"] != current_kommune:
                current_kommune = x["kommune"]
                print(f"\n{current_kommune}")

            print(f"{x['dato']} | {x['navn']} ({x['orgnr']}) | {x['adresse']}")
    else:
        print("Ingen nye foretak siste døgn")

    print("---------------------------------")


if __name__ == "__main__":
    main()

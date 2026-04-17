import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"

NAMDAL_KOMMUNER = {
    "NAMSOS", "NAMSSKOGAN", "GRONG", "HØYLANDET",
    "OVERHALLA", "FLATANGER", "LIERNE", "RØYRVIK",
    "NÆRØYSUND"
}


def parse_iso_datetime(dato_str):
    try:
        return datetime.fromisoformat(dato_str.replace("Z", "+00:00"))
    except Exception:
        return None


def hent(sist):
    liste = []
    url = BASE_URL
    params = {
        "size": 100,
        "sort": "registreringsdatoEnhetsregisteret,desc"
    }

    session = requests.Session()

    while url:
        try:
            r = session.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"Feil ved henting av data: {e}")
            break

        enheter = data.get("_embedded", {}).get("enheter", [])
        if not enheter:
            break

        for enhet in enheter:
            dato_str = enhet.get("registreringsdatoEnhetsregisteret")
            if not dato_str:
                continue

            dato = parse_iso_datetime(dato_str)
            if not dato:
                continue

            if dato < sist:
                return liste

            adr = enhet.get("forretningsadresse") or {}
            kommune = adr.get("kommune", "").strip().upper()

            if kommune not in NAMDAL_KOMMUNER:
                continue

            adresse = " ".join(adr.get("adresse", [])) if adr else "Ukjent"

            liste.append({
                "navn": enhet.get("navn", "Ukjent navn"),
                "dato": dato,
                "adresse": adresse,
                "kommune": kommune
            })

        next_link = data.get("_links", {}).get("next", {}).get("href")
        if next_link:
            url = next_link
            params = None
        else:
            url = None

    return liste


def main():
    now = datetime.now(timezone.utc)
    sist = now - timedelta(days=30)

    nye = hent(sist)

    nye.sort(key=lambda x: (x["kommune"], -x["dato"].timestamp()))

    print("---- NYE FORETAK (30 DAGER) ----")

    if nye:
        current_kommune = None

        for x in nye:
            if x["kommune"] != current_kommune:
                current_kommune = x["kommune"]
                print(f"\n{current_kommune}")

            dato_fmt = x["dato"].strftime("%Y-%m-%d")

            print(f"{dato_fmt} | {x['navn']} | {x['adresse']}")
    else:
        print("Ingen nye foretak funnet")

    print("--------------------------------")


if __name__ == "__main__":
    main()
    

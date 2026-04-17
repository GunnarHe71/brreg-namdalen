import requests
import os
import smtplib
from email.mime.text import MIMEText
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


def lag_melding(nye):
    if not nye:
        return "Ingen nye foretak siste døgn."

    nye.sort(key=lambda x: x["kommune"])

    linjer = []
    current_kommune = None

    for x in nye:
        if x["kommune"] != current_kommune:
            current_kommune = x["kommune"]
            linjer.append(f"\n{current_kommune}")

        linjer.append(f"{x['dato']} | {x['navn']} ({x['orgnr']}) | {x['adresse']}")

    return "\n".join(linjer)


def send_epost(innhold):
    SMTP_SERVER = "smtp.office365.com"
    SMTP_PORT = 587

    SMTP_USER = os.environ.get("EMAIL_USER")
    SMTP_PASS = os.environ.get("EMAIL_PASS")

    msg = MIMEText(innhold)
    msg["Subject"] = "Nye foretak siste døgn (Namdalen)"
    msg["From"] = SMTP_USER
    msg["To"] = "gunnarhemming@hotmail.com"

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def main():
    now = datetime.now()
    sist = now - timedelta(days=1)

    nye = hent(sist)
    melding = lag_melding(nye)

    send_epost(melding)
    print(melding)


if __name__ == "__main__":
    main()
    

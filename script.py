import requests
from datetime import datetime
import json
import os
import smtplib
from email.mime.text import MIMEText

BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"
STATE_FILE = "state.json"

NAMDAL_KOMMUNER = {
    "NAMSOS","NAMSSKOGAN","GRONG","HØYLANDET",
    "OVERHALLA","FLATANGER","LIERNE","RØYRVIK","NÆRØYSUND"
}

EMAIL = "gunnarhemming@hotmail.com"
PASSORD = os.environ["EMAIL_PASS"]


def hent_sist():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return datetime.fromisoformat(json.load(f)["last"])


def lagre(tid):
    with open(STATE_FILE, "w") as f:
        json.dump({"last": tid.isoformat()}, f)


def hent(sist):
    page = 0
    nye = []

    while True:
        r = requests.get(f"{BASE_URL}?page={page}&size=100")
        data = r.json()
        enheter = data.get("_embedded", {}).get("enheter", [])

        if not enheter:
            break

        for e in enheter:
            adr = e.get("forretningsadresse", {})
            kommune = adr.get("kommunenavn", "").upper()
            dato = e.get("registreringsdatoEnhetsregisteret")

            if not dato or kommune not in NAMDAL_KOMMUNER:
                continue

            dato_dt = datetime.fromisoformat(dato)

            if sist is None or dato_dt > sist:
                nye.append(f"{dato} - {e['navn']} ({kommune})")

        page += 1

    return nye


def send(liste):
    tekst = "\n".join(liste) if liste else "Ingen nye foretak"

    msg = MIMEText(tekst)
    msg["Subject"] = "Nye foretak Namdalen"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    #with smtplib.SMTP("smtp.office365.com", 587) as s:
    #    s.starttls()
    #    s.login(EMAIL, PASSORD)
    #    s.send_message(msg)


if __name__ == "__main__":
    now = datetime.now()
    sist = hent_sist()

    nye = hent(sist)

    print("---- RESULTAT ----")
    if nye:
        for x in nye:
            print(x["navn"])
    else:
        print("Ingen nye foretak")
    print("------------------")

    send(nye)
    lagre(now)

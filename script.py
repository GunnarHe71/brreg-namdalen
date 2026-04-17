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
    liste = []
    url = BASE_URL
    params = {
        "size": 100,
        "sort": "registreringsdato,desc"
    }

    while url:
        r = requests.get(url, params=params)
        data = r.json()

        for enhet in data.get("_embedded", {}).get("enheter", []):
            if enhet.get("forretningsadresse") is None:
                continue

            kommune = enhet["forretningsadresse"].get("kommune", "").upper()
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
                # siden vi sorterer desc kan vi stoppe her
                return liste

        # paging
        next_link = data.get("_links", {}).get("next", {}).get("href")
        if next_link:
            url = next_link
            params = None  # viktig: ikke send params på neste kall
        else:
            url = None

    return liste


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


from datetime import timedelta

if __name__ == "__main__":
    now = datetime.now()
    sist = now - timedelta(days=7)

    nye = hent(sist)

    print("---- RESULTAT ----")
    if nye:
        for x in nye:
            print(x["navn"])
    else:
        print("Ingen nye foretak")
    print("------------------")

from flask import Flask, render_template, request
import pandas as pd
import smtplib
import os
from email.mime.text import MIMEText

app = Flask(__name__)

CSV_FILE = "donnees_etudiants.csv"

# CONFIGURATION EMAIL VIA VARIABLES D'ENVIRONNEMENT
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")


def envoyer_mail(destinataire, rattrapages, classement, moyenne):
    sujet = "Vos résultats"
    corps = f"""Bonjour,

Voici vos informations :

Rattrapages : {rattrapages}
Classement provisoire : {classement}
Moyenne : {moyenne}

Cordialement
"""

    msg = MIMEText(corps, "plain", "utf-8")
    msg["Subject"] = sujet
    msg["From"] = SENDER_EMAIL
    msg["To"] = destinataire

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        try:
            df = pd.read_csv(CSV_FILE, sep=";")
            df.columns = df.columns.str.strip()
            df["email"] = df["email"].astype(str).str.strip().str.lower()

            ligne = df[df["email"] == email]

            if not ligne.empty:
                rattrapages = ligne.iloc[0]["Rattrapages"]
                classement = ligne.iloc[0]["classement_provisoire"]
                moyenne = ligne.iloc[0]["moyenne"]

                envoyer_mail(email, rattrapages, classement, moyenne)

            message = "Si cette adresse figure dans notre base, un email a été envoyé."

        except Exception as e:
            print("Erreur :", e)
            message = "Une erreur technique est survenue."

    return render_template("index.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)
"""
POSTE CLIENT - Application web de login (multi-template)
----------------------------------------------------------------
Lancement :
    pip install flask
    python3 client_app.py

Au démarrage, le script demande quel TYPE DE PLATEFORME simuler
(coffre crypto, paiement en ligne, console serveur, webmail,
réseau social...). L'objectif est de montrer que la même faille
peut se cacher derrière n'importe quelle interface du quotidien —
"le danger est partout", pas seulement sur les sites qui "ont l'air"
sensibles.

Faille pédagogique IDENTIQUE sur tous les templates :
    /backup/users.txt expose le hash MD5 du mot de passe choisi.

La liste des templates disponibles vient de templates_site/ : pour
en ajouter un, voir templates_site/__init__.py.
"""

from flask import Flask, request, redirect, session, render_template_string
import hashlib
import os

from templates_site import TEMPLATES

app = Flask(__name__)
app.secret_key = os.urandom(16)

USERS_FILE = "users.txt"
ADMIN_LOGIN = "admin"


def choisir_template():
    print("\n=== Choix de la plateforme à simuler ===")
    for cle, tpl in TEMPLATES.items():
        print(f"  {cle}. {tpl.NOM:<12} — {tpl.DESCRIPTION}")
    while True:
        choix = input(f"\nTon choix ({'/'.join(TEMPLATES.keys())}) : ").strip()
        if choix in TEMPLATES:
            return TEMPLATES[choix]
        print("Choix invalide, réessaie.")


# Le template actif est choisi une fois, au lancement du script
TPL = choisir_template()


# ═══════════════════════════════════════════════════════════════════════
#  LOGIQUE BACKEND (identique quel que soit le template choisi)
# ═══════════════════════════════════════════════════════════════════════
def users_file_exists():
    return os.path.exists(USERS_FILE)


def write_user_hash(login, password):
    h = hashlib.md5(password.encode()).hexdigest()
    with open(USERS_FILE, "w") as f:
        f.write(f"{login}:{h}\n")


def check_password(login, password):
    if not users_file_exists():
        return False
    with open(USERS_FILE) as f:
        for line in f:
            u, h = line.strip().split(":")
            if u == login and hashlib.md5(password.encode()).hexdigest() == h:
                return True
    return False


@app.route("/", methods=["GET", "POST"])
def index():
    if not users_file_exists():
        if request.method == "POST":
            pwd = request.form["password"]
            write_user_hash(ADMIN_LOGIN, pwd)
            return redirect("/")
        return render_template_string(TPL.SETUP_PAGE)

    if session.get("logged_in"):
        return render_template_string(TPL.DASHBOARD_PAGE, login=ADMIN_LOGIN)

    error = None
    if request.method == "POST":
        login = request.form["login"]
        pwd = request.form["password"]
        if check_password(login, pwd):
            session["logged_in"] = True
            return redirect("/")
        error = "Identifiants invalides."
    return render_template_string(TPL.LOGIN_PAGE, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# --- Faille simulée : backup de la base de comptes oublié en accès libre ---
@app.route("/backup/users.txt")
def backup_leak():
    if not users_file_exists():
        return "Aucun compte configuré.", 404
    with open(USERS_FILE) as f:
        return f.read(), 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    if users_file_exists():
        os.remove(USERS_FILE)
        print(f"{USERS_FILE} supprimé (reset avant lancement).")
    print(f"\n[+] Plateforme choisie : {TPL.NOM} — {TPL.DESCRIPTION}")
    print("Client démarré sur http://0.0.0.0:5000")
    print("Faille de démo exposée sur /backup/users.txt (format John: login:hash)")
    app.run(host="0.0.0.0", port=5000, debug=False)

"""
Registre des templates de plateforme simulée pour la démo bruteforce.

Chaque template est un module exposant :
    NOM, DESCRIPTION, SETUP_PAGE, LOGIN_PAGE, DASHBOARD_PAGE

Pour ajouter un nouveau template (ex. "reseau administratif d'école",
"boutique en ligne"...) :
  1. Crée templates_site/mon_site.py en copiant un template existant
     (coffre_crypto.py est le plus court).
  2. Personnalise NOM, DESCRIPTION, icon, tagline, login_label,
     dashboard_title et dashboard_rows.
  3. Ajoute-le dans TEMPLATES ci-dessous avec une clé courte.

La faille pédagogique (/backup/users.txt expose le hash MD5) et la
logique Flask sont entièrement partagées dans client_app.py : un
nouveau template ne change QUE l'apparence et les textes, jamais la
mécanique de l'attaque.
"""

from . import coffre_crypto, paiement, serveur_admin, webmail, reseau_social

TEMPLATES = {
    "1": coffre_crypto,
    "2": paiement,
    "3": serveur_admin,
    "4": webmail,
    "5": reseau_social,
}

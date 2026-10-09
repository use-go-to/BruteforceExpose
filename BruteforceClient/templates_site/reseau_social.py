from ._base import build_style, build_pages

NOM = "SocialHub"
DESCRIPTION = "Réseau social — profil privé, messages et historique de connexion"

STYLE = build_style(accent="#a855f7", accent2="#ec4899", bg0="#0a0510")

SETUP_PAGE, LOGIN_PAGE, DASHBOARD_PAGE = build_pages(
    nom="SocialHub",
    icon="👥",
    tagline="Connecte-toi à ton compte",
    login_label="Nom d'utilisateur",
    dashboard_title="Mon profil",
    dashboard_rows=[
        ("Messages privés non lus", "9"),
        ("Dernière localisation partagée", "Rennes, FR — il y a 2 h"),
        ("Photos privées", "214 photos, 18 albums"),
        ("Visibilité du profil", "Public ⚠️"),
        ("Appareils connectés", "iPhone, PC portable"),
    ],
    style=STYLE,
)

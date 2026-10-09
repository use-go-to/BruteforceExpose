from ._base import build_style, build_pages

NOM = "ServerOps"
DESCRIPTION = "Console d'administration serveur / cloud — type VPS ou hébergeur"

STYLE = build_style(accent="#2f6fed", accent2="#7c5cff", bg0="#05070d")

SETUP_PAGE, LOGIN_PAGE, DASHBOARD_PAGE = build_pages(
    nom="ServerOps",
    icon="🖥️",
    tagline="Console d'administration du serveur",
    login_label="Identifiant root",
    dashboard_title="Console serveur",
    dashboard_rows=[
        ("Uptime", "214 jours"),
        ("Charge CPU", "12 % — 8 vCPU"),
        ("Mémoire utilisée", "3.1 / 16 Go"),
        ("Services actifs", "nginx, postgres, redis"),
        ("Dernière connexion SSH", "10.192.21.4 — il y a 3 min"),
    ],
    style=STYLE,
)

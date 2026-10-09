from ._base import build_style, build_pages

NOM = "MailCore"
DESCRIPTION = "Webmail professionnel — faux client mail d'entreprise"

STYLE = build_style(accent="#e5533d", accent2="#ffb020", bg0="#120705")

SETUP_PAGE, LOGIN_PAGE, DASHBOARD_PAGE = build_pages(
    nom="MailCore",
    icon="📧",
    tagline="Votre messagerie professionnelle",
    login_label="Adresse e-mail",
    dashboard_title="Boîte de réception",
    dashboard_rows=[
        ("Messages non lus", "37"),
        ("Dernier message reçu", "RH — Note de service interne"),
        ("Pièces jointes récentes", "Contrat_2026.pdf, Badge_acces.pdf"),
        ("Quota de stockage", "8.2 / 50 Go"),
        ("Appareils connectés", "2 — PC bureau, smartphone"),
    ],
    style=STYLE,
)

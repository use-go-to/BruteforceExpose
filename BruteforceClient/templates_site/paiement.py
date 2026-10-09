from ._base import build_style, build_pages

NOM = "PayFlow"
DESCRIPTION = "Plateforme de paiement en ligne — faux espace marchand / bancaire"

STYLE = build_style(accent="#00c389", accent2="#00e5ff", bg0="#04100c")

SETUP_PAGE, LOGIN_PAGE, DASHBOARD_PAGE = build_pages(
    nom="PayFlow",
    icon="💳",
    tagline="Accédez à votre espace marchand",
    login_label="Identifiant marchand",
    dashboard_title="Tableau de bord marchand",
    dashboard_rows=[
        ("Solde disponible", "48 320,00 €"),
        ("Paiements aujourd'hui", "214 transactions"),
        ("Dernier virement sortant", "12 000,00 € — SEPA"),
        ("Carte principale", "•••• •••• •••• 4471"),
        ("Statut du compte", "Vérifié ✅"),
    ],
    style=STYLE,
)

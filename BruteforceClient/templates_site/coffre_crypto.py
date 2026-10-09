from ._base import build_style, build_pages

NOM = "NovaVault"
DESCRIPTION = "Coffre-fort crypto / wallet d'échange — fausses cryptomonnaies"

STYLE = build_style(accent="#00e5ff", accent2="#7c5cff", bg0="#04060c")

SETUP_PAGE, LOGIN_PAGE, DASHBOARD_PAGE = build_pages(
    nom="NovaVault",
    icon="🔐",
    tagline="Votre coffre-fort crypto sécurisé",
    login_label="Identifiant",
    dashboard_title="Portefeuille NovaVault",
    dashboard_rows=[
        ("Solde total", "12.4821 BTC ≈ 742 300 €"),
        ("Dernière transaction", "+0.2841 BTC — il y a 12 min"),
        ("Adresse de réception", "bc1q7f4k…8e2a"),
        ("Double authentification", "Désactivée ⚠️"),
        ("Dernière connexion", "il y a 3 min — réseau local"),
    ],
    style=STYLE,
)

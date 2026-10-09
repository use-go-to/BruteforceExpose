"""
Composants HTML/CSS communs à tous les templates de plateforme simulée.
Chaque template (paiement, serveur, webmail...) ne définit que ses
couleurs, son icône et ses textes : le layout (carte de connexion,
dashboard, badge de succès) est partagé ici pour rester cohérent et
facile à maintenir.

IMPORTANT : le badge du dashboard contient volontairement le texte
"Accès administrateur confirmé" — c'est la chaîne que gui_attacker.py
et attacker.py recherchent dans la réponse HTTP pour confirmer que
l'attaque a réussi. Ne pas la modifier dans un nouveau template sans
mettre à jour les scripts attaquants en conséquence.
"""


def build_style(accent="#2f6fed", accent2="#7c5cff", bg0="#05070d"):
    return f"""
    <style>
      :root{{
        --accent:{accent}; --accent-2:{accent2};
        --bg-0:{bg0}; --bg-1:#0a0e18; --panel:rgba(14,18,30,0.75);
        --border:rgba(255,255,255,0.08); --text:#e9edf7; --muted:#8891a8;
        --success:#28d17c; --danger:#ff5d73;
        --mono:'JetBrains Mono','Consolas',monospace;
        --sans:'Inter','Segoe UI',system-ui,sans-serif;
      }}
      *{{box-sizing:border-box;margin:0;padding:0;}}
      body{{
        font-family:var(--sans); color:var(--text); min-height:100vh;
        background:
          radial-gradient(ellipse 800px 500px at 10% -10%, {accent}2e, transparent 60%),
          radial-gradient(ellipse 900px 600px at 90% 110%, {accent2}28, transparent 60%),
          linear-gradient(160deg, var(--bg-0), var(--bg-1));
      }}
      .wrap{{min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px;}}
      .card{{
        width:420px; padding:38px 34px; background:var(--panel);
        backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
        border:1px solid var(--border); border-radius:20px;
        box-shadow:0 30px 70px rgba(0,0,0,0.55);
        animation:rise .5s ease both;
      }}
      @keyframes rise{{from{{opacity:0; transform:translateY(14px);}}to{{opacity:1; transform:translateY(0);}}}}
      .icon{{font-size:32px; text-align:center; margin-bottom:12px;}}
      h1{{font-size:19px; text-align:center; margin-bottom:4px;}}
      .subtitle{{color:var(--muted); font-size:13px; text-align:center; margin-bottom:24px;}}
      .field{{margin-bottom:16px;}}
      label{{display:block; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px;}}
      input{{
        width:100%; padding:12px 14px; border-radius:10px;
        border:1px solid var(--border); background:rgba(0,0,0,0.3);
        color:var(--text); font-size:14px; font-family:var(--mono); outline:none;
      }}
      input:focus{{border-color:var(--accent);}}
      button{{
        width:100%; padding:13px; border:none; border-radius:10px; margin-top:6px;
        background:linear-gradient(90deg, var(--accent), var(--accent-2));
        color:white; font-weight:700; font-size:14px; cursor:pointer;
        transition:transform .15s ease;
      }}
      button:hover{{transform:translateY(-1px);}}
      .error{{
        background:rgba(255,93,115,0.1); border:1px solid rgba(255,93,115,0.3);
        color:var(--danger); padding:10px 12px; border-radius:10px;
        font-size:13px; margin-bottom:16px;
      }}
      .foot{{text-align:center; margin-top:18px; font-size:11.5px; color:var(--muted);}}
      .dash{{min-height:100vh; padding:40px 24px;}}
      .dash-card{{
        max-width:720px; margin:0 auto; background:var(--panel);
        border:1px solid var(--border); border-radius:18px; padding:30px;
        backdrop-filter:blur(20px);
      }}
      .dash-top{{display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;}}
      .dash-top h1{{font-size:20px; text-align:left;}}
      .badge{{
        display:inline-flex; align-items:center; gap:6px; font-size:12px;
        color:var(--success); background:rgba(40,209,124,0.1);
        border:1px solid rgba(40,209,124,0.3); padding:5px 12px;
        border-radius:20px; margin-top:8px;
      }}
      .logout{{color:var(--muted); font-size:12.5px; text-decoration:none;}}
      .logout:hover{{color:var(--text);}}
      table{{width:100%; border-collapse:collapse; margin-top:20px;}}
      td{{padding:11px 0; border-bottom:1px solid var(--border); font-size:13.5px;}}
      td:first-child{{color:var(--muted);}}
      td:last-child{{text-align:right; font-family:var(--mono);}}
    </style>
    """


def build_pages(nom, icon, tagline, login_label, dashboard_title, dashboard_rows, style):
    """Construit (SETUP_PAGE, LOGIN_PAGE, DASHBOARD_PAGE) pour un template."""

    setup_page = style + f"""
    <div class="wrap"><div class="card">
      <div class="icon">{icon}</div>
      <h1>{nom}</h1>
      <div class="subtitle">Première connexion — définis le mot de passe administrateur</div>
      <form method="POST">
        <div class="field">
          <label>Nouveau mot de passe</label>
          <input type="password" name="password" required autofocus>
        </div>
        <button type="submit">Configurer le compte</button>
      </form>
      <div class="foot">{tagline}</div>
    </div></div>
    """

    login_page = style + f"""
    <div class="wrap"><div class="card">
      <div class="icon">{icon}</div>
      <h1>{nom}</h1>
      <div class="subtitle">{tagline}</div>
      {{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
      <form method="POST">
        <div class="field">
          <label>{login_label}</label>
          <input type="text" name="login" value="admin" required>
        </div>
        <div class="field">
          <label>Mot de passe</label>
          <input type="password" name="password" required>
        </div>
        <button type="submit">Se connecter</button>
      </form>
      <div class="foot">Connexion sécurisée · session chiffrée</div>
    </div></div>
    """

    rows_html = "".join(
        f"<tr><td>{label}</td><td>{valeur}</td></tr>" for label, valeur in dashboard_rows
    )

    dashboard_page = style + f"""
    <div class="dash"><div class="dash-card">
      <div class="dash-top">
        <div>
          <h1>{icon} {dashboard_title}</h1>
          <span class="badge">● Accès administrateur confirmé</span>
        </div>
        <a class="logout" href="/logout">Déconnexion ↗</a>
      </div>
      <table>{rows_html}</table>
    </div></div>
    """

    return setup_page, login_page, dashboard_page

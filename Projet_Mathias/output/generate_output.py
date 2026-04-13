"""
Génère tous les fichiers CSV nettoyés dans le dossier output/.

Utilise les loaders pandas pour charger et nettoyer les données sources,
puis les enregistre avec df.to_csv() (index non inclus).

Utilisation :
    python -m Projet_Mathias.output.generate_output
    # ou depuis la racine du projet :
    python Projet-1A-2026/Projet_Mathias/output/generate_output.py
"""

from pathlib import Path
import sys

# Permet d'importer les loaders quel que soit le répertoire de lancement
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Projet_Mathias.loaders import (
    TennisLoader,
    BasketballLoader,
    FootballLoader,
    LolLoader,
    VolleyballLoader,
)

OUTPUT = Path(__file__).parent


def sauvegarder(df, nom_fichier: str) -> None:
    """Sauvegarde un DataFrame pandas en CSV dans le dossier output/."""
    chemin = OUTPUT / nom_fichier
    df.to_csv(chemin, index=False)
    print(f"  OK  {nom_fichier}  ({len(df)} lignes)")


def generer_tennis() -> None:
    print("Tennis...")
    loader = TennisLoader()
    sauvegarder(loader.load_atp_players(), "tennis_atp_players_clean.csv")
    sauvegarder(loader.load_wta_players(), "tennis_wta_players_clean.csv")
    sauvegarder(loader.load_atp_matches(), "tennis_atp_matches_clean.csv")
    sauvegarder(loader.load_wta_matches(), "tennis_wta_matches_clean.csv")


def generer_basketball() -> None:
    print("Basketball...")
    loader = BasketballLoader()
    sauvegarder(loader.load_players(), "players_clean.csv")
    sauvegarder(loader.load_teams(), "teams_clean.csv")
    sauvegarder(loader.load_matches(), "matches_clean.csv")


def generer_football() -> None:
    print("Football...")
    loader = FootballLoader()
    sauvegarder(loader.load_countries(), "football_countries_clean.csv")
    sauvegarder(loader.load_leagues(), "football_leagues_clean.csv")
    sauvegarder(loader.load_games(), "football_games_clean.csv")


def generer_lol() -> None:
    print("LoL...")
    loader = LolLoader()
    sauvegarder(loader.load_players(), "lol_players_clean.csv")
    sauvegarder(loader.load_coaches(), "lol_coaches_clean.csv")
    sauvegarder(loader.load_teams(), "lol_teams_clean.csv")
    sauvegarder(loader.load_matches(), "lol_matches_clean.csv")


def generer_volleyball() -> None:
    print("Volleyball...")
    loader = VolleyballLoader()
    sauvegarder(loader.load_countries(), "volleyball_countries_clean.csv")
    sauvegarder(loader.load_players_men(), "volleyball_players_men_clean.csv")
    sauvegarder(loader.load_players_women(), "volleyball_players_women_clean.csv")
    sauvegarder(loader.load_coaches_men(), "volleyball_coaches_men_clean.csv")
    sauvegarder(loader.load_coaches_women(), "volleyball_coaches_women_clean.csv")
    sauvegarder(loader.load_matches_men(), "volleyball_matches_men_clean.csv")
    sauvegarder(loader.load_matches_women(), "volleyball_matches_women_clean.csv")


if __name__ == "__main__":
    print(f"Génération des CSV dans : {OUTPUT}\n")
    generer_tennis()
    generer_basketball()
    generer_football()
    generer_lol()
    generer_volleyball()
    print("\nTerminé.")

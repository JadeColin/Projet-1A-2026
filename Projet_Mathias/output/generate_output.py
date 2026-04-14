from Projet_Mathias.loaders import (
    BadmintonLoader,
    BasketballLoader,
    ChessLoader,
    Cs2Loader,
    FootballLoader,
    FootballChampionsLeagueLoader,
    LolLoader,
    Starcraft2Loader,
    TennisLoader,
    VolleyballLoader,
)

from pathlib import Path  # noqa: E402
import sys  # noqa: E402

# Permet d'importer les loaders quel que soit le répertoire de lancement
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # noqa: F821


"""
Génère tous les fichiers CSV nettoyés dans le dossier output/.

Utilise les loaders pandas pour charger et nettoyer les données sources,
puis les enregistre avec df.to_csv() (index non inclus).

Utilisation :
    python -m Projet_Mathias.output.generate_output
    # ou depuis la racine du projet :
    python Projet-1A-2026/Projet_Mathias/output/generate_output.py
"""


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


def generer_badminton() -> None:
    print("Badminton...")
    loader = BadmintonLoader()
    sauvegarder(loader.load_players(), "badminton_players_clean.csv")
    sauvegarder(loader.load_matches(), "badminton_matches_clean.csv")


def generer_chess() -> None:
    print("Chess...")
    loader = ChessLoader()
    sauvegarder(loader.load_players(), "chess_players_clean.csv")
    sauvegarder(loader.load_matches(), "chess_matches_clean.csv")


def generer_cs2() -> None:
    print("CS2...")
    loader = Cs2Loader()
    sauvegarder(loader.load_players(), "cs2_players_clean.csv")
    sauvegarder(loader.load_coaches(), "cs2_coaches_clean.csv")
    sauvegarder(loader.load_teams(), "cs2_teams_clean.csv")
    sauvegarder(loader.load_matches(), "cs2_matches_clean.csv")


def generer_football_champions_league() -> None:
    print("Football Champions League...")
    loader = FootballChampionsLeagueLoader()
    sauvegarder(loader.load_players(), "football_champions_league_players_clean.csv")
    sauvegarder(loader.load_teams(), "football_champions_league_teams_clean.csv")
    sauvegarder(loader.load_matches(), "football_champions_league_matches_clean.csv")


def generer_starcraft2() -> None:
    print("StarCraft 2...")
    loader = Starcraft2Loader()
    sauvegarder(loader.load_players(), "starcraft2_players_clean.csv")
    sauvegarder(loader.load_matches(), "starcraft2_matches_clean.csv")


if __name__ == "__main__":
    print(f"Génération des CSV dans : {OUTPUT}\n")
    generer_tennis()
    generer_basketball()
    generer_football()
    generer_lol()
    generer_volleyball()
    generer_badminton()
    generer_chess()
    generer_cs2()
    generer_football_champions_league()
    generer_starcraft2()
    print("\nTerminé.")

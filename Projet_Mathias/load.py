"""
Point d'entrée unique pour charger n'importe quelle table du projet.

Utilisation :
    from Projet_Mathias.load import load

    df = load("basketball", "players")
    df = load("tennis", "atp_matches")
    df = load("volleyball", "players_men")

Pour voir toutes les tables disponibles :
    from Projet_Mathias.load import list_tables
    list_tables()
"""

import pandas as pd

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

# Registre : sport -> { table -> méthode du loader }
_REGISTRY: dict[str, dict[str, callable]] = {
    "badminton": {
        "players": BadmintonLoader().load_players,
        "matches": BadmintonLoader().load_matches,
    },
    "basketball": {
        "players": BasketballLoader().load_players,
        "teams":   BasketballLoader().load_teams,
        "matches": BasketballLoader().load_matches,
    },
    "chess": {
        "players": ChessLoader().load_players,
        "matches": ChessLoader().load_matches,
    },
    "cs2": {
        "players": Cs2Loader().load_players,
        "coaches": Cs2Loader().load_coaches,
        "teams":   Cs2Loader().load_teams,
        "matches": Cs2Loader().load_matches,
    },
    "football": {
        "countries": FootballLoader().load_countries,
        "leagues":   FootballLoader().load_leagues,
        "games":     FootballLoader().load_games,
    },
    "football_champions_league": {
        "players": FootballChampionsLeagueLoader().load_players,
        "teams":   FootballChampionsLeagueLoader().load_teams,
        "matches": FootballChampionsLeagueLoader().load_matches,
    },
    "lol": {
        "players": LolLoader().load_players,
        "coaches": LolLoader().load_coaches,
        "teams":   LolLoader().load_teams,
        "matches": LolLoader().load_matches,
    },
    "starcraft2": {
        "players": Starcraft2Loader().load_players,
        "matches": Starcraft2Loader().load_matches,
    },
    "tennis": {
        "atp_players": TennisLoader().load_atp_players,
        "wta_players": TennisLoader().load_wta_players,
        "atp_matches": TennisLoader().load_atp_matches,
        "wta_matches": TennisLoader().load_wta_matches,
    },
    "volleyball": {
        "countries":    VolleyballLoader().load_countries,
        "players_men":  VolleyballLoader().load_players_men,
        "players_women": VolleyballLoader().load_players_women,
        "coaches_men":  VolleyballLoader().load_coaches_men,
        "coaches_women": VolleyballLoader().load_coaches_women,
        "matches_men":  VolleyballLoader().load_matches_men,
        "matches_women": VolleyballLoader().load_matches_women,
    },
}


def load(sport: str, table: str) -> pd.DataFrame:
    """
    Charge un DataFrame à partir du nom du sport et de la table.

    Paramètres :
        sport  : "basketball", "football", "lol", "tennis" ou "volleyball"
        table  : nom de la table (voir list_tables() pour la liste complète)

    Retourne :
        Un DataFrame pandas prêt à l'emploi.

    Exemple :
        df = load("basketball", "players")
        df = load("tennis", "atp_matches")
    """
    sport = sport.lower().strip()
    table = table.lower().strip()

    if sport not in _REGISTRY:
        sports_dispo = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"Sport inconnu : '{sport}'. Disponibles : {sports_dispo}")

    if table not in _REGISTRY[sport]:
        tables_dispo = ", ".join(sorted(_REGISTRY[sport]))
        raise ValueError(
            f"Table inconnue : '{table}' pour le sport '{sport}'.\n"
            f"Tables disponibles : {tables_dispo}"
        )

    return _REGISTRY[sport][table]()


def list_tables() -> None:
    """Affiche toutes les combinaisons sport / table disponibles."""
    print("Tables disponibles :\n")
    for sport, tables in sorted(_REGISTRY.items()):
        for table in sorted(tables):
            print(f"  load({sport!r}, {table!r})")
    print()

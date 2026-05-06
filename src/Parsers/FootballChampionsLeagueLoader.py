import pandas as pd

from src.Parsers.BaseLoader import BaseLoader


class FootballChampionsLeagueLoader(BaseLoader):
    """
    Charge les données de la base Football Champions League (UEFA).

    Fichiers sources :
        - player.csv : statistiques individuelles des joueurs (751 joueurs)
        - team.csv   : équipes participantes (32 équipes)
        - match.csv  : matchs de la compétition (125 matchs)

    Exemple d'utilisation :
        loader = FootballChampionsLeagueLoader()
        players = loader.load_players()
        matches = loader.load_matches()
        players, teams, matches = loader.load_all()
    """

    SPORT_FOLDER = "football_champions_league"

    def load_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les statistiques joueurs de la Ligue des Champions.

        Colonnes principales : player_name, club, position, assists, goals,
        goals_right_foot, goals_left_foot, goals_headers, minutes_played,
        pass_attempted, pass_completed, tackles_won, fouls_committed, yellow, red,
        saved, conceded, cleansheets, distance_covered.

        Note : le fichier source contient deux colonnes 'match_played' ;
               la première est renommée 'match_played_field', la seconde 'match_played'.
               Typos conservés depuis la source : 'balls_recoverd',
               'cross_complted', 'punches made'.
        """
        df = self._load_csv("player.csv")
        df = df.rename(columns={"match_played": "match_played_field", "match_played.1": "match_played"})
        return df

    def load_teams(self) -> pd.DataFrame:
        """
        Charge les équipes de la Ligue des Champions.

        Colonnes : full_name, short_name, year_founded, country, league, city
        """
        return self._load_csv("team.csv")

    def load_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs de la Ligue des Champions.

        Colonnes : date, phase, round, matchday, group, team_home, team_away,
                   score_team_home, score_team_away

        Colonnes ajoutées :
            - date : converti en datetime
        """
        return self._load_csv("match.csv", date_cols=["date"])

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge les trois tables en une seule fois. Renvoie : players, teams, matches"""
        return self.load_players(), self.load_teams(), self.load_matches()

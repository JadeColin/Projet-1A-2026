import pandas as pd

from Projet_Mathias.loaders.BaseLoader import BaseLoader


class Cs2Loader(BaseLoader):
    """
    Charge les données de la base Counter-Strike 2 (CS2).

    Fichiers sources :
        - player.csv : joueurs professionnels (160 joueurs)
        - coach.csv  : coachs (32 coachs)
        - team.csv   : équipes (32 équipes)
        - match.csv  : matchs (106 matchs)

    Exemple d'utilisation :
        loader = Cs2Loader()
        players = loader.load_players()
        matches = loader.load_matches()
        players, coaches, teams, matches = loader.load_all()
    """

    SPORT_FOLDER = "counter_strike_2"

    def load_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueurs CS2.

        Colonnes : pseudo, name, nationality, birthdate, role, team

        Colonnes ajoutées :
            - birthdate : converti en datetime
        """
        return self._load_csv("player.csv", date_cols=["birthdate"])

    def load_coaches(self) -> pd.DataFrame:
        """
        Charge et nettoie les coachs CS2.

        Colonnes : pseudo, name, nationality, birthdate, team

        Colonnes ajoutées :
            - birthdate : converti en datetime
        """
        return self._load_csv("coach.csv", date_cols=["birthdate"])

    def load_teams(self) -> pd.DataFrame:
        """
        Charge les équipes CS2.

        Colonnes : team, team_abbreviation, location, region
        """
        return self._load_csv("team.csv")

    def load_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs CS2.

        Colonnes : date, stage, round, best_of, team_1, team_2,
                   score_team_1, score_team_2

        Colonnes ajoutées :
            - date : converti en datetime
        """
        return self._load_csv("match.csv", date_cols=["date"])

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge les quatre tables en une seule fois. Renvoie : players, coaches, teams, matches"""
        return self.load_players(), self.load_coaches(), self.load_teams(), self.load_matches()

import pandas as pd

from Projet_Mathias.loaders.BaseLoader import BaseLoader


class Starcraft2Loader(BaseLoader):
    """
    Charge les données de la base StarCraft II (SC2).

    Fichiers sources :
        - player.csv : joueurs professionnels (32 joueurs)
        - match.csv  : matchs (67 matchs)

    Exemple d'utilisation :
        loader = Starcraft2Loader()
        players = loader.load_players()
        matches = loader.load_matches()
        players, matches = loader.load_all()
    """

    SPORT_FOLDER = "starcraft_2"

    def load_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueurs SC2.

        Colonnes : pseudo, name, nationality, birthdate, race, team

        Colonnes ajoutées :
            - birthdate : converti en datetime
        """
        return self._load_csv("player.csv", date_cols=["birthdate"])

    def load_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs SC2.

        Colonnes : date, round, group, best_of, player_1, player_2,
                   score_player_1, score_player_2

        Colonnes ajoutées :
            - date : converti en datetime
        """
        return self._load_csv("match.csv", date_cols=["date"])

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Charge les deux tables en une seule fois. Renvoie : players, matches"""
        return self.load_players(), self.load_matches()

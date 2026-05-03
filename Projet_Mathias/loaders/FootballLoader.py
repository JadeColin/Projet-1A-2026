import pandas as pd

from Projet_Mathias.loaders.BaseLoader import BaseLoader


class FootballLoader(BaseLoader):
    """
    Charge les données de la base Football (ligues européennes).

    Fichiers sources :
        - country.csv : pays participants (11 pays)
        - league.csv  : ligues (11 ligues)
        - game.csv    : matchs (attention : contient des statistiques NBA
                        mal placées dans ce dossier)

    Exemple d'utilisation :
        loader = FootballLoader()
        countries = loader.load_countries()
        leagues   = loader.load_leagues()
        countries, leagues, games = loader.load_all()
    """

    SPORT_FOLDER = "Football"

    def load_countries(self) -> pd.DataFrame:
        """
        Charge les pays du football européen.

        Colonnes : id, name
        """
        return self._load_csv("country.csv", dtype={"id": int})

    def load_leagues(self) -> pd.DataFrame:
        """
        Charge les ligues de football européen.

        Colonnes : id, country_id, name
        """
        return self._load_csv("league.csv", dtype={"id": int, "country_id": int})

    def load_games(self) -> pd.DataFrame:
        """
        Charge le fichier game.csv.

        ATTENTION : ce fichier contient des statistiques de matchs NBA
        (fgm, fg3m, pts…) et non du football.

        Colonnes ajoutées :
            - game_date : converti en datetime
        """
        return self._load_csv("game.csv", date_cols=["game_date"])

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge les trois tables en une seule fois. Renvoie : countries, leagues, games"""
        return self.load_countries(), self.load_leagues(), self.load_games()

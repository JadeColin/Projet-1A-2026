import pandas as pd

from Projet_Mathias.loaders.BaseLoader import BaseLoader


class FootballLoader(BaseLoader):
    """
    Charge les données de la base Football (ligues européennes).

    Fichiers sources :
        - country.csv : pays participants (11 pays)
        - league.csv  : ligues (11 ligues)
        - team.csv    : équipes (id, team_api_id, team_long_name, team_short_name)
        - player.csv  : joueurs (id, player_api_id, player_name, birthday, weight, height)
        - match.csv   : matchs (25 979 matchs, saisons 2008-2016)

    Exemple d'utilisation :
        loader = FootballLoader()
        countries = loader.load_countries()
        leagues   = loader.load_leagues()
        countries, leagues, matches = loader.load_all()
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

    def load_teams(self) -> pd.DataFrame:
        """
        Charge les équipes de football européen.

        Colonnes : id, team_api_id, team_long_name, team_short_name
        """
        return self._load_csv("team.csv", dtype={"id": int, "team_api_id": int})

    def load_players(self) -> pd.DataFrame:
        """
        Charge les joueurs de football européen.

        Colonnes : id, player_api_id, player_name, birthday, weight (kg), height (cm)
        """
        return self._load_csv("player.csv", dtype={"id": int, "player_api_id": int})

    def load_matches(self) -> pd.DataFrame:
        """
        Charge les matchs de football européen.

        Colonnes principales : id, country_id, league_id, season, stage, date,
        match_api_id, home_team_api_id, away_team_api_id,
        home_team_goal, away_team_goal, home_player_1..11, away_player_1..11

        Colonnes ajoutées :
            - date : converti en datetime
        """
        return self._load_csv("match.csv", date_cols=["date"])

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge les trois tables principales. Renvoie : countries, leagues, matches"""
        return self.load_countries(), self.load_leagues(), self.load_matches()

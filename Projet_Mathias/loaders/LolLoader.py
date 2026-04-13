from pathlib import Path

import pandas as pd


class LolLoader:
    """
    Charge les données de la base League of Legends (EMEA 2025).

    Fichiers sources :
        - player.csv : joueurs professionnels (50 joueurs)
        - coach.csv  : coachs (25 coachs)
        - team.csv   : équipes (10 équipes)
        - match.csv  : matchs de la saison régulière (45 matchs)

    Exemple d'utilisation :
        loader = LolLoader()
        players = loader.load_players()
        matches = loader.load_matches()
        players, coaches, teams, matches = loader.load_all()
    """

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "Lol"

    def load_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueurs LoL.

        Colonnes : pseudo, name, country_of_birth, birthdate, role, team

        Colonnes ajoutées :
            - birthdate : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "player.csv")
        df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce")
        return df

    def load_coaches(self) -> pd.DataFrame:
        """
        Charge et nettoie les coachs LoL.

        Colonnes : pseudo, name, country_of_birth, birthdate, role, team

        Colonnes ajoutées :
            - birthdate : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "coach.csv")
        df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce")
        return df

    def load_teams(self) -> pd.DataFrame:
        """
        Charge les équipes LoL.

        Colonnes : team, team_abbreviation, location, region
        """
        return pd.read_csv(self.ROOT / "team.csv")

    def load_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs LoL.

        Colonnes principales : patch, date, week, day, team_blue, team_red,
        winner, time, kills/assists/deaths/gold/turrets/dragons/barons
        par équipe, joueurs titulaires par rôle, picks et bans.

        Colonnes ajoutées :
            - date       : converti en datetime
            - duration_s : durée en secondes (calculée depuis le format HH:MM:SS)
        """
        df = pd.read_csv(self.ROOT / "match.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["duration_s"] = (
            pd.to_timedelta(df["time"], errors="coerce").dt.total_seconds().astype("Int64")
        )
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les quatre tables en une seule fois.

        Renvoie :
            players, coaches, teams, matches
        """
        return self.load_players(), self.load_coaches(), self.load_teams(), self.load_matches()

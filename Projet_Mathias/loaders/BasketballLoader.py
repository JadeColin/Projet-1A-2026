from pathlib import Path

import pandas as pd


class BasketballLoader:
    """
    Charge les données de la base Basketball (NBA).

    Fichiers sources :
        - player.csv  : joueurs NBA (431 joueurs)
        - team.csv    : franchises NBA (30 équipes)
        - match.csv   : matchs (attention : contient des données de football
                        européen mal placées dans ce dossier)

    Exemple d'utilisation :
        loader = BasketballLoader()
        players = loader.load_players()
        teams   = loader.load_teams()
        players, teams, matches = loader.load_all()
    """

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "Basketball"

    def load_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueurs NBA.

        Colonnes ajoutées :
            - full_name  : prénom + nom
            - height_cm  : taille convertie depuis le format pieds-pouces '6-8'
            - birthdate  : converti en datetime
        """
        df = pd.read_csv(
            self.ROOT / "player.csv",
            dtype={"person_id": int, "jersey": "Int64", "weight": "Int64", "team_id": int},
        )
        df["full_name"] = df["first_name"].str.strip() + " " + df["last_name"].str.strip()
        df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce")
        df["height_cm"] = df["height"].apply(self._height_to_cm)
        return df

    def load_teams(self) -> pd.DataFrame:
        """
        Charge les franchises NBA.

        Colonnes : id, full_name, abbreviation, nickname, city, state
        """
        return pd.read_csv(self.ROOT / "team.csv", dtype={"id": int})

    def load_matches(self) -> pd.DataFrame:
        """
        Charge le fichier match.csv.

        ATTENTION : ce fichier contient des données de football européen
        (saisons 2008-2016, 11 joueurs par équipe) et non du basketball NBA.
        Les colonnes home_team_goal / away_team_goal correspondent à des buts.

        Colonnes ajoutées :
            - date : converti en datetime
        """
        df = pd.read_csv(
            self.ROOT / "match.csv",
            dtype={
                "id": int,
                "country_id": "Int64",
                "league_id": "Int64",
                "stage": "Int64",
                "home_team_goal": "Int64",
                "away_team_goal": "Int64",
            },
        )
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les trois tables en une seule fois.

        Renvoie :
            players, teams, matches
        """
        return self.load_players(), self.load_teams(), self.load_matches()

    @staticmethod
    def _height_to_cm(height_str: str) -> float | None:
        """Convertit le format pieds-pouces '6-8' en centimètres."""
        if pd.isna(height_str):
            return None
        parts = str(height_str).split("-")
        if len(parts) == 2:
            feet, inches = int(parts[0]), int(parts[1])
            return round((feet * 12 + inches) * 2.54, 1)
        return None

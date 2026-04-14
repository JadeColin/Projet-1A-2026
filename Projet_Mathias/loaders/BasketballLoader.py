from pathlib import Path

import pandas as pd


class BasketballLoader:
    """
    Charge les données de la base Basketball (NBA).

    Fichiers sources :
        - player.csv  : joueurs NBA (431 joueurs)
        - team.csv    : franchises NBA (30 équipes)
        - game.csv    : matchs NBA (saison 2022-2023, statistiques complètes
                        par équipe : points, rebonds, passes, etc.)

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
        Charge le fichier game.csv.

        Données NBA saison 2022-2023 (Regular Season) avec les statistiques
        complètes par équipe : points, rebonds, passes décisives, etc.

        Colonnes ajoutées :
            - game_date : converti en datetime
        """
        df = pd.read_csv(
            self.ROOT / "game.csv",
            dtype={
                "game_id": int,
                "team_id_home": int,
                "team_id_away": int,
                "pts_home": "Int64",
                "pts_away": "Int64",
            },
        )
        df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les trois tables en une seule fois.

        Renvoie :
            players, teams, matches
        """
        return self.load_players(), self.load_teams(), self.load_matches()

    def get_team_roster(
        self, players: pd.DataFrame, teams: pd.DataFrame, team_name: str
    ) -> pd.DataFrame:
        """
        Retourne les joueurs d'une équipe à partir de son nom complet, abréviation ou surnom.

        Exemple :
            loader = BasketballLoader()
            players, teams, _ = loader.load_all()
            roster = loader.get_team_roster(players, teams, "Lakers")
        """
        mask = (
            teams["full_name"].str.contains(team_name, case=False, na=False)
            | teams["abbreviation"].str.contains(team_name, case=False, na=False)
            | teams["nickname"].str.contains(team_name, case=False, na=False)
        )
        matched = teams[mask]
        if matched.empty:
            raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")
        team_id = matched.iloc[0]["id"]
        return players[players["team_id"] == team_id].reset_index(drop=True)

    @staticmethod
    def players_with_team(players: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
        """
        Joint les joueurs avec leur équipe.

        Retourne un DataFrame enrichi avec les colonnes de l'équipe
        (full_name de l'équipe renommée en team_name, abbreviation, city…).
        """
        return players.merge(
            teams.rename(columns={"full_name": "team_name", "id": "team_id"}),
            on="team_id",
            how="left",
        )

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

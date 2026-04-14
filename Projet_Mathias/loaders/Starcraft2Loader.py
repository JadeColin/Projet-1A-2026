from pathlib import Path

import pandas as pd


class Starcraft2Loader:
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

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "starcraft_2"

    def load_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueurs SC2.

        Colonnes : pseudo, name, nationality, birthdate, race, team

        Colonnes ajoutées :
            - birthdate : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "player.csv")
        df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce")
        return df

    def load_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs SC2.

        Colonnes : date, round, group, best_of, player_1, player_2,
                   score_player_1, score_player_2

        Colonnes ajoutées :
            - date : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "match.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Charge les deux tables en une seule fois.

        Renvoie :
            players, matches
        """
        return self.load_players(), self.load_matches()

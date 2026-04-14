from pathlib import Path

import pandas as pd


class BadmintonLoader:
    """
    Charge les données de la base Badminton (BWF World Tour).

    Fichiers sources :
        - player.csv : joueuses du circuit BWF (88 joueuses)
        - match.csv  : matchs du circuit (226 matchs)

    Exemple d'utilisation :
        loader = BadmintonLoader()
        players = loader.load_players()
        matches = loader.load_matches()
        players, matches = loader.load_all()
    """

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "badminton"

    def load_players(self) -> pd.DataFrame:
        """
        Charge les joueuses du circuit BWF.

        Colonnes : name, country, continent
        """
        return pd.read_csv(self.ROOT / "player.csv")

    def load_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs BWF.

        Colonnes : tournament, city, country, date, tournament_type, round,
                   player_1, player_2, winner, game_1_score, game_2_score,
                   game_3_score

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

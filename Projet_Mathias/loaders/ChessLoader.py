from pathlib import Path

import pandas as pd


class ChessLoader:
    """
    Charge les données de la base Échecs (FIDE).

    Fichiers sources :
        - player.csv : joueurs FIDE (206 joueurs)
        - match.csv  : matchs (256 matchs)

    Exemple d'utilisation :
        loader = ChessLoader()
        players = loader.load_players()
        matches = loader.load_matches()
        players, matches = loader.load_all()
    """

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "chess"

    def load_players(self) -> pd.DataFrame:
        """
        Charge les joueurs FIDE.

        Colonnes : name, fide_id, birth_year, gender, federation, fide_title,
                   rating_standard, rating_rapid, rating_blitz
        """
        return pd.read_csv(
            self.ROOT / "player.csv",
            dtype={
                "fide_id": "Int64",
                "birth_year": "Int64",
                "rating_standard": "Int64",
                "rating_rapid": "Int64",
                "rating_blitz": "Int64",
            },
        )

    def load_matches(self) -> pd.DataFrame:
        """
        Charge les matchs d'échecs.

        Colonnes : round, section, match, player_1, player_2,
                   score_player_1, score_player_2, seed_player_1, seed_player_2

        Note : score_player_1 peut contenir 'Bye' lorsqu'un joueur est exempt
               de tour. score_player_2 est NaN dans ce cas.
        """
        return pd.read_csv(
            self.ROOT / "match.csv",
            dtype={
                "section": "Float64",
                "seed_player_2": "Float64",
            },
        )

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Charge les deux tables en une seule fois.

        Renvoie :
            players, matches
        """
        return self.load_players(), self.load_matches()

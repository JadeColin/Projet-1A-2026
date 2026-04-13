from pathlib import Path

import pandas as pd


class TennisLoader:
    """
    Charge les données de la base Tennis (ATP et WTA 2024).

    Fichiers sources :
        - atp_players_2024.csv : joueurs ATP (443 joueurs)
        - wta_players_2024.csv : joueuses WTA (335 joueuses)
        - atp_matches_2024.csv : matchs ATP (3 076 matchs)
        - wta_matches_2024.csv : matchs WTA (2 689 matchs)

    Exemple d'utilisation :
        loader = TennisLoader()
        atp_players = loader.load_atp_players()
        wta_matches = loader.load_wta_matches()
        atp_players, wta_players, atp_matches, wta_matches = loader.load_all()
    """

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "tennis"

    def load_atp_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueurs ATP 2024.

        Colonnes : player_id, name_first, name_last, hand, dob, ioc, height

        Colonnes ajoutées :
            - full_name : prénom + nom
            - dob       : converti en datetime (depuis le format YYYYMMDD)
        """
        df = pd.read_csv(self.ROOT / "atp_players_2024.csv", dtype={"player_id": int})
        df["dob"] = self._parse_dob(df["dob"])
        df["full_name"] = df["name_first"].str.strip() + " " + df["name_last"].str.strip()
        return df

    def load_wta_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueuses WTA 2024.

        Colonnes : player_id, name_first, name_last, hand, dob, ioc, height

        Colonnes ajoutées :
            - full_name : prénom + nom
            - dob       : converti en datetime (depuis le format YYYYMMDD)
        """
        df = pd.read_csv(self.ROOT / "wta_players_2024.csv", dtype={"player_id": int})
        df["dob"] = self._parse_dob(df["dob"])
        df["full_name"] = df["name_first"].str.strip() + " " + df["name_last"].str.strip()
        return df

    def load_atp_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs ATP 2024.

        Colonnes principales : tourney_id, tourney_name, surface, tourney_date,
        winner_id, loser_id, score, round, minutes, statistiques de service
        (aces, doubles fautes, points de service…).

        Colonnes ajoutées :
            - tourney_date : converti en datetime (depuis le format YYYYMMDD)
        """
        df = pd.read_csv(self.ROOT / "atp_matches_2024.csv")
        df["tourney_date"] = self._parse_tourney_date(df["tourney_date"])
        return df

    def load_wta_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs WTA 2024.

        Mêmes colonnes que les matchs ATP.

        Colonnes ajoutées :
            - tourney_date : converti en datetime (depuis le format YYYYMMDD)
        """
        df = pd.read_csv(self.ROOT / "wta_matches_2024.csv")
        df["tourney_date"] = self._parse_tourney_date(df["tourney_date"])
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les quatre tables en une seule fois.

        Renvoie :
            atp_players, wta_players, atp_matches, wta_matches
        """
        return (
            self.load_atp_players(),
            self.load_wta_players(),
            self.load_atp_matches(),
            self.load_wta_matches(),
        )

    @staticmethod
    def _parse_dob(series: pd.Series) -> pd.Series:
        """Convertit les dates de naissance YYYYMMDD (float) en datetime."""
        return pd.to_datetime(
            series.dropna().astype(int).astype(str),
            format="%Y%m%d",
            errors="coerce",
        ).reindex(series.index)

    @staticmethod
    def _parse_tourney_date(series: pd.Series) -> pd.Series:
        """Convertit les dates de tournoi YYYYMMDD (int) en datetime."""
        return pd.to_datetime(series.astype(str), format="%Y%m%d", errors="coerce")

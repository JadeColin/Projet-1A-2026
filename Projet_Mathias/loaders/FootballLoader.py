from pathlib import Path

import pandas as pd


class FootballLoader:
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

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "Football"

    def load_countries(self) -> pd.DataFrame:
        """
        Charge les pays du football européen.

        Colonnes : id, name
        """
        return pd.read_csv(self.ROOT / "country.csv", dtype={"id": int})

    def load_leagues(self) -> pd.DataFrame:
        """
        Charge les ligues de football européen.

        Colonnes : id, country_id, name
        """
        return pd.read_csv(self.ROOT / "league.csv", dtype={"id": int, "country_id": int})

    def load_games(self) -> pd.DataFrame:
        """
        Charge le fichier game.csv.

        ATTENTION : ce fichier contient des statistiques de matchs NBA
        (fgm, fg3m, pts…) et non du football. Les IDs d'équipes correspondent
        aux franchises NBA.

        Colonnes ajoutées :
            - game_date : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "game.csv")
        df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les trois tables en une seule fois.

        Renvoie :
            countries, leagues, games
        """
        return (
            self.load_countries(),
            self.load_leagues(),
            self.load_games()
        )

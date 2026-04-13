from pathlib import Path

import pandas as pd


class VolleyballLoader:
    """
    Charge les données de la base Volleyball (JO Paris 2024).

    Fichiers sources :
        - country.csv        : pays (224 codes IOC)
        - player_men.csv     : joueurs masculins (156 joueurs)
        - player_women.csv   : joueuses (155 joueuses)
        - coach_men.csv      : coachs masculins (39 coachs)
        - coach_women.csv    : coachs féminins (42 coachs)
        - match_men.csv      : matchs masculins (26 matchs)
        - match_women.csv    : matchs féminins (26 matchs)

    Exemple d'utilisation :
        loader = VolleyballLoader()
        players_men   = loader.load_players_men()
        matches_women = loader.load_matches_women()
        (countries, players_men, players_women,
         coaches_men, coaches_women,
         matches_men, matches_women) = loader.load_all()
    """

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "volleyball"

    def load_countries(self) -> pd.DataFrame:
        """
        Charge la table des pays (codes IOC).

        Colonnes : code, country, country_long
        """
        return pd.read_csv(self.ROOT / "country.csv")

    def load_players_men(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueurs masculins.

        Colonnes : name, country_code, height, birth_date, birth_place, nickname

        Colonnes ajoutées :
            - birth_date : converti en datetime
            - gender     : 'M'
        """
        df = pd.read_csv(self.ROOT / "player_men.csv", dtype={"height": "Int64"})
        df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
        df["gender"] = "M"
        return df

    def load_players_women(self) -> pd.DataFrame:
        """
        Charge et nettoie les joueuses.

        Colonnes : name, country_code, height, birth_date, birth_place, nickname

        Colonnes ajoutées :
            - birth_date : converti en datetime
            - gender     : 'F'
        """
        df = pd.read_csv(self.ROOT / "player_women.csv", dtype={"height": "Int64"})
        df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
        df["gender"] = "F"
        return df

    def load_coaches_men(self) -> pd.DataFrame:
        """
        Charge et nettoie les coachs masculins.

        Colonnes : name, birth_date, gender, function, country_code

        Colonnes ajoutées :
            - birth_date : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "coach_men.csv")
        df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
        return df

    def load_coaches_women(self) -> pd.DataFrame:
        """
        Charge et nettoie les coachs féminins.

        Colonnes : name, birth_date, gender, function, country_code

        Colonnes ajoutées :
            - birth_date : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "coach_women.csv")
        df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
        return df

    def load_matches_men(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs masculins.

        Colonnes : date, stage, country_code_1, country_code_2,
                   set_country_1, set_country_2

        Colonnes ajoutées :
            - date   : converti en datetime
            - winner : pays ayant remporté le match
        """
        df = pd.read_csv(self.ROOT / "match_men.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["winner"] = df.apply(
            lambda r: r["country_code_1"] if r["set_country_1"] > r["set_country_2"] else r["country_code_2"],
            axis=1,
        )
        return df

    def load_matches_women(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs féminins.

        Note : le fichier source utilise 'country_1/2' (noms complets) au lieu
        de 'country_code_1/2'. Les colonnes sont renommées pour uniformité
        avec load_matches_men().

        Colonnes : date, stage, country_code_1, country_code_2,
                   set_country_1, set_country_2

        Colonnes ajoutées :
            - date   : converti en datetime
            - winner : pays ayant remporté le match
        """
        df = pd.read_csv(self.ROOT / "match_women.csv")
        df = df.rename(columns={"country_1": "country_code_1", "country_2": "country_code_2"})
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["winner"] = df.apply(
            lambda r: r["country_code_1"] if r["set_country_1"] > r["set_country_2"] else r["country_code_2"],
            axis=1,
        )
        return df

    def load_all(self) -> tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame,
        pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ]:
        """
        Charge toutes les tables en une seule fois.

        Renvoie :
            countries, players_men, players_women,
            coaches_men, coaches_women, matches_men, matches_women
        """
        return (
            self.load_countries(),
            self.load_players_men(),
            self.load_players_women(),
            self.load_coaches_men(),
            self.load_coaches_women(),
            self.load_matches_men(),
            self.load_matches_women(),
        )

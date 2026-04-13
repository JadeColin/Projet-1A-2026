from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent.parent / "Base_de_données" / "volleyball"


# ---------------------------------------------------------------------------
# Téléchargement des bases de données
# ---------------------------------------------------------------------------

def load_countries() -> pd.DataFrame:
    """
    Charge la table des pays (codes IOC).

    Colonnes : code, country, country_long
    """
    return pd.read_csv(ROOT / "country.csv")


def load_players_men() -> pd.DataFrame:
    """
    Charge et nettoie les joueurs masculins de volleyball (JO 2024).

    Colonnes : name, country_code, height, birth_date, birth_place, nickname

    Colonnes ajoutées :
        - birth_date : converti en datetime
        - gender     : 'M'
    """
    df = pd.read_csv(ROOT / "player_men.csv", dtype={"height": "Int64"})
    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    df["gender"] = "M"
    return df


def load_players_women() -> pd.DataFrame:
    """
    Charge et nettoie les joueuses de volleyball (JO 2024).

    Colonnes : name, country_code, height, birth_date, birth_place, nickname

    Colonnes ajoutées :
        - birth_date : converti en datetime
        - gender     : 'F'
    """
    df = pd.read_csv(ROOT / "player_women.csv", dtype={"height": "Int64"})
    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    df["gender"] = "F"
    return df


def load_coaches_men() -> pd.DataFrame:
    """
    Charge et nettoie les coachs masculins de volleyball (JO 2024).

    Colonnes : name, birth_date, gender, function, country_code

    Colonnes ajoutées :
        - birth_date : converti en datetime
    """
    df = pd.read_csv(ROOT / "coach_men.csv")
    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    return df


def load_coaches_women() -> pd.DataFrame:
    """
    Charge et nettoie les coachs féminins de volleyball (JO 2024).

    Colonnes : name, birth_date, gender, function, country_code

    Colonnes ajoutées :
        - birth_date : converti en datetime
    """
    df = pd.read_csv(ROOT / "coach_women.csv")
    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    return df


def load_matches_men() -> pd.DataFrame:
    """
    Charge et nettoie les matchs masculins de volleyball (JO 2024).

    Colonnes : date, stage, country_code_1, country_code_2,
               set_country_1, set_country_2

    Colonnes ajoutées :
        - date   : converti en datetime
        - winner : pays ayant remporté le match (sets dominants)
    """
    df = pd.read_csv(ROOT / "match_men.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["winner"] = df.apply(
        lambda r: r["country_code_1"] if r["set_country_1"] > r["set_country_2"] else r["country_code_2"],
        axis=1,
    )
    return df


def load_matches_women() -> pd.DataFrame:
    """
    Charge et nettoie les matchs féminins de volleyball (JO 2024).

    Note : le fichier source utilise 'country_1/2' (noms complets) au lieu
    de 'country_code_1/2'. Les colonnes sont renommées pour uniformité.

    Colonnes : date, stage, country_code_1, country_code_2,
               set_country_1, set_country_2

    Colonnes ajoutées :
        - date   : converti en datetime
        - winner : pays ayant remporté le match
    """
    df = pd.read_csv(ROOT / "match_women.csv")
    df = df.rename(columns={"country_1": "country_code_1", "country_2": "country_code_2"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["winner"] = df.apply(
        lambda r: r["country_code_1"] if r["set_country_1"] > r["set_country_2"] else r["country_code_2"],
        axis=1,
    )
    return df


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Charge toutes les tables volleyball en une seule fois.

    Renvoie :
        countries       : DataFrame des pays
        players_men     : DataFrame des joueurs masculins
        players_women   : DataFrame des joueuses
        coaches_men     : DataFrame des coachs masculins
        coaches_women   : DataFrame des coachs féminins
        matches_men     : DataFrame des matchs masculins
        matches_women   : DataFrame des matchs féminins
    """
    return (
        load_countries(),
        load_players_men(),
        load_players_women(),
        load_coaches_men(),
        load_coaches_women(),
        load_matches_men(),
        load_matches_women(),
    )


# ---------------------------------------------------------------------------
# Export CSV
# ---------------------------------------------------------------------------

def export_all(output_dir: str | Path = Path(__file__).parent / "output") -> None:
    """
    Exporte toutes les tables volleyball en fichiers CSV nettoyés.

    Fichiers générés dans output_dir :
        - volleyball_countries_clean.csv
        - volleyball_players_men_clean.csv
        - volleyball_players_women_clean.csv
        - volleyball_coaches_men_clean.csv
        - volleyball_coaches_women_clean.csv
        - volleyball_matches_men_clean.csv
        - volleyball_matches_women_clean.csv
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    countries, players_men, players_women, coaches_men, coaches_women, matches_men, matches_women = load_all()

    countries.to_csv(output_dir / "volleyball_countries_clean.csv", index=False, encoding="utf-8")
    players_men.to_csv(output_dir / "volleyball_players_men_clean.csv", index=False, encoding="utf-8")
    players_women.to_csv(output_dir / "volleyball_players_women_clean.csv", index=False, encoding="utf-8")
    coaches_men.to_csv(output_dir / "volleyball_coaches_men_clean.csv", index=False, encoding="utf-8")
    coaches_women.to_csv(output_dir / "volleyball_coaches_women_clean.csv", index=False, encoding="utf-8")
    matches_men.to_csv(output_dir / "volleyball_matches_men_clean.csv", index=False, encoding="utf-8")
    matches_women.to_csv(output_dir / "volleyball_matches_women_clean.csv", index=False, encoding="utf-8")

    print(f"Exports sauvegardés dans : {output_dir.resolve()}")
    print(f"  volleyball_countries_clean.csv       — {len(countries)} lignes")
    print(f"  volleyball_players_men_clean.csv     — {len(players_men)} lignes")
    print(f"  volleyball_players_women_clean.csv   — {len(players_women)} lignes")
    print(f"  volleyball_coaches_men_clean.csv     — {len(coaches_men)} lignes")
    print(f"  volleyball_coaches_women_clean.csv   — {len(coaches_women)} lignes")
    print(f"  volleyball_matches_men_clean.csv     — {len(matches_men)} lignes")
    print(f"  volleyball_matches_women_clean.csv   — {len(matches_women)} lignes")


if __name__ == "__main__":
    export_all()

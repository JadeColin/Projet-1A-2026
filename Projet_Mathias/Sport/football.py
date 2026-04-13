from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent.parent / "Base_de_données" / "Football"


# ---------------------------------------------------------------------------
# Téléchargement des bases de données
# ---------------------------------------------------------------------------

def load_countries() -> pd.DataFrame:
    """
    Charge les pays du football européen.

    Colonnes : id, name
    """
    return pd.read_csv(ROOT / "country.csv", dtype={"id": int})


def load_leagues() -> pd.DataFrame:
    """
    Charge les ligues du football européen.

    Colonnes : id, country_id, name
    """
    return pd.read_csv(ROOT / "league.csv", dtype={"id": int, "country_id": int})


def load_games() -> pd.DataFrame:
    """
    Charge les matchs.

    ATTENTION : ce fichier contient des statistiques de matchs NBA
    (fgm, fg3m, pts…) et non du football. Il est présent dans le dossier
    par erreur. Les IDs d'équipes correspondent aux franchises NBA.

    Colonnes ajoutées :
        - game_date : converti en datetime
    """
    df = pd.read_csv(ROOT / "game.csv")
    df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
    return df


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Charge les trois tables football en une seule fois.

    Renvoie :
        countries : DataFrame des pays
        leagues   : DataFrame des ligues
        games     : DataFrame des matchs (voir avertissement dans load_games)
    """
    return load_countries(), load_leagues(), load_games()


# ---------------------------------------------------------------------------
# Export CSV
# ---------------------------------------------------------------------------

def export_all(output_dir: str | Path = Path(__file__).parent / "output") -> None:
    """
    Exporte les trois tables football en fichiers CSV nettoyés.

    Fichiers générés dans output_dir :
        - football_countries_clean.csv
        - football_leagues_clean.csv
        - football_games_clean.csv
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    countries, leagues, games = load_all()

    countries.to_csv(output_dir / "football_countries_clean.csv", index=False, encoding="utf-8")
    leagues.to_csv(output_dir / "football_leagues_clean.csv", index=False, encoding="utf-8")
    games.to_csv(output_dir / "football_games_clean.csv", index=False, encoding="utf-8")

    print(f"Exports sauvegardés dans : {output_dir.resolve()}")
    print(f"  football_countries_clean.csv  — {len(countries)} lignes")
    print(f"  football_leagues_clean.csv    — {len(leagues)} lignes")
    print(f"  football_games_clean.csv      — {len(games)} lignes")


if __name__ == "__main__":
    export_all()

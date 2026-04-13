from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent.parent / "Base_de_données" / "tennis"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _dob_to_datetime(series: pd.Series) -> pd.Series:
    """Convertit les dates de naissance au format YYYYMMDD (float) en datetime."""
    return pd.to_datetime(
        series.dropna().astype(int).astype(str),
        format="%Y%m%d",
        errors="coerce",
    ).reindex(series.index)


def _tourney_date_to_datetime(series: pd.Series) -> pd.Series:
    """Convertit les dates de tournoi au format YYYYMMDD (int) en datetime."""
    return pd.to_datetime(series.astype(str), format="%Y%m%d", errors="coerce")


# ---------------------------------------------------------------------------
# Téléchargement des bases de données
# ---------------------------------------------------------------------------

def load_atp_players() -> pd.DataFrame:
    """
    Charge et nettoie les joueurs ATP 2024.

    Colonnes : player_id, name_first, name_last, hand, dob, ioc, height

    Colonnes ajoutées :
        - full_name : prénom + nom
        - dob       : converti en datetime (depuis YYYYMMDD)
    """
    df = pd.read_csv(ROOT / "atp_players_2024.csv", dtype={"player_id": int})
    df["dob"] = _dob_to_datetime(df["dob"])
    df["full_name"] = df["name_first"].str.strip() + " " + df["name_last"].str.strip()
    return df


def load_wta_players() -> pd.DataFrame:
    """
    Charge et nettoie les joueuses WTA 2024.

    Colonnes : player_id, name_first, name_last, hand, dob, ioc, height

    Colonnes ajoutées :
        - full_name : prénom + nom
        - dob       : converti en datetime (depuis YYYYMMDD)
    """
    df = pd.read_csv(ROOT / "wta_players_2024.csv", dtype={"player_id": int})
    df["dob"] = _dob_to_datetime(df["dob"])
    df["full_name"] = df["name_first"].str.strip() + " " + df["name_last"].str.strip()
    return df


def load_atp_matches() -> pd.DataFrame:
    """
    Charge et nettoie les matchs ATP 2024.

    Colonnes principales : tourney_id, tourney_name, surface, tourney_date,
    winner_id, loser_id, score, round, minutes, statistiques de service
    (aces, double fautes, points de service…).

    Colonnes ajoutées :
        - tourney_date : converti en datetime (depuis YYYYMMDD)
    """
    df = pd.read_csv(ROOT / "atp_matches_2024.csv")
    df["tourney_date"] = _tourney_date_to_datetime(df["tourney_date"])
    return df


def load_wta_matches() -> pd.DataFrame:
    """
    Charge et nettoie les matchs WTA 2024.

    Mêmes colonnes que les matchs ATP.

    Colonnes ajoutées :
        - tourney_date : converti en datetime (depuis YYYYMMDD)
    """
    df = pd.read_csv(ROOT / "wta_matches_2024.csv")
    df["tourney_date"] = _tourney_date_to_datetime(df["tourney_date"])
    return df


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Charge les quatre tables tennis en une seule fois.

    Renvoie :
        atp_players : DataFrame des joueurs ATP
        wta_players : DataFrame des joueuses WTA
        atp_matches : DataFrame des matchs ATP
        wta_matches : DataFrame des matchs WTA
    """
    return load_atp_players(), load_wta_players(), load_atp_matches(), load_wta_matches()


# ---------------------------------------------------------------------------
# Export CSV
# ---------------------------------------------------------------------------

def export_all(output_dir: str | Path = Path(__file__).parent / "output") -> None:
    """
    Exporte les quatre tables tennis en fichiers CSV nettoyés.

    Fichiers générés dans output_dir :
        - tennis_atp_players_clean.csv
        - tennis_wta_players_clean.csv
        - tennis_atp_matches_clean.csv
        - tennis_wta_matches_clean.csv
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    atp_players, wta_players, atp_matches, wta_matches = load_all()

    atp_players.to_csv(output_dir / "tennis_atp_players_clean.csv", index=False, encoding="utf-8")
    wta_players.to_csv(output_dir / "tennis_wta_players_clean.csv", index=False, encoding="utf-8")
    atp_matches.to_csv(output_dir / "tennis_atp_matches_clean.csv", index=False, encoding="utf-8")
    wta_matches.to_csv(output_dir / "tennis_wta_matches_clean.csv", index=False, encoding="utf-8")

    print(f"Exports sauvegardés dans : {output_dir.resolve()}")
    print(f"  tennis_atp_players_clean.csv  — {len(atp_players)} lignes")
    print(f"  tennis_wta_players_clean.csv  — {len(wta_players)} lignes")
    print(f"  tennis_atp_matches_clean.csv  — {len(atp_matches)} lignes")
    print(f"  tennis_wta_matches_clean.csv  — {len(wta_matches)} lignes")


if __name__ == "__main__":
    export_all()

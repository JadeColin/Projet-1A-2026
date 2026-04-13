from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent.parent / "Base_de_données" / "Lol"


# ---------------------------------------------------------------------------
# Téléchargement des bases de données
# ---------------------------------------------------------------------------

def load_players() -> pd.DataFrame:
    """
    Charge et nettoie les données des joueurs LoL (EMEA).

    Colonnes : pseudo, name, country_of_birth, birthdate, role, team

    Colonnes ajoutées :
        - birthdate : converti en datetime
    """
    df = pd.read_csv(ROOT / "player.csv")
    df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce")
    return df


def load_coaches() -> pd.DataFrame:
    """
    Charge et nettoie les données des coachs LoL (EMEA).

    Colonnes : pseudo, name, country_of_birth, birthdate, role, team

    Colonnes ajoutées :
        - birthdate : converti en datetime
    """
    df = pd.read_csv(ROOT / "coach.csv")
    df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce")
    return df


def load_teams() -> pd.DataFrame:
    """
    Charge les équipes LoL (EMEA).

    Colonnes : team, team_abbreviation, location, region
    """
    return pd.read_csv(ROOT / "team.csv")


def load_matches() -> pd.DataFrame:
    """
    Charge et nettoie les matchs LoL (EMEA 2025).

    Colonnes principales : patch, date, week, day, team_blue, team_red,
    winner, time, kills/assists/deaths/gold/turrets/dragons/barons par équipe,
    joueurs titulaires par rôle (top, jungle, mid, bot, sup) pour chaque équipe,
    picks et bans.

    Colonnes ajoutées :
        - date      : converti en datetime
        - duration_s: durée du match convertie en secondes (depuis HH:MM:SS)
    """
    df = pd.read_csv(ROOT / "match.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["duration_s"] = pd.to_timedelta(df["time"], errors="coerce").dt.total_seconds().astype("Int64")
    return df


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Charge les quatre tables LoL en une seule fois.

    Renvoie :
        players : DataFrame des joueurs
        coaches : DataFrame des coachs
        teams   : DataFrame des équipes
        matches : DataFrame des matchs
    """
    return load_players(), load_coaches(), load_teams(), load_matches()


# ---------------------------------------------------------------------------
# Export CSV
# ---------------------------------------------------------------------------

def export_all(output_dir: str | Path = Path(__file__).parent / "output") -> None:
    """
    Exporte les quatre tables LoL en fichiers CSV nettoyés.

    Fichiers générés dans output_dir :
        - lol_players_clean.csv
        - lol_coaches_clean.csv
        - lol_teams_clean.csv
        - lol_matches_clean.csv
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    players, coaches, teams, matches = load_all()

    players.to_csv(output_dir / "lol_players_clean.csv", index=False, encoding="utf-8")
    coaches.to_csv(output_dir / "lol_coaches_clean.csv", index=False, encoding="utf-8")
    teams.to_csv(output_dir / "lol_teams_clean.csv", index=False, encoding="utf-8")
    matches.to_csv(output_dir / "lol_matches_clean.csv", index=False, encoding="utf-8")

    print(f"Exports sauvegardés dans : {output_dir.resolve()}")
    print(f"  lol_players_clean.csv  — {len(players)} lignes")
    print(f"  lol_coaches_clean.csv  — {len(coaches)} lignes")
    print(f"  lol_teams_clean.csv    — {len(teams)} lignes")
    print(f"  lol_matches_clean.csv  — {len(matches)} lignes")


if __name__ == "__main__":
    export_all()

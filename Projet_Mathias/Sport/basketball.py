from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "Basketball"


# ---------------------------------------------------------------------------
# Convertion feet-inches en centimètre (taille)
# ---------------------------------------------------------------------------

def _height_to_cm(height_str: str) -> float | None:
    """Convertit le format pieds-pouces '6-8' en centimètres."""
    if pd.isna(height_str):
        return None
    parts = str(height_str).split("-")
    if len(parts) == 2:
        feet, inches = int(parts[0]), int(parts[1])
        return round((feet * 12 + inches) * 2.54, 1)
    return None


# ---------------------------------------------------------------------------
# Téléchargement des bases de données
# ---------------------------------------------------------------------------

def load_players() -> pd.DataFrame:
    """
    Charge et nettoie les données des joueurs NBA.

    Colonnes ajoutées :
        - full_name  : prénom + nom
        - height_cm  : taille convertie en centimètres
    """
    df = pd.read_csv(
        ROOT / "player.csv",
        dtype={"person_id": int, "jersey": "Int64", "weight": "Int64", "team_id": int},
    )
    df["full_name"] = df["first_name"].str.strip() + " " + df["last_name"].str.strip()
    df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce")
    df["height_cm"] = df["height"].apply(_height_to_cm)
    return df


def load_teams() -> pd.DataFrame:
    """
    Charge et nettoie les données des équipes NBA.

    Renvoie un DataFrame avec les 30 franchises.
    """
    df = pd.read_csv(ROOT / "team.csv", dtype={"id": int})
    return df


def load_matches() -> pd.DataFrame:
    """
    Charge et nettoie le fichier match.csv.

    ATTENTION : ce fichier contient des données de football européen
    (saisons 2008-2016, 11 joueurs par équipe) et non du basketball NBA.
    Il est présent dans le dossier par erreur. Les colonnes home_team_goal
    et away_team_goal correspondent à des buts, pas à des points.
    """
    df = pd.read_csv(
        ROOT / "match.csv",
        dtype={
            "id": int,
            "country_id": "Int64",
            "league_id": "Int64",
            "stage": "Int64",
            "home_team_goal": "Int64",
            "away_team_goal": "Int64",
        },
    )
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Chargement global
# ---------------------------------------------------------------------------

def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Charge les trois tables basketball en une seule fois.

    Renvoie :
        players  : DataFrame des joueurs
        teams    : DataFrame des équipes
        matches  : DataFrame des matchs (voir avertissement dans load_matches)
    """
    players = load_players()
    teams = load_teams()
    matches = load_matches()
    return players, teams, matches


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def get_team_roster(players: pd.DataFrame, teams: pd.DataFrame, team_name: str) -> pd.DataFrame:
    """
    Retourne les joueurs d'une équipe à partir de son nom complet, abréviation ou surnom.

    Exemple :
        roster = get_team_roster(players, teams, "Lakers")
    """
    mask = (
        teams["full_name"].str.contains(team_name, case=False, na=False)
        | teams["abbreviation"].str.contains(team_name, case=False, na=False)
        | teams["nickname"].str.contains(team_name, case=False, na=False)
    )
    matched = teams[mask]
    if matched.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")
    team_id = matched.iloc[0]["id"]
    return players[players["team_id"] == team_id].reset_index(drop=True)


def players_with_team(players: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """
    Joint les joueurs avec leur équipe.

    Retourne un DataFrame enrichi avec les colonnes de l'équipe
    (full_name de l'équipe renommée en team_name, abbreviation, city…).
    """
    return players.merge(
        teams.rename(columns={"full_name": "team_name", "id": "team_id"}),
        on="team_id",
        how="left",
    )


# ---------------------------------------------------------------------------
# Export CSV
# ---------------------------------------------------------------------------

def export_all(output_dir: str | Path = Path(__file__).parent / "output") -> None:
    """
    Exporte les trois tables basketball en fichiers CSV nettoyés.

    Les fichiers sont sauvegardés dans output_dir (créé automatiquement) :
        - players_clean.csv
        - teams_clean.csv
        - matches_clean.csv
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    players, teams, matches = load_all()

    players.to_csv(output_dir / "players_clean.csv", index=False, encoding="utf-8")
    teams.to_csv(output_dir / "teams_clean.csv", index=False, encoding="utf-8")
    matches.to_csv(output_dir / "matches_clean.csv", index=False, encoding="utf-8")

    print(f"Exports sauvegardés dans : {output_dir.resolve()}")
    print(f"  players_clean.csv  — {len(players)} lignes")
    print(f"  teams_clean.csv    — {len(teams)} lignes")
    print(f"  matches_clean.csv  — {len(matches)} lignes")


# ---------------------------------------------------------------------------
# Point d'entrée rapide pour vérifier le chargement
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    export_all()

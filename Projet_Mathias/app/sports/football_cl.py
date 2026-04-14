import pandas as pd

from Projet_Mathias.loaders.FootballChampionsLeagueLoader import FootballChampionsLeagueLoader

_loader = None
_players: pd.DataFrame = None
_teams: pd.DataFrame = None
_matches: pd.DataFrame = None


def _load():
    global _loader, _players, _teams, _matches
    if _loader is None:
        _loader = FootballChampionsLeagueLoader()
        _players, _teams, _matches = _loader.load_all()


# ---------------------------------------------------------------------------
# 1. Meilleurs buteurs
# ---------------------------------------------------------------------------

def meilleurs_buteurs(n: int = 10) -> pd.DataFrame:
    """Top N joueurs par nombre de buts en Ligue des Champions."""
    _load()
    df = _players[["player_name", "club", "position", "goals"]].copy()
    df = df.sort_values("goals", ascending=False).head(n).reset_index(drop=True)
    df.index += 1
    return df.rename(columns={"player_name": "Joueur", "club": "Club", "position": "Poste", "goals": "Buts"})


# ---------------------------------------------------------------------------
# 2. Meilleurs passeurs
# ---------------------------------------------------------------------------

def meilleurs_passeurs(n: int = 10) -> pd.DataFrame:
    """Top N joueurs par nombre de passes décisives."""
    _load()
    df = _players[["player_name", "club", "position", "assists"]].copy()
    df = df.sort_values("assists", ascending=False).head(n).reset_index(drop=True)
    df.index += 1
    return df.rename(columns={"player_name": "Joueur", "club": "Club", "position": "Poste", "assists": "Passes déc."})


# ---------------------------------------------------------------------------
# 3. Stats d'une équipe (joueurs)
# ---------------------------------------------------------------------------

def stats_equipe(team_name: str) -> pd.DataFrame:
    """Statistiques collectives d'une équipe (somme sur tous les joueurs)."""
    _load()

    mask = _players["club"].str.contains(team_name, case=False, na=False)
    squad = _players[mask]
    if squad.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    club_label = squad.iloc[0]["club"]
    stat_cols = ["goals", "assists", "minutes_played", "yellow", "red"]
    existing = [c for c in stat_cols if c in squad.columns]
    totaux = squad[existing].sum()

    labels = {
        "goals": "Buts", "assists": "Passes déc.",
        "minutes_played": "Minutes jouées", "yellow": "Cartons jaunes", "red": "Cartons rouges",
    }
    result = totaux.rename(labels).reset_index()
    result.columns = ["Statistique", f"{club_label} (total saison)"]
    return result


# ---------------------------------------------------------------------------
# 4. Résultats par phase
# ---------------------------------------------------------------------------

def resultats_par_phase() -> pd.DataFrame:
    """Nombre de matchs et buts marqués par phase de compétition."""
    _load()
    m = _matches.copy()
    m["buts_total"] = m["score_team_home"] + m["score_team_away"]
    grouped = m.groupby("phase").agg(
        Matchs=("phase", "count"),
        Buts_total=("buts_total", "sum"),
        Moy_buts=("buts_total", "mean"),
    ).round({"Moy_buts": 2}).reset_index()
    grouped = grouped.rename(columns={"phase": "Phase", "Buts_total": "Buts totaux", "Moy_buts": "Moy. buts/match"})
    return grouped

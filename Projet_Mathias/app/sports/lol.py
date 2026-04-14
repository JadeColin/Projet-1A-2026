import pandas as pd

from Projet_Mathias.loaders.LolLoader import LolLoader

_loader = None
_players: pd.DataFrame = None
_coaches: pd.DataFrame = None
_teams: pd.DataFrame = None
_matches: pd.DataFrame = None


def _load():
    global _loader, _players, _coaches, _teams, _matches
    if _loader is None:
        _loader = LolLoader()
        _players, _coaches, _teams, _matches = _loader.load_all()


# ---------------------------------------------------------------------------
# 1. Classement EMEA (victoires)
# ---------------------------------------------------------------------------

def classement_emea() -> pd.DataFrame:
    """Classement des équipes EMEA 2025 par victoires."""
    _load()
    total = (
        pd.concat([_matches["team_blue"], _matches["team_red"]])
        .value_counts()
        .rename("Matchs joués")
    )
    victoires = _matches["winner"].value_counts().rename("Victoires")
    classement = pd.DataFrame({"Victoires": victoires, "Matchs joués": total}).fillna(0).astype(int)
    classement["Défaites"] = classement["Matchs joués"] - classement["Victoires"]
    classement["% Victoires"] = (classement["Victoires"] / classement["Matchs joués"] * 100).round(1)
    classement = classement.sort_values("Victoires", ascending=False).reset_index()
    classement = classement.rename(columns={"index": "Équipe"})
    classement.index += 1
    return classement[["Équipe", "Victoires", "Défaites", "Matchs joués", "% Victoires"]]


# ---------------------------------------------------------------------------
# 2. Stats d'une équipe
# ---------------------------------------------------------------------------

def stats_equipe(team_name: str) -> pd.DataFrame:
    """Statistiques moyennes par match pour une équipe LoL."""
    _load()

    # Vérifier que l'équipe existe
    all_teams = pd.concat([_matches["team_blue"], _matches["team_red"]]).unique()
    matches_team = pd.concat([
        _matches[_matches["team_blue"].str.contains(team_name, case=False, na=False)],
        _matches[_matches["team_red"].str.contains(team_name, case=False, na=False)],
    ]).drop_duplicates()

    if matches_team.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    team_label = matches_team.iloc[0]["team_blue"] if team_name.lower() in matches_team.iloc[0]["team_blue"].lower() else matches_team.iloc[0]["team_red"]

    blue = matches_team[matches_team["team_blue"] == team_label].rename(
        columns={c: c.replace("_team_blue", "") for c in matches_team.columns}
    )
    red = matches_team[matches_team["team_red"] == team_label].rename(
        columns={c: c.replace("_team_red", "") for c in matches_team.columns}
    )
    combined = pd.concat([blue, red])

    stat_cols = ["kills", "assists", "deaths", "gold", "turrets", "dragons", "barons"]
    existing = [c for c in stat_cols if c in combined.columns]
    moyennes = combined[existing].mean().round(2)

    labels = {
        "kills": "Kills", "assists": "Assists", "deaths": "Morts",
        "gold": "Or total", "turrets": "Tourelles", "dragons": "Dragons", "barons": "Barons",
    }
    result = moyennes.rename(labels).reset_index()
    result.columns = ["Statistique", f"{team_label} (moy./match)"]
    return result


# ---------------------------------------------------------------------------
# 3. Champions les plus pickés / bannés
# ---------------------------------------------------------------------------

def champions_picks_bans(n: int = 10) -> pd.DataFrame:
    """Top N champions par nombre de picks et de bans."""
    _load()

    pick_cols = [c for c in _matches.columns if c.startswith("pick_")]
    ban_cols = [c for c in _matches.columns if c.startswith("ban_")]

    picks = _matches[pick_cols].values.flatten()
    bans = _matches[ban_cols].values.flatten()

    picks_count = pd.Series(picks).dropna().value_counts().rename("Picks").head(n)
    bans_count = pd.Series(bans).dropna().value_counts().rename("Bans").head(n)

    result = pd.DataFrame({"Picks": picks_count, "Bans": bans_count}).fillna(0).astype(int)
    result = result.sort_values("Picks", ascending=False).head(n).reset_index()
    result = result.rename(columns={"index": "Champion"})
    result.index += 1
    return result[["Champion", "Picks", "Bans"]]


# ---------------------------------------------------------------------------
# 4. Durée moyenne des parties
# ---------------------------------------------------------------------------

def duree_moyenne_parties() -> pd.DataFrame:
    """Durée moyenne des parties par équipe (en minutes)."""
    _load()

    rows = []
    all_teams = pd.concat([_matches["team_blue"], _matches["team_red"]]).unique()
    for team in sorted(all_teams):
        mask = (_matches["team_blue"] == team) | (_matches["team_red"] == team)
        moy_s = _matches.loc[mask, "duration_s"].mean()
        rows.append({"Équipe": team, "Durée moy. (min)": round(moy_s / 60, 1) if pd.notna(moy_s) else None})

    result = pd.DataFrame(rows).sort_values("Durée moy. (min)").reset_index(drop=True)
    result.index += 1

    # Ligne globale
    global_moy = _matches["duration_s"].mean()
    global_row = pd.DataFrame([{"Équipe": "TOUTES ÉQUIPES", "Durée moy. (min)": round(global_moy / 60, 1)}])
    return pd.concat([global_row, result], ignore_index=True)

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
    classement["% Victoires"] = (
        classement["Victoires"] / classement["Matchs joués"] * 100).round(1)
    classement = classement.sort_values("Victoires", ascending=False).reset_index()
    classement = classement.rename(columns={"index": "Équipe"})
    classement.index += 1
    return classement[["Équipe", "Victoires", "Défaites", "Matchs joués", "% Victoires"]]


# ---------------------------------------------------------------------------
# 2. Stats d'une équipe plus duree moyenne 
# ---------------------------------------------------------------------------

def stats_equipe(team_name: str) -> pd.DataFrame:
    """Statistiques moyennes par match pour une équipe LoL, incluant la durée moyenne."""
    _load()

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

    # Ajouter la durée moyenne ici
    if "duration_s" in combined.columns:
        duree_moy = round(combined["duration_s"].mean() / 60, 1)
        moyennes["duration_s"] = duree_moy

    labels = {
        "kills": "Kills", "assists": "Assists", "deaths": "Morts",
        "gold": "Or total", "turrets": "Tourelles", "dragons": "Dragons",
        "barons": "Barons", "duration_s": "Durée moy. (min)"
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
# 5. Roster d'une équipe (joueurs + coachs)
# ---------------------------------------------------------------------------

def roster_equipe(team_name: str) -> pd.DataFrame:
    """Roster d'une équipe LoL : joueurs et coachs avec nom, pseudo, date de naissance, position."""
    _load()

    # Joueurs
    mask_players = _players["team"].str.contains(team_name, case=False, na=False)
    joueurs = _players[mask_players].copy()
    joueurs["type"] = "Joueur"

    # Coachs
    mask_coaches = _coaches["team"].str.contains(team_name, case=False, na=False)
    coachs = _coaches[mask_coaches].copy()
    coachs["type"] = "Coach"

    if joueurs.empty and coachs.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    # Fusionner joueurs + coachs
    combined = pd.concat([joueurs, coachs], ignore_index=True)

    cols = ["type", "name", "pseudo", "birthdate", "role"]
    labels = {
        "type": "Type", "name": "Nom", "pseudo": "Pseudo",
        "birthdate": "Date de naissance", "role": "Position"
    }
    existing = [c for c in cols if c in combined.columns]
    result = combined[existing].rename(columns=labels).reset_index(drop=True)
    result.index += 1
    return result
import pandas as pd

from Projet_Mathias.loaders.BasketballLoader import BasketballLoader

_loader = None
_players: pd.DataFrame = None
_teams: pd.DataFrame = None
_matches: pd.DataFrame = None


def _load():
    global _loader, _players, _teams, _matches
    if _loader is None:
        _loader = BasketballLoader()
        _players, _teams, _matches = _loader.load_all()


# ---------------------------------------------------------------------------
# 1. Classement des équipes (victoires / défaites)
# ---------------------------------------------------------------------------

def classement_equipes() -> pd.DataFrame:
    """Classement NBA par victoires sur la saison 2022-2023."""
    _load()
    m = _matches.copy()

    # Déterminer le gagnant de chaque match
    m["winner_id"] = m.apply(
        lambda r: r["team_id_home"] if r["pts_home"] > r["pts_away"] else r["team_id_away"],
        axis=1,
    )

    victoires = m["winner_id"].value_counts().rename("Victoires")
    total = len(m)

    # Compter les matchs joués par équipe
    matchs_joues = (
        pd.concat([m["team_id_home"], m["team_id_away"]])
        .value_counts()
        .rename("Matchs joués")
    )

    classement = pd.DataFrame({"Victoires": victoires, "Matchs joués": matchs_joues}).fillna(0)
    classement["Défaites"] = classement["Matchs joués"] - classement["Victoires"]
    classement = classement.astype(int)
    classement[
        "% Victoires"] = (classement["Victoires"] / classement["Matchs joués"] * 100).round(1)

    # Joindre les noms d'équipes
    teams_idx = _teams.set_index("id")[["full_name", "abbreviation"]]
    classement = classement.join(teams_idx).reset_index(drop=True)
    classement = classement.rename(columns={"full_name": "Équipe", "abbreviation": "Abrév."})
    classement = classement.sort_values("Victoires", ascending=False).reset_index(drop=True)
    classement.index += 1

    return classement[["Équipe", "Abrév.", "Victoires", "Défaites", "Matchs joués", "% Victoires"]]


# ---------------------------------------------------------------------------
# 2. Top équipes offensives (points marqués en moyenne)
# ---------------------------------------------------------------------------

def top_equipes_offensives(n: int = 10) -> pd.DataFrame:
    """Top N équipes par moyenne de points marqués par match."""
    _load()
    m = _matches.copy()

    home = m[["team_id_home", "pts_home"]].rename(columns={
        "team_id_home": "team_id", "pts_home": "pts"})
    away = m[["team_id_away", "pts_away"]].rename(columns={
        "team_id_away": "team_id", "pts_away": "pts"})
    all_pts = pd.concat([home, away])

    moy = all_pts.groupby("team_id")["pts"].mean().round(1).sort_values(ascending=False).head(n)
    teams_idx = _teams.set_index("id")[["full_name", "abbreviation"]]
    result = moy.to_frame("Moy. pts/match").join(teams_idx)
    result = result.rename(columns={"full_name": "Équipe", "abbreviation": "Abrév."})
    result = result.reset_index(drop=True)
    result.index += 1
    return result[["Équipe", "Abrév.", "Moy. pts/match"]]


# ---------------------------------------------------------------------------
# 3. Stats d'une équipe
# ---------------------------------------------------------------------------

def stats_equipe(team_name: str) -> pd.DataFrame:
    """Statistiques moyennes par match pour une équipe (recherche insensible à la casse)."""
    _load()

    mask = (
        _teams["full_name"].str.contains(team_name, case=False, na=False)
        | _teams["abbreviation"].str.contains(team_name, case=False, na=False)
        | _teams["nickname"].str.contains(team_name, case=False, na=False)
    )
    matched = _teams[mask]
    if matched.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    team_id = int(matched.iloc[0]["id"])
    team_label = matched.iloc[0]["full_name"]

    home = _matches[_matches["team_id_home"] == team_id].rename(
        columns={c: c.replace("_home", "") for c in _matches.columns if c.endswith("_home")}
    )
    away = _matches[_matches["team_id_away"] == team_id].rename(
        columns={c: c.replace("_away", "") for c in _matches.columns if c.endswith("_away")}
    )
    combined = pd.concat([home, away])

    stat_cols = [
        "pts", "fgm", "fga", "fg3m", "fg3a", "ftm", "fta", "reb", "ast", "stl", "blk", "tov"]
    existing = [c for c in stat_cols if c in combined.columns]
    moyennes = combined[existing].mean().round(2)

    labels = {
        "pts": "Points", "fgm": "Tirs réussis", "fga": "Tirs tentés",
        "fg3m": "3pts réussis", "fg3a": "3pts tentés",
        "ftm": "LF réussies", "fta": "LF tentées",
        "reb": "Rebonds", "ast": "Passes", "stl": "Interceptions",
        "blk": "Contres", "tov": "Pertes de balle",
    }
    result = moyennes.rename(labels).reset_index()
    result.columns = ["Statistique", f"{team_label} (moy./match)"]
    return result


# ---------------------------------------------------------------------------
# 4. Roster d'une équipe
# ---------------------------------------------------------------------------

def roster_equipe(team_name: str) -> pd.DataFrame:
    """Liste des joueurs d'une équipe avec poste, année de naissance et poids."""
    _load()
    df = _loader.get_team_roster(_players, _teams, team_name)
    
    df = df.copy()
    df["birth_year"] = pd.to_datetime(df["birthdate"], errors="coerce").dt.year

    cols = ["full_name", "position", "birth_year", "weight", "height_cm", "jersey"]
    labels = {
        "full_name": "Joueur",
        "position": "Poste",
        "birth_year": "Année naissance",
        "weight": "Poids (lbs)",
        "height_cm": "Taille (cm)",
        "jersey": "Numéro",
    }
    existing = [c for c in cols if c in df.columns]
    result = df[existing].rename(columns=labels).reset_index(drop=True)
    result.index += 1
    return result

# ---------------------------------------------------------------------------
# 5. Classement défensif
# ---------------------------------------------------------------------------

def classement_defensif(n: int = 10) -> pd.DataFrame:
    """Top N équipes les plus défensives (points encaissés, blocks, interceptions)."""
    _load()
    m = _matches.copy()

    # Points encaissés par équipe (quand tu joues à domicile, tu encaisses les points de l'adversaire)
    pts_encaisses_home = m[["team_id_home", "pts_away"]].rename(columns={"team_id_home": "team_id", "pts_away": "pts_encaisses"})
    pts_encaisses_away = m[["team_id_away", "pts_home"]].rename(columns={"team_id_away": "team_id", "pts_home": "pts_encaisses"})
    pts_encaisses = pd.concat([pts_encaisses_home, pts_encaisses_away]).groupby("team_id")["pts_encaisses"].mean().round(1)

    # Blocks par équipe
    blk_home = m[["team_id_home", "blk_home"]].rename(columns={"team_id_home": "team_id", "blk_home": "blk"})
    blk_away = m[["team_id_away", "blk_away"]].rename(columns={"team_id_away": "team_id", "blk_away": "blk"})
    blk = pd.concat([blk_home, blk_away]).groupby("team_id")["blk"].mean().round(1)

    # Interceptions par équipe
    stl_home = m[["team_id_home", "stl_home"]].rename(columns={"team_id_home": "team_id", "stl_home": "stl"})
    stl_away = m[["team_id_away", "stl_away"]].rename(columns={"team_id_away": "team_id", "stl_away": "stl"})
    stl = pd.concat([stl_home, stl_away]).groupby("team_id")["stl"].mean().round(1)

    # Assembler tout ensemble
    result = pd.DataFrame({
        "Pts encaissés/match": pts_encaisses,
        "Blocks/match": blk,
        "Interceptions/match": stl,
    })

    # Ajouter les noms d'équipes
    teams_idx = _teams.set_index("id")["full_name"]
    result["Équipe"] = result.index.map(teams_idx)

    # Trier par points encaissés (moins = meilleure défense)
    result = result.sort_values("Pts encaissés/match", ascending=True).head(n)
    result = result.reset_index(drop=True)
    result.index += 1

    return result[["Équipe", "Pts encaissés/match", "Blocks/match", "Interceptions/match"]]
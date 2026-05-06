import pandas as pd

from src.Parsers.BasketballLoader import BasketballLoader
from src.Analysis.générique import (
    afficher_classement,
    formater_roster,
    fiche_joueur,
    lister_joueurs,
)

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
# 1. Top équipes offensives (points marqués en moyenne)
# ---------------------------------------------------------------------------

def top_equipes_offensives(n: int = 10) -> pd.DataFrame:
    """Top N équipes par moyenne de points marqués par match."""
    _load()
    m = _matches.copy()

    home = m[["team_id_home", "pts_home"]].rename(
        columns={"team_id_home": "team_id", "pts_home": "pts"}
    )
    away = m[["team_id_away", "pts_away"]].rename(
        columns={"team_id_away": "team_id", "pts_away": "pts"}
    )
    all_pts = pd.concat([home, away])

    moy = (
        all_pts.groupby("team_id")["pts"]
        .mean()
        .round(1)
        .sort_values(ascending=False)
        .head(n)
    )
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
        "pts", "fgm", "fga", "fg3m", "fg3a", "ftm", "fta",
        "reb", "ast", "stl", "blk", "tov",
    ]
    existing = [c for c in stat_cols if c in combined.columns]
    moyennes = combined[existing].mean().round(2)

    labels = {
        "pts": "Points", "fgm": "Tirs réussis", "fga": "Tirs tentés",
        "fg3m": "3pts réussis", "fg3a": "3pts tentés",
        "ftm": "LF réussies", "fta": "LF tentées",
        "reb": "Rebonds", "ast": "Passes", "stl": "Interceptions",
        "blk": "Contres", "tov": "Pertes de balle",
    }
    row = {"Équipe": team_label}
    row.update({labels.get(k, k): v for k, v in moyennes.items()})
    return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# 4. Roster d'une équipe
# ---------------------------------------------------------------------------

def roster_equipe(team_name: str) -> pd.DataFrame:
    """Roster d'une équipe NBA : nom complet, nationalité, date de naissance."""
    _load()
    df = _loader.get_team_roster(_players, _teams, team_name)
    return formater_roster(
        df_joueurs=df,
        col_nom="full_name",
        col_nationalite="country",
        col_naissance="birthdate",
        est_esport=False,
    )


# ---------------------------------------------------------------------------
# 5. Classement défensif
# ---------------------------------------------------------------------------

def classement_defensif(n: int = 10) -> pd.DataFrame:
    """Top N équipes les plus défensives (points encaissés, blocks, interceptions)."""
    _load()
    m = _matches.copy()

    pts_h = m[["team_id_home", "pts_away"]].rename(
        columns={"team_id_home": "team_id", "pts_away": "pts_encaisses"}
    )
    pts_a = m[["team_id_away", "pts_home"]].rename(
        columns={"team_id_away": "team_id", "pts_home": "pts_encaisses"}
    )
    pts_encaisses = (
        pd.concat([pts_h, pts_a]).groupby("team_id")["pts_encaisses"].mean().round(1)
    )

    blk_h = m[["team_id_home", "blk_home"]].rename(
        columns={"team_id_home": "team_id", "blk_home": "blk"}
    )
    blk_a = m[["team_id_away", "blk_away"]].rename(
        columns={"team_id_away": "team_id", "blk_away": "blk"}
    )
    blk = pd.concat([blk_h, blk_a]).groupby("team_id")["blk"].mean().round(1)

    stl_h = m[["team_id_home", "stl_home"]].rename(
        columns={"team_id_home": "team_id", "stl_home": "stl"}
    )
    stl_a = m[["team_id_away", "stl_away"]].rename(
        columns={"team_id_away": "team_id", "stl_away": "stl"}
    )
    stl = pd.concat([stl_h, stl_a]).groupby("team_id")["stl"].mean().round(1)

    result = pd.DataFrame({
        "Pts encaissés/match": pts_encaisses,
        "Blocks/match": blk,
        "Interceptions/match": stl,
    })

    teams_idx = _teams.set_index("id")["full_name"]
    result["Équipe"] = result.index.map(teams_idx)
    result = result.sort_values("Pts encaissés/match", ascending=True).head(n)
    result = result.reset_index(drop=True)
    result.index += 1

    return result[["Équipe", "Pts encaissés/match", "Blocks/match", "Interceptions/match"]]


# ---------------------------------------------------------------------------
# 6. Fiche individuelle d'un joueur
# ---------------------------------------------------------------------------

_LABELS_BASKETBALL = {
    "full_name": "Nom complet", "first_name": "Prénom", "last_name": "Nom",
    "birthdate": "Date de naissance", "height": "Taille", "weight": "Poids (lbs)",
    "jersey": "Numéro", "position": "Poste", "country": "Nationalité",
}


def fiche_joueur_basketball(nom: str) -> pd.DataFrame:
    """Fiche complète d'un joueur NBA (toutes les données disponibles)."""
    _load()
    return fiche_joueur(
        df_joueurs=_players,
        col_nom="full_name",
        nom_joueur=nom,
        col_labels=_LABELS_BASKETBALL,
        cols_dates=["birthdate"],
    )


def liste_joueurs(equipe: str | None = None) -> pd.DataFrame:
    """Liste tous les joueurs NBA, ou ceux d'une équipe si un team_id est précisé."""
    _load()
    if equipe is not None:
        mask = (
            _teams["full_name"].str.contains(equipe, case=False, na=False)
            | _teams["abbreviation"].str.contains(equipe, case=False, na=False)
        )
        matched = _teams[mask]
        if matched.empty:
            raise ValueError(f"Aucune équipe trouvée pour : '{equipe}'")
        team_id = int(matched.iloc[0]["id"])
        df = _players[_players["team_id"] == team_id].copy()
    else:
        df = _players.copy()
    return lister_joueurs(df, col_nom="full_name", col_labels=_LABELS_BASKETBALL)


# ---------------------------------------------------------------------------
# 7. Données agenda
# ---------------------------------------------------------------------------

def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs Basketball au format standard pour l'agenda."""
    _load()
    m = _matches.copy()
    teams_idx = _teams.set_index("id")["full_name"]
    return pd.DataFrame({
        "Sport": "Basketball",
        "Date": m["game_date"],
        "Équipe 1": m["team_id_home"].map(teams_idx).fillna(m["team_id_home"].astype(str)),
        "Équipe 2": m["team_id_away"].map(teams_idx).fillna(m["team_id_away"].astype(str)),
        "Score 1": m["pts_home"].astype(int).astype(str),
        "Score 2": m["pts_away"].astype(int).astype(str),
    })


# ---------------------------------------------------------------------------
# 8. Classement par points
# ---------------------------------------------------------------------------

def classement_points(saison: str | None = None, top_qualifies: int | None = None) -> None:
    """
    Affiche le classement NBA par points (victoires/défaites/nuls).

    Paramètres
    ----------
    saison        : Saison à afficher (ex: '2022-2023'). Si None, toutes les
                    saisons Regular Season sont agrégées.
    top_qualifies : Nombre d'équipes affichées avant le séparateur (optionnel).
    """
    _load()
    teams_idx = _teams.set_index("id")["full_name"]
    m = _matches[_matches["season_type"] == "Regular Season"].copy()
    if saison:
        m = m[m["season"] == saison]
    m["equipe_home"] = m["team_id_home"].map(teams_idx).fillna(m["team_id_home"].astype(str))
    m["equipe_away"] = m["team_id_away"].map(teams_idx).fillna(m["team_id_away"].astype(str))
    afficher_classement(
        df=m,
        col_equipe1="equipe_home",
        col_equipe2="equipe_away",
        col_score1="pts_home",
        col_score2="pts_away",
        col_groupe=None,
        top_qualifies=top_qualifies,
    )

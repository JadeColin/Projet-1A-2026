import pandas as pd

from Projet_Mathias.loaders.LolLoader import LolLoader
from Projet_Mathias.app.sports.générique import (
    formater_roster, fiche_joueur, lister_joueurs,
)

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
    classement = (
        pd.DataFrame({"Victoires": victoires, "Matchs joués": total})
        .fillna(0)
        .astype(int)
    )
    classement["Défaites"] = classement["Matchs joués"] - classement["Victoires"]
    classement["% Victoires"] = (
        classement["Victoires"] / classement["Matchs joués"] * 100
    ).round(1)
    classement = classement.sort_values("Victoires", ascending=False).reset_index()
    classement = classement.rename(columns={"index": "Équipe"})
    classement.index += 1
    return classement[["Équipe", "Victoires", "Défaites", "Matchs joués", "% Victoires"]]


# ---------------------------------------------------------------------------
# 2. Stats d'une équipe
# ---------------------------------------------------------------------------

def stats_equipe(team_name: str) -> pd.DataFrame:
    """Statistiques moyennes par match pour une équipe LoL, incluant la durée moyenne."""
    _load()

    matches_team = pd.concat([
        _matches[_matches["team_blue"].str.contains(team_name, case=False, na=False)],
        _matches[_matches["team_red"].str.contains(team_name, case=False, na=False)],
    ]).drop_duplicates()

    if matches_team.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    first = matches_team.iloc[0]
    if team_name.lower() in first["team_blue"].lower():
        team_label = first["team_blue"]
    else:
        team_label = first["team_red"]

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

    if "duration_s" in combined.columns:
        moyennes["duration_s"] = round(combined["duration_s"].mean() / 60, 1)

    labels = {
        "kills": "Kills", "assists": "Assists", "deaths": "Morts",
        "gold": "Or total", "turrets": "Tourelles", "dragons": "Dragons",
        "barons": "Barons", "duration_s": "Durée moy. (min)",
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
# 4. Roster d'une équipe (joueurs + coachs)
# ---------------------------------------------------------------------------

def roster_equipe(team_name: str) -> pd.DataFrame:
    """Roster d'une équipe LoL : joueurs et coachs avec nom, pseudo, nationalité, naissance."""
    _load()

    joueurs = _players[_players["team"].str.contains(team_name, case=False, na=False)]
    coachs = _coaches[_coaches["team"].str.contains(team_name, case=False, na=False)]

    if joueurs.empty and coachs.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    return formater_roster(
        df_joueurs=joueurs,
        col_nom="name",
        col_pseudo="pseudo",
        col_nationalite="country_of_birth",
        col_naissance="birthdate",
        df_coachs=coachs,
        est_esport=True,
    )


# ---------------------------------------------------------------------------
# 5. Fiche individuelle d'un joueur
# ---------------------------------------------------------------------------

_LABELS_LOL = {
    "pseudo": "Pseudo", "name": "Nom complet",
    "country_of_birth": "Pays de naissance", "birthdate": "Date de naissance",
    "role": "Rôle", "team": "Équipe",
}


def fiche_joueur_lol(nom: str) -> pd.DataFrame:
    """Fiche complète d'un joueur LoL (toutes les données disponibles)."""
    _load()
    return fiche_joueur(
        df_joueurs=_players,
        col_nom="name",
        nom_joueur=nom,
        col_labels=_LABELS_LOL,
        cols_dates=["birthdate"],
    )


def liste_joueurs(equipe: str | None = None) -> pd.DataFrame:
    """Liste tous les joueurs LoL, ou uniquement ceux d'une équipe si précisée."""
    _load()
    df = _players if equipe is None else _players[
        _players["team"].str.contains(equipe, case=False, na=False)
    ]
    return lister_joueurs(df, col_nom="name", col_equipe="team", col_labels=_LABELS_LOL)


# ---------------------------------------------------------------------------
# 6. Données agenda
# ---------------------------------------------------------------------------

def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs LoL au format standard pour l'agenda.

    Le score est 1 pour le gagnant, 0 pour le perdant (une partie = un match).
    """
    _load()
    m = _matches.copy()
    score1 = (m["winner"] == m["team_blue"]).astype(int).astype(str)
    score2 = (m["winner"] == m["team_red"]).astype(int).astype(str)
    return pd.DataFrame({
        "Sport": "LoL",
        "Date": m["date"],
        "Équipe 1": m["team_blue"],
        "Équipe 2": m["team_red"],
        "Score 1": score1,
        "Score 2": score2,
    })

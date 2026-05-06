import pandas as pd

from src.Parsers.Cs2Loader import Cs2Loader
from src.Analysis.générique import (
    afficher_bracket,
    afficher_classement,
    formater_roster,
    fiche_joueur,
    lister_joueurs,
)

_loader = None
_players: pd.DataFrame = None
_coaches: pd.DataFrame = None
_teams: pd.DataFrame = None
_matches: pd.DataFrame = None


def _load():
    global _loader, _players, _coaches, _teams, _matches
    if _loader is None:
        _loader = Cs2Loader()
        _players, _coaches, _teams, _matches = _loader.load_all()


# ---------------------------------------------------------------------------
# 1. Classement de la phase de groupes (victoires)
# ---------------------------------------------------------------------------

def classement() -> pd.DataFrame:
    """Classement des équipes CS2 par victoires sur l'ensemble de la compétition."""
    _load()
    m = _matches.copy()

    total = (
        pd.concat([m["team_1"], m["team_2"]])
        .value_counts()
        .rename("Matchs joués")
    )
    victoires = m.apply(
        lambda r: r["team_1"] if r["score_team_1"] > r["score_team_2"] else r["team_2"],
        axis=1,
    ).value_counts().rename("Victoires")

    classement_df = (
        pd.DataFrame({"Victoires": victoires, "Matchs joués": total}).fillna(0).astype(int)
    )
    classement_df["Défaites"] = classement_df["Matchs joués"] - classement_df["Victoires"]
    classement_df["% Victoires"] = (
        classement_df["Victoires"] / classement_df["Matchs joués"] * 100
    ).round(1)
    classement_df = classement_df.sort_values("Victoires", ascending=False).reset_index()
    classement_df = classement_df.rename(columns={"index": "Équipe"})
    classement_df.index += 1
    return classement_df[["Équipe", "Victoires", "Défaites", "Matchs joués", "% Victoires"]]


# ---------------------------------------------------------------------------
# 2. Stats d'une équipe
# ---------------------------------------------------------------------------

def stats_equipe(team_name: str) -> pd.DataFrame:
    """Statistiques d'une équipe CS2 : maps jouées, gagnées, perdues, % victoires."""
    _load()

    mask = (
        _matches["team_1"].str.contains(team_name, case=False, na=False)
        | _matches["team_2"].str.contains(team_name, case=False, na=False)
    )
    matches_team = _matches[mask]

    if matches_team.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    team_label = (
        matches_team.iloc[0]["team_1"]
        if team_name.lower() in matches_team.iloc[0]["team_1"].lower()
        else matches_team.iloc[0]["team_2"]
    )

    victoires = matches_team.apply(
        lambda r: r["team_1"] if r["score_team_1"] > r["score_team_2"] else r["team_2"],
        axis=1,
    ).eq(team_label).sum()

    maps_gagnes = (
        matches_team.loc[matches_team["team_1"] == team_label, "score_team_1"].sum()
        + matches_team.loc[matches_team["team_2"] == team_label, "score_team_2"].sum()
    )
    maps_perdus = (
        matches_team.loc[matches_team["team_1"] == team_label, "score_team_2"].sum()
        + matches_team.loc[matches_team["team_2"] == team_label, "score_team_1"].sum()
    )

    return pd.DataFrame([{
        "Équipe": team_label,
        "Matchs joués": len(matches_team),
        "Victoires": int(victoires),
        "Défaites": len(matches_team) - int(victoires),
        "Maps gagnées": int(maps_gagnes),
        "Maps perdues": int(maps_perdus),
        "% Victoires": round(victoires / len(matches_team) * 100, 1),
    }])


# ---------------------------------------------------------------------------
# 3. Roster d'une équipe (joueurs + coachs)
# ---------------------------------------------------------------------------

def roster_equipe(team_name: str) -> pd.DataFrame:
    """Roster d'une équipe CS2 : joueurs et coachs avec pseudo, nom, nationalité, naissance."""
    _load()

    joueurs = _players[_players["team"].str.contains(team_name, case=False, na=False)]
    coachs = _coaches[_coaches["team"].str.contains(team_name, case=False, na=False)]

    if joueurs.empty and coachs.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    return formater_roster(
        df_joueurs=joueurs,
        col_nom="name",
        col_pseudo="pseudo",
        col_nationalite="nationality",
        col_naissance="birthdate",
        df_coachs=coachs,
        est_esport=True,
    )


_LABELS_CS2 = {
    "pseudo": "Pseudo", "name": "Nom complet", "nationality": "Nationalité",
    "birthdate": "Date de naissance", "role": "Rôle", "team": "Équipe",
}

# ---------------------------------------------------------------------------
# 4. Fiche individuelle d'un joueur
# ---------------------------------------------------------------------------


def fiche_joueur_cs2(nom: str) -> pd.DataFrame:
    """Fiche complète d'un joueur CS2 (toutes les données disponibles)."""
    _load()
    return fiche_joueur(
        df_joueurs=_players,
        col_nom="name",
        nom_joueur=nom,
        col_labels=_LABELS_CS2,
        cols_dates=["birthdate"],
    )


def liste_joueurs(equipe: str | None = None) -> pd.DataFrame:
    """Liste tous les joueurs CS2, ou uniquement ceux d'une équipe si précisée."""
    _load()
    df = _players if equipe is None else _players[
        _players["team"].str.contains(equipe, case=False, na=False)
    ]
    return lister_joueurs(df, col_nom="name", col_equipe="team", col_labels=_LABELS_CS2)


# ---------------------------------------------------------------------------
# 5. Bracket des PlayOffs
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 5. Données agenda
# ---------------------------------------------------------------------------

def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs CS2 au format standard pour l'agenda."""
    _load()
    m = _matches.copy()
    return pd.DataFrame({
        "Sport": "CS2",
        "Date": m["date"],
        "Équipe 1": m["team_1"],
        "Équipe 2": m["team_2"],
        "Score 1": m["score_team_1"].astype(int).astype(str),
        "Score 2": m["score_team_2"].astype(int).astype(str),
    })


_ORDRE_ROUNDS_PLAYOFFS = ["RO8", "RO4", "RO2"]


def bracket() -> None:
    """
    Affiche le bracket des PlayOffs CS2.

    Seuls les matchs de stage 'PlayOffs' sont pris en compte (RO8, RO4, RO2).
    Chaque ligne du CSV correspond à une série complète (score = maps gagnées).
    Le chemin du gagnant est affiché en vert dans le terminal.
    """
    _load()
    df_playoffs = _matches[_matches["stage"] == "PlayOffs"].copy()
    afficher_bracket(
        df=df_playoffs,
        col_equipe1="team_1",
        col_equipe2="team_2",
        col_score1="score_team_1",
        col_score2="score_team_2",
        col_round="round",
        ordre_rounds=_ORDRE_ROUNDS_PLAYOFFS,
        deux_manches=False,
    )


# ---------------------------------------------------------------------------
# 7. Classement par points (phases de groupes)
# ---------------------------------------------------------------------------


def classement_stages(top_qualifies: int | None = None) -> None:
    """
    Affiche le classement CS2 par phase de groupes (stages 1, 2, 3).

    Chaque stage est affiché comme un groupe distinct.
    Les PlayOffs sont exclus.

    Paramètres
    ----------
    top_qualifies : Nombre d'équipes affichées avant le séparateur (optionnel).
    """
    _load()
    m = _matches[_matches["stage"] != "PlayOffs"].copy()
    m["stage_label"] = "Phase " + m["stage"].astype(str)
    afficher_classement(
        df=m,
        col_equipe1="team_1",
        col_equipe2="team_2",
        col_score1="score_team_1",
        col_score2="score_team_2",
        col_groupe="stage_label",
        top_qualifies=top_qualifies,
    )

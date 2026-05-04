import pandas as pd

from Projet_Mathias.loaders.Cs2Loader import Cs2Loader
from Projet_Mathias.app.sports.générique import afficher_bracket, formater_roster

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

    rows = [
        ("Matchs joués", len(matches_team)),
        ("Victoires", int(victoires)),
        ("Défaites", len(matches_team) - int(victoires)),
        ("Maps gagnées", int(maps_gagnes)),
        ("Maps perdues", int(maps_perdus)),
        ("% Victoires", round(victoires / len(matches_team) * 100, 1)),
    ]
    return pd.DataFrame(rows, columns=["Statistique", team_label])


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


# ---------------------------------------------------------------------------
# 4. Bracket des PlayOffs
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 5. Données agenda
# ---------------------------------------------------------------------------

def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs CS2 au format standard pour l'agenda."""
    _load()
    m = _matches.copy()
    winner = m.apply(
        lambda r: r["team_1"] if r["score_team_1"] > r["score_team_2"] else r["team_2"],
        axis=1,
    )
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

import pandas as pd

from Projet_Mathias.loaders.VolleyballLoader import VolleyballLoader
from Projet_Mathias.app.sports.générique import formater_roster

_loader = None
_countries: pd.DataFrame = None
_players_men: pd.DataFrame = None
_players_women: pd.DataFrame = None
_coaches_men: pd.DataFrame = None
_coaches_women: pd.DataFrame = None
_matches_men: pd.DataFrame = None
_matches_women: pd.DataFrame = None


def _load():
    global _loader, _countries, _players_men, _players_women
    global _coaches_men, _coaches_women, _matches_men, _matches_women
    if _loader is None:
        _loader = VolleyballLoader()
        (
            _countries, _players_men, _players_women,
            _coaches_men, _coaches_women, _matches_men, _matches_women,
        ) = _loader.load_all()


def _matches(genre: str) -> pd.DataFrame:
    return _matches_men if genre.lower() in ("hommes", "m", "men") else _matches_women


def _players(genre: str) -> pd.DataFrame:
    return _players_men if genre.lower() in ("hommes", "m", "men") else _players_women


def _country_name(code: str) -> str:
    _load()
    row = _countries[_countries["code"] == code]
    return row.iloc[0]["country"] if not row.empty else code


# ---------------------------------------------------------------------------
# 1. Classement
# ---------------------------------------------------------------------------

def classement(genre: str = "hommes") -> pd.DataFrame:
    """Classement des équipes JO Paris 2024 par victoires."""
    _load()
    m = _matches(genre)

    total = (
        pd.concat([m["country_code_1"], m["country_code_2"]])
        .value_counts()
        .rename("Matchs joués")
    )
    victoires = m["winner"].value_counts().rename("Victoires")

    classement_df = pd.DataFrame({"Victoires": victoires, "Matchs joués": total}).fillna(
        0).astype(int)
    classement_df["Défaites"] = classement_df["Matchs joués"] - classement_df["Victoires"]

    # Enrichir avec le nom complet du pays
    country_map = _countries.set_index("code")["country"]
    classement_df["Pays"] = classement_df.index.map(country_map).fillna(classement_df.index)

    sets_gagnes = (
        pd.concat([
            m[["country_code_1", "set_country_1"]].rename(columns={
                "country_code_1": "code", "set_country_1": "sets"}),
            m[["country_code_2", "set_country_2"]].rename(columns={
                "country_code_2": "code", "set_country_2": "sets"}),
        ])
        .groupby("code")["sets"]
        .sum()
        .rename("Sets gagnés")
    )
    classement_df = classement_df.join(sets_gagnes)
    classement_df = classement_df.sort_values([
        "Victoires", "Sets gagnés"], ascending=False).reset_index(drop=True)
    classement_df.index += 1
    return classement_df[["Pays", "Victoires", "Défaites", "Matchs joués", "Sets gagnés"]]


# ---------------------------------------------------------------------------
# 2. Bilan d'une équipe
# ---------------------------------------------------------------------------

def bilan_equipe(team_code: str, genre: str = "hommes") -> pd.DataFrame:
    """Bilan détaillé d'une équipe (code IOC, ex: 'FRA')."""
    _load()
    m = _matches(genre)
    code = team_code.upper()

    mask = (m["country_code_1"] == code) | (m["country_code_2"] == code)
    team_matches = m[mask]

    if team_matches.empty:
        raise ValueError(f"Aucune équipe trouvée pour le code : '{code}'")

    team_name = _country_name(code)
    victoires = (team_matches["winner"] == code).sum()
    defaites = len(team_matches) - victoires

    sets_gagnes = (
        team_matches.loc[team_matches["country_code_1"] == code, "set_country_1"].sum()
        + team_matches.loc[team_matches["country_code_2"] == code, "set_country_2"].sum()
    )
    sets_perdus = (
        team_matches.loc[team_matches["country_code_1"] == code, "set_country_2"].sum()
        + team_matches.loc[team_matches["country_code_2"] == code, "set_country_1"].sum()
    )

    rows = [
        ("Matchs joués", len(team_matches)),
        ("Victoires", victoires),
        ("Défaites", defaites),
        ("Sets gagnés", int(sets_gagnes)),
        ("Sets perdus", int(sets_perdus)),
    ]
    return pd.DataFrame(rows, columns=["Statistique", team_name])


# ---------------------------------------------------------------------------
# 3. Roster d'équipe (Joueurs et Coachs)
# ---------------------------------------------------------------------------

def roster_equipe(team_code: str, genre: str = "hommes") -> pd.DataFrame:
    """Roster d'une équipe de volleyball : joueurs et coachs avec nom, nationalité, date de naissance."""
    _load()
    code = team_code.upper()

    if genre.lower() in ("hommes", "m", "men"):
        df_players = _players_men
        df_coaches = _coaches_men
    else:
        df_players = _players_women
        df_coaches = _coaches_women

    joueurs = df_players[df_players["country_code"] == code]
    if joueurs.empty:
        raise ValueError(f"Aucun membre trouvé pour le code : '{code}'")

    coachs = df_coaches[df_coaches["country_code"] == code]

    return formater_roster(
        df_joueurs=joueurs,
        col_nom="name",
        col_nationalite="country_code",
        col_naissance="birth_date",
        df_coachs=coachs,
        est_esport=False,
    )

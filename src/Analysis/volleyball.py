import pandas as pd

from src.Parsers.VolleyballLoader import VolleyballLoader
from src.Analysis.générique import (
    afficher_classement,
    formater_roster,
    fiche_joueur,
    lister_joueurs,
)

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
    classement_df["Pays"] = classement_df.index.map(lambda code: country_map.get(code, code))

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

    return pd.DataFrame([{
        "Équipe": team_name,
        "Matchs joués": len(team_matches),
        "Victoires": victoires,
        "Défaites": defaites,
        "Sets gagnés": int(sets_gagnes),
        "Sets perdus": int(sets_perdus),
    }])



def roster_equipe(team_code: str, genre: str = "hommes") -> pd.DataFrame:
    """Roster d'une équipe de volleyball : joueurs et coachs avec nom, nationalité, naissance."""
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


_LABELS_VB = {
    "name": "Nom complet", "country_code": "Code pays",
    "height": "Taille (cm)", "birth_date": "Date de naissance",
    "birth_place": "Lieu de naissance", "nickname": "Surnom",
}



def fiche_joueur_volleyball(nom: str, genre: str = "hommes") -> pd.DataFrame:
    """Fiche complète d'un joueur de volleyball (toutes les données disponibles)."""
    _load()
    df = _players_men if genre.lower() in ("hommes", "m", "men") else _players_women
    return fiche_joueur(
        df_joueurs=df,
        col_nom="name",
        nom_joueur=nom,
        col_labels=_LABELS_VB,
        cols_dates=["birth_date"],
    )


def liste_joueurs(genre: str = "hommes", equipe: str | None = None) -> pd.DataFrame:
    """Liste tous les joueurs de volleyball d'un genre, filtrables par code pays."""
    _load()
    df = _players_men if genre.lower() in ("hommes", "m", "men") else _players_women
    if equipe is not None:
        df = df[df["country_code"].str.contains(equipe, case=False, na=False)]
    return lister_joueurs(df, col_nom="name", col_equipe="country_code", col_labels=_LABELS_VB)



def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs Volleyball (hommes + femmes) au format standard pour l'agenda."""
    _load()
    country_map = _countries.set_index("code")["country"]

    def _standardiser(m: pd.DataFrame, label: str) -> pd.DataFrame:
        return pd.DataFrame({
            "Sport": f"Volleyball {label}",
            "Date": m["date"],
            "Équipe 1": m["country_code_1"].map(country_map).fillna(m["country_code_1"]),
            "Équipe 2": m["country_code_2"].map(country_map).fillna(m["country_code_2"]),
            "Score 1": m["set_country_1"].astype(int).astype(str),
            "Score 2": m["set_country_2"].astype(int).astype(str),
        })

    return pd.concat([
        _standardiser(_matches_men, "Hommes"),
        _standardiser(_matches_women, "Femmes"),
    ], ignore_index=True)



def classement_groupes(genre: str = "hommes", top_qualifies: int = 2) -> None:
    """
    Affiche le classement de la phase de groupes (poules) par genre.

    Un tableau par poule est affiché, trié par points décroissants.

    Paramètres
    ----------
    genre         : 'hommes' ou 'femmes' (défaut : 'hommes').
    top_qualifies : Nombre d'équipes qualifiées par poule (défaut : 2).
    """
    _load()
    m = _matches(genre).copy()
    poules = m[m["stage"].str.startswith("Preliminary Round", na=False)].copy()
    poules["poule"] = poules["stage"].str.extract(r"Pool ([A-Z])")

    afficher_classement(
        df=poules,
        col_equipe1="country_code_1",
        col_equipe2="country_code_2",
        col_score1="set_country_1",
        col_score2="set_country_2",
        col_groupe="poule",
        top_qualifies=top_qualifies,
    )

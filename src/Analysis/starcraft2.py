import pandas as pd

from src.Parsers.Starcraft2Loader import Starcraft2Loader
from src.Analysis.générique import fiche_joueur

_loader = None
_players: pd.DataFrame = None
_matches: pd.DataFrame = None


def _load():
    global _loader, _players, _matches
    if _loader is None:
        _loader = Starcraft2Loader()
        _players, _matches = _loader.load_all()


_LABELS_SC2 = {
    "pseudo": "Pseudo", "name": "Nom complet", "nationality": "Nationalité",
    "birthdate": "Date de naissance", "race": "Race", "team": "Équipe",
}


# ---------------------------------------------------------------------------
# 1. Fiche individuelle d'un joueur
# ---------------------------------------------------------------------------

def fiche_joueur_sc2(nom: str) -> pd.DataFrame:
    """Fiche complète d'un joueur StarCraft II (toutes les données disponibles)."""
    _load()
    return fiche_joueur(
        df_joueurs=_players,
        col_nom="name",
        nom_joueur=nom,
        col_labels=_LABELS_SC2,
        cols_dates=["birthdate"],
    )


# ---------------------------------------------------------------------------
# 2. Bilan victoires/défaites d'un joueur
# ---------------------------------------------------------------------------

def bilan_joueur_sc2(nom: str) -> pd.DataFrame:
    """Bilan victoires/défaites d'un joueur StarCraft II sur la saison."""
    _load()

    mask = _players["name"].str.contains(nom, case=False, na=False)
    matched = _players[mask]
    if matched.empty:
        raise ValueError(f"Aucun joueur trouvé pour : '{nom}'")

    name = matched.iloc[0]["name"]

    as_p1 = _matches[_matches["player_1"] == name]
    as_p2 = _matches[_matches["player_2"] == name]

    victoires = int(
        (as_p1["score_player_1"] > as_p1["score_player_2"]).sum()
        + (as_p2["score_player_2"] > as_p2["score_player_1"]).sum()
    )
    defaites = int(
        (as_p1["score_player_1"] < as_p1["score_player_2"]).sum()
        + (as_p2["score_player_2"] < as_p2["score_player_1"]).sum()
    )
    joues = victoires + defaites

    rows = [
        ("Matchs joués", joues),
        ("Victoires", victoires),
        ("Défaites", defaites),
        ("% Victoires", round(victoires / max(joues, 1) * 100, 1)),
    ]
    return pd.DataFrame(rows, columns=["Statistique", name])


# ---------------------------------------------------------------------------
# 3. Données agenda
# ---------------------------------------------------------------------------

def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs StarCraft II au format standard pour l'agenda."""
    _load()
    m = _matches.copy()
    return pd.DataFrame({
        "Sport": "StarCraft II",
        "Date": m["date"],
        "Équipe 1": m["player_1"],
        "Équipe 2": m["player_2"],
        "Score 1": m["score_player_1"].astype(int).astype(str),
        "Score 2": m["score_player_2"].astype(int).astype(str),
    })

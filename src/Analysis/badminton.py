import pandas as pd

from src.Parsers.BadmintonLoader import BadmintonLoader
from src.Analysis.générique import fiche_joueur, lister_joueurs

_loader = None
_players: pd.DataFrame = None
_matches: pd.DataFrame = None


def _load():
    global _loader, _players, _matches
    if _loader is None:
        _loader = BadmintonLoader()
        _players, _matches = _loader.load_all()


def _compter_jeux(row: pd.Series) -> tuple[int, int]:
    """Compte les jeux gagnés par chaque joueur depuis les colonnes game_X_score."""
    wins1, wins2 = 0, 0
    for col in ["game_1_score", "game_2_score", "game_3_score"]:
        val = row.get(col)
        if pd.isna(val) or str(val).strip() == "":
            continue
        parts = str(val).strip().split("-")
        if len(parts) == 2:
            try:
                s1, s2 = int(parts[0]), int(parts[1])
                if s1 > s2:
                    wins1 += 1
                else:
                    wins2 += 1
            except ValueError:
                pass
    return wins1, wins2


_LABELS_BADMINTON = {
    "name": "Nom complet", "country": "Pays", "continent": "Continent",
}


# ---------------------------------------------------------------------------
# 1. Fiche individuelle d'un joueur
# ---------------------------------------------------------------------------

def fiche_joueur_badminton(nom: str) -> pd.DataFrame:
    """Fiche complète d'un joueur de badminton (toutes les données disponibles)."""
    _load()
    return fiche_joueur(
        df_joueurs=_players,
        col_nom="name",
        nom_joueur=nom,
        col_labels=_LABELS_BADMINTON,
    )


def liste_joueurs() -> pd.DataFrame:
    """Liste tous les joueurs de badminton."""
    _load()
    return lister_joueurs(_players, col_nom="name", col_labels=_LABELS_BADMINTON)


# ---------------------------------------------------------------------------
# 2. Données agenda
# ---------------------------------------------------------------------------

def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs Badminton au format standard pour l'agenda.

    Score 1 / Score 2 = nombre de jeux gagnés par chaque joueur.
    """
    _load()
    m = _matches.copy()
    scores = m.apply(_compter_jeux, axis=1)
    return pd.DataFrame({
        "Sport": "Badminton",
        "Date": m["date"],
        "Équipe 1": m["player_1"],
        "Équipe 2": m["player_2"],
        "Score 1": [str(s[0]) for s in scores],
        "Score 2": [str(s[1]) for s in scores],
    })

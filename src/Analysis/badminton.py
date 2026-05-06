import pandas as pd

from src.Parsers.BadmintonLoader import BadmintonLoader
from src.Analysis.générique import afficher_bracket, fiche_joueur

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


# ---------------------------------------------------------------------------
# 2. Bilan victoires/défaites d'un joueur
# ---------------------------------------------------------------------------

def bilan_joueur_badminton(nom: str) -> pd.DataFrame:
    """Bilan victoires/défaites d'un joueur de badminton sur la saison."""
    _load()

    mask = _players["name"].str.contains(nom, case=False, na=False)
    matched = _players[mask]
    if matched.empty:
        raise ValueError(f"Aucun joueur trouvé pour : '{nom}'")

    name = matched.iloc[0]["name"]

    as_p1 = _matches[_matches["player_1"] == name]
    as_p2 = _matches[_matches["player_2"] == name]

    scores_p1 = as_p1.apply(_compter_jeux, axis=1)
    wins_as_p1 = sum(1 for s in scores_p1 if s[0] > s[1])
    losses_as_p1 = sum(1 for s in scores_p1 if s[0] < s[1])

    scores_p2 = as_p2.apply(_compter_jeux, axis=1)
    wins_as_p2 = sum(1 for s in scores_p2 if s[1] > s[0])
    losses_as_p2 = sum(1 for s in scores_p2 if s[1] < s[0])

    victoires = wins_as_p1 + wins_as_p2
    defaites = losses_as_p1 + losses_as_p2
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

_BRACKET_ROUNDS = ["Round of 32", "Round of 16", "Quarter final", "Semi final", "Final"]


def bracket(tournament_name: str) -> None:
    """Affiche le bracket d'un tournoi de badminton.

    Le score de chaque joueur correspond au nombre de jeux gagnés sur le match.
    """
    _load()

    m = _matches[
        _matches["tournament"].str.contains(tournament_name, case=False, na=False)
    ].copy()

    if m.empty:
        raise ValueError(f"Tournoi introuvable : '{tournament_name}'")

    m = m[m["round"].isin(_BRACKET_ROUNDS)].copy()

    if m.empty:
        raise ValueError(f"Pas de phase bracket pour '{tournament_name}'")

    scores = m.apply(_compter_jeux, axis=1, result_type="expand")
    m["score_1"] = scores[0]
    m["score_2"] = scores[1]

    ordre_present = [r for r in _BRACKET_ROUNDS if r in m["round"].values]

    afficher_bracket(
        df=m,
        col_equipe1="player_1",
        col_equipe2="player_2",
        col_score1="score_1",
        col_score2="score_2",
        col_round="round",
        ordre_rounds=ordre_present,
    )


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

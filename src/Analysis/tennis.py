import re
import pandas as pd

from src.Parsers.TennisLoader import TennisLoader
from src.Analysis.générique import afficher_bracket, fiche_joueur, lister_joueurs

_loader = None
_atp_players: pd.DataFrame = None
_wta_players: pd.DataFrame = None
_atp_matches: pd.DataFrame = None
_wta_matches: pd.DataFrame = None


def _load():
    global _loader, _atp_players, _wta_players, _atp_matches, _wta_matches
    if _loader is None:
        _loader = TennisLoader()
        _atp_players, _wta_players, _atp_matches, _wta_matches = _loader.load_all()


def _matches(circuit: str) -> pd.DataFrame:
    return _atp_matches if circuit.upper() == "ATP" else _wta_matches


def _players(circuit: str) -> pd.DataFrame:
    return _atp_players if circuit.upper() == "ATP" else _wta_players


# ---------------------------------------------------------------------------
# 1. Classement par victoires ATP / WTA
# ---------------------------------------------------------------------------

def classement_victoires(circuit: str = "ATP", n: int = 20) -> pd.DataFrame:
    """Top N joueurs par victoires sur la saison 2024."""
    _load()
    m = _matches(circuit)
    p = _players(circuit)

    victoires = m["winner_id"].value_counts().rename("Victoires")
    defaites = m["loser_id"].value_counts().rename("Défaites")

    result = pd.DataFrame({"Victoires": victoires, "Défaites": defaites}).fillna(0).astype(int)
    result["Matchs joués"] = result["Victoires"] + result["Défaites"]
    result["% Victoires"] = (result["Victoires"] / result["Matchs joués"] * 100).round(1)

    players_idx = p.set_index("player_id")["full_name"]
    result = result.join(players_idx).reset_index(drop=True)
    result = result.rename(columns={"full_name": "Joueur"})
    result = result.sort_values("Victoires", ascending=False).head(n).reset_index(drop=True)
    result.index += 1
    return result[["Joueur", "Victoires", "Défaites", "Matchs joués", "% Victoires"]]


# ---------------------------------------------------------------------------
# 2. Stats d'un joueur
# ---------------------------------------------------------------------------

def stats_joueur(player_name: str, circuit: str = "ATP") -> pd.DataFrame:
    """Statistiques d'un joueur sur la saison 2024."""
    _load()
    m = _matches(circuit)
    p = _players(circuit)

    mask = p["full_name"].str.contains(player_name, case=False, na=False)
    matched = p[mask]
    if matched.empty:
        raise ValueError(f"Aucun joueur trouvé pour : '{player_name}' ({circuit})")

    pid = int(matched.iloc[0]["player_id"])
    name = matched.iloc[0]["full_name"]

    wins = m[m["winner_id"] == pid]
    losses = m[m["loser_id"] == pid]

    row = {
        "Joueur": name,
        "Victoires": len(wins),
        "Défaites": len(losses),
        "Matchs joués": len(wins) + len(losses),
        "% Victoires": round(len(wins) / max(len(wins) + len(losses), 1) * 100, 1),
        "Tournois joués": (m[m["winner_id"] == pid]["tourney_name"].nunique()
                           + m[m["loser_id"] == pid]["tourney_name"].nunique()),
    }

    if "minutes" in m.columns:
        all_m = pd.concat([wins, losses])
        row["Durée moy. match (min)"] = round(all_m["minutes"].mean(), 1)

    return pd.DataFrame([row])


_LABELS_TENNIS = {
    "full_name": "Nom complet", "name_first": "Prénom", "name_last": "Nom",
    "hand": "Main dominante", "dob": "Date de naissance",
    "ioc": "Nationalité (IOC)", "height": "Taille (cm)",
}


# ---------------------------------------------------------------------------
# 5. Fiche individuelle d'un joueur
# ---------------------------------------------------------------------------

def fiche_joueur_tennis(nom: str, circuit: str = "ATP") -> pd.DataFrame:
    """Fiche complète d'un joueur de tennis (toutes les données disponibles)."""
    _load()
    p = _atp_players if circuit.upper() == "ATP" else _wta_players
    return fiche_joueur(
        df_joueurs=p,
        col_nom="full_name",
        nom_joueur=nom,
        col_labels=_LABELS_TENNIS,
        cols_dates=["dob"],
    )


def liste_joueurs(circuit: str = "ATP") -> pd.DataFrame:
    """Liste tous les joueurs du circuit ATP ou WTA."""
    _load()
    p = _atp_players if circuit.upper() == "ATP" else _wta_players
    return lister_joueurs(p, col_nom="full_name", col_labels=_LABELS_TENNIS)


# ---------------------------------------------------------------------------
# 6. Données agenda
# ---------------------------------------------------------------------------

def _compter_sets(score: str) -> tuple[int, int]:
    """Retourne (sets_gagnant, sets_perdant) depuis une chaîne de score tennis.

    Exemples : '7-6(5) 6-4'  → (2, 0)
               '6-4 3-6 7-5' → (2, 1)
    """
    if pd.isna(score):
        return 0, 0
    sets = re.sub(r'\(\d+\)', '', str(score)).strip().split()
    gagnant, perdant = 0, 0
    for s in sets:
        parts = s.split("-")
        if len(parts) == 2:
            try:
                s1, s2 = int(parts[0]), int(parts[1])
                if s1 > s2:
                    gagnant += 1
                else:
                    perdant += 1
            except ValueError:
                pass
    return gagnant, perdant


def _standardiser_tennis(
    matches: pd.DataFrame,
    players: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    players_idx = players.set_index("player_id")["full_name"]
    winner_names = matches["winner_id"].map(players_idx).fillna(
        matches["winner_id"].astype(str)
    )
    loser_names = matches["loser_id"].map(players_idx).fillna(
        matches["loser_id"].astype(str)
    )
    sets = matches["score"].apply(_compter_sets)
    return pd.DataFrame({
        "Sport": f"Tennis {label}",
        "Date": matches["tourney_date"],
        "Équipe 1": winner_names.values,
        "Équipe 2": loser_names.values,
        "Score 1": [str(s[0]) for s in sets],
        "Score 2": [str(s[1]) for s in sets],
    })


def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs Tennis ATP et WTA au format standard pour l'agenda.

    Score 1 / Score 2 = sets gagnés par le vainqueur / le perdant.
    Joueur 1 = gagnant, Joueur 2 = perdant.
    """
    _load()
    return pd.concat([
        _standardiser_tennis(_atp_matches, _atp_players, "ATP"),
        _standardiser_tennis(_wta_matches, _wta_players, "WTA"),
    ], ignore_index=True)


# ---------------------------------------------------------------------------
# Bracket
# ---------------------------------------------------------------------------

_BRACKET_ROUNDS = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]


def bracket(tourney_name: str, circuit: str = "ATP") -> None:
    """Affiche le bracket d'un tournoi de tennis (Grand Chelem ou autre).

    Les matchs sont affichés depuis le premier round disponible jusqu'à la finale.
    Le vainqueur de chaque match est le gagnant du plus grand nombre de sets.
    """
    _load()

    matches = _atp_matches if circuit.upper() == "ATP" else _wta_matches
    players = _atp_players if circuit.upper() == "ATP" else _wta_players

    m = matches[
        matches["tourney_name"].str.contains(tourney_name, case=False, na=False)
    ].copy()

    if m.empty:
        raise ValueError(f"Tournoi introuvable : '{tourney_name}' ({circuit})")

    names = players.set_index("player_id")["full_name"]
    m["player_winner"] = m["winner_id"].map(names).fillna(m["winner_id"].astype(str))
    m["player_loser"] = m["loser_id"].map(names).fillna(m["loser_id"].astype(str))

    sets_parsed = m["score"].apply(
        lambda s: pd.Series(_compter_sets(s), index=["sets_w", "sets_l"])
    )
    m = pd.concat([m, sets_parsed], axis=1)

    m = m[m["round"].isin(_BRACKET_ROUNDS)].sort_values("match_num")
    ordre_present = [r for r in _BRACKET_ROUNDS if r in m["round"].values]

    afficher_bracket(
        df=m,
        col_equipe1="player_winner",
        col_equipe2="player_loser",
        col_score1="sets_w",
        col_score2="sets_l",
        col_round="round",
        ordre_rounds=ordre_present,
    )

import pandas as pd

from src.Parsers.FootballChampionsLeagueLoader import FootballChampionsLeagueLoader
from src.Analysis.générique import (
    afficher_bracket,
    afficher_classement,
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
        _loader = FootballChampionsLeagueLoader()
        _players, _teams, _matches = _loader.load_all()


# ---------------------------------------------------------------------------
# 1. Meilleurs buteurs
# ---------------------------------------------------------------------------

def meilleurs_buteurs(n: int = 10) -> pd.DataFrame:
    """Top N joueurs par nombre de buts avec % de tirs cadrés."""
    _load()
    cols = ["player_name", "club", "position", "goals", "total_attempts", "on_target"]
    df = _players[cols].copy()

    df["% Tirs cadrés"] = (df["on_target"] / df["total_attempts"] * 100).round(1)
    df["% Tirs tentés/match"] = (
        df["total_attempts"] / _players["match_played"] * 100
    ).round(1)

    df = df.sort_values("goals", ascending=False).head(n).reset_index(drop=True)
    df.index += 1
    return df.rename(columns={
        "player_name": "Joueur", "club": "Club", "position": "Poste",
        "goals": "Buts", "total_attempts": "Tirs tentés", "on_target": "Tirs cadrés",
    })


# ---------------------------------------------------------------------------
# 2. Meilleurs passeurs
# ---------------------------------------------------------------------------

def meilleurs_passeurs(n: int = 10) -> pd.DataFrame:
    """Top N joueurs par nombre de passes décisives."""
    _load()
    df = _players[["player_name", "club", "position", "assists"]].copy()
    df = df.sort_values("assists", ascending=False).head(n).reset_index(drop=True)
    df.index += 1
    return df.rename(columns={
        "player_name": "Joueur", "club": "Club",
        "position": "Poste", "assists": "Passes déc.",
    })


# ---------------------------------------------------------------------------
# 3. Stats d'une équipe (joueurs)
# ---------------------------------------------------------------------------

def stats_equipe(team_name: str) -> pd.DataFrame:
    """Statistiques collectives d'une équipe (somme sur tous les joueurs)."""
    _load()

    mask = _players["club"].str.contains(team_name, case=False, na=False)
    squad = _players[mask]
    if squad.empty:
        raise ValueError(f"Aucune équipe trouvée pour : '{team_name}'")

    club_label = squad.iloc[0]["club"]
    stat_cols = ["goals", "assists", "minutes_played", "yellow", "red"]
    existing = [c for c in stat_cols if c in squad.columns]
    totaux = squad[existing].sum()

    labels = {
        "goals": "Buts", "assists": "Passes déc.",
        "minutes_played": "Minutes jouées",
        "yellow": "Cartons jaunes", "red": "Cartons rouges",
    }
    result = totaux.rename(labels).reset_index()
    result.columns = ["Statistique", f"{club_label} (total saison)"]
    return result


# ---------------------------------------------------------------------------
# 4. Statistiques complètes d'un joueur
# ---------------------------------------------------------------------------

def stats_joueur(player_name: str) -> pd.DataFrame:
    """Statistiques complètes d'un joueur de la Champions League."""
    _load()

    mask = _players["player_name"].str.contains(player_name, case=False, na=False)
    matched = _players[mask]
    if matched.empty:
        raise ValueError(f"Aucun joueur trouvé pour : '{player_name}'")

    joueur = matched.iloc[0]

    cols = [
        "player_name", "club", "position", "match_played",
        "goals", "assists", "dribbles", "tackles_won",
        "yellow", "red", "pass_completed", "pass_attempted",
        "minutes_played",
    ]
    labels = {
        "player_name": "Joueur", "club": "Club", "position": "Poste",
        "match_played": "Matchs joués", "goals": "Buts", "assists": "Passes déc.",
        "dribbles": "Dribbles", "tackles_won": "Tacles réussis",
        "yellow": "Cartons jaunes", "red": "Cartons rouges",
        "pass_completed": "Passes réussies", "pass_attempted": "Passes tentées",
        "minutes_played": "Minutes jouées",
    }

    existing = [c for c in cols if c in joueur.index]
    result = joueur[existing].rename(labels).reset_index()
    result.columns = ["Statistique", joueur["player_name"]]
    return result


# ---------------------------------------------------------------------------
# 6. Statistiques des gardiens
# ---------------------------------------------------------------------------

def stats_gardiens(n: int = 10) -> pd.DataFrame:
    """Statistiques des meilleurs gardiens de la Champions League."""
    _load()

    gardiens = _players[
        _players["position"].str.contains("Goalkeeper|GK|Gardien", case=False, na=False)
    ].copy()

    if gardiens.empty:
        raise ValueError("Aucun gardien trouvé dans les données.")

    cols = [
        "player_name", "club", "match_played", "saved",
        "conceded", "cleansheets", "saved_penalties",
    ]
    labels = {
        "player_name": "Gardien", "club": "Club",
        "match_played": "Matchs joués", "saved": "Arrêts",
        "conceded": "Buts encaissés", "cleansheets": "Clean sheets",
        "saved_penalties": "Pénaltys arrêtés",
    }

    existing = [c for c in cols if c in gardiens.columns]
    result = gardiens[existing].rename(columns=labels)
    result = result.sort_values("Arrêts", ascending=False).head(n).reset_index(drop=True)
    result.index += 1
    return result


_LABELS_FCL = {
    "player_name": "Joueur", "club": "Club", "position": "Poste",
    "match_played": "Matchs joués", "goals": "Buts", "assists": "Passes déc.",
    "dribbles": "Dribbles", "tackles_won": "Tacles réussis",
    "yellow": "Cartons jaunes", "red": "Cartons rouges",
    "pass_completed": "Passes réussies", "pass_attempted": "Passes tentées",
    "minutes_played": "Minutes jouées", "total_attempts": "Tirs tentés",
    "on_target": "Tirs cadrés", "saved": "Arrêts", "conceded": "Buts encaissés",
    "cleansheets": "Clean sheets", "saved_penalties": "Pénaltys arrêtés",
}

# ---------------------------------------------------------------------------
# 7. Fiche individuelle d'un joueur
# ---------------------------------------------------------------------------


def fiche_joueur_fcl(nom: str) -> pd.DataFrame:
    """Fiche complète d'un joueur de la Champions League (toutes les données disponibles)."""
    _load()
    return fiche_joueur(
        df_joueurs=_players,
        col_nom="player_name",
        nom_joueur=nom,
        col_labels=_LABELS_FCL,
    )


def liste_joueurs(club: str | None = None) -> pd.DataFrame:
    """Liste tous les joueurs de la CL, ou ceux d'un club si précisé."""
    _load()
    df = _players if club is None else _players[
        _players["club"].str.contains(club, case=False, na=False)
    ]
    return lister_joueurs(
        df, col_nom="player_name", col_equipe="club", col_labels=_LABELS_FCL
    )


# ---------------------------------------------------------------------------
# 8. Classement de la phase de groupes
# ---------------------------------------------------------------------------

def classement_groupes(top_qualifies: int = 2) -> None:
    """
    Affiche le classement de chaque groupe de la phase de poules.

    Un tableau par groupe est affiché, trié par points décroissants.
    Une ligne de séparation marque le seuil de qualification.

    Paramètres
    ----------
    top_qualifies : nombre d'équipes qualifiées par groupe (défaut : 2).
    """
    _load()
    df_groupes = _matches[_matches["phase"] == "group"].copy()
    afficher_classement(
        df=df_groupes,
        col_equipe1="team_home",
        col_equipe2="team_away",
        col_score1="score_team_home",
        col_score2="score_team_away",
        col_groupe="group",
        top_qualifies=top_qualifies,
    )


# ---------------------------------------------------------------------------
# 9. Données agenda
# ---------------------------------------------------------------------------

def get_agenda_data() -> pd.DataFrame:
    """Retourne les matchs Football CL au format standard pour l'agenda."""
    _load()
    m = _matches.copy()
    return pd.DataFrame({
        "Sport": "Football CL",
        "Date": m["date"],
        "Équipe 1": m["team_home"],
        "Équipe 2": m["team_away"],
        "Score 1": m["score_team_home"].astype(int).astype(str),
        "Score 2": m["score_team_away"].astype(int).astype(str),
    })


# ---------------------------------------------------------------------------
# 8. Bracket de la phase éliminatoire
# ---------------------------------------------------------------------------

_ORDRE_ROUNDS_KNOCKOUT = ["RO16", "RO8", "RO4", "RO2"]


def bracket() -> None:
    """
    Affiche le bracket de la phase éliminatoire de la Champions League.

    Seuls les matchs de phase 'knockout' sont pris en compte (RO16, RO8, RO4, RO2).
    Les confrontations aller/retour sont agrégées automatiquement.
    Le chemin du gagnant est affiché en vert dans le terminal.
    """
    _load()
    df_knockout = _matches[_matches["phase"] == "knockout"].copy()
    afficher_bracket(
        df=df_knockout,
        col_equipe1="team_home",
        col_equipe2="team_away",
        col_score1="score_team_home",
        col_score2="score_team_away",
        col_round="round",
        ordre_rounds=_ORDRE_ROUNDS_KNOCKOUT,
        deux_manches=True,
    )

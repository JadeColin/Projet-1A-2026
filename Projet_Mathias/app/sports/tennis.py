import pandas as pd

from Projet_Mathias.loaders.TennisLoader import TennisLoader

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

    victoires = m["winner_id"].value_counts().rename("Victoires").head(n)
    defaites = m["loser_id"].value_counts().rename("Défaites")

    result = pd.DataFrame({"Victoires": victoires, "Défaites": defaites}).fillna(0).astype(int)
    result["Matchs joués"] = result["Victoires"] + result["Défaites"]
    result["% Victoires"] = (result["Victoires"] / result["Matchs joués"] * 100).round(1)

    players_idx = p.set_index("player_id")["full_name"]
    result = result.join(players_idx).reset_index(drop=True)
    result = result.rename(columns={"full_name": "Joueur"})
    result = result.sort_values("Victoires", ascending=False).reset_index(drop=True)
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

    rows = [
        ("Victoires", len(wins)),
        ("Défaites", len(losses)),
        ("Matchs joués", len(wins) + len(losses)),
        ("% Victoires", round(len(wins) / max(len(wins) + len(losses), 1) * 100, 1)),
        ("Tournois joués", m[m["winner_id"] == pid]["tourney_name"].nunique() +
         m[m["loser_id"] == pid]["tourney_name"].nunique()),
    ]

    if "minutes" in m.columns:
        all_m = pd.concat([wins, losses])
        rows.append(("Durée moy. match (min)", round(all_m["minutes"].mean(), 1)))

    result = pd.DataFrame(rows, columns=["Statistique", name])
    return result


# ---------------------------------------------------------------------------
# 3. Résultats par surface
# ---------------------------------------------------------------------------

def resultats_par_surface(circuit: str = "ATP") -> pd.DataFrame:
    """Nombre de matchs et durée moyenne par surface."""
    _load()
    m = _matches(circuit)

    grouped = m.groupby("surface").agg(
        Matchs=("surface", "count"),
        Durée_moy=("minutes", "mean"),
    ).round({"Durée_moy": 1}).reset_index()
    grouped = grouped.rename(columns={"surface": "Surface", "Durée_moy": "Durée moy. (min)"})
    grouped = grouped.sort_values("Matchs", ascending=False).reset_index(drop=True)
    grouped.index += 1
    return grouped


# ---------------------------------------------------------------------------
# 4. Stats par tournoi
# ---------------------------------------------------------------------------

def stats_par_tournoi(circuit: str = "ATP", n: int = 20) -> pd.DataFrame:
    """Statistiques par tournoi : matchs joués et durée moyenne."""
    _load()
    m = _matches(circuit)

    grouped = m.groupby("tourney_name").agg(
        Matchs=("tourney_name", "count"),
        Surface=("surface", "first"),
        Durée_moy=("minutes", "mean"),
    ).round({"Durée_moy": 1}).reset_index()
    grouped = grouped.rename(columns={"tourney_name": "Tournoi", "Durée_moy": "Durée moy. (min)"})
    grouped = grouped.sort_values("Matchs", ascending=False).head(n).reset_index(drop=True)
    grouped.index += 1
    return grouped[["Tournoi", "Surface", "Matchs", "Durée moy. (min)"]]

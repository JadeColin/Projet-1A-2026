import pandas as pd

from Projet_Mathias.loaders.ChessLoader import ChessLoader

_loader = None
_players: pd.DataFrame = None
_matches: pd.DataFrame = None


def _load():
    global _loader, _players, _matches
    if _loader is None:
        _loader = ChessLoader()
        _players, _matches = _loader.load_all()


# ---------------------------------------------------------------------------
# 1. Classement Elo
# ---------------------------------------------------------------------------

def classement_elo(mode: str = "standard", n: int = 20) -> pd.DataFrame:
    """Top N joueurs par classement Elo (standard / rapid / blitz)."""
    _load()
    col_map = {"standard": "rating_standard", "rapid": "rating_rapid", "blitz": "rating_blitz"}
    col = col_map.get(mode.lower())
    if col is None:
        raise ValueError(f"Mode invalide : '{mode}'. Choisir parmi : standard, rapid, blitz")

    df = _players[["name", "federation", "fide_title", col]].copy()
    df = df.dropna(subset=[col]).sort_values(col, ascending=False).head(n).reset_index(drop=True)
    df.index += 1
    labels = {col: f"Elo {mode.capitalize()}", "name": "Joueur", "federation": "Fédération", "fide_title": "Titre"}
    return df.rename(columns=labels)


# ---------------------------------------------------------------------------
# 2. Bilan d'un joueur
# ---------------------------------------------------------------------------

def bilan_joueur(player_name: str) -> pd.DataFrame:
    """Bilan victoires/défaites/nuls d'un joueur (recherche insensible à la casse)."""
    _load()

    mask = _players["name"].str.contains(player_name, case=False, na=False)
    matched = _players[mask]
    if matched.empty:
        raise ValueError(f"Aucun joueur trouvé pour : '{player_name}'")

    name = matched.iloc[0]["name"]

    as_p1 = _matches[_matches["player_1"] == name]
    as_p2 = _matches[_matches["player_2"] == name]

    def count_result(df, col_score):
        scores = pd.to_numeric(df[col_score], errors="coerce").dropna()
        wins = (scores == 1).sum()
        draws = (scores == 0.5).sum()
        losses = (scores == 0).sum()
        return wins, draws, losses

    w1, d1, l1 = count_result(as_p1, "score_player_1")
    w2, d2, l2 = count_result(as_p2, "score_player_2")

    victoires = w1 + w2
    nuls = d1 + d2
    defaites = l1 + l2
    joues = victoires + nuls + defaites

    rows = [
        ("Parties jouées", joues),
        ("Victoires", victoires),
        ("Nuls", nuls),
        ("Défaites", defaites),
        ("Score total", victoires + nuls * 0.5),
    ]
    return pd.DataFrame(rows, columns=["Statistique", name])


# ---------------------------------------------------------------------------
# 3. Stats par titre FIDE
# ---------------------------------------------------------------------------

def stats_par_titre() -> pd.DataFrame:
    """Nombre de joueurs et Elo moyen (standard) par titre FIDE."""
    _load()
    grouped = _players.groupby("fide_title").agg(
        Joueurs=("name", "count"),
        Elo_moy_standard=("rating_standard", "mean"),
        Elo_moy_rapid=("rating_rapid", "mean"),
        Elo_moy_blitz=("rating_blitz", "mean"),
    ).round(0).reset_index()
    grouped = grouped.rename(columns={
        "fide_title": "Titre FIDE",
        "Elo_moy_standard": "Elo moy. Standard",
        "Elo_moy_rapid": "Elo moy. Rapid",
        "Elo_moy_blitz": "Elo moy. Blitz",
    })
    grouped = grouped.sort_values("Elo moy. Standard", ascending=False).reset_index(drop=True)
    grouped.index += 1
    return grouped

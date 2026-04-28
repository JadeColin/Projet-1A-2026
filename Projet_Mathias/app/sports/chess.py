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
    labels = {
        col: f"Elo {mode.capitalize()}",
        "name": "Joueur", "federation": "Fédération", "fide_title": "Titre"}
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

# ---------------------------------------------------------------------------
# 4. Statistiques globales des joueurs
# ---------------------------------------------------------------------------

def stats_globales_joueurs() -> pd.DataFrame:
    """Renvoie les informations globales de tous les joueurs."""
    _load()
    
    # On définit les colonnes qu'on veut afficher (selon ta liste de tâches)
    # Note: On utilise les noms de colonnes anglais que ton équipe semble utiliser
    colonnes_souhaitees = [
        "name",             # nom
        "sex",              # sexe (à vérifier si c'est 'sex' ou 'gender' dans vos données)
        "birthday",         # date de naissance (à vérifier si c'est 'birthday' ou 'dob')
        "federation",       # fédération
        "fide_id",          # numéro fide
        "fide_title",       # titre
        "rating_standard",  # elo
        "rating_blitz",     # elo blitz
        "rating_rapid"      # elo rapide
    ]
    
    # On filtre pour ne garder que les colonnes qui existent vraiment 
    # (au cas où le nom des colonnes diffère un peu dans votre CSV)
    colonnes_existantes = [col for col in colonnes_souhaitees if col in _players.columns]
    
    # On crée le tableau final
    df = _players[colonnes_existantes].copy()
    
    # On renomme proprement en français pour l'affichage
    labels_francais = {
        "name": "Nom",
        "sex": "Sexe",
        "birthday": "Date de Naissance",
        "federation": "Fédération",
        "fide_id": "Numéro FIDE",
        "fide_title": "Titre",
        "rating_standard": "Elo Standard",
        "rating_blitz": "Elo Blitz",
        "rating_rapid": "Elo Rapide"
    }
    
    return df.rename(columns=labels_francais)

    # ---------------------------------------------------------------------------
# 5. Tous les classements Elo
# ---------------------------------------------------------------------------

def classements_tous_elo(n: int = 10) -> dict:
    """
    Renvoie les 3 classements (Standard, Rapide, Blitz) d'un seul coup 
    sous forme de dictionnaire.
    """
    # On utilise la fonction 'classement_elo' qui existe déjà plus haut !
    classements = {
        "Top Standard": classement_elo(mode="standard", n=n),
        "Top Rapide": classement_elo(mode="rapid", n=n),
        "Top Blitz": classement_elo(mode="blitz", n=n)
    }
    
    return classements
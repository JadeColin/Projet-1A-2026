import pandas as pd

# Charger les données des matchs
df_matchs = pd.read_csv("Projet-1A-2026/Projet_Mathias/output/chess_matches_clean.csv")

# Charger les données des joueurs
df_joueurs = pd.read_csv("Projet-1A-2026/Projet_Mathias/output/chess_players_clean.csv")


def statistiques_globales_joueurs(df_joueurs):
    """
    Retourne les statistiques globales des joueurs :
    - nom
    - titre
    - sexe
    - date de naissance
    - fédération
    - numéro FIDE
    - Elo standard
    - Elo Blitz
    - Elo Rapide
    """
    # Sélectionner les colonnes pertinentes
    stats = df_joueurs[['name', 'fide_title', 'gender', 'birth_year', 'federation', 'fide_id', 
                        'rating_standard', 'rating_blitz', 'rating_rapid']]
    
    # Renommer les colonnes pour plus de clarté
    stats.columns = ['Nom', 'Titre', 'Sexe', 'Année de naissance', 'Fédération', 'Numéro FIDE', 
                     'Elo Standard', 'Elo Blitz', 'Elo Rapide']
    
    return stats

# Exemple d'utilisation
stats_globales = statistiques_globales_joueurs(df_joueurs)
print(stats_globales)
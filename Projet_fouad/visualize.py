from Projet_Mathias.classes.joueur import Joueur, Joueurs
from Projet_Mathias.classes.sport import Sport, SPORTS
from Projet_Adam.classe_competition import Competition
from Projet_Adam.Evenements import Evenement
from Projet_Adam.Match import Match
from Projet_Adam.Participation import Participation
from Projet_Mathias.load import load
from datetime import date


# ── Configuration par sport ─────────────────────────────────────────────────
# Relie chaque sport (nom) à sa clé loader, ses tables, et ses colonnes

SPORT_CONFIG = {
    "Basketball": {
        "loader_key": "basketball",
        "match_table": "matches",
        "player_table": "players",
        "competitions": [
            {"id": 1, "name": "NBA 2024-2025", "location": "USA",
             "debut": date(2024, 10, 22), "fin": date(2025, 6, 15)},
        ],
        "col_equipe1": "team_id_home",
        "col_equipe2": "team_id_away",
        "col_score1": "pts_home",
        "col_score2": "pts_away",
        "col_date": "game_date",
    },
    "League of Legends": {
        "loader_key": "lol",
        "match_table": "matches",
        "player_table": "players",
        "competitions": [
            {"id": 2, "name": "LEC EMEA 2024", "location": "Europe",
             "debut": date(2024, 1, 15), "fin": date(2024, 9, 30)},
        ],
        "col_equipe1": "team_blue",
        "col_equipe2": "team_red",
        "col_gagnant": "winner",
        "col_date": "date",
    },
    "Football Champions L.": {
        "loader_key": "football_champions_league",
        "match_table": "matches",
        "player_table": "players",
        "competitions": [
            {"id": 3, "name": "UEFA Champions League 2024-2025", "location": "Europe",
             "debut": date(2024, 9, 17), "fin": date(2025, 5, 31)},
        ],
        "col_equipe1": "home_team_api_id",
        "col_equipe2": "away_team_api_id",
        "col_score1": "home_team_goal",
        "col_score2": "away_team_goal",
        "col_date": "date",
    },
    "Tennis": {
        "loader_key": "tennis",
        "match_table": "atp_matches",
        "player_table": "atp_players",
        "competitions": [
            {"id": 4, "name": "ATP Tour 2024", "location": "Mondial",
             "debut": date(2024, 1, 1), "fin": date(2024, 12, 31)},
        ],
        "col_equipe1": "winner_id",
        "col_equipe2": "loser_id",
        "col_gagnant": "winner_id",
        "col_date": "tourney_date",
    },
    "Échecs": {
        "loader_key": "chess",
        "match_table": "matches",
        "player_table": "players",
        "competitions": [
            {"id": 5, "name": "Championnat du Monde d'Échecs", "location": "Mondial",
             "debut": date(2024, 1, 1), "fin": date(2024, 12, 31)},
        ],
        "col_equipe1": "white_id",
        "col_equipe2": "black_id",
        "col_gagnant": "winner",
    },
    "Volleyball": {
        "loader_key": "volleyball",
        "match_table": "matches_men",
        "player_table": "players_men",
        "competitions": [
            {"id": 6, "name": "Ligue des Nations Hommes", "location": "Mondial",
             "debut": date(2024, 5, 1), "fin": date(2024, 7, 31)},
        ],
        "col_equipe1": "country_code_1",
        "col_equipe2": "country_code_2",
        "col_score1": "set_country_1",
        "col_score2": "set_country_2",
        "col_gagnant": "winner",
        "col_date": "date",
    },
}


# ── Cache pour éviter de recharger les données à chaque appel ───────────────
_cache_competitions = {}


def _build_competitions(sport: Sport):
    """
    Construit la hiérarchie complète Competition → Evenement → Match
    à partir des données CSV chargées via load.py.
    """
    if sport.nom in _cache_competitions:
        return _cache_competitions[sport.nom]

    config = SPORT_CONFIG.get(sport.nom)
    if config is None:
        _cache_competitions[sport.nom] = []
        return []

    loader_key = config["loader_key"]
    match_table = config["match_table"]

    # Charger le DataFrame des matchs
    try:
        df = load(loader_key, match_table)
    except Exception as e:
        print(f"Erreur lors du chargement des matchs pour {sport.nom} : {e}")
        _cache_competitions[sport.nom] = []
        return []

    # Colonnes de mapping
    col_eq1 = config.get("col_equipe1")
    col_eq2 = config.get("col_equipe2")
    col_s1 = config.get("col_score1")
    col_s2 = config.get("col_score2")
    col_date = config.get("col_date")
    col_gagnant = config.get("col_gagnant")

    competitions = []

    for comp_info in config["competitions"]:
        # Créer la compétition
        comp = Competition(
            comp_info["id"],
            comp_info["name"],
            comp_info["location"],
            comp_info["debut"],
            comp_info["fin"],
        )

        # Créer un événement principal pour cette compétition
        event = Evenement(
            id_evenement=comp_info["id"] * 10,
            sport=sport.nom,
            categorie=str(sport.type_sport),
            id_competition=comp.id_competition,
        )

        # Peupler l'événement avec les matchs du DataFrame
        for idx, row in df.iterrows():
            # Récupérer la date du match
            match_date = None
            if col_date and col_date in df.columns:
                try:
                    match_date = date.fromisoformat(str(row[col_date])[:10])
                except (ValueError, TypeError):
                    match_date = date.today()

            # Créer le match 
            match =Match(
                id_match=int(idx),
                date_match=match_date or date.today(),
                localisation=comp_info["location"],
                id_evenement=event.id_evenement,
            )

            # Récupérer les noms/IDs des équipes
            equipe1 = str(row[col_eq1]) if col_eq1 and col_eq1 in df.columns else "?"
            equipe2 = str(row[col_eq2]) if col_eq2 and col_eq2 in df.columns else "?"

            # Récupérer les scores
            score1 = row.get(col_s1) if col_s1 else None
            score2 = row.get(col_s2) if col_s2 else None

            # Déterminer le gagnant
            if col_gagnant and col_gagnant in df.columns:
                gagnant = str(row[col_gagnant])
                status1 = "victoire" if gagnant == equipe1 else "defaite"
                status2 = "victoire" if gagnant == equipe2 else "defaite"
            elif score1 is not None and score2 is not None:
                try:
                    if float(score1) > float(score2):
                        status1, status2 = "victoire", "defaite"
                    elif float(score2) > float(score1):
                        status1, status2 = "defaite", "victoire"
                    else:
                        status1, status2 = "nul", "nul"
                except (ValueError, TypeError):
                    status1, status2 = "inconnu", "inconnu"
            else:
                status1, status2 = "inconnu", "inconnu"

            # Créer les participations
            p1 = Participation(
                id_participation=int(idx) * 2,
                id_match=match.id_match,
                status=status1,
            )
            p2 = Participation(
                id_participation=int(idx) * 2 + 1,
                id_match=match.id_match,
                status=status2,
            )

            # Stocker le nom de l'équipe sur la participation pour l'affichage
            p1.nom_equipe = equipe1
            p1.score = score1
            p2.nom_equipe = equipe2
            p2.score = score2

            match.ajouter_participation(p1)
            match.ajouter_participation(p2)

            # Stocker aussi les infos d'affichage directement sur le match
            match.equipe_1 = equipe1
            match.equipe_2 = equipe2
            match.score_1 = score1
            match.score_2 = score2

            event.ajouter_match(match)

        comp.ajouter_evenement(event)
        competitions.append(comp)

    _cache_competitions[sport.nom] = competitions
    return competitions

#  Classes de visualisation


class SportVisualizer():

    @staticmethod
    def display_all_sports():
        """Affiche et retourne la liste de tous les sports disponibles."""
        return SPORTS


class CompetitionVisualizer():

    @staticmethod
    def display_all_competitions(sport: Sport):
        """Retourne les compétitions associées à un sport."""
        return _build_competitions(sport)


class EventVisualizer():

    @staticmethod
    def display_all_events(comp: Competition):
        """Retourne les événements associés à une compétition."""
        return comp.evenements

    @staticmethod
    def display_winner(event: Evenement):
        """Affiche le gagnant d'un événement en analysant les participations."""
        if not event.matchs:
            print("Aucun match dans cet événement.")
            return None

        # Compter les victoires par équipe
        victoires = {}
        for match in event.matchs:
            for p in match.participations:
                nom = getattr(p, 'nom_equipe', str(p.id_participation))
                if p.status == "victoire":
                    victoires[nom] = victoires.get(nom, 0) + 1

        if not victoires:
            print("Aucun résultat disponible.")
            return None

        gagnant = max(victoires, key=victoires.get)
        print(f"Gagnant : {gagnant} avec {victoires[gagnant]} victoire(s)")
        return gagnant


class PlayerVisualizer():

    @staticmethod
    def display_all_players(sport: Sport):
        """Charge et retourne la collection Joueurs pour un sport."""
        config = SPORT_CONFIG.get(sport.nom)
        if config is None:
            print(f"Sport '{sport.nom}' non configuré.")
            return Joueurs.__new__(Joueurs)

        loader_key = config["loader_key"]
        player_table = config.get("player_table")
        if player_table is None:
            print(f"Pas de table de joueurs pour {sport.nom}.")
            return None

        try:
            df = load(loader_key, player_table)
            joueurs = Joueurs(df)
            print(f"{len(joueurs)} joueur(s) trouvé(s) pour {sport.nom}.")
            return joueurs
        except Exception as e:
            print(f"Erreur lors du chargement des joueurs : {e}")
            return None
from Projet_Mathias.classes.match import *
from Projet_Mathias.classes.sport import *


class MatchVisualizer():

    @staticmethod
    def display_all_matches(sport: Sport):
        pass  # TODO: implémenter l'affichage de tous les matchs

    @staticmethod
    def display_match_title(match: Match, sport: Sport):
        if sport.est_individuel:
            return f'{match.equipe_1} VS {match.equipe_2}'
        return f'Équipe {match.equipe_1} VS Équipe {match.equipe_2}'

    @staticmethod
    def display_match_resultat(match: Match):
        return f'{match.equipe_1} : {match.score_1} VS {match.equipe_2}: {match.score_2}'

    @staticmethod
    def display_match_score(match: Match):
        return f'{match.score_1} : {match.score_2}'
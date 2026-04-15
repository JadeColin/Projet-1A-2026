from Projet_Mathias.match import *
from Projet_Mathias.sport import *

class MatchVisualizer():
    def display_all_matches(sport:Sport):
        

    def display_match_title(match: Match, sport: Sport):
        if sport.is_individual:
            return '{match.player_1} VS {match.player_2}'

        return 'Équipe {match.player_1} VS Équipe {match.player_2}'

    def display_match_resultat(match:Match):
        return '{match.player_1} : {match.score_1} VS {match.player_2}: {match.score_2}'

    def display_match_score(match:Match):
        return ' {match.score_1} : {match.score_2}'
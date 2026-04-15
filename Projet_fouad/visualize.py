from Projet_Adam.classe_competition import Competition
from Projet_Adam.Evenements import Evenement
from Projet_Mathias.match import Match
from Projet_Mathias.joueur import Joueur
from Projet_Mathias.sport import *

class SportVisializer() :

class CompetitionVisualizer():
    def display_all_competitions(sport: Sport):
    
class EventVisualizer():
    def display_all_events(comp:Competition):
    
    def display_winner():

class MatchVisualizer():
    def display_match_title(match: Match, sport: Sport):
        if sport.is_individual:
            return '{match.player_1} VS {match.player_2}'

        return 'Équipe {match.player_1} VS Équipe {match.player_2}'

    def display_match_resultat(match:Match):
        return '{match.player_1} : {match.score_1} VS {match.player_2}: {match.score_2}'

    def display_match_score(match:Match):
        return ' {match.score_1} : {match.score_2}'
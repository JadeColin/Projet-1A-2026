from Projet_Adam.competition import Competition
from Projet_Adam.evenement import Evenenment
from Projet_Mathias import 

supported_sports = display_sport(comp)

selected_sport = input("Sélectionnez un sport parmi {supported_sports}")
if selected_sport not in supported_sports:
    raise Exception("Sport pas encore supporté par l'appli")

selected_competions = input("Sélectionnez une compétition parmi {display_all_competitions(selected_sport)}")
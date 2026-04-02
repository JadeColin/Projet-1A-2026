from src.Model.Sport import Sport
from src.Analysis import display_all_competitions

supported_sports = [
    Sport(name="football",team_sport=True),
    Sport(name="tennis",team_sport=False)
]

selected_sport = input("Sélectionnez un sport parmi {supported_sports}")
if selected_sport not in supported_sports:
    raise Exception("Sport pas encore supporté par l'appli")

selected_competion = input("Sélectionnez une compétition parmi {display_all_competitions(selected_sport)}")

if selected_competion not in display_all_competitions(selected_sport):
    raise Exception("Compétition pas encore supporté par l'appli")
selected_event = input("Sélectionnez un évenement sportif parmi {display_all_events(selected_competion)}")
if selected_event not in display_all_events(selected_competion):
    raise Exception("Evenement pas encore supporté par l'appli")
selected_match = input("Sélectionnez un match parmi {display_all_events(selected_event)}")
if selected_match not in display_all_events(selected_event):
    raise Exception("Match pas encore supporté par l'appli")
display_all_players(selected_match)
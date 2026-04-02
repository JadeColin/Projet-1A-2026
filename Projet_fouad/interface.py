from src.Model.Sport import Sport
from src.Analysis import display_all_competitions

supported_sports = [
    Sport(name="football",team_sport=True),
    Sport(name="tennis",team_sport=False)
]

selected_sport = input("Sélectionnez un sport parmi {supported_sports}")
if selected_sport not in supported_sports:
    raise Exception("Sport pas encore supporté par l'appli")

selected_competions = input("Sélectionnez une compétition parmi {display_all_competitions(selected_sport)}")
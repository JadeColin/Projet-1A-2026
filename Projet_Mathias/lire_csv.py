import pandas as pd
from pathlib import Path
from.src.Model.Match import Match
from .src.Model.Sport import Sport
from .adapters.FootballMatchLoader import FootballMatchLoader
from .adapters.TennisMatchLoader import TennisMatchLoader
from .adapters.BasketballMatchLoader import BasketballMatchLoader
from .adapters.LolMatchLoader import LolMatchLoader
from .adapters.VolleyballLoader import VolleyballMatchLoader


ROOT = Path("Base_de_données")

sport_1 = "Basketball"
sport_2 = "Football"
sport_3 = "Lol"
sport_4 = "tennis"
sport_5 = "volleyball"

joueur_femme = ROOT / sport_4 / "wta_players_2024"

df = pd.read_csv(joueur_femme)


class MatchLoader():
    def __init__(self, sport: Sport):
        self.sport = sport

    def load_all_matches(self):
        if self.sport.name == "tennis":
            return TennisMatchLoader().load_all_matches()
        elif self.sport.name == "basketball":
            return BasketballMatchLoader().load_all_matches()
        elif self.sport.name == "volleyball":
            return VolleyballMatchLoader().load_all_matches()
        elif self.sport.nam == "Lol":
            return LolMatchLoader().load_all_matches()
        elif self.sport.name == "football":
            return FootballMatchLoader().load_all_matches()

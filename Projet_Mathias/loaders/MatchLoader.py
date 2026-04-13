from .src.Model.Match import Match
from .src.Model.Sport import Sport
from .adapters.FootballMatchLoader import FootballMatchLoader
from .adapters.TennisMatchLoader import TennisMatchLoader
from .adapters.BasketballMatchLoader import BasketballMatchLoader
from .adapters.LolMatchLoader import LolMatchLoader
from .adapters.VolleyballLoader import VolleyballMatchLoader
from pandas import df


class MatchLoader():
    def __init__(self, sport: Sport):
        self.sport = sport

    def load_all_matches(self) -> df[Match]:
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
        else:
            raise Exception("Le sport n'est pas dans la base de donnée")


"""
Exemple d'utilisation :

loader = MatchLoader(Sport(name="football"))
mes_matchs: df[Match] = loader.load_all_matches()
"""

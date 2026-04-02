from .src.Model.Joueur import Joueur
from .adapters.HommeTennisLoader import HommeTennisLoader
from .adapters.FemmeTennisLoader import FemmeTennisLoader


class TennisMatchLoader():
    def __init__(self, joueurs: Joueur):
        self.joueurs = joueurs

    def LoadSexTennis(self):
        if self.joueurs.sexe == "homme":
            return HommeTennisLoader().LoadSexTennis()
        elif self.joueurs.sexe == "femme":
            return FemmeTennisLoader().LoadSexTennis()
        else:
            return Exception("Le sexe n'est pas compatible")

    def Id_player(self):
        

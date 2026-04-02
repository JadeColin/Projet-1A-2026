from .joueur import Joueur
from .equipe import Equipe
from datetime import date

class Joueur_equipe:
    def __init__(self,joueur: Joueur, equipe : Equipe, date_debut: date, date_fin : date, type_equipe : str):
        if isinstance(joueur, Joueur):
            self.joueur= joueur 
        else: 
            raise TypeError("le joueur doit etre un Joueur")

        if isinstance(equipe, Equipe):
            self.equipe= equipe
        else : 
            raise TypeError("l'equipe doit etre une Equipe")
        
        if isinstance(date_debut, date):
            self.date_debut = date_debut
        else:
            raise TypeError("la date de début doit etre une date")

        if isinstance(date_fin, date):
            self.date_fin = date_fin
        else : 
            raise TypeError("la date de fin doit etre une date")

        if isinstance(type_equipe, str):
            self.type_equipe= type_equipe
        else: 
            raise TypeError("le type de l'équipe doit etre une string")

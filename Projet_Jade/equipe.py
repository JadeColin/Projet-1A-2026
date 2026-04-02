
from .participation import Participation

class Equipe :

    def__init__(self,id_equipe : int, nom_equipe : str, type_equipe: str, pays : str, participation : Participation):
        
        if isinstance(id_equipe, int):
            self.id_equipe= id_equipe
        else :
            raise TypeError("id équipe doit etre un entier")

        if isinstance(nom_equipe, str):
            self.nom_equipe= nom_equipe
        else:
            raise TypeError("le nom de l'équipe doit etre une chaine de caractère")
        
        if isinstance(type_equipe, str):
            self.type_equipe = type_equipe
        else:
            raise TypeError("le type de l'équipe doit etre une chaine de caractère")

        if isinstance(pays, str):
            self.pays= pays
        else:
            raise TypeError("le pays doit etre une string")

        if isinstance(participation, Participation):
            self.participation= participation
        else:
            raise TypeError("la participation doit etre un objet de Participation")

    
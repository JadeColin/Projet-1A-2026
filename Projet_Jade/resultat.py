from .participation import Participation

class Resultat:

    def__init__(self, id_resultat : int, score: int, rang: int, trophee: bool, participation : Participation):
    if isinstance(id_resultat, int):
        self.id_resultat = id_resultat
    else : 
        raise TypeError("l'id du résultat doit etre un entier")
    
    if isinstance(score, int):
        self.score= score
    else : 
        raise TypeError("le score doit etre un entier")

    if isinstance(rang, int):
        self.rang= rang
    else: 
        raise TypeError("le rang doit etre un entier")

    if isinstance(trophee, bool):
        self.trophee= trophee
    else: 
        raise TypeError("le trophee doit etre un booléen")

    if isinstance(participation, Participation):
        self.participation= participation
    else:
        raise TypeError("la participation doit etre un objet de Participation")

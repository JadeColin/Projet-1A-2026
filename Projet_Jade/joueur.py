
from datetime import date

class Joueur:

    def__init__(self, id_joueur: int, nom_joueur: str, sexe : str, date_naissance: date, nationalite: str, participation: Participation):
        if isinstance(id_joueur, int):
            self.id_joueur= id_joueur
        else : 
            raise TypeError("id_joueur doit etre un entier")
        
        if isinstance(nom_joueur, str):
            self.nom_joueur= nom_joueur
        else: 
            raise TypeError("le nom du joueur doit etre une chaine de caractère")

        sexes_valides=["Homme", "Femme"]
        if sexe in sexes_valides:
            self.sexe=sexe
        else: 
            raise ValueError("le sexe doit etre 'Homme' ou 'Femme' ")

        if isinstance(date_naissance, date):
            self.date_naissance = date_naissance
        else : 
            raise TypeError("la date de naissance doit etre une date")

        if isinstance(nationalite, str):
            self.nationalite=nationalite
        else : 
            raise TypeError("la nationalité doit etre une chaine de caractère")
        
        if isinstance(participation, Participation):
            self.participation = participation
        else:
            raise TypeError("la participation doit etre un objet de Participation")

    def __str__(self):
        return self.nom_joueur

    def __repr__(self):
        return (f"Joueur(id = {self.id_joueur}, nom = {self.nom_joueur},"
        f"né le {self.date_naissance}, de nationalité {self.nationalite}, participation = {self.participation})")
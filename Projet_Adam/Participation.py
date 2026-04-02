class Participation:
    def __init__(self, id_participation: int, id_match: int, status: str):
        self.id_participation = id_participation
        self.id_match = id_match  
        self.status = status
        self.resultats = []
        self.joueurs = []
        self.equipes = []

    def ajouter_joueur(self, joueur):
        self.joueurs.append(joueur)

    def ajouter_equipe(self, equipe):
        self.equipes.append(equipe)

    def ajouter_resultat(self, resultat):
        self.resultats.append(resultat)

    def __repr__(self):
        return (f"Participation(id={self.id_participation}, "
                f"id_match={self.id_match}, status='{self.status}')")
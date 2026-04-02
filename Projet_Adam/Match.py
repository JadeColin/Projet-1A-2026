from datetime import date

class Match:
    def __init__(self, id_match: int, date_match: date, localisation: str, id_evenement: int):
        self.id_match = id_match
        self.date_match = date_match
        self.localisation = localisation
        self.id_evenement = id_evenement
        self.participations = []
        self.resultats = []

    def ajouter_resultat(self, resultat):
        self.resultats.append(resultat)

    def ajouter_participation(self, participation):
        self.participations.append(participation)
    

    def __repr__(self):
        return (f"Match(id={self.id_match}, date='{self.date_match}', "
                f"localisation='{self.localisation}', id_evenement={self.id_evenement})")
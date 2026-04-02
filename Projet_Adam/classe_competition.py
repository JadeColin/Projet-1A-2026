from datetime import date

class Competition:
    def __init__(self, id_competition: int, name: str, location: str, debut_date: date, fin_date: date):
        self.id_competition = id_competition
        self.name = name
        self.location = location
        self.debut_date = debut_date
        self.fin_date = fin_date
        self.evenements = []
    
    def ajouter_evenement(self, evenement):
        self.evenements.append(evenement)
    
    def __repr__(self):
        return (f"Competition(id={self.id_competition}, name='{self.name}', "
                f"location='{self.location}', debut={self.debut_date}, fin={self.fin_date})")
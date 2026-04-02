class Evenements:
    def __init__(self, id_evenement: int, sport: str, categorie: str, id_competition: int):
        self.id_evenement = id_evenement
        self.sport = sport
        self.categorie = categorie
        self.id_competition = id_competition 

    def __repr__(self):
        return (f"Evenements(id={self.id_evenement}, sport='{self.sport}', "
                f"categorie='{self.categorie}', id_competition={self.id_competition})")
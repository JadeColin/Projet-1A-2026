class Match:
    def __init__(self, id_match: int, date_match: str, localisation: str, id_evenements: int):
        self.id_match = id_match
        self.date_match = date_match
        self.localisation = localisation
        self.id_evenements = id_evenements  

    def __repr__(self):
        return (f"Match(id={self.id_match}, date='{self.date_match}', "
                f"localisation='{self.localisation}', id_evenements={self.id_evenements})")
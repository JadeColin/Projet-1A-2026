"""
On va s'intéresser ici à l'utilisation de Parsers. C'es-à-dire à des éléments qui vont permettrent
de lire les bases de données. On transforme une base illisible pour Python en découpant les
paramètres et en leur mettant une étiquette.

Pour ce faire, nous allons créer des Parsers et de mappers assez génériques. L'objectif est que de
cette manière en ajoutant des bases de données ce soit plus facile à gérer. Ce sera la pipeline qui
permettra de d'assembler les parsers avec les mappers.
"""


"""
Une classe de Parsers générique
"""


import csv  # noqa: E402
from abc import ABC, abstractmethod  # noqa: E402


class Parser(ABC):
    @abstractmethod
    def load(self, source: str) -> list[dict]:
        pass


"""
On sécurise le VSC Parsers
"""


class CSVParser(Parser):
    def load(self, source: str) -> list[dict]:
        try:
            with open(source, newline='', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            raise ParserError(source, "fichier introuvable")
        except UnicodeDecodeError:
            raise ParserError(source, "encodage invalide, attendu UTF-8")
        except csv.Error as e:
            raise ParserError(source, f"fichier CSV malformé ({e})")


"""
Création de l'élément Team
"""


class Team:
    """
    Représente une équipe de basketball NBA.

    Parameters
    ----------
    team_id : int
        Identifiant unique de l'équipe.
    full_name : str
        Nom complet de l'équipe (ex: "Boston Celtics").
    abbreviation : str
        Abréviation officielle (ex: "BOS").
    nickname : str
        Surnom de l'équipe (ex: "Celtics").
    city : str
        Ville de l'équipe.
    state : str
        État ou province de l'équipe.
    """

    def __init__(self, team_id, full_name, abbreviation, nickname, city, state):
        self.team_id = team_id
        self.full_name = full_name
        self.abbreviation = abbreviation
        self.nickname = nickname
        self.city = city
        self.state = state

    def __repr__(self):
        return f"Team({self.abbreviation} - {self.full_name})"


"""
Création d'un DataMapper générique
"""


class DataMapper(ABC):
    @abstractmethod
    def map(self, raw_data: list[dict]) -> list:
        pass


"""
Gestion des erreurs par des exceptions personnalisés
"""


class ParserError(Exception):
    """
    Levée quand la lecture du fichier source échoue.

    Parameters
    ----------
    source : str
        Chemin du fichier qui a causé l'erreur.
    reason : str
        Explication de la cause de l'erreur.
    """
    def __init__(self, source: str, reason: str):
        self.source = source
        self.reason = reason
        super().__init__(f"Erreur de lecture pour '{source}' : {reason}")


class MappingError(Exception):
    """
    Levée quand la transformation d'une ligne échoue.

    Parameters
    ----------
    row : dict
        La ligne de données qui a causé l'erreur.
    reason : str
        Explication de la cause de l'erreur.
    """
    def __init__(self, row: dict, reason: str):
        self.row = row
        self.reason = reason
        super().__init__(f"Erreur de mapping sur la ligne {row} : {reason}")


"""
Sécuriser la base de données Team NBA
"""


class NBATeamMapper(DataMapper):

    COLONNES_REQUISES = {"id", "full_name", "abbreviation", "nickname", "city", "state"}

    def map(self, raw_data: list[dict]) -> list[Team]:
        self._verifier_colonnes(raw_data)
        teams = []
        for row in raw_data:
            teams.append(self._map_row(row))
        return teams

    def _verifier_colonnes(self, raw_data: list[dict]) -> None:
        """
        Vérifie que toutes les colonnes requises sont présentes.

        Parameters
        ----------
        raw_data : list[dict]
            Les données brutes à vérifier.

        Raises
        ------
        MappingError
            Si une ou plusieurs colonnes sont manquantes.
        """
        if not raw_data:
            return
        colonnes_presentes = set(raw_data[0].keys())
        colonnes_manquantes = self.COLONNES_REQUISES - colonnes_presentes
        if colonnes_manquantes:
            raise MappingError(
                row={},
                reason=f"colonnes manquantes : {colonnes_manquantes}"
            )

    def _map_row(self, row: dict) -> Team:
        """
        Transforme une ligne brute en objet Team.

        Parameters
        ----------
        row : dict
            Une ligne de données brutes.

        Returns
        -------
        Team
            L'objet Team correspondant.

        Raises
        ------
        MappingError
            Si l'id ne peut pas être converti en entier.
        """
        try:
            team_id = int(row["id"])
        except ValueError:
            raise MappingError(row, f"id '{row['id']}' n'est pas un entier valide")

        return Team(
            team_id=team_id,
            full_name=row["full_name"],
            abbreviation=row["abbreviation"],
            nickname=row["nickname"],
            city=row["city"],
            state=row["state"]
        )


"""
Création et sécurisation du datapipeline
"""


class DataPipeline:
    def __init__(self, parser: Parser, mapper: DataMapper):
        self.parser = parser
        self.mapper = mapper

    def run(self, source: str) -> list:
        try:
            raw_data = self.parser.load(source)
        except ParserError as e:
            print(f"[ERREUR LECTURE] {e}")
            return []

        try:
            return self.mapper.map(raw_data)
        except MappingError as e:
            print(f"[ERREUR MAPPING] {e}")
            return []
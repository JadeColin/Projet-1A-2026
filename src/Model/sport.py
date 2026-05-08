"""
Modèle de données pour les sports.

Définit :
- TypeSport        : enum distinguant sports individuels et collectifs
- CategorieSport   : enum distinguant sport traditionnel et e-sport
- TypeCompetition  : enum distinguant compétition en points, éliminatoire, ou mixte
- Sport            : classe représentant un sport avec ses caractéristiques
- SPORTS           : registre de tous les sports disponibles dans l'application
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass


class TypeSport(Enum):
    """Type d'un sport : individuel ou collectif."""

    INDIVIDUEL = "Individuel"
    COLLECTIF = "Collectif"

    def __str__(self) -> str:
        return self.value


class CategorieSport(Enum):
    """Catégorie d'un sport : sport traditionnel ou e-sport."""

    SPORT = "Sport"
    ESPORT = "E-sport"

    def __str__(self) -> str:
        return self.value


class TypeCompetition(Enum):
    """Format de compétition : par points, phase éliminatoire, ou les deux."""

    POINTS = "Points"
    ELIMINATOIRE = "Éliminatoire"
    MIXTE = "Mixte"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Sport:
    """Représente un sport avec son nom, son type, sa catégorie et sa couleur d'interface."""

    nom: str
    type_sport: TypeSport
    categorie: CategorieSport
    type_competition: TypeCompetition
    couleur: str

  
    @property
    def est_individuel(self) -> bool:
        return self.type_sport == TypeSport.INDIVIDUEL

    @property
    def est_collectif(self) -> bool:
        return self.type_sport == TypeSport.COLLECTIF

    @property
    def est_esport(self) -> bool:
        return self.categorie == CategorieSport.ESPORT

    @property
    def est_sport(self) -> bool:
        return self.categorie == CategorieSport.SPORT

    @property
    def est_en_points(self) -> bool:
        return self.type_competition in (TypeCompetition.POINTS, TypeCompetition.MIXTE)

    @property
    def est_eliminatoire(self) -> bool:
        return self.type_competition in (TypeCompetition.ELIMINATOIRE, TypeCompetition.MIXTE)

    def __str__(self) -> str:
        return self.nom



SPORTS: list[Sport] = [
    Sport(
        "Basketball",
        TypeSport.COLLECTIF,
        CategorieSport.SPORT,
        TypeCompetition.POINTS,
        "#f9a825",
    ),
    Sport(
        "League of Legends",
        TypeSport.COLLECTIF,
        CategorieSport.ESPORT,
        TypeCompetition.POINTS,
        "#8e24aa",
    ),
    Sport(
        "Football Champions L.",
        TypeSport.COLLECTIF,
        CategorieSport.SPORT,
        TypeCompetition.MIXTE,
        "#1565c0",
    ),
    Sport(
        "Tennis",
        TypeSport.INDIVIDUEL,
        CategorieSport.SPORT,
        TypeCompetition.ELIMINATOIRE,
        "#2e7d32",
    ),
    Sport(
        "Échecs",
        TypeSport.INDIVIDUEL,
        CategorieSport.ESPORT,
        TypeCompetition.ELIMINATOIRE,
        "#4e342e",
    ),
    Sport(
        "Volleyball",
        TypeSport.COLLECTIF,
        CategorieSport.SPORT,
        TypeCompetition.MIXTE,
        "#d84315",
    ),
    Sport(
        "CS2",
        TypeSport.COLLECTIF,
        CategorieSport.ESPORT,
        TypeCompetition.MIXTE,
        "#546e7a",
    ),
    Sport(
        "StarCraft II",
        TypeSport.INDIVIDUEL,
        CategorieSport.ESPORT,
        TypeCompetition.ELIMINATOIRE,
        "#6a1b9a",
    ),
    Sport(
        "Badminton",
        TypeSport.INDIVIDUEL,
        CategorieSport.SPORT,
        TypeCompetition.ELIMINATOIRE,
        "#00838f",
    ),
]

# Accès rapide par nom
SPORTS_PAR_NOM: dict[str, Sport] = {s.nom: s for s in SPORTS}



def get_sport(nom: str) -> Sport | None:
    """Retourne le Sport correspondant au nom, ou None s'il n'existe pas."""
    return SPORTS_PAR_NOM.get(nom)



def filtrer_par_type(type_sport: TypeSport) -> list[Sport]:
    """Retourne les sports filtrés par type (individuel / collectif)."""
    return [s for s in SPORTS if s.type_sport == type_sport]


def filtrer_par_categorie(categorie: CategorieSport) -> list[Sport]:
    """Retourne les sports filtrés par catégorie (sport / e-sport)."""
    return [s for s in SPORTS if s.categorie == categorie]


def filtrer_par_competition(type_competition: TypeCompetition) -> list[Sport]:
    """Retourne les sports filtrés par type de compétition.

    Les sports MIXTE apparaissent dans les résultats de POINTS et de ELIMINATOIRE.
    """
    if type_competition == TypeCompetition.POINTS:
        return [s for s in SPORTS if s.est_en_points]
    if type_competition == TypeCompetition.ELIMINATOIRE:
        return [s for s in SPORTS if s.est_eliminatoire]
    return [s for s in SPORTS if s.type_competition == TypeCompetition.MIXTE]



def filtrer(
    type_sport: TypeSport | None = None,
    categorie: CategorieSport | None = None,
    type_competition: TypeCompetition | None = None,
) -> list[Sport]:
    """Retourne les sports vérifiant TOUS les critères fournis (logique ET).

    Les paramètres à None sont ignorés (pas de contrainte sur ce critère).

    Exemples
    --------
    # Sports collectifs e-sport
    filtrer(type_sport=TypeSport.COLLECTIF, categorie=CategorieSport.ESPORT)

    # Sports individuels avec phase éliminatoire
    filtrer(type_sport=TypeSport.INDIVIDUEL, type_competition=TypeCompetition.ELIMINATOIRE)

    # Tous les sports (aucun filtre)
    filtrer()
    """
    result = SPORTS
    if type_sport is not None:
        result = [s for s in result if s.type_sport == type_sport]
    if categorie is not None:
        result = [s for s in result if s.categorie == categorie]
    if type_competition is not None:
        if type_competition == TypeCompetition.POINTS:
            result = [s for s in result if s.est_en_points]
        elif type_competition == TypeCompetition.ELIMINATOIRE:
            result = [s for s in result if s.est_eliminatoire]
        else:
            result = [s for s in result if s.type_competition == TypeCompetition.MIXTE]
    return result

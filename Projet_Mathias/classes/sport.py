"""
Modèle de données pour les sports.

Définit :
- TypeSport      : enum distinguant sports individuels et collectifs
- CategorieSport : enum distinguant sport traditionnel et e-sport
- Sport          : classe représentant un sport avec son type, sa catégorie et sa couleur
- SPORTS         : registre de tous les sports disponibles dans l'application
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


@dataclass(frozen=True)
class Sport:
    """Représente un sport avec son nom, son type, sa catégorie et sa couleur d'interface."""

    nom: str
    type_sport: TypeSport
    categorie: CategorieSport
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

    def __str__(self) -> str:
        return self.nom


# ── Registre des sports disponibles ─────────────────────────────────────────

SPORTS: list[Sport] = [
    Sport("Basketball",            TypeSport.COLLECTIF,   CategorieSport.SPORT,  "#f9a825"),
    Sport("League of Legends",     TypeSport.COLLECTIF,   CategorieSport.ESPORT, "#8e24aa"),
    Sport("Football Champions L.", TypeSport.COLLECTIF,   CategorieSport.SPORT,  "#1565c0"),
    Sport("Tennis",                TypeSport.INDIVIDUEL,  CategorieSport.SPORT,  "#2e7d32"),
    Sport("Échecs",                TypeSport.INDIVIDUEL,  CategorieSport.ESPORT, "#4e342e"),
    Sport("Volleyball",            TypeSport.COLLECTIF,   CategorieSport.SPORT,  "#d84315"),
]

# Accès rapide par nom
SPORTS_PAR_NOM: dict[str, Sport] = {s.nom: s for s in SPORTS}


def get_sport(nom: str) -> Sport | None:
    """Retourne le Sport correspondant au nom, ou None s'il n'existe pas."""
    return SPORTS_PAR_NOM.get(nom)


def filtrer_par_type(type_sport: TypeSport) -> list[Sport]:
    """Retourne la liste des sports filtrés par type (individuel / collectif)."""
    return [s for s in SPORTS if s.type_sport == type_sport]


def filtrer_par_categorie(categorie: CategorieSport) -> list[Sport]:
    """Retourne la liste des sports filtrés par catégorie (sport / e-sport)."""
    return [s for s in SPORTS if s.categorie == categorie]

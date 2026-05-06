"""
Tests du module src/Model/sport.py.

Couvre : TypeSport, CategorieSport, TypeCompetition, Sport,
         SPORTS, SPORTS_PAR_NOM, get_sport, filtrer_par_type,
         filtrer_par_categorie, filtrer_par_competition, filtrer.
"""

import pytest

from src.Model.sport import (
    TypeSport,
    CategorieSport,
    TypeCompetition,
    Sport,
    SPORTS,
    SPORTS_PAR_NOM,
    get_sport,
    filtrer,
    filtrer_par_type,
    filtrer_par_categorie,
    filtrer_par_competition,
)


# ── Enums ─────────────────────────────────────────────────────────────────────


class TestEnumsStr:
    def test_type_sport_str(self):
        assert str(TypeSport.INDIVIDUEL) == "Individuel"
        assert str(TypeSport.COLLECTIF) == "Collectif"

    def test_categorie_sport_str(self):
        assert str(CategorieSport.SPORT) == "Sport"
        assert str(CategorieSport.ESPORT) == "E-sport"

    def test_type_competition_str(self):
        assert str(TypeCompetition.POINTS) == "Points"
        assert str(TypeCompetition.ELIMINATOIRE) == "Éliminatoire"
        assert str(TypeCompetition.MIXTE) == "Mixte"


# ── Sport (propriétés) ────────────────────────────────────────────────────────


@pytest.fixture
def sport_collectif_esport_mixte():
    return Sport("CS2", TypeSport.COLLECTIF, CategorieSport.ESPORT, TypeCompetition.MIXTE, "#546e7a")


@pytest.fixture
def sport_individuel_sport_eliminatoire():
    return Sport("Tennis", TypeSport.INDIVIDUEL, CategorieSport.SPORT, TypeCompetition.ELIMINATOIRE, "#2e7d32")


@pytest.fixture
def sport_collectif_sport_points():
    return Sport("Basketball", TypeSport.COLLECTIF, CategorieSport.SPORT, TypeCompetition.POINTS, "#f9a825")


class TestSportProperties:
    def test_est_collectif(self, sport_collectif_esport_mixte):
        assert sport_collectif_esport_mixte.est_collectif
        assert not sport_collectif_esport_mixte.est_individuel

    def test_est_individuel(self, sport_individuel_sport_eliminatoire):
        assert sport_individuel_sport_eliminatoire.est_individuel
        assert not sport_individuel_sport_eliminatoire.est_collectif

    def test_est_esport(self, sport_collectif_esport_mixte):
        assert sport_collectif_esport_mixte.est_esport
        assert not sport_collectif_esport_mixte.est_sport

    def test_est_sport(self, sport_individuel_sport_eliminatoire):
        assert sport_individuel_sport_eliminatoire.est_sport
        assert not sport_individuel_sport_eliminatoire.est_esport

    def test_est_en_points_pour_points(self, sport_collectif_sport_points):
        assert sport_collectif_sport_points.est_en_points

    def test_est_en_points_pour_mixte(self, sport_collectif_esport_mixte):
        assert sport_collectif_esport_mixte.est_en_points

    def test_est_en_points_false_pour_eliminatoire(self, sport_individuel_sport_eliminatoire):
        assert not sport_individuel_sport_eliminatoire.est_en_points

    def test_est_eliminatoire_pour_eliminatoire(self, sport_individuel_sport_eliminatoire):
        assert sport_individuel_sport_eliminatoire.est_eliminatoire

    def test_est_eliminatoire_pour_mixte(self, sport_collectif_esport_mixte):
        assert sport_collectif_esport_mixte.est_eliminatoire

    def test_est_eliminatoire_false_pour_points(self, sport_collectif_sport_points):
        assert not sport_collectif_sport_points.est_eliminatoire

    def test_str_retourne_le_nom(self, sport_collectif_sport_points):
        assert str(sport_collectif_sport_points) == "Basketball"


# ── Registre SPORTS ───────────────────────────────────────────────────────────


class TestRegistreSports:
    def test_sports_est_non_vide(self):
        assert len(SPORTS) > 0

    def test_sports_par_nom_contient_tous_les_sports(self):
        for sport in SPORTS:
            assert sport.nom in SPORTS_PAR_NOM

    def test_sports_par_nom_renvoie_le_bon_sport(self):
        assert SPORTS_PAR_NOM["Basketball"].type_sport == TypeSport.COLLECTIF

    def test_tous_les_sports_ont_une_couleur(self):
        for sport in SPORTS:
            assert sport.couleur


# ── get_sport ─────────────────────────────────────────────────────────────────


class TestGetSport:
    def test_retourne_le_sport_existant(self):
        s = get_sport("Tennis")
        assert s is not None
        assert s.nom == "Tennis"

    def test_retourne_none_pour_nom_inconnu(self):
        assert get_sport("SportInexistant") is None

    def test_sensible_a_la_casse(self):
        assert get_sport("tennis") is None


# ── filtrer_par_type ──────────────────────────────────────────────────────────


class TestFiltrerParType:
    def test_renvoie_uniquement_les_collectifs(self):
        result = filtrer_par_type(TypeSport.COLLECTIF)
        assert all(s.est_collectif for s in result)

    def test_renvoie_uniquement_les_individuels(self):
        result = filtrer_par_type(TypeSport.INDIVIDUEL)
        assert all(s.est_individuel for s in result)

    def test_collectifs_et_individuels_sont_complementaires(self):
        collectifs = filtrer_par_type(TypeSport.COLLECTIF)
        individuels = filtrer_par_type(TypeSport.INDIVIDUEL)
        assert len(collectifs) + len(individuels) == len(SPORTS)


# ── filtrer_par_categorie ─────────────────────────────────────────────────────


class TestFiltrerParCategorie:
    def test_renvoie_uniquement_les_sports_traditionnels(self):
        result = filtrer_par_categorie(CategorieSport.SPORT)
        assert all(s.est_sport for s in result)

    def test_renvoie_uniquement_les_esports(self):
        result = filtrer_par_categorie(CategorieSport.ESPORT)
        assert all(s.est_esport for s in result)

    def test_sport_et_esport_sont_complementaires(self):
        sports = filtrer_par_categorie(CategorieSport.SPORT)
        esports = filtrer_par_categorie(CategorieSport.ESPORT)
        assert len(sports) + len(esports) == len(SPORTS)


# ── filtrer_par_competition ───────────────────────────────────────────────────


class TestFiltrerParCompetition:
    def test_points_inclut_les_sports_mixte(self):
        result = filtrer_par_competition(TypeCompetition.POINTS)
        types = {s.type_competition for s in result}
        assert TypeCompetition.MIXTE in types

    def test_eliminatoire_inclut_les_sports_mixte(self):
        result = filtrer_par_competition(TypeCompetition.ELIMINATOIRE)
        types = {s.type_competition for s in result}
        assert TypeCompetition.MIXTE in types

    def test_mixte_retourne_uniquement_les_sports_mixte(self):
        result = filtrer_par_competition(TypeCompetition.MIXTE)
        assert all(s.type_competition == TypeCompetition.MIXTE for s in result)
        assert len(result) > 0


# ── filtrer (combiné) ─────────────────────────────────────────────────────────


class TestFiltrer:
    def test_sans_filtre_retourne_tous_les_sports(self):
        assert filtrer() == SPORTS

    def test_filtre_par_type_seul(self):
        result = filtrer(type_sport=TypeSport.INDIVIDUEL)
        assert all(s.est_individuel for s in result)

    def test_filtre_par_categorie_seule(self):
        result = filtrer(categorie=CategorieSport.ESPORT)
        assert all(s.est_esport for s in result)

    def test_filtre_combine_type_et_categorie(self):
        result = filtrer(type_sport=TypeSport.COLLECTIF, categorie=CategorieSport.ESPORT)
        assert all(s.est_collectif and s.est_esport for s in result)
        assert len(result) > 0

    def test_filtre_combine_sans_resultat(self):
        # Il n'existe pas de sport individuel e-sport à compétition par points purs
        result = filtrer(
            type_sport=TypeSport.INDIVIDUEL,
            categorie=CategorieSport.ESPORT,
            type_competition=TypeCompetition.POINTS,
        )
        assert result == []

    def test_mixte_apparait_dans_filtre_points(self):
        result = filtrer(type_competition=TypeCompetition.POINTS)
        noms = [s.nom for s in result]
        assert "Football Champions L." in noms  # TypeCompetition.MIXTE

    def test_mixte_apparait_dans_filtre_eliminatoire(self):
        result = filtrer(type_competition=TypeCompetition.ELIMINATOIRE)
        noms = [s.nom for s in result]
        assert "Football Champions L." in noms

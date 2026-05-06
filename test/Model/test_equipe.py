"""
Tests du module src/Model/equipe.py.

Couvre : Equipe (propriétés, relations, accès brut) et Equipes (filtres, relations).
Tous les tests utilisent des DataFrames in-memory — aucune lecture de fichier.
"""

import pandas as pd
import pytest

from src.Model.equipe import Equipe, Equipes
from src.Model.joueur import Joueurs


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def df_teams():
    return pd.DataFrame(
        {
            "id": [10, 20, 30],
            "full_name": ["Los Angeles Lakers", "Boston Celtics", "Golden State Warriors"],
            "abbreviation": ["LAL", "BOS", "GSW"],
            "city": ["Los Angeles", "Boston", "San Francisco"],
        }
    )


@pytest.fixture
def df_players():
    return pd.DataFrame(
        {
            "person_id": [1, 2, 3, 4],
            "full_name": ["LeBron James", "Anthony Davis", "Jayson Tatum", "Stephen Curry"],
            "team_id": [10, 10, 20, 30],
        }
    )


@pytest.fixture
def equipes(df_teams):
    return Equipes(
        df_teams,
        col_id="id",
        col_nom="full_name",
        col_abrev="abbreviation",
        col_ville="city",
    )


@pytest.fixture
def joueurs(df_players):
    return Joueurs(df_players, col_id="person_id", col_nom="full_name", col_equipe="team_id")


@pytest.fixture
def equipe_lakers(df_teams):
    return Equipe(
        df_teams.iloc[0],
        col_id="id",
        col_nom="full_name",
        col_abrev="abbreviation",
        col_ville="city",
    )


# ── Equipe : propriétés ───────────────────────────────────────────────────────


class TestEquipeProprietes:
    def test_id(self, equipe_lakers):
        assert equipe_lakers.id == 10

    def test_nom(self, equipe_lakers):
        assert equipe_lakers.nom == "Los Angeles Lakers"

    def test_abreviation(self, equipe_lakers):
        assert equipe_lakers.abreviation == "LAL"

    def test_ville(self, equipe_lakers):
        assert equipe_lakers.ville == "Los Angeles"

    def test_abreviation_none_quand_non_configuree(self, df_teams):
        e = Equipe(df_teams.iloc[0], col_id="id", col_nom="full_name")
        assert e.abreviation is None

    def test_ville_none_quand_non_configuree(self, df_teams):
        e = Equipe(df_teams.iloc[0], col_id="id", col_nom="full_name")
        assert e.ville is None


class TestEquipeRelations:
    def test_get_joueurs_retourne_les_joueurs_de_l_equipe(self, equipe_lakers, joueurs):
        roster = equipe_lakers.get_joueurs(joueurs)
        assert len(roster) == 2
        noms = [j.nom for j in roster]
        assert "LeBron James" in noms
        assert "Anthony Davis" in noms


class TestEquipeAccesBrut:
    def test_getitem(self, equipe_lakers):
        assert equipe_lakers["abbreviation"] == "LAL"

    def test_to_dict(self, equipe_lakers):
        d = equipe_lakers.to_dict()
        assert d["full_name"] == "Los Angeles Lakers"

    def test_repr_contient_le_nom(self, equipe_lakers):
        assert "Los Angeles Lakers" in repr(equipe_lakers)

    def test_repr_contient_abreviation_si_configuree(self, equipe_lakers):
        assert "LAL" in repr(equipe_lakers)


# ── Equipes : filtres ─────────────────────────────────────────────────────────


class TestEquipesFiltres:
    def test_get_par_id_existant(self, equipes):
        e = equipes.get_par_id(20)
        assert e is not None
        assert e.nom == "Boston Celtics"

    def test_get_par_id_inexistant_retourne_none(self, equipes):
        assert equipes.get_par_id(999) is None

    def test_get_par_nom_partiel(self, equipes):
        result = equipes.get_par_nom("celtics")
        assert len(result) == 1
        assert result[0].nom == "Boston Celtics"

    def test_get_par_nom_partiel_insensible_casse(self, equipes):
        result = equipes.get_par_nom("LAKERS")
        assert len(result) == 1

    def test_get_par_nom_exact(self, equipes):
        result = equipes.get_par_nom("Boston Celtics", exact=True)
        assert len(result) == 1

    def test_get_par_nom_exact_echoue_si_partiel(self, equipes):
        result = equipes.get_par_nom("Celtics", exact=True)
        assert len(result) == 0

    def test_filtrer_generique(self, equipes):
        result = equipes.filtrer(city="Boston")
        assert len(result) == 1


# ── Equipes : relations ───────────────────────────────────────────────────────


class TestEquipesRelations:
    def test_get_joueurs_retourne_tous_les_joueurs_des_equipes(self, equipes, joueurs):
        # Toutes les équipes → tous les joueurs
        all_players = equipes.get_joueurs(joueurs)
        assert len(all_players) == 4

    def test_get_joueurs_sur_sous_ensemble(self, equipes, joueurs):
        # Seulement les Lakers (id=10)
        lakers = equipes.get_par_id(10)
        # Utiliser Equipes avec un seul element
        equipes_lakers = equipes.get_par_nom("Lakers")
        roster = equipes_lakers.get_joueurs(joueurs)
        assert len(roster) == 2


# ── Equipes : interface Python ────────────────────────────────────────────────


class TestEquipesInterface:
    def test_len(self, equipes):
        assert len(equipes) == 3

    def test_iter_produit_des_equipe(self, equipes):
        for e in equipes:
            assert isinstance(e, Equipe)

    def test_getitem_int(self, equipes):
        e = equipes[0]
        assert e.nom == "Los Angeles Lakers"

    def test_to_dataframe_est_une_copie(self, equipes):
        df = equipes.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_repr_contient_le_nombre_d_equipes(self, equipes):
        assert "3" in repr(equipes)

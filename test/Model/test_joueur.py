"""
Tests du module src/Model/joueur.py.

Couvre : Joueur (propriétés, accès brut) et Joueurs (filtres, statistiques).
Tous les tests utilisent des DataFrames in-memory — aucune lecture de fichier.
"""

import pandas as pd
import pytest

from src.Model.joueur import Joueur, Joueurs


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def df_joueurs():
    return pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "full_name": ["LeBron James", "Stephen Curry", "Kevin Durant"],
            "birthdate": ["1984-12-30", "1988-03-14", "1988-09-27"],
            "team_id": [10, 20, 10],
            "height_cm": [206.0, 190.5, 208.3],
        }
    )


@pytest.fixture
def joueurs(df_joueurs):
    return Joueurs(
        df_joueurs,
        col_id="person_id",
        col_nom="full_name",
        col_naissance="birthdate",
        col_equipe="team_id",
        col_taille="height_cm",
    )


@pytest.fixture
def joueur_lebron(df_joueurs):
    return Joueur(
        df_joueurs.iloc[0],
        col_id="person_id",
        col_nom="full_name",
        col_naissance="birthdate",
        col_equipe="team_id",
        col_taille="height_cm",
    )


# ── Joueur : propriétés ───────────────────────────────────────────────────────


class TestJoueurProprietes:
    def test_id(self, joueur_lebron):
        assert joueur_lebron.id == 1

    def test_nom(self, joueur_lebron):
        assert joueur_lebron.nom == "LeBron James"

    def test_naissance_est_un_timestamp(self, joueur_lebron):
        assert joueur_lebron.naissance == pd.Timestamp("1984-12-30")

    def test_age_est_positif(self, joueur_lebron):
        assert joueur_lebron.age > 0

    def test_equipe(self, joueur_lebron):
        assert joueur_lebron.equipe == 10

    def test_taille(self, joueur_lebron):
        assert joueur_lebron.taille == 206.0

    def test_naissance_none_quand_non_configure(self, df_joueurs):
        j = Joueur(df_joueurs.iloc[0], col_id="person_id", col_nom="full_name")
        assert j.naissance is None

    def test_age_none_quand_naissance_non_configuree(self, df_joueurs):
        j = Joueur(df_joueurs.iloc[0], col_id="person_id", col_nom="full_name")
        assert j.age is None

    def test_equipe_none_quand_non_configuree(self, df_joueurs):
        j = Joueur(df_joueurs.iloc[0], col_id="person_id", col_nom="full_name")
        assert j.equipe is None

    def test_taille_none_quand_non_configuree(self, df_joueurs):
        j = Joueur(df_joueurs.iloc[0], col_id="person_id", col_nom="full_name")
        assert j.taille is None


class TestJoueurAccesBrut:
    def test_getitem_retourne_la_valeur_brute(self, joueur_lebron):
        assert joueur_lebron["height_cm"] == 206.0

    def test_to_dict_retourne_un_dict(self, joueur_lebron):
        d = joueur_lebron.to_dict()
        assert isinstance(d, dict)
        assert d["full_name"] == "LeBron James"

    def test_repr_contient_le_nom(self, joueur_lebron):
        assert "LeBron James" in repr(joueur_lebron)


# ── Joueurs : filtres ─────────────────────────────────────────────────────────


class TestJoueursFiltres:
    def test_get_par_id_existant(self, joueurs):
        j = joueurs.get_par_id(2)
        assert j is not None
        assert j.nom == "Stephen Curry"

    def test_get_par_id_inexistant_retourne_none(self, joueurs):
        assert joueurs.get_par_id(999) is None

    def test_get_par_nom_partiel(self, joueurs):
        result = joueurs.get_par_nom("curry")
        assert len(result) == 1
        assert result[0].nom == "Stephen Curry"

    def test_get_par_nom_partiel_insensible_casse(self, joueurs):
        result = joueurs.get_par_nom("LEBRON")
        assert len(result) == 1

    def test_get_par_nom_exact(self, joueurs):
        result = joueurs.get_par_nom("Stephen Curry", exact=True)
        assert len(result) == 1

    def test_get_par_nom_exact_retourne_vide_si_partiel(self, joueurs):
        result = joueurs.get_par_nom("Curry", exact=True)
        assert len(result) == 0

    def test_get_par_equipe(self, joueurs):
        result = joueurs.get_par_equipe(10)
        assert len(result) == 2

    def test_get_par_equipe_sans_col_leve_erreur(self, df_joueurs):
        j = Joueurs(df_joueurs, col_id="person_id", col_nom="full_name")
        with pytest.raises(ValueError):
            j.get_par_equipe(10)

    def test_filtrer_generique(self, joueurs):
        result = joueurs.filtrer(team_id=20)
        assert len(result) == 1
        assert result[0].nom == "Stephen Curry"


# ── Joueurs : statistiques ────────────────────────────────────────────────────


class TestJoueursStats:
    def test_ages_retourne_une_serie(self, joueurs):
        ages = joueurs.ages()
        assert isinstance(ages, pd.Series)
        assert len(ages) == 3

    def test_ages_sans_col_naissance_leve_erreur(self, df_joueurs):
        j = Joueurs(df_joueurs, col_id="person_id", col_nom="full_name")
        with pytest.raises(ValueError):
            j.ages()

    def test_age_moyen_est_positif(self, joueurs):
        assert joueurs.age_moyen() > 0

    def test_taille_moyenne(self, joueurs):
        esperee = round((206.0 + 190.5 + 208.3) / 3, 1)
        assert joueurs.taille_moyenne() == esperee

    def test_taille_moyenne_sans_col_leve_erreur(self, df_joueurs):
        j = Joueurs(df_joueurs, col_id="person_id", col_nom="full_name")
        with pytest.raises(ValueError):
            j.taille_moyenne()

    def test_resume_contient_les_colonnes_configurees(self, joueurs):
        df = joueurs.resume()
        assert "person_id" in df.columns
        assert "full_name" in df.columns
        assert "height_cm" in df.columns


# ── Joueurs : interface Python ────────────────────────────────────────────────


class TestJoueursInterface:
    def test_len(self, joueurs):
        assert len(joueurs) == 3

    def test_iter_produit_des_joueur(self, joueurs):
        for j in joueurs:
            assert isinstance(j, Joueur)

    def test_getitem_int(self, joueurs):
        j = joueurs[0]
        assert j.nom == "LeBron James"

    def test_to_dataframe_est_une_copie(self, joueurs):
        df = joueurs.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_repr_contient_le_nombre_de_joueurs(self, joueurs):
        assert "3" in repr(joueurs)

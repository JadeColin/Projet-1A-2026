
import pandas as pd
import pytest

from src.Model.stats_sport import StatsSport




class SportIndividuelMinimal(StatsSport):
    """Implémentation concrète sans roster (sport individuel)."""

    def classement(self, n=10):
        return pd.DataFrame({"joueur": ["A", "B"], "Victoires": [5, 3]})

    def nb_joueurs(self):
        return 50

    def nb_matchs(self):
        return 120

    def stats_entite(self, nom):
        return pd.DataFrame({"stat": [nom]})


class SportCollectifMinimal(StatsSport):
    """Implémentation concrète avec roster (sport collectif)."""

    def classement(self, n=10):
        return pd.DataFrame({"equipe": ["TeamA", "TeamB"], "Victoires": [8, 4]})

    def nb_joueurs(self):
        return 100

    def nb_matchs(self):
        return 45

    def stats_entite(self, nom):
        return pd.DataFrame({"stat": [nom]})

    def roster(self, nom_equipe):
        return pd.DataFrame({"joueur": ["Joueur1", "Joueur2"]})




class TestStatsSportAbstraite:
    def test_instantiation_directe_impossible(self):
        with pytest.raises(TypeError):
            StatsSport()

    def test_sous_classe_sans_toutes_les_abstraites_impossible(self):
        class Incomplete(StatsSport):
            def classement(self, n=10):
                return pd.DataFrame()
            # nb_joueurs, nb_matchs, stats_entite manquants

        with pytest.raises(TypeError):
            Incomplete()




class TestResume:
    def test_resume_retourne_les_bonnes_cles(self):
        sport = SportIndividuelMinimal()
        r = sport.resume()
        assert set(r.keys()) == {"joueurs", "matchs"}

    def test_resume_valeurs_correctes(self):
        sport = SportIndividuelMinimal()
        r = sport.resume()
        assert r["joueurs"] == 50
        assert r["matchs"] == 120




class TestEstCollectif:
    def test_sport_sans_roster_n_est_pas_collectif(self):
        sport = SportIndividuelMinimal()
        assert not sport.est_collectif()

    def test_sport_avec_roster_est_collectif(self):
        sport = SportCollectifMinimal()
        assert sport.est_collectif()

    def test_roster_par_defaut_leve_not_implemented(self):
        sport = SportIndividuelMinimal()
        with pytest.raises(NotImplementedError):
            sport.roster("quelconque")

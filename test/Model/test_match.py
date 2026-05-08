
import pandas as pd
import pytest

from src.Model.match import Match, Matchs




@pytest.fixture
def df_matchs():
    """5 matchs de volleyball avec gagnant explicite et score."""
    return pd.DataFrame(
        {
            "match_id": [1, 2, 3, 4, 5],
            "date": ["2024-07-27", "2024-07-28", "2024-07-29", "2024-07-30", "2024-07-31"],
            "country_code_1": ["FRA", "BRA", "USA", "FRA", "ITA"],
            "country_code_2": ["ITA", "USA", "POL", "BRA", "POL"],
            "set_country_1":  [3, 1, 3, 3, 2],
            "set_country_2":  [1, 3, 1, 2, 3],
            "winner":         ["FRA", "USA", "USA", "FRA", "POL"],
        }
    )


@pytest.fixture
def matchs_avec_gagnant(df_matchs):
    return Matchs(
        df_matchs,
        col_id="match_id",
        col_date="date",
        col_equipe1="country_code_1",
        col_equipe2="country_code_2",
        col_score1="set_country_1",
        col_score2="set_country_2",
        col_gagnant="winner",
    )


@pytest.fixture
def matchs_sans_col_gagnant(df_matchs):
    """Matchs sans col_gagnant : le gagnant est déduit des scores."""
    return Matchs(
        df_matchs,
        col_id="match_id",
        col_date="date",
        col_equipe1="country_code_1",
        col_equipe2="country_code_2",
        col_score1="set_country_1",
        col_score2="set_country_2",
    )


@pytest.fixture
def match_fra_vs_ita(df_matchs):
    return Match(
        df_matchs.iloc[0],
        col_id="match_id",
        col_date="date",
        col_equipe1="country_code_1",
        col_equipe2="country_code_2",
        col_score1="set_country_1",
        col_score2="set_country_2",
        col_gagnant="winner",
    )




class TestMatchProprietes:
    def test_id(self, match_fra_vs_ita):
        assert match_fra_vs_ita.id == 1

    def test_date_est_un_timestamp(self, match_fra_vs_ita):
        assert match_fra_vs_ita.date == pd.Timestamp("2024-07-27")

    def test_equipe_1(self, match_fra_vs_ita):
        assert match_fra_vs_ita.equipe_1 == "FRA"

    def test_equipe_2(self, match_fra_vs_ita):
        assert match_fra_vs_ita.equipe_2 == "ITA"

    def test_score_1(self, match_fra_vs_ita):
        assert match_fra_vs_ita.score_1 == 3

    def test_score_2(self, match_fra_vs_ita):
        assert match_fra_vs_ita.score_2 == 1

    def test_id_none_quand_non_configure(self, df_matchs):
        m = Match(df_matchs.iloc[0])
        assert m.id is None

    def test_date_none_quand_non_configuree(self, df_matchs):
        m = Match(df_matchs.iloc[0])
        assert m.date is None

    def test_score_none_quand_non_configure(self, df_matchs):
        m = Match(df_matchs.iloc[0])
        assert m.score_1 is None
        assert m.score_2 is None


class TestMatchGagnant:
    def test_gagnant_depuis_col_gagnant(self, match_fra_vs_ita):
        assert match_fra_vs_ita.gagnant == "FRA"

    def test_gagnant_deduit_depuis_scores_equipe1(self, df_matchs):
        # FRA 3-1 ITA → FRA gagne
        m = Match(
            df_matchs.iloc[0],
            col_equipe1="country_code_1",
            col_equipe2="country_code_2",
            col_score1="set_country_1",
            col_score2="set_country_2",
        )
        assert m.gagnant == "FRA"

    def test_gagnant_deduit_depuis_scores_equipe2(self, df_matchs):
        # BRA 1-3 USA → USA gagne
        m = Match(
            df_matchs.iloc[1],
            col_equipe1="country_code_1",
            col_equipe2="country_code_2",
            col_score1="set_country_1",
            col_score2="set_country_2",
        )
        assert m.gagnant == "USA"

    def test_gagnant_none_sans_configuration(self, df_matchs):
        m = Match(df_matchs.iloc[0])
        assert m.gagnant is None


class TestMatchAccesBrut:
    def test_getitem(self, match_fra_vs_ita):
        assert match_fra_vs_ita["winner"] == "FRA"

    def test_to_dict(self, match_fra_vs_ita):
        d = match_fra_vs_ita.to_dict()
        assert d["country_code_1"] == "FRA"

    def test_repr_contient_les_equipes(self, match_fra_vs_ita):
        r = repr(match_fra_vs_ita)
        assert "FRA" in r
        assert "ITA" in r



class TestMatchsFiltres:
    def test_get_par_equipe_retourne_les_matchs_de_l_equipe(self, matchs_avec_gagnant):
        fra_matchs = matchs_avec_gagnant.get_par_equipe("FRA")
        assert len(fra_matchs) == 2

    def test_get_par_equipe_inclut_domicile_et_exterieur(self, matchs_avec_gagnant):
        usa_matchs = matchs_avec_gagnant.get_par_equipe("USA")
        assert len(usa_matchs) == 2

    def test_get_par_equipe_sans_colonnes_leve_erreur(self, df_matchs):
        m = Matchs(df_matchs)
        with pytest.raises(ValueError):
            m.get_par_equipe("FRA")

    def test_get_par_date_filtre_correctement(self, matchs_avec_gagnant):
        result = matchs_avec_gagnant.get_par_date("2024-07-27", "2024-07-28")
        assert len(result) == 2

    def test_get_par_date_sans_col_date_leve_erreur(self, df_matchs):
        m = Matchs(df_matchs)
        with pytest.raises(ValueError):
            m.get_par_date("2024-01-01")

    def test_filtrer_generique(self, matchs_avec_gagnant):
        result = matchs_avec_gagnant.filtrer(winner="USA")
        assert len(result) == 2



class TestMatchsStats:
    def test_victoires_avec_col_gagnant(self, matchs_avec_gagnant):
        assert matchs_avec_gagnant.victoires("USA") == 2
        assert matchs_avec_gagnant.victoires("FRA") == 2

    def test_victoires_deduites_depuis_scores(self, matchs_sans_col_gagnant):
        assert matchs_sans_col_gagnant.victoires("USA") == 2

    def test_defaites(self, matchs_avec_gagnant):
        fra_matchs = matchs_avec_gagnant.get_par_equipe("FRA")
        assert fra_matchs.defaites("FRA") == 0

    def test_nuls_quand_aucun_match_nul(self, matchs_avec_gagnant):
        assert matchs_avec_gagnant.nuls() == 0

    def test_nuls_sans_score_retourne_zero(self, df_matchs):
        m = Matchs(df_matchs, col_equipe1="country_code_1", col_equipe2="country_code_2")
        assert m.nuls() == 0

    def test_bilan_retourne_les_bonnes_cles(self, matchs_avec_gagnant):
        bilan = matchs_avec_gagnant.bilan("FRA")
        assert set(bilan.keys()) == {"victoires", "defaites", "nuls", "joues"}

    def test_bilan_coherent(self, matchs_avec_gagnant):
        bilan = matchs_avec_gagnant.bilan("FRA")
        assert bilan["joues"] == bilan["victoires"] + bilan["defaites"] + bilan["nuls"]

    def test_score_moyen(self, matchs_avec_gagnant):
        sm = matchs_avec_gagnant.score_moyen()
        assert "equipe1" in sm
        assert "equipe2" in sm
        assert sm["equipe1"] > 0

    def test_score_moyen_sans_scores_leve_erreur(self, df_matchs):
        m = Matchs(df_matchs, col_equipe1="country_code_1", col_equipe2="country_code_2")
        with pytest.raises(ValueError):
            m.score_moyen()

    def test_classement_trie_par_victoires_decroissantes(self, matchs_avec_gagnant):
        df = matchs_avec_gagnant.classement()
        assert list(df.columns[:2]) == ["equipe", "victoires"]
        victoires = df["victoires"].tolist()
        assert victoires == sorted(victoires, reverse=True)

    def test_classement_contient_toutes_les_equipes(self, matchs_avec_gagnant):
        df = matchs_avec_gagnant.classement()
        equipes = set(df["equipe"].tolist())
        assert {"FRA", "USA", "BRA", "ITA", "POL"}.issubset(equipes)



class TestMatchsInterface:
    def test_len(self, matchs_avec_gagnant):
        assert len(matchs_avec_gagnant) == 5

    def test_iter_produit_des_match(self, matchs_avec_gagnant):
        for m in matchs_avec_gagnant:
            assert isinstance(m, Match)

    def test_getitem_int(self, matchs_avec_gagnant):
        m = matchs_avec_gagnant[0]
        assert m.equipe_1 == "FRA"

    def test_to_dataframe_est_une_copie(self, matchs_avec_gagnant):
        df = matchs_avec_gagnant.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_repr_contient_le_nombre_de_matchs(self, matchs_avec_gagnant):
        assert "5" in repr(matchs_avec_gagnant)

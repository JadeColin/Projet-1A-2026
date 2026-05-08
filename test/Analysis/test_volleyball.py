
import pytest
import pandas as pd

import src.Analysis.volleyball as vb_mod



@pytest.fixture
def mock_countries():
    return pd.DataFrame([
        {"code": "FRA", "country": "France"},
        {"code": "BRA", "country": "Brazil"},
        {"code": "USA", "country": "United States"},
        {"code": "ITA", "country": "Italy"},
    ])


@pytest.fixture
def mock_players_men():
    return pd.DataFrame([
        {"name": "Earvin Ngapeth", "country_code": "FRA", "height": 196,
         "birth_date": "1991-02-12", "birth_place": "Cannes", "nickname": "Magic"},
        {"name": "Natan Leal", "country_code": "BRA", "height": 201,
         "birth_date": "1998-08-04", "birth_place": "São Paulo", "nickname": None},
        {"name": "Matt Anderson", "country_code": "USA", "height": 202,
         "birth_date": "1987-04-15", "birth_place": "Geneva", "nickname": None},
    ])


@pytest.fixture
def mock_players_women():
    return pd.DataFrame([
        {"name": "Egonu Paola", "country_code": "ITA", "height": 193,
         "birth_date": "1998-12-18", "birth_place": "Cittadella", "nickname": "Paolona"},
        {"name": "Destinee Hooker", "country_code": "USA", "height": 193,
         "birth_date": "1987-10-08", "birth_place": "Lubbock", "nickname": None},
    ])


@pytest.fixture
def mock_coaches_men():
    return pd.DataFrame([
        {"name": "Andrea Giani", "country_code": "FRA", "birth_date": "1969-05-14"},
    ])


@pytest.fixture
def mock_coaches_women():
    return pd.DataFrame(columns=["name", "country_code", "birth_date"])


@pytest.fixture
def mock_matches_men():
    return pd.DataFrame([
        {"date": "2024-07-27", "country_code_1": "FRA", "country_code_2": "BRA",
         "set_country_1": 3, "set_country_2": 0, "winner": "FRA",
         "stage": "Preliminary Round Pool A"},
        {"date": "2024-07-29", "country_code_1": "FRA", "country_code_2": "USA",
         "set_country_1": 1, "set_country_2": 3, "winner": "USA",
         "stage": "Preliminary Round Pool A"},
        {"date": "2024-07-31", "country_code_1": "BRA", "country_code_2": "USA",
         "set_country_1": 3, "set_country_2": 2, "winner": "BRA",
         "stage": "Preliminary Round Pool A"},
    ])


@pytest.fixture
def mock_matches_women():
    return pd.DataFrame([
        {"date": "2024-07-28", "country_code_1": "ITA", "country_code_2": "USA",
         "set_country_1": 3, "set_country_2": 1, "winner": "ITA",
         "stage": "Preliminary Round Pool B"},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(
    monkeypatch,
    mock_countries, mock_players_men, mock_players_women,
    mock_coaches_men, mock_coaches_women,
    mock_matches_men, mock_matches_women,
):
    monkeypatch.setattr(vb_mod, "_loader", object())
    monkeypatch.setattr(vb_mod, "_countries", mock_countries)
    monkeypatch.setattr(vb_mod, "_players_men", mock_players_men)
    monkeypatch.setattr(vb_mod, "_players_women", mock_players_women)
    monkeypatch.setattr(vb_mod, "_coaches_men", mock_coaches_men)
    monkeypatch.setattr(vb_mod, "_coaches_women", mock_coaches_women)
    monkeypatch.setattr(vb_mod, "_matches_men", mock_matches_men)
    monkeypatch.setattr(vb_mod, "_matches_women", mock_matches_women)



class TestClassement:
    def test_returns_dataframe(self):
        result = vb_mod.classement(genre="hommes")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = vb_mod.classement(genre="hommes")
        for col in ("Pays", "Victoires", "Défaites", "Matchs joués", "Sets gagnés"):
            assert col in result.columns

    def test_sorted_by_victoires_desc(self):
        result = vb_mod.classement(genre="hommes")
        assert result["Victoires"].is_monotonic_decreasing

    def test_country_names_resolved(self):
        result = vb_mod.classement(genre="hommes")
        pays = result["Pays"].tolist()
        assert "France" in pays or "FRA" in pays  # resolved or fallback to code

    def test_index_starts_at_1(self):
        result = vb_mod.classement(genre="hommes")
        assert result.index[0] == 1

    def test_women_genre_alias(self):
        result_f = vb_mod.classement(genre="femmes")
        result_w = vb_mod.classement(genre="women")
        assert len(result_f) == len(result_w)



class TestBilanEquipe:
    def test_returns_dataframe(self):
        result = vb_mod.bilan_equipe("FRA", genre="hommes")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = vb_mod.bilan_equipe("FRA", genre="hommes")
        for col in ("Équipe", "Matchs joués", "Victoires", "Défaites", "Sets gagnés", "Sets perdus"):
            assert col in result.columns

    def test_fra_wins_one_loses_one(self):
        result = vb_mod.bilan_equipe("FRA", genre="hommes")
        assert result.iloc[0]["Victoires"] == 1
        assert result.iloc[0]["Défaites"] == 1

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucune équipe"):
            vb_mod.bilan_equipe("XXX", genre="hommes")

    def test_case_insensitive_code(self):
        result = vb_mod.bilan_equipe("fra", genre="hommes")
        assert result.iloc[0]["Matchs joués"] == 2



class TestRosterEquipe:
    def test_returns_dataframe(self):
        result = vb_mod.roster_equipe("FRA", genre="hommes")
        assert isinstance(result, pd.DataFrame)

    def test_has_role_column(self):
        result = vb_mod.roster_equipe("FRA", genre="hommes")
        assert "Rôle" in result.columns

    def test_coach_appears_first(self):
        result = vb_mod.roster_equipe("FRA", genre="hommes")
        assert result.iloc[0]["Rôle"] == "Coach"

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucun membre"):
            vb_mod.roster_equipe("XXX", genre="hommes")

    def test_index_starts_at_1(self):
        result = vb_mod.roster_equipe("FRA", genre="hommes")
        assert result.index[0] == 1



class TestListeJoueurs:
    def test_returns_all_men_players(self):
        result = vb_mod.liste_joueurs(genre="hommes")
        assert len(result) == 3

    def test_returns_all_women_players(self):
        result = vb_mod.liste_joueurs(genre="femmes")
        assert len(result) == 2

    def test_filter_by_country_code(self):
        result = vb_mod.liste_joueurs(genre="hommes", equipe="FRA")
        assert len(result) == 1

    def test_sorted_by_name(self):
        result = vb_mod.liste_joueurs(genre="hommes")
        names = list(result["Nom complet"])
        assert names == sorted(names)

    def test_index_starts_at_1(self):
        result = vb_mod.liste_joueurs(genre="hommes")
        assert result.index[0] == 1


class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = vb_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = vb_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_contains_hommes_and_femmes(self):
        result = vb_mod.get_agenda_data()
        sports = result["Sport"].unique()
        assert "Volleyball Hommes" in sports
        assert "Volleyball Femmes" in sports

    def test_row_count(self):
        result = vb_mod.get_agenda_data()
        # 3 men + 1 women = 4 total
        assert len(result) == 4

    def test_scores_are_strings(self):
        result = vb_mod.get_agenda_data()
        assert result["Score 1"].dtype == object
        assert result["Score 2"].dtype == object


import pytest
import pandas as pd

import src.Analysis.football_cl as fcl_mod



@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"player_name": "Erling Haaland", "club": "Manchester City", "position": "Forward",
         "goals": 12, "assists": 5, "total_attempts": 40, "on_target": 25,
         "dribbles": 8, "tackles_won": 2, "yellow": 1, "red": 0,
         "pass_completed": 200, "pass_attempted": 240, "minutes_played": 900,
         "match_played_field": 10, "match_played": 10,
         "saved": 0, "conceded": 0, "cleansheets": 0, "saved_penalties": 0},
        {"player_name": "Kylian Mbappé", "club": "Paris Saint-Germain", "position": "Forward",
         "goals": 10, "assists": 7, "total_attempts": 35, "on_target": 20,
         "dribbles": 15, "tackles_won": 1, "yellow": 2, "red": 0,
         "pass_completed": 180, "pass_attempted": 210, "minutes_played": 850,
         "match_played_field": 9, "match_played": 9,
         "saved": 0, "conceded": 0, "cleansheets": 0, "saved_penalties": 0},
        {"player_name": "Toni Kroos", "club": "Real Madrid", "position": "Midfielder",
         "goals": 2, "assists": 10, "total_attempts": 10, "on_target": 5,
         "dribbles": 3, "tackles_won": 8, "yellow": 1, "red": 0,
         "pass_completed": 500, "pass_attempted": 530, "minutes_played": 1000,
         "match_played_field": 11, "match_played": 11,
         "saved": 0, "conceded": 0, "cleansheets": 0, "saved_penalties": 0},
        {"player_name": "Alisson Becker", "club": "Liverpool", "position": "Goalkeeper",
         "goals": 0, "assists": 0, "total_attempts": 0, "on_target": 0,
         "dribbles": 0, "tackles_won": 0, "yellow": 0, "red": 0,
         "pass_completed": 100, "pass_attempted": 110, "minutes_played": 900,
         "match_played_field": 10, "match_played": 10,
         "saved": 30, "conceded": 8, "cleansheets": 6, "saved_penalties": 2},
        {"player_name": "Marc-André ter Stegen", "club": "Barcelona", "position": "Goalkeeper",
         "goals": 0, "assists": 0, "total_attempts": 0, "on_target": 0,
         "dribbles": 0, "tackles_won": 0, "yellow": 1, "red": 0,
         "pass_completed": 90, "pass_attempted": 100, "minutes_played": 810,
         "match_played_field": 9, "match_played": 9,
         "saved": 25, "conceded": 10, "cleansheets": 4, "saved_penalties": 1},
    ])


@pytest.fixture
def mock_teams():
    return pd.DataFrame([
        {"full_name": "Manchester City", "short_name": "MCI", "year_founded": 1880,
         "country": "England", "league": "Premier League", "city": "Manchester"},
        {"full_name": "Real Madrid", "short_name": "RMA", "year_founded": 1902,
         "country": "Spain", "league": "La Liga", "city": "Madrid"},
        {"full_name": "Paris Saint-Germain", "short_name": "PSG", "year_founded": 1970,
         "country": "France", "league": "Ligue 1", "city": "Paris"},
        {"full_name": "Liverpool", "short_name": "LIV", "year_founded": 1892,
         "country": "England", "league": "Premier League", "city": "Liverpool"},
        {"full_name": "Barcelona", "short_name": "BAR", "year_founded": 1899,
         "country": "Spain", "league": "La Liga", "city": "Barcelona"},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {"date": "2023-09-19", "phase": "group", "round": None, "matchday": 1,
         "group": "A", "team_home": "Manchester City", "team_away": "Real Madrid",
         "score_team_home": 3, "score_team_away": 3},
        {"date": "2023-10-03", "phase": "group", "round": None, "matchday": 2,
         "group": "A", "team_home": "Real Madrid", "team_away": "Barcelona",
         "score_team_home": 1, "score_team_away": 0},
        {"date": "2023-10-04", "phase": "group", "round": None, "matchday": 2,
         "group": "B", "team_home": "Paris Saint-Germain", "team_away": "Liverpool",
         "score_team_home": 2, "score_team_away": 1},
        {"date": "2024-02-14", "phase": "knockout", "round": "RO16", "matchday": None,
         "group": None, "team_home": "Manchester City", "team_away": "Barcelona",
         "score_team_home": 3, "score_team_away": 1},
        {"date": "2024-03-12", "phase": "knockout", "round": "RO8", "matchday": None,
         "group": None, "team_home": "Real Madrid", "team_away": "Manchester City",
         "score_team_home": 1, "score_team_away": 0},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_teams, mock_matches):
    monkeypatch.setattr(fcl_mod, "_loader", object())
    monkeypatch.setattr(fcl_mod, "_players", mock_players)
    monkeypatch.setattr(fcl_mod, "_teams", mock_teams)
    monkeypatch.setattr(fcl_mod, "_matches", mock_matches)



class TestMeilleursButeurs:
    def test_returns_dataframe(self):
        result = fcl_mod.meilleurs_buteurs()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = fcl_mod.meilleurs_buteurs()
        for col in ("Joueur", "Club", "Poste", "Buts", "Tirs tentés", "Tirs cadrés"):
            assert col in result.columns

    def test_sorted_by_buts_desc(self):
        result = fcl_mod.meilleurs_buteurs()
        buts = result["Buts"].tolist()
        assert buts == sorted(buts, reverse=True)

    def test_n_limits_results(self):
        result = fcl_mod.meilleurs_buteurs(n=2)
        assert len(result) == 2

    def test_haaland_is_top_scorer(self):
        result = fcl_mod.meilleurs_buteurs(n=1)
        assert result.iloc[0]["Joueur"] == "Erling Haaland"

    def test_index_starts_at_1(self):
        result = fcl_mod.meilleurs_buteurs()
        assert result.index[0] == 1



class TestMeilleursPasseurs:
    def test_returns_dataframe(self):
        result = fcl_mod.meilleurs_passeurs()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = fcl_mod.meilleurs_passeurs()
        for col in ("Joueur", "Club", "Poste", "Passes déc."):
            assert col in result.columns

    def test_sorted_by_passes_desc(self):
        result = fcl_mod.meilleurs_passeurs()
        passes = result["Passes déc."].tolist()
        assert passes == sorted(passes, reverse=True)

    def test_n_limits_results(self):
        result = fcl_mod.meilleurs_passeurs(n=1)
        assert len(result) == 1

    def test_kroos_is_top_assist(self):
        result = fcl_mod.meilleurs_passeurs(n=1)
        assert result.iloc[0]["Joueur"] == "Toni Kroos"



class TestStatsEquipe:
    def test_returns_dataframe(self):
        result = fcl_mod.stats_equipe("Manchester City")
        assert isinstance(result, pd.DataFrame)

    def test_team_label_in_result(self):
        result = fcl_mod.stats_equipe("Manchester City")
        assert result.iloc[0]["Équipe"] == "Manchester City"

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucune équipe"):
            fcl_mod.stats_equipe("Unknown FC")

    def test_case_insensitive(self):
        result = fcl_mod.stats_equipe("manchester")
        assert result.iloc[0]["Équipe"] == "Manchester City"

    def test_buts_column_present(self):
        result = fcl_mod.stats_equipe("Liverpool")
        assert "Buts" in result.columns



class TestStatsJoueur:
    def test_returns_dataframe(self):
        result = fcl_mod.stats_joueur("Haaland")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = fcl_mod.stats_joueur("Haaland")
        for col in ("Joueur", "Club", "Buts", "Passes déc."):
            assert col in result.columns

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucun joueur"):
            fcl_mod.stats_joueur("Unknown Player")

    def test_case_insensitive(self):
        result = fcl_mod.stats_joueur("haaland")
        assert result.iloc[0]["Joueur"] == "Erling Haaland"



class TestStatsGardiens:
    def test_returns_dataframe(self):
        result = fcl_mod.stats_gardiens()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = fcl_mod.stats_gardiens()
        for col in ("Gardien", "Club", "Arrêts"):
            assert col in result.columns

    def test_only_goalkeepers(self):
        result = fcl_mod.stats_gardiens()
        # Should only contain Alisson and ter Stegen
        assert len(result) == 2

    def test_sorted_by_arrets_desc(self):
        result = fcl_mod.stats_gardiens()
        arrets = result["Arrêts"].tolist()
        assert arrets == sorted(arrets, reverse=True)

    def test_n_limits_results(self):
        result = fcl_mod.stats_gardiens(n=1)
        assert len(result) == 1

    def test_index_starts_at_1(self):
        result = fcl_mod.stats_gardiens()
        assert result.index[0] == 1



class TestListeJoueurs:
    def test_returns_all_players(self):
        result = fcl_mod.liste_joueurs()
        assert len(result) == 5

    def test_filter_by_club(self):
        result = fcl_mod.liste_joueurs(club="Liverpool")
        assert len(result) == 1
        assert result.iloc[0]["Joueur"] == "Alisson Becker"

    def test_sorted_by_name(self):
        result = fcl_mod.liste_joueurs()
        names = list(result["Joueur"])
        assert names == sorted(names)

    def test_index_starts_at_1(self):
        result = fcl_mod.liste_joueurs()
        assert result.index[0] == 1



class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = fcl_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = fcl_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_sport_label(self):
        result = fcl_mod.get_agenda_data()
        assert all(result["Sport"] == "Football CL")

    def test_row_count(self):
        result = fcl_mod.get_agenda_data()
        assert len(result) == 5

    def test_scores_are_strings(self):
        result = fcl_mod.get_agenda_data()
        assert result["Score 1"].dtype == object
        assert result["Score 2"].dtype == object

"""
Tests for src/Analysis/basketball.py

Module-level globals are monkeypatched with in-memory DataFrames.
"""

import pytest
import pandas as pd

import src.Analysis.basketball as bball_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_teams():
    return pd.DataFrame([
        {"id": 1, "full_name": "Los Angeles Lakers", "abbreviation": "LAL", "nickname": "Lakers"},
        {"id": 2, "full_name": "Boston Celtics", "abbreviation": "BOS", "nickname": "Celtics"},
        {"id": 3, "full_name": "Golden State Warriors", "abbreviation": "GSW", "nickname": "Warriors"},
    ])


@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"full_name": "LeBron James", "first_name": "LeBron", "last_name": "James",
         "team_id": 1, "country": "USA", "birthdate": "1984-12-30",
         "height": "6-9", "weight": 250, "jersey": 23, "position": "SF"},
        {"full_name": "Stephen Curry", "first_name": "Stephen", "last_name": "Curry",
         "team_id": 2, "country": "USA", "birthdate": "1988-03-14",
         "height": "6-2", "weight": 185, "jersey": 30, "position": "PG"},
        {"full_name": "Klay Thompson", "first_name": "Klay", "last_name": "Thompson",
         "team_id": 3, "country": "USA", "birthdate": "1990-02-08",
         "height": "6-6", "weight": 215, "jersey": 11, "position": "SG"},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {"team_id_home": 1, "team_id_away": 2, "pts_home": 110, "pts_away": 105,
         "blk_home": 5, "blk_away": 3, "stl_home": 8, "stl_away": 6,
         "fgm_home": 40, "fga_home": 85, "reb_home": 45, "ast_home": 25,
         "tov_home": 12, "fg3m_home": 12, "fg3a_home": 30,
         "ftm_home": 18, "fta_home": 22,
         "fgm_away": 38, "fga_away": 82, "reb_away": 42, "ast_away": 22,
         "tov_away": 14, "fg3m_away": 10, "fg3a_away": 28,
         "ftm_away": 19, "fta_away": 23,
         "season_type": "Regular Season", "season": "2023-2024",
         "game_date": "2024-01-15"},
        {"team_id_home": 2, "team_id_away": 3, "pts_home": 120, "pts_away": 98,
         "blk_home": 4, "blk_away": 2, "stl_home": 7, "stl_away": 5,
         "fgm_home": 45, "fga_home": 90, "reb_home": 48, "ast_home": 28,
         "tov_home": 10, "fg3m_home": 15, "fg3a_home": 35,
         "ftm_home": 15, "fta_home": 18,
         "fgm_away": 35, "fga_away": 80, "reb_away": 38, "ast_away": 20,
         "tov_away": 16, "fg3m_away": 8, "fg3a_away": 25,
         "ftm_away": 17, "fta_away": 20,
         "season_type": "Regular Season", "season": "2023-2024",
         "game_date": "2024-01-20"},
        {"team_id_home": 1, "team_id_away": 3, "pts_home": 95, "pts_away": 112,
         "blk_home": 3, "blk_away": 6, "stl_home": 5, "stl_away": 9,
         "fgm_home": 35, "fga_home": 80, "reb_home": 40, "ast_home": 20,
         "tov_home": 15, "fg3m_home": 9, "fg3a_home": 25,
         "ftm_home": 12, "fta_home": 15,
         "fgm_away": 42, "fga_away": 88, "reb_away": 46, "ast_away": 26,
         "tov_away": 11, "fg3m_away": 14, "fg3a_away": 32,
         "ftm_away": 14, "fta_away": 17,
         "season_type": "Regular Season", "season": "2023-2024",
         "game_date": "2024-01-25"},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_teams, mock_matches):
    monkeypatch.setattr(bball_mod, "_loader", object())
    monkeypatch.setattr(bball_mod, "_players", mock_players)
    monkeypatch.setattr(bball_mod, "_teams", mock_teams)
    monkeypatch.setattr(bball_mod, "_matches", mock_matches)


# ---------------------------------------------------------------------------
# top_equipes_offensives
# ---------------------------------------------------------------------------

class TestTopEquipesOffensives:
    def test_returns_dataframe(self):
        result = bball_mod.top_equipes_offensives()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = bball_mod.top_equipes_offensives()
        assert set(result.columns) == {"Équipe", "Abrév.", "Moy. pts/match"}

    def test_sorted_by_pts_desc(self):
        result = bball_mod.top_equipes_offensives()
        pts = result["Moy. pts/match"].tolist()
        assert pts == sorted(pts, reverse=True)

    def test_n_limits_results(self):
        result = bball_mod.top_equipes_offensives(n=1)
        assert len(result) == 1

    def test_index_starts_at_1(self):
        result = bball_mod.top_equipes_offensives()
        assert result.index[0] == 1


# ---------------------------------------------------------------------------
# stats_equipe
# ---------------------------------------------------------------------------

class TestStatsEquipe:
    def test_returns_dataframe(self):
        result = bball_mod.stats_equipe("Lakers")
        assert isinstance(result, pd.DataFrame)

    def test_team_label_in_result(self):
        result = bball_mod.stats_equipe("Lakers")
        assert result.iloc[0]["Équipe"] == "Los Angeles Lakers"

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucune équipe"):
            bball_mod.stats_equipe("Unknown Team")

    def test_abbreviation_search(self):
        result = bball_mod.stats_equipe("LAL")
        assert result.iloc[0]["Équipe"] == "Los Angeles Lakers"

    def test_nickname_search(self):
        result = bball_mod.stats_equipe("Celtics")
        assert result.iloc[0]["Équipe"] == "Boston Celtics"

    def test_pts_column_present(self):
        result = bball_mod.stats_equipe("Lakers")
        assert "Points" in result.columns

    def test_case_insensitive(self):
        result = bball_mod.stats_equipe("lakers")
        assert result.iloc[0]["Équipe"] == "Los Angeles Lakers"


# ---------------------------------------------------------------------------
# classement_defensif
# ---------------------------------------------------------------------------

class TestClassementDefensif:
    def test_returns_dataframe(self):
        result = bball_mod.classement_defensif()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = bball_mod.classement_defensif()
        assert "Équipe" in result.columns
        assert "Pts encaissés/match" in result.columns
        assert "Blocks/match" in result.columns
        assert "Interceptions/match" in result.columns

    def test_sorted_by_pts_encaisses_asc(self):
        result = bball_mod.classement_defensif()
        pts = result["Pts encaissés/match"].tolist()
        assert pts == sorted(pts)

    def test_n_limits_results(self):
        result = bball_mod.classement_defensif(n=1)
        assert len(result) == 1

    def test_index_starts_at_1(self):
        result = bball_mod.classement_defensif()
        assert result.index[0] == 1


# ---------------------------------------------------------------------------
# get_agenda_data
# ---------------------------------------------------------------------------

class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = bball_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = bball_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_sport_label(self):
        result = bball_mod.get_agenda_data()
        assert all(result["Sport"] == "Basketball")

    def test_row_count(self):
        result = bball_mod.get_agenda_data()
        assert len(result) == 3  # 3 matches in mock data

    def test_team_names_resolved(self):
        result = bball_mod.get_agenda_data()
        # Team IDs should be mapped to full names
        assert "Los Angeles Lakers" in result["Équipe 1"].values or \
               "Los Angeles Lakers" in result["Équipe 2"].values


# ---------------------------------------------------------------------------
# liste_joueurs
# ---------------------------------------------------------------------------

class TestListeJoueurs:
    def test_returns_all_players(self):
        result = bball_mod.liste_joueurs()
        assert len(result) == 3

    def test_sorted_by_name(self):
        result = bball_mod.liste_joueurs()
        names = list(result["Nom complet"])
        assert names == sorted(names)

    def test_filter_by_team(self):
        result = bball_mod.liste_joueurs(equipe="Lakers")
        assert len(result) == 1
        assert result.iloc[0]["Nom complet"] == "LeBron James"

    def test_unknown_team_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucune équipe"):
            bball_mod.liste_joueurs(equipe="Unknown FC")

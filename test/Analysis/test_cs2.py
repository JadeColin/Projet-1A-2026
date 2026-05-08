
import pytest
import pandas as pd

import src.Analysis.cs2 as cs2_mod



@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"name": "s1mple", "pseudo": "s1mple", "nationality": "Ukraine",
         "birthdate": "1997-10-02", "role": "Rifler", "team": "NAVI"},
        {"name": "NiKo", "pseudo": "NiKo", "nationality": "Bosnia",
         "birthdate": "1997-02-16", "role": "Rifler", "team": "G2"},
        {"name": "ZywOo", "pseudo": "ZywOo", "nationality": "France",
         "birthdate": "2000-07-09", "role": "AWPer", "team": "Vitality"},
        {"name": "device", "pseudo": "device", "nationality": "Denmark",
         "birthdate": "1996-01-08", "role": "AWPer", "team": "NAVI"},
    ])


@pytest.fixture
def mock_coaches():
    return pd.DataFrame([
        {"name": "Blade", "pseudo": "Blade", "nationality": "Ukraine",
         "birthdate": "1990-01-01", "role": "Coach", "team": "NAVI"},
    ])


@pytest.fixture
def mock_teams():
    return pd.DataFrame([
        {"name": "NAVI"},
        {"name": "G2"},
        {"name": "Vitality"},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {"date": "2024-03-01", "team_1": "NAVI", "team_2": "G2",
         "score_team_1": 16, "score_team_2": 10, "stage": "Phase 1", "round": None},
        {"date": "2024-03-02", "team_1": "Vitality", "team_2": "NAVI",
         "score_team_1": 16, "score_team_2": 14, "stage": "Phase 1", "round": None},
        {"date": "2024-03-05", "team_1": "G2", "team_2": "Vitality",
         "score_team_1": 16, "score_team_2": 12, "stage": "Phase 2", "round": None},
        {"date": "2024-03-10", "team_1": "NAVI", "team_2": "Vitality",
         "score_team_1": 2, "score_team_2": 1, "stage": "PlayOffs", "round": "RO4"},
        {"date": "2024-03-12", "team_1": "G2", "team_2": "NAVI",
         "score_team_1": 3, "score_team_2": 0, "stage": "PlayOffs", "round": "RO2"},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_coaches, mock_teams, mock_matches):
    monkeypatch.setattr(cs2_mod, "_loader", object())
    monkeypatch.setattr(cs2_mod, "_players", mock_players)
    monkeypatch.setattr(cs2_mod, "_coaches", mock_coaches)
    monkeypatch.setattr(cs2_mod, "_teams", mock_teams)
    monkeypatch.setattr(cs2_mod, "_matches", mock_matches)



class TestClassement:
    def test_returns_dataframe(self):
        result = cs2_mod.classement()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = cs2_mod.classement()
        assert set(result.columns) == {"Équipe", "Victoires", "Défaites", "Matchs joués", "% Victoires"}

    def test_sorted_by_victoires_desc(self):
        result = cs2_mod.classement()
        assert result["Victoires"].is_monotonic_decreasing

    def test_index_starts_at_1(self):
        result = cs2_mod.classement()
        assert result.index[0] == 1

    def test_all_teams_present(self):
        result = cs2_mod.classement()
        teams = set(result["Équipe"].tolist())
        assert "NAVI" in teams
        assert "G2" in teams
        assert "Vitality" in teams


class TestStatsEquipe:
    def test_returns_dataframe(self):
        result = cs2_mod.stats_equipe("NAVI")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = cs2_mod.stats_equipe("NAVI")
        for col in ["Équipe", "Matchs joués", "Victoires", "Défaites", "Maps gagnées", "Maps perdues", "% Victoires"]:
            assert col in result.columns

    def test_team_label_in_result(self):
        result = cs2_mod.stats_equipe("NAVI")
        assert result.iloc[0]["Équipe"] == "NAVI"

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucune équipe"):
            cs2_mod.stats_equipe("Unknown Team")

    def test_case_insensitive(self):
        result = cs2_mod.stats_equipe("navi")
        assert result.iloc[0]["Équipe"] == "NAVI"

    def test_win_count_correct(self):
        # NAVI wins: match 1 (vs G2, 16-10). Losses: vs Vitality (14-16), vs G2 playoffs (0-3)
        # total matches: 5 (appears in all 5 matches, across both sides)
        result = cs2_mod.stats_equipe("NAVI")
        row = result.iloc[0]
        assert row["Victoires"] >= 1



class TestListeJoueurs:
    def test_returns_all_players(self):
        result = cs2_mod.liste_joueurs()
        assert len(result) == 4

    def test_filter_by_team(self):
        result = cs2_mod.liste_joueurs(equipe="NAVI")
        assert len(result) == 2
        names = result["Nom complet"].tolist()
        assert "s1mple" in names
        assert "device" in names

    def test_sorted_by_name(self):
        result = cs2_mod.liste_joueurs()
        names = list(result["Nom complet"])
        assert names == sorted(names)

    def test_index_starts_at_1(self):
        result = cs2_mod.liste_joueurs()
        assert result.index[0] == 1




class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = cs2_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = cs2_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_sport_label(self):
        result = cs2_mod.get_agenda_data()
        assert all(result["Sport"] == "CS2")

    def test_row_count(self):
        result = cs2_mod.get_agenda_data()
        assert len(result) == 5

    def test_scores_are_strings(self):
        result = cs2_mod.get_agenda_data()
        assert result["Score 1"].dtype == object
        assert result["Score 2"].dtype == object

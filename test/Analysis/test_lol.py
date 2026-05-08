

import pytest
import pandas as pd

import src.Analysis.lol as lol_mod



@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"name": "Faker", "pseudo": "Faker", "country_of_birth": "South Korea",
         "birthdate": "1996-05-07", "role": "Mid", "team": "T1"},
        {"name": "Chovy", "pseudo": "Chovy", "country_of_birth": "South Korea",
         "birthdate": "1999-07-19", "role": "Mid", "team": "Gen.G"},
        {"name": "Zeus", "pseudo": "Zeus", "country_of_birth": "South Korea",
         "birthdate": "2003-04-05", "role": "Top", "team": "T1"},
        {"name": "Keria", "pseudo": "Keria", "country_of_birth": "South Korea",
         "birthdate": "2001-04-04", "role": "Support", "team": "T1"},
        {"name": "Ruler", "pseudo": "Ruler", "country_of_birth": "South Korea",
         "birthdate": "1998-06-03", "role": "ADC", "team": "Gen.G"},
    ])


@pytest.fixture
def mock_coaches():
    return pd.DataFrame([
        {"name": "Polt", "pseudo": "Polt", "country_of_birth": "South Korea",
         "birthdate": "1990-01-01", "role": "Coach", "team": "T1"},
    ])


@pytest.fixture
def mock_teams():
    return pd.DataFrame([
        {"name": "T1"},
        {"name": "Gen.G"},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {"date": "2024-01-10", "team_blue": "T1", "team_red": "Gen.G",
         "winner": "T1",
         "kills_team_blue": 15, "kills_team_red": 8,
         "assists_team_blue": 30, "assists_team_red": 15,
         "deaths_team_blue": 8, "deaths_team_red": 15,
         "gold_team_blue": 60000, "gold_team_red": 50000,
         "turrets_team_blue": 7, "turrets_team_red": 2,
         "dragons_team_blue": 4, "dragons_team_red": 1,
         "barons_team_blue": 2, "barons_team_red": 0,
         "duration_s": 1800,
         "pick_1_team_blue": "Jinx", "pick_2_team_blue": "Thresh",
         "ban_1_team_blue": "Zed", "ban_2_team_blue": "Lee Sin",
         "pick_1_team_red": "Jinx", "pick_2_team_red": "Lulu",
         "ban_1_team_red": "Thresh", "ban_2_team_red": "Yasuo"},
        {"date": "2024-01-15", "team_blue": "Gen.G", "team_red": "T1",
         "winner": "Gen.G",
         "kills_team_blue": 12, "kills_team_red": 10,
         "assists_team_blue": 25, "assists_team_red": 20,
         "deaths_team_blue": 10, "deaths_team_red": 12,
         "gold_team_blue": 55000, "gold_team_red": 52000,
         "turrets_team_blue": 5, "turrets_team_red": 3,
         "dragons_team_blue": 3, "dragons_team_red": 2,
         "barons_team_blue": 1, "barons_team_red": 1,
         "duration_s": 2100,
         "pick_1_team_blue": "Jinx", "pick_2_team_blue": "Thresh",
         "ban_1_team_blue": "Zed", "ban_2_team_blue": "Lee Sin",
         "pick_1_team_red": "Jhin", "pick_2_team_red": "Thresh",
         "ban_1_team_red": "Jinx", "ban_2_team_red": "Yasuo"},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_coaches, mock_teams, mock_matches):
    monkeypatch.setattr(lol_mod, "_loader", object())
    monkeypatch.setattr(lol_mod, "_players", mock_players)
    monkeypatch.setattr(lol_mod, "_coaches", mock_coaches)
    monkeypatch.setattr(lol_mod, "_teams", mock_teams)
    monkeypatch.setattr(lol_mod, "_matches", mock_matches)



class TestStatsEquipe:
    def test_returns_dataframe(self):
        result = lol_mod.stats_equipe("T1")
        assert isinstance(result, pd.DataFrame)

    def test_team_label_in_result(self):
        result = lol_mod.stats_equipe("T1")
        assert result.iloc[0]["Équipe"] == "T1"

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucune équipe"):
            lol_mod.stats_equipe("Unknown Team")

    def test_kills_column_present(self):
        result = lol_mod.stats_equipe("T1")
        assert "Kills" in result.columns

    def test_duration_converted_to_minutes(self):
        result = lol_mod.stats_equipe("T1")
        assert "Durée moy. (min)" in result.columns
        # 1800s + 2100s = average 1950s = 32.5 min
        assert result.iloc[0]["Durée moy. (min)"] == pytest.approx(32.5, abs=0.5)



class TestChampionsPicksBans:
    def test_returns_dataframe(self):
        result = lol_mod.champions_picks_bans()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = lol_mod.champions_picks_bans()
        assert set(result.columns) == {"Champion", "Picks", "Bans"}

    def test_most_picked_champion_first(self):
        result = lol_mod.champions_picks_bans()
        picks = result["Picks"].tolist()
        assert picks == sorted(picks, reverse=True)

    def test_jinx_high_pick_count(self):
        result = lol_mod.champions_picks_bans()
        # Jinx is picked in pick_1 of both matches (2 picks)
        jinx_row = result[result["Champion"] == "Jinx"]
        assert not jinx_row.empty
        assert jinx_row.iloc[0]["Picks"] >= 2

    def test_n_limits_results(self):
        result = lol_mod.champions_picks_bans(n=3)
        assert len(result) <= 3

    def test_index_starts_at_1(self):
        result = lol_mod.champions_picks_bans()
        assert result.index[0] == 1



class TestListeJoueurs:
    def test_returns_all_players(self):
        result = lol_mod.liste_joueurs()
        assert len(result) == 5

    def test_filter_by_team(self):
        result = lol_mod.liste_joueurs(equipe="T1")
        assert len(result) == 3

    def test_sorted_by_name(self):
        result = lol_mod.liste_joueurs()
        names = list(result["Nom complet"])
        assert names == sorted(names)

    def test_index_starts_at_1(self):
        result = lol_mod.liste_joueurs()
        assert result.index[0] == 1



class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = lol_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = lol_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_sport_label(self):
        result = lol_mod.get_agenda_data()
        assert all(result["Sport"] == "LoL")

    def test_row_count(self):
        result = lol_mod.get_agenda_data()
        assert len(result) == 2

    def test_winner_has_score_1(self):
        result = lol_mod.get_agenda_data()
        # First match: T1 is team_blue and winner → Score 1 should be "1"
        first_row = result.iloc[0]
        assert first_row["Score 1"] == "1"
        assert first_row["Score 2"] == "0"

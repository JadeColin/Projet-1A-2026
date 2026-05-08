"""
Tests for src/Analysis/badminton.py

Pure functions tested directly; global state monkeypatched.
"""

import pytest
import pandas as pd

import src.Analysis.badminton as badminton_mod
from src.Analysis.badminton import _compter_jeux


@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"name": "Viktor Axelsen", "country": "Denmark", "continent": "Europe"},
        {"name": "Lee Zii Jia", "country": "Malaysia", "continent": "Asia"},
        {"name": "Kunlavut Vitidsarn", "country": "Thailand", "continent": "Asia"},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {
            "tournament": "All England 2024", "round": "Final",
            "player_1": "Viktor Axelsen", "player_2": "Lee Zii Jia",
            "game_1_score": "21-15", "game_2_score": "21-18", "game_3_score": None,
            "date": "2024-03-17",
        },
        {
            "tournament": "All England 2024", "round": "Semi final",
            "player_1": "Viktor Axelsen", "player_2": "Kunlavut Vitidsarn",
            "game_1_score": "21-19", "game_2_score": "18-21", "game_3_score": "21-17",
            "date": "2024-03-16",
        },
        {
            "tournament": "All England 2024", "round": "Semi final",
            "player_1": "Lee Zii Jia", "player_2": "Kunlavut Vitidsarn",
            "game_1_score": "21-18", "game_2_score": "17-21", "game_3_score": "21-19",
            "date": "2024-03-15",
        },
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_matches):
    monkeypatch.setattr(badminton_mod, "_loader", object())
    monkeypatch.setattr(badminton_mod, "_players", mock_players)
    monkeypatch.setattr(badminton_mod, "_matches", mock_matches)



class TestCompterJeux:
    def test_straight_games_player1(self):
        row = pd.Series({
            "game_1_score": "21-15",
            "game_2_score": "21-18",
            "game_3_score": None,
        })
        assert _compter_jeux(row) == (2, 0)

    def test_straight_games_player2(self):
        row = pd.Series({
            "game_1_score": "15-21",
            "game_2_score": "18-21",
            "game_3_score": None,
        })
        assert _compter_jeux(row) == (0, 2)

    def test_three_game_match_player1_wins(self):
        row = pd.Series({
            "game_1_score": "21-19",
            "game_2_score": "18-21",
            "game_3_score": "21-17",
        })
        assert _compter_jeux(row) == (2, 1)

    def test_three_game_match_player2_wins(self):
        row = pd.Series({
            "game_1_score": "19-21",
            "game_2_score": "21-18",
            "game_3_score": "17-21",
        })
        assert _compter_jeux(row) == (1, 2)

    def test_nan_game_ignored(self):
        row = pd.Series({
            "game_1_score": "21-10",
            "game_2_score": float("nan"),
            "game_3_score": None,
        })
        assert _compter_jeux(row) == (1, 0)

    def test_empty_string_game_ignored(self):
        row = pd.Series({
            "game_1_score": "21-10",
            "game_2_score": "  ",
            "game_3_score": None,
        })
        assert _compter_jeux(row) == (1, 0)


class TestBilanJoueurBadminton:
    def test_returns_dataframe(self):
        result = badminton_mod.bilan_joueur_badminton("Axelsen")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = badminton_mod.bilan_joueur_badminton("Axelsen")
        stats = result["Statistique"].tolist()
        assert "Matchs joués" in stats
        assert "Victoires" in stats
        assert "Défaites" in stats
        assert "% Victoires" in stats

    def test_axelsen_wins_both_matches(self):
        result = badminton_mod.bilan_joueur_badminton("Axelsen")
        row_victoires = result[result["Statistique"] == "Victoires"].iloc[0]
        assert row_victoires["Viktor Axelsen"] == 2

    def test_player_name_as_column(self):
        result = badminton_mod.bilan_joueur_badminton("Axelsen")
        assert "Viktor Axelsen" in result.columns

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucun joueur"):
            badminton_mod.bilan_joueur_badminton("Unknown Player")

    def test_case_insensitive(self):
        result = badminton_mod.bilan_joueur_badminton("axelsen")
        assert "Viktor Axelsen" in result.columns

    def test_win_rate_between_0_and_100(self):
        result = badminton_mod.bilan_joueur_badminton("Axelsen")
        wr = result[result["Statistique"] == "% Victoires"].iloc[0]["Viktor Axelsen"]
        assert 0 <= wr <= 100



class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = badminton_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = badminton_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_sport_label(self):
        result = badminton_mod.get_agenda_data()
        assert all(result["Sport"] == "Badminton")

    def test_row_count(self):
        result = badminton_mod.get_agenda_data()
        assert len(result) == 3

    def test_scores_are_strings(self):
        result = badminton_mod.get_agenda_data()
        assert result["Score 1"].dtype == object
        assert result["Score 2"].dtype == object

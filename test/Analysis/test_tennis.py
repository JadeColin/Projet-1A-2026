
import pytest
import pandas as pd

import src.Analysis.tennis as tennis_mod
from src.Analysis.tennis import _compter_sets, _standardiser_tennis



@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"player_id": 1, "full_name": "Carlos Alcaraz", "hand": "R", "dob": "20030505",
         "ioc": "ESP", "height": 185.0},
        {"player_id": 2, "full_name": "Novak Djokovic", "hand": "R", "dob": "19870522",
         "ioc": "SRB", "height": 188.0},
        {"player_id": 3, "full_name": "Jannik Sinner", "hand": "R", "dob": "20010816",
         "ioc": "ITA", "height": 188.0},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {"winner_id": 1, "loser_id": 2, "tourney_name": "Wimbledon",
         "round": "F", "score": "6-4 7-5", "tourney_date": "2024-07-14", "minutes": 95},
        {"winner_id": 1, "loser_id": 3, "tourney_name": "Roland Garros",
         "round": "SF", "score": "7-6(5) 6-4 6-2", "tourney_date": "2024-06-07", "minutes": 140},
        {"winner_id": 2, "loser_id": 3, "tourney_name": "Wimbledon",
         "round": "SF", "score": "6-3 6-4", "tourney_date": "2024-07-12", "minutes": 80},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_matches):
    """Inject mock DataFrames into tennis module, bypassing real file I/O."""
    monkeypatch.setattr(tennis_mod, "_loader", object())  # non-None → _load() won't run
    monkeypatch.setattr(tennis_mod, "_atp_players", mock_players)
    monkeypatch.setattr(tennis_mod, "_wta_players", mock_players)
    monkeypatch.setattr(tennis_mod, "_atp_matches", mock_matches)
    monkeypatch.setattr(tennis_mod, "_wta_matches", mock_matches)




class TestCompterSets:
    def test_straight_sets(self):
        assert _compter_sets("6-4 7-5") == (2, 0)

    def test_three_sets(self):
        assert _compter_sets("6-4 3-6 7-5") == (2, 1)

    def test_tiebreak_ignored(self):
        assert _compter_sets("7-6(5) 6-4") == (2, 0)

    def test_nan_returns_zero_zero(self):
        assert _compter_sets(float("nan")) == (0, 0)

    def test_five_set_match(self):
        assert _compter_sets("6-4 3-6 6-3 3-6 6-4") == (3, 2)

    def test_all_sets_to_loser(self):
        # Shouldn't happen in real data, but logic handles it
        assert _compter_sets("4-6 5-7") == (0, 2)



class TestClassementVictoires:
    def test_returns_dataframe(self):
        result = tennis_mod.classement_victoires(circuit="ATP", n=10)
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = tennis_mod.classement_victoires(circuit="ATP")
        assert set(result.columns) == {"Joueur", "Victoires", "Défaites", "Matchs joués", "% Victoires"}

    def test_sorted_by_victoires_desc(self):
        result = tennis_mod.classement_victoires(circuit="ATP")
        assert result["Victoires"].is_monotonic_decreasing

    def test_n_limits_results(self):
        result = tennis_mod.classement_victoires(circuit="ATP", n=1)
        assert len(result) == 1

    def test_leader_has_most_wins(self):
        result = tennis_mod.classement_victoires(circuit="ATP")
        assert result.iloc[0]["Joueur"] == "Carlos Alcaraz"

    def test_index_starts_at_1(self):
        result = tennis_mod.classement_victoires(circuit="ATP")
        assert result.index[0] == 1



class TestStatsJoueur:
    def test_returns_dataframe(self):
        result = tennis_mod.stats_joueur("Alcaraz", circuit="ATP")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = tennis_mod.stats_joueur("Alcaraz", circuit="ATP")
        for col in ["Joueur", "Victoires", "Défaites", "Matchs joués", "% Victoires"]:
            assert col in result.columns

    def test_correct_win_count(self):
        result = tennis_mod.stats_joueur("Alcaraz", circuit="ATP")
        assert result.iloc[0]["Victoires"] == 2

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucun joueur"):
            tennis_mod.stats_joueur("Unknown Player", circuit="ATP")

    def test_case_insensitive(self):
        result = tennis_mod.stats_joueur("alcaraz", circuit="ATP")
        assert result.iloc[0]["Joueur"] == "Carlos Alcaraz"



class TestStandardiserTennis:
    def test_columns(self, mock_matches, mock_players):
        result = _standardiser_tennis(mock_matches, mock_players, "ATP")
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_sport_label(self, mock_matches, mock_players):
        result = _standardiser_tennis(mock_matches, mock_players, "ATP")
        assert all(result["Sport"] == "Tennis ATP")

    def test_row_count(self, mock_matches, mock_players):
        result = _standardiser_tennis(mock_matches, mock_players, "ATP")
        assert len(result) == len(mock_matches)



class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = tennis_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = tennis_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_contains_atp_and_wta(self):
        result = tennis_mod.get_agenda_data()
        sports = result["Sport"].unique()
        assert "Tennis ATP" in sports
        assert "Tennis WTA" in sports

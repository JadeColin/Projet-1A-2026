
import pytest
import pandas as pd

import src.Analysis.starcraft2 as sc2_mod



@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"name": "Serral", "pseudo": "Serral", "nationality": "Finland",
         "birthdate": "1998-03-24", "race": "Zerg", "team": "ENCE"},
        {"name": "Maru", "pseudo": "Maru", "nationality": "South Korea",
         "birthdate": "1998-09-09", "race": "Terran", "team": "Jin Air"},
        {"name": "Reynor", "pseudo": "Reynor", "nationality": "Italy",
         "birthdate": "2002-06-06", "race": "Zerg", "team": "Shopify Rebellion"},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {"date": "2024-08-01", "player_1": "Serral", "player_2": "Maru",
         "score_player_1": 3, "score_player_2": 1},
        {"date": "2024-08-02", "player_1": "Maru", "player_2": "Serral",
         "score_player_1": 2, "score_player_2": 3},
        {"date": "2024-08-03", "player_1": "Serral", "player_2": "Reynor",
         "score_player_1": 3, "score_player_2": 0},
        {"date": "2024-08-04", "player_1": "Reynor", "player_2": "Maru",
         "score_player_1": 2, "score_player_2": 3},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_matches):
    monkeypatch.setattr(sc2_mod, "_loader", object())
    monkeypatch.setattr(sc2_mod, "_players", mock_players)
    monkeypatch.setattr(sc2_mod, "_matches", mock_matches)



class TestBilanJoueurSc2:
    def test_returns_dataframe(self):
        result = sc2_mod.bilan_joueur_sc2("Serral")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = sc2_mod.bilan_joueur_sc2("Serral")
        stats = result["Statistique"].tolist()
        assert "Matchs joués" in stats
        assert "Victoires" in stats
        assert "Défaites" in stats
        assert "% Victoires" in stats

    def test_player_name_as_column(self):
        result = sc2_mod.bilan_joueur_sc2("Serral")
        assert "Serral" in result.columns

    def test_serral_wins_all(self):
        # Serral: wins as p1 vs Maru (3-1), wins as p2 vs Maru (3-2), wins as p1 vs Reynor (3-0)
        result = sc2_mod.bilan_joueur_sc2("Serral")
        row_v = result[result["Statistique"] == "Victoires"].iloc[0]
        row_d = result[result["Statistique"] == "Défaites"].iloc[0]
        assert row_v["Serral"] == 3
        assert row_d["Serral"] == 0

    def test_maru_loses_to_serral(self):
        result = sc2_mod.bilan_joueur_sc2("Maru")
        row_v = result[result["Statistique"] == "Victoires"].iloc[0]
        row_d = result[result["Statistique"] == "Défaites"].iloc[0]
        assert row_v["Maru"] == 1  # wins vs Reynor
        assert row_d["Maru"] == 2  # loses to Serral twice

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucun joueur"):
            sc2_mod.bilan_joueur_sc2("Unknown Player")

    def test_case_insensitive(self):
        result = sc2_mod.bilan_joueur_sc2("serral")
        assert "Serral" in result.columns

    def test_win_rate_between_0_and_100(self):
        result = sc2_mod.bilan_joueur_sc2("Serral")
        wr = result[result["Statistique"] == "% Victoires"].iloc[0]["Serral"]
        assert 0 <= wr <= 100



class TestGetAgendaData:
    def test_returns_dataframe(self):
        result = sc2_mod.get_agenda_data()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = sc2_mod.get_agenda_data()
        assert set(result.columns) == {"Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"}

    def test_sport_label(self):
        result = sc2_mod.get_agenda_data()
        assert all(result["Sport"] == "StarCraft II")

    def test_row_count(self):
        result = sc2_mod.get_agenda_data()
        assert len(result) == 4

    def test_scores_are_strings(self):
        result = sc2_mod.get_agenda_data()
        assert result["Score 1"].dtype == object
        assert result["Score 2"].dtype == object

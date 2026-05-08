
import pytest
import pandas as pd

import src.Analysis.chess as chess_mod



@pytest.fixture
def mock_players():
    return pd.DataFrame([
        {"name": "Magnus Carlsen", "federation": "NOR", "fide_title": "GM",
         "rating_standard": 2830.0, "rating_rapid": 2820.0, "rating_blitz": 2810.0},
        {"name": "Hikaru Nakamura", "federation": "USA", "fide_title": "GM",
         "rating_standard": 2794.0, "rating_rapid": 2810.0, "rating_blitz": 2850.0},
        {"name": "Fabiano Caruana", "federation": "USA", "fide_title": "GM",
         "rating_standard": 2804.0, "rating_rapid": 2750.0, "rating_blitz": 2730.0},
        {"name": "Wei Yi", "federation": "CHN", "fide_title": "GM",
         "rating_standard": 2762.0, "rating_rapid": 2755.0, "rating_blitz": 2745.0},
        {"name": "Jan Krzyzstof Duda", "federation": "POL", "fide_title": "GM",
         "rating_standard": 2750.0, "rating_rapid": 2720.0, "rating_blitz": 2700.0},
    ])


@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {"player_1": "Magnus Carlsen", "player_2": "Hikaru Nakamura",
         "score_player_1": 1.0, "score_player_2": 0.0},
        {"player_1": "Magnus Carlsen", "player_2": "Fabiano Caruana",
         "score_player_1": 0.5, "score_player_2": 0.5},
        {"player_1": "Hikaru Nakamura", "player_2": "Magnus Carlsen",
         "score_player_1": 0.0, "score_player_2": 1.0},
        {"player_1": "Fabiano Caruana", "player_2": "Hikaru Nakamura",
         "score_player_1": 1.0, "score_player_2": 0.0},
    ])


@pytest.fixture(autouse=True)
def inject_mock_data(monkeypatch, mock_players, mock_matches):
    monkeypatch.setattr(chess_mod, "_loader", object())
    monkeypatch.setattr(chess_mod, "_players", mock_players)
    monkeypatch.setattr(chess_mod, "_matches", mock_matches)


class TestClassementElo:
    def test_standard_mode_returns_dataframe(self):
        result = chess_mod.classement_elo(mode="standard")
        assert isinstance(result, pd.DataFrame)

    def test_standard_columns(self):
        result = chess_mod.classement_elo(mode="standard")
        assert "Joueur" in result.columns
        assert "Elo Standard" in result.columns
        assert "Fédération" in result.columns
        assert "Titre" in result.columns

    def test_sorted_by_elo_desc(self):
        result = chess_mod.classement_elo(mode="standard")
        elos = result["Elo Standard"].tolist()
        assert elos == sorted(elos, reverse=True)

    def test_n_limits_results(self):
        result = chess_mod.classement_elo(mode="standard", n=2)
        assert len(result) == 2

    def test_rapid_mode(self):
        result = chess_mod.classement_elo(mode="rapid")
        assert "Elo Rapid" in result.columns

    def test_blitz_mode(self):
        result = chess_mod.classement_elo(mode="blitz")
        assert "Elo Blitz" in result.columns

    def test_invalid_mode_raises_value_error(self):
        with pytest.raises(ValueError, match="Mode invalide"):
            chess_mod.classement_elo(mode="invalid_mode")

    def test_index_starts_at_1(self):
        result = chess_mod.classement_elo()
        assert result.index[0] == 1

    def test_leader_is_carlsen(self):
        result = chess_mod.classement_elo(mode="standard")
        assert result.iloc[0]["Joueur"] == "Magnus Carlsen"


class TestBilanJoueur:
    def test_returns_dataframe(self):
        result = chess_mod.bilan_joueur("Carlsen")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = chess_mod.bilan_joueur("Carlsen")
        for col in ["Joueur", "Parties jouées", "Victoires", "Nuls", "Défaites", "Score total"]:
            assert col in result.columns

    def test_correct_win_count(self):
        # Carlsen: wins as p1 (vs Nakamura: score 1.0), wins as p2 (vs Nakamura: score 1.0)
        # Also: draw as p1 (vs Caruana: 0.5)
        result = chess_mod.bilan_joueur("Carlsen")
        row = result.iloc[0]
        assert row["Victoires"] == 2
        assert row["Nuls"] == 1
        assert row["Défaites"] == 0

    def test_score_total(self):
        result = chess_mod.bilan_joueur("Carlsen")
        row = result.iloc[0]
        # 2 wins + 1 draw = 2.5
        assert row["Score total"] == 2.5

    def test_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Aucun joueur"):
            chess_mod.bilan_joueur("Unknown GM")

    def test_case_insensitive(self):
        result = chess_mod.bilan_joueur("carlsen")
        assert result.iloc[0]["Joueur"] == "Magnus Carlsen"



class TestStatsParTitre:
    def test_returns_dataframe(self):
        result = chess_mod.stats_par_titre()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self):
        result = chess_mod.stats_par_titre()
        assert "Titre FIDE" in result.columns
        assert "Joueurs" in result.columns
        assert "Elo moy. Standard" in result.columns

    def test_all_gms_in_one_group(self):
        result = chess_mod.stats_par_titre()
        # All 5 players are GM
        assert result.iloc[0]["Joueurs"] == 5

    def test_sorted_by_elo_desc(self):
        result = chess_mod.stats_par_titre()
        elos = result["Elo moy. Standard"].tolist()
        assert elos == sorted(elos, reverse=True)

    def test_index_starts_at_1(self):
        result = chess_mod.stats_par_titre()
        assert result.index[0] == 1

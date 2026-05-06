"""
Tests des loaders de données sportives.

Deux niveaux de tests :
    - Tests unitaires : transformations pures (méthodes statiques) sans I/O.
    - Tests d'intégration : chargement réel des CSV pour vérifier structure et
      colonnes calculées.
"""

import pandas as pd
import pytest

from src.Parsers.BasketballLoader import BasketballLoader
from src.Parsers.ChessLoader import ChessLoader
from src.Parsers.TennisLoader import TennisLoader
from src.Parsers.LolLoader import LolLoader
from src.Parsers.VolleyballLoader import VolleyballLoader


# ── BasketballLoader ──────────────────────────────────────────────────────────


class TestBasketballLoaderHeightToCm:
    """Tests unitaires de la conversion pieds-pouces → centimètres."""

    def test_standard_height_is_converted_correctly(self):
        # 6 pieds 8 pouces = (6*12 + 8) * 2.54 = 203.2 cm
        assert BasketballLoader._height_to_cm("6-8") == 203.2

    def test_zero_inches_is_handled(self):
        # 7 pieds 0 pouces = 84 * 2.54 = 213.4 cm
        assert BasketballLoader._height_to_cm("7-0") == 213.4

    def test_nan_returns_none(self):
        assert BasketballLoader._height_to_cm(float("nan")) is None

    def test_missing_value_returns_none(self):
        assert BasketballLoader._height_to_cm(None) is None


class TestBasketballLoaderIntegration:
    """Tests d'intégration sur les vrais fichiers CSV."""

    @pytest.fixture(scope="class")
    def loader(self):
        return BasketballLoader()

    @pytest.fixture(scope="class")
    def players(self, loader):
        return loader.load_players()

    @pytest.fixture(scope="class")
    def teams(self, loader):
        return loader.load_teams()

    def test_load_players_is_not_empty(self, players):
        assert len(players) > 0

    def test_load_players_has_full_name_column(self, players):
        assert "full_name" in players.columns

    def test_load_players_full_name_has_no_leading_trailing_spaces(self, players):
        assert not players["full_name"].str.startswith(" ").any()
        assert not players["full_name"].str.endswith(" ").any()

    def test_load_players_has_height_cm_column(self, players):
        assert "height_cm" in players.columns

    def test_load_players_birthdate_is_datetime(self, players):
        assert pd.api.types.is_datetime64_any_dtype(players["birthdate"])

    def test_load_teams_is_not_empty(self, teams):
        assert len(teams) > 0

    def test_load_teams_has_expected_columns(self, teams):
        for col in ("id", "full_name", "abbreviation", "nickname"):
            assert col in teams.columns

    def test_load_matches_is_not_empty(self, loader):
        matches = loader.load_matches()
        assert len(matches) > 0

    def test_load_matches_game_date_is_datetime(self, loader):
        matches = loader.load_matches()
        assert pd.api.types.is_datetime64_any_dtype(matches["game_date"])

    def test_get_team_roster_returns_players_for_valid_team(self, loader, players, teams):
        roster = loader.get_team_roster(players, teams, "Lakers")
        assert len(roster) > 0

    def test_get_team_roster_raises_for_unknown_team(self, loader, players, teams):
        with pytest.raises(ValueError, match="Aucune équipe trouvée"):
            loader.get_team_roster(players, teams, "TeamQuiNExistePas")


# ── ChessLoader ───────────────────────────────────────────────────────────────


class TestChessLoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return ChessLoader()

    def test_load_players_is_not_empty(self, loader):
        players = loader.load_players()
        assert len(players) > 0

    def test_load_players_has_expected_columns(self, loader):
        players = loader.load_players()
        for col in ("name", "fide_id", "rating_standard", "fide_title"):
            assert col in players.columns

    def test_load_matches_is_not_empty(self, loader):
        matches = loader.load_matches()
        assert len(matches) > 0

    def test_load_matches_has_expected_columns(self, loader):
        matches = loader.load_matches()
        for col in ("player_1", "player_2", "score_player_1"):
            assert col in matches.columns

    def test_load_all_returns_two_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 2
        for df in result:
            assert isinstance(df, pd.DataFrame)


# ── TennisLoader ──────────────────────────────────────────────────────────────


class TestTennisLoaderParseDob:
    """Tests unitaires de la conversion de date de naissance YYYYMMDD."""

    def test_valid_dob_is_parsed(self):
        series = pd.Series([19970420.0])
        result = TennisLoader._parse_dob(series)
        assert result.iloc[0] == pd.Timestamp("1997-04-20")

    def test_nan_dob_produces_nat(self):
        series = pd.Series([float("nan")])
        result = TennisLoader._parse_dob(series)
        assert pd.isna(result.iloc[0])

    def test_multiple_values_are_all_parsed(self):
        series = pd.Series([19900101.0, 20001231.0])
        result = TennisLoader._parse_dob(series)
        assert result.iloc[0] == pd.Timestamp("1990-01-01")
        assert result.iloc[1] == pd.Timestamp("2000-12-31")


class TestTennisLoaderParseTourneyDate:
    """Tests unitaires de la conversion de date de tournoi YYYYMMDD."""

    def test_valid_tourney_date_is_parsed(self):
        series = pd.Series([20240115])
        result = TennisLoader._parse_tourney_date(series)
        assert result.iloc[0] == pd.Timestamp("2024-01-15")


class TestTennisLoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return TennisLoader()

    def test_load_atp_players_is_not_empty(self, loader):
        assert len(loader.load_atp_players()) > 0

    def test_load_atp_players_has_full_name_column(self, loader):
        players = loader.load_atp_players()
        assert "full_name" in players.columns

    def test_load_atp_players_dob_is_datetime(self, loader):
        players = loader.load_atp_players()
        assert pd.api.types.is_datetime64_any_dtype(players["dob"])

    def test_load_wta_players_has_full_name_column(self, loader):
        players = loader.load_wta_players()
        assert "full_name" in players.columns

    def test_load_atp_matches_tourney_date_is_datetime(self, loader):
        matches = loader.load_atp_matches()
        assert pd.api.types.is_datetime64_any_dtype(matches["tourney_date"])

    def test_load_wta_matches_tourney_date_is_datetime(self, loader):
        matches = loader.load_wta_matches()
        assert pd.api.types.is_datetime64_any_dtype(matches["tourney_date"])

    def test_load_all_returns_four_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 4
        for df in result:
            assert isinstance(df, pd.DataFrame)


# ── LolLoader ─────────────────────────────────────────────────────────────────


class TestLolLoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return LolLoader()

    def test_load_players_is_not_empty(self, loader):
        assert len(loader.load_players()) > 0

    def test_load_matches_has_duration_s_column(self, loader):
        matches = loader.load_matches()
        assert "duration_s" in matches.columns

    def test_load_matches_duration_s_values_are_positive(self, loader):
        matches = loader.load_matches()
        durations = matches["duration_s"].dropna()
        assert (durations > 0).all()

    def test_load_matches_date_is_datetime(self, loader):
        matches = loader.load_matches()
        assert pd.api.types.is_datetime64_any_dtype(matches["date"])

    def test_load_all_returns_four_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 4


# ── VolleyballLoader ──────────────────────────────────────────────────────────


class TestVolleyballLoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return VolleyballLoader()

    def test_load_players_men_has_gender_column_set_to_M(self, loader):
        players = loader.load_players_men()
        assert "gender" in players.columns
        assert (players["gender"] == "M").all()

    def test_load_players_women_has_gender_column_set_to_F(self, loader):
        players = loader.load_players_women()
        assert "gender" in players.columns
        assert (players["gender"] == "F").all()

    def test_load_players_men_birth_date_is_datetime(self, loader):
        players = loader.load_players_men()
        assert pd.api.types.is_datetime64_any_dtype(players["birth_date"])

    def test_load_matches_men_has_winner_column(self, loader):
        matches = loader.load_matches_men()
        assert "winner" in matches.columns

    def test_load_matches_men_winner_is_one_of_the_two_teams(self, loader):
        matches = loader.load_matches_men()
        valid = matches.apply(
            lambda r: r["winner"] in (r["country_code_1"], r["country_code_2"]), axis=1
        )
        assert valid.all()

    def test_load_matches_women_columns_are_renamed_uniformly(self, loader):
        matches = loader.load_matches_women()
        assert "country_code_1" in matches.columns
        assert "country_code_2" in matches.columns

    def test_load_matches_women_winner_is_one_of_the_two_teams(self, loader):
        matches = loader.load_matches_women()
        valid = matches.apply(
            lambda r: r["winner"] in (r["country_code_1"], r["country_code_2"]), axis=1
        )
        assert valid.all()

    def test_load_all_returns_seven_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 7
        for df in result:
            assert isinstance(df, pd.DataFrame)

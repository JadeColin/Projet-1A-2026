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
from src.Parsers.BadmintonLoader import BadmintonLoader
from src.Parsers.ChessLoader import ChessLoader
from src.Parsers.Cs2Loader import Cs2Loader
from src.Parsers.FootballChampionsLeagueLoader import FootballChampionsLeagueLoader
from src.Parsers.FootballLoader import FootballLoader
from src.Parsers.LolLoader import LolLoader
from src.Parsers.Starcraft2Loader import Starcraft2Loader
from src.Parsers.TennisLoader import TennisLoader
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


# ── BadmintonLoader ───────────────────────────────────────────────────────────


class TestBadmintonLoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return BadmintonLoader()

    @pytest.fixture(scope="class")
    def players(self, loader):
        return loader.load_players()

    @pytest.fixture(scope="class")
    def matches(self, loader):
        return loader.load_matches()

    def test_load_players_is_not_empty(self, players):
        assert len(players) > 0

    def test_load_players_has_expected_columns(self, players):
        for col in ("name", "country", "continent"):
            assert col in players.columns

    def test_load_matches_is_not_empty(self, matches):
        assert len(matches) > 0

    def test_load_matches_has_expected_columns(self, matches):
        for col in ("tournament", "round", "player_1", "player_2"):
            assert col in matches.columns

    def test_load_matches_date_is_datetime(self, matches):
        assert pd.api.types.is_datetime64_any_dtype(matches["date"])

    def test_load_matches_has_game_score_columns(self, matches):
        assert "game_1_score" in matches.columns
        assert "game_2_score" in matches.columns

    def test_load_all_returns_two_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 2
        for df in result:
            assert isinstance(df, pd.DataFrame)


# ── Cs2Loader ─────────────────────────────────────────────────────────────────


class TestCs2LoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return Cs2Loader()

    @pytest.fixture(scope="class")
    def players(self, loader):
        return loader.load_players()

    @pytest.fixture(scope="class")
    def matches(self, loader):
        return loader.load_matches()

    def test_load_players_is_not_empty(self, players):
        assert len(players) > 0

    def test_load_players_has_expected_columns(self, players):
        for col in ("pseudo", "name", "nationality", "team"):
            assert col in players.columns

    def test_load_players_birthdate_is_datetime(self, players):
        assert pd.api.types.is_datetime64_any_dtype(players["birthdate"])

    def test_load_coaches_is_not_empty(self, loader):
        coaches = loader.load_coaches()
        assert len(coaches) > 0

    def test_load_coaches_birthdate_is_datetime(self, loader):
        coaches = loader.load_coaches()
        assert pd.api.types.is_datetime64_any_dtype(coaches["birthdate"])

    def test_load_teams_is_not_empty(self, loader):
        teams = loader.load_teams()
        assert len(teams) > 0

    def test_load_matches_is_not_empty(self, matches):
        assert len(matches) > 0

    def test_load_matches_has_expected_columns(self, matches):
        for col in ("team_1", "team_2", "score_team_1", "score_team_2"):
            assert col in matches.columns

    def test_load_matches_date_is_datetime(self, matches):
        assert pd.api.types.is_datetime64_any_dtype(matches["date"])

    def test_load_all_returns_four_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 4
        for df in result:
            assert isinstance(df, pd.DataFrame)


# ── FootballChampionsLeagueLoader ─────────────────────────────────────────────


class TestFootballChampionsLeagueLoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return FootballChampionsLeagueLoader()

    @pytest.fixture(scope="class")
    def players(self, loader):
        return loader.load_players()

    @pytest.fixture(scope="class")
    def matches(self, loader):
        return loader.load_matches()

    def test_load_players_is_not_empty(self, players):
        assert len(players) > 0

    def test_load_players_has_expected_columns(self, players):
        for col in ("player_name", "club", "position", "goals", "assists"):
            assert col in players.columns

    def test_load_players_duplicate_match_played_renamed(self, players):
        # FootballChampionsLeagueLoader renames 'match_played' → 'match_played_field'
        # and 'match_played.1' → 'match_played'
        assert "match_played_field" in players.columns
        assert "match_played" in players.columns

    def test_load_teams_is_not_empty(self, loader):
        teams = loader.load_teams()
        assert len(teams) > 0

    def test_load_teams_has_expected_columns(self, loader):
        teams = loader.load_teams()
        for col in ("full_name", "country"):
            assert col in teams.columns

    def test_load_matches_is_not_empty(self, matches):
        assert len(matches) > 0

    def test_load_matches_has_expected_columns(self, matches):
        for col in ("team_home", "team_away", "score_team_home", "score_team_away", "phase"):
            assert col in matches.columns

    def test_load_matches_date_is_datetime(self, matches):
        assert pd.api.types.is_datetime64_any_dtype(matches["date"])

    def test_load_all_returns_three_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 3
        for df in result:
            assert isinstance(df, pd.DataFrame)


# ── FootballLoader ────────────────────────────────────────────────────────────


class TestFootballLoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return FootballLoader()

    def test_load_countries_is_not_empty(self, loader):
        countries = loader.load_countries()
        assert len(countries) > 0

    def test_load_countries_has_expected_columns(self, loader):
        countries = loader.load_countries()
        for col in ("id", "name"):
            assert col in countries.columns

    def test_load_leagues_is_not_empty(self, loader):
        leagues = loader.load_leagues()
        assert len(leagues) > 0

    def test_load_leagues_has_expected_columns(self, loader):
        leagues = loader.load_leagues()
        for col in ("id", "country_id", "name"):
            assert col in leagues.columns

    def test_load_matches_is_not_empty(self, loader):
        matches = loader.load_matches()
        assert len(matches) > 0

    def test_load_matches_date_is_datetime(self, loader):
        matches = loader.load_matches()
        assert pd.api.types.is_datetime64_any_dtype(matches["date"])

    def test_load_matches_has_goal_columns(self, loader):
        matches = loader.load_matches()
        for col in ("home_team_goal", "away_team_goal"):
            assert col in matches.columns

    def test_load_all_returns_three_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 3
        for df in result:
            assert isinstance(df, pd.DataFrame)


# ── Starcraft2Loader ──────────────────────────────────────────────────────────


class TestStarcraft2LoaderIntegration:

    @pytest.fixture(scope="class")
    def loader(self):
        return Starcraft2Loader()

    @pytest.fixture(scope="class")
    def players(self, loader):
        return loader.load_players()

    @pytest.fixture(scope="class")
    def matches(self, loader):
        return loader.load_matches()

    def test_load_players_is_not_empty(self, players):
        assert len(players) > 0

    def test_load_players_has_expected_columns(self, players):
        for col in ("name", "nationality", "race", "team"):
            assert col in players.columns

    def test_load_players_birthdate_is_datetime(self, players):
        assert pd.api.types.is_datetime64_any_dtype(players["birthdate"])

    def test_load_matches_is_not_empty(self, matches):
        assert len(matches) > 0

    def test_load_matches_has_expected_columns(self, matches):
        for col in ("player_1", "player_2", "score_player_1", "score_player_2"):
            assert col in matches.columns

    def test_load_matches_date_is_datetime(self, matches):
        assert pd.api.types.is_datetime64_any_dtype(matches["date"])

    def test_load_all_returns_two_dataframes(self, loader):
        result = loader.load_all()
        assert len(result) == 2
        for df in result:
            assert isinstance(df, pd.DataFrame)


import pytest
import pandas as pd

from src.Analysis.générique import (
    ResultatMatch,
    _agreger_deux_manches,
    formater_roster,
    agenda_recents,
    _calculer_classement,
    fiche_joueur,
    lister_joueurs,
)



class TestResultatMatch:
    def test_equipe1_wins(self):
        m = ResultatMatch("Alpha", "Beta", 3, 1)
        assert m.joue is True
        assert m.gagnant == "Alpha"
        assert m.perdant == "Beta"

    def test_equipe2_wins(self):
        m = ResultatMatch("Alpha", "Beta", 0, 2)
        assert m.joue is True
        assert m.gagnant == "Beta"
        assert m.perdant == "Alpha"

    def test_draw(self):
        m = ResultatMatch("Alpha", "Beta", 1, 1)
        assert m.joue is True
        assert m.gagnant is None
        assert m.perdant is None

    def test_nan_score_not_played(self):
        m = ResultatMatch("Alpha", "Beta", float("nan"), float("nan"))
        assert m.joue is False
        assert m.gagnant is None

    def test_none_score_not_played(self):
        m = ResultatMatch("Alpha", "Beta", None, None)
        assert m.joue is False
        assert m.gagnant is None

    def test_label_equipe_played_equipe1(self):
        m = ResultatMatch("Alpha", "Beta", 3, 1)
        assert m.label_equipe("Alpha") == "3-1"

    def test_label_equipe_played_equipe2(self):
        m = ResultatMatch("Alpha", "Beta", 3, 1)
        assert m.label_equipe("Beta") == "1-3"

    def test_label_equipe_not_played(self):
        m = ResultatMatch("Alpha", "Beta", None, None)
        assert m.label_equipe("Alpha") == "???"
        assert m.label_equipe("Beta") == "???"

    def test_zero_zero_draw(self):
        m = ResultatMatch("A", "B", 0, 0)
        assert m.joue is True
        assert m.gagnant is None



class TestAgregerDeuxManches:
    @pytest.fixture
    def df_deux_manches(self):
        return pd.DataFrame([
            {"round": "RO8", "eq1": "TeamA", "eq2": "TeamB", "s1": 2, "s2": 1},
            {"round": "RO8", "eq1": "TeamB", "eq2": "TeamA", "s1": 0, "s2": 2},
        ])

    def test_scores_aggregated(self, df_deux_manches):
        result = _agreger_deux_manches(
            df_deux_manches, "eq1", "eq2", "s1", "s2", "round"
        )
        assert len(result) == 1
        # TeamA total = 2 + 2 = 4, TeamB total = 1 + 0 = 1
        row = result.iloc[0]
        # pair is sorted, so eq1=TeamA, eq2=TeamB
        assert row["s1"] == 4
        assert row["s2"] == 1

    def test_result_has_one_row_per_confrontation(self, df_deux_manches):
        result = _agreger_deux_manches(
            df_deux_manches, "eq1", "eq2", "s1", "s2", "round"
        )
        assert len(result) == 1

    def test_multiple_rounds(self):
        df = pd.DataFrame([
            {"round": "RO8", "eq1": "A", "eq2": "B", "s1": 1, "s2": 2},
            {"round": "RO8", "eq1": "B", "eq2": "A", "s1": 1, "s2": 1},
            {"round": "RO4", "eq1": "C", "eq2": "D", "s1": 3, "s2": 0},
            {"round": "RO4", "eq1": "D", "eq2": "C", "s1": 1, "s2": 2},
        ])
        result = _agreger_deux_manches(df, "eq1", "eq2", "s1", "s2", "round")
        assert len(result) == 2
        rounds = sorted(result["round"].tolist())
        assert rounds == ["RO4", "RO8"]



class TestFormaterRoster:
    @pytest.fixture
    def df_joueurs(self):
        return pd.DataFrame([
            {"name": "LeBron James", "country": "USA", "birthdate": "1984-12-30"},
            {"name": "Stephen Curry", "country": "USA", "birthdate": "1988-03-14"},
        ])

    def test_basic_columns(self, df_joueurs):
        result = formater_roster(df_joueurs, col_nom="name")
        assert "Rôle" in result.columns
        assert "Nom complet" in result.columns
        assert list(result["Rôle"]) == ["Joueur", "Joueur"]

    def test_index_starts_at_1(self, df_joueurs):
        result = formater_roster(df_joueurs, col_nom="name")
        assert result.index[0] == 1

    def test_nationalite_column(self, df_joueurs):
        result = formater_roster(df_joueurs, col_nom="name", col_nationalite="country")
        assert "Nationalité" in result.columns
        assert result.iloc[0]["Nationalité"] == "USA"

    def test_date_formatted(self, df_joueurs):
        result = formater_roster(df_joueurs, col_nom="name", col_naissance="birthdate")
        assert result.iloc[0]["Date de naissance"] == "30/12/1984"

    def test_missing_column_gives_na(self, df_joueurs):
        result = formater_roster(df_joueurs, col_nom="name")
        assert result.iloc[0]["Nationalité"] == "N/A"
        assert result.iloc[0]["Date de naissance"] == "N/A"

    def test_esport_pseudo_column(self):
        df = pd.DataFrame([
            {"name": "Player One", "pseudo": "p1", "country": "KR"},
        ])
        result = formater_roster(
            df, col_nom="name", col_pseudo="pseudo", est_esport=True
        )
        assert "Pseudo" in result.columns
        assert result.iloc[0]["Pseudo"] == "p1"

    def test_non_esport_no_pseudo_column(self):
        df = pd.DataFrame([{"name": "Player One", "pseudo": "p1"}])
        result = formater_roster(df, col_nom="name", col_pseudo="pseudo", est_esport=False)
        assert "Pseudo" not in result.columns

    def test_coachs_appear_first(self, df_joueurs):
        df_coachs = pd.DataFrame([{"name": "Coach A", "country": "FR"}])
        result = formater_roster(
            df_joueurs, col_nom="name", df_coachs=df_coachs
        )
        assert result.iloc[0]["Rôle"] == "Coach"
        assert result.iloc[0]["Nom complet"] == "Coach A"
        assert result.iloc[1]["Rôle"] == "Joueur"

    def test_empty_coachs_ignored(self, df_joueurs):
        df_coachs = pd.DataFrame(columns=["name"])
        result = formater_roster(df_joueurs, col_nom="name", df_coachs=df_coachs)
        assert all(r == "Joueur" for r in result["Rôle"])

    def test_row_count(self, df_joueurs):
        result = formater_roster(df_joueurs, col_nom="name")
        assert len(result) == 2



class TestAgendaRecents:
    @pytest.fixture
    def df_sport1(self):
        return pd.DataFrame({
            "Sport": ["Tennis", "Tennis"],
            "Date": ["2024-07-01", "2024-06-15"],
            "Équipe 1": ["A", "C"],
            "Équipe 2": ["B", "D"],
            "Score 1": ["3", "2"],
            "Score 2": ["1", "0"],
        })

    @pytest.fixture
    def df_sport2(self):
        return pd.DataFrame({
            "Sport": ["Basketball"],
            "Date": ["2024-07-10"],
            "Équipe 1": ["Lakers"],
            "Équipe 2": ["Celtics"],
            "Score 1": ["110"],
            "Score 2": ["105"],
        })

    def test_sorted_most_recent_first(self, df_sport1, df_sport2):
        result = agenda_recents([df_sport1, df_sport2], n=10)
        dates = pd.to_datetime(result["Date"], format="%d/%m/%Y")
        assert dates.is_monotonic_decreasing

    def test_n_limits_rows(self, df_sport1, df_sport2):
        result = agenda_recents([df_sport1, df_sport2], n=2)
        assert len(result) == 2

    def test_empty_sources_returns_empty(self):
        result = agenda_recents([])
        assert result.empty
        expected = ["Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"]
        assert list(result.columns) == expected

    def test_index_starts_at_1(self, df_sport1):
        result = agenda_recents([df_sport1])
        assert result.index[0] == 1

    def test_nan_dates_excluded(self, df_sport1):
        df_with_nan = df_sport1.copy()
        df_with_nan.loc[0, "Date"] = None
        result = agenda_recents([df_with_nan])
        assert len(result) == 1

    def test_date_formatted_ddmmyyyy(self, df_sport1):
        result = agenda_recents([df_sport1], n=1)
        date_val = result.iloc[0]["Date"]
        # format dd/mm/yyyy: first part <= 31, third part 4 digits
        parts = date_val.split("/")
        assert len(parts) == 3
        assert len(parts[2]) == 4

    def test_correct_columns(self, df_sport1):
        result = agenda_recents([df_sport1])
        expected = ["Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"]
        assert list(result.columns) == expected



class TestCalculerClassement:
    @pytest.fixture
    def df_matches(self):
        """A wins 2, B wins 1 draw 1, C loses 2, D draw 1 lose 1."""
        return pd.DataFrame([
            {"eq1": "A", "eq2": "B", "s1": 3, "s2": 1},  # A wins
            {"eq1": "A", "eq2": "C", "s1": 2, "s2": 0},  # A wins
            {"eq1": "B", "eq2": "C", "s1": 1, "s2": 0},  # B wins
            {"eq1": "B", "eq2": "D", "s1": 1, "s2": 1},  # draw
            {"eq1": "D", "eq2": "C", "s1": 0, "s2": 2},  # C wins
        ])

    def test_returns_expected_columns(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        expected_cols = {"Rang", "Équipe", "MJ", "V", "N", "D", "Pts", "Diff", "Winrate"}
        assert set(result.columns) == expected_cols

    def test_win_gives_3_pts(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        a_row = result[result["Équipe"] == "A"].iloc[0]
        assert a_row["V"] == 2
        assert a_row["Pts"] == 6

    def test_draw_gives_1_pt_each(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        b_row = result[result["Équipe"] == "B"].iloc[0]
        d_row = result[result["Équipe"] == "D"].iloc[0]
        assert b_row["N"] == 1
        assert b_row["Pts"] == 4  # 1 win + 1 draw
        assert d_row["N"] == 1
        assert d_row["Pts"] == 1

    def test_leader_has_highest_pts(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        assert result.iloc[0]["Équipe"] == "A"

    def test_rang_1_for_leader(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        assert result.iloc[0]["Rang"] == 1

    def test_matches_jouees_count(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        a_row = result[result["Équipe"] == "A"].iloc[0]
        assert a_row["MJ"] == 2

    def test_diff_positive_for_winner(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        a_row = result[result["Équipe"] == "A"].iloc[0]
        assert a_row["Diff"] > 0

    def test_winrate_format(self, df_matches):
        result = _calculer_classement(df_matches, "eq1", "eq2", "s1", "s2")
        for val in result["Winrate"]:
            assert "%" in val or val == "N/A"



class TestFicheJoueur:
    @pytest.fixture
    def df_players(self):
        return pd.DataFrame([
            {"name": "Magnus Carlsen", "federation": "NOR", "rating": 2830},
            {"name": "Hikaru Nakamura", "federation": "USA", "rating": 2794},
            {"name": "Fabiano Caruana", "federation": "USA", "rating": 2804},
        ])

    def test_exact_match(self, df_players):
        result = fiche_joueur(df_players, "name", "Magnus Carlsen")
        assert result.index[0] == "Magnus Carlsen"

    def test_partial_case_insensitive_match(self, df_players):
        result = fiche_joueur(df_players, "name", "carlsen")
        assert "Magnus Carlsen" in result.index[0]

    def test_not_found_raises_value_error(self, df_players):
        with pytest.raises(ValueError, match="Aucun joueur"):
            fiche_joueur(df_players, "name", "Unknown Player")

    def test_multiple_matches_raises_value_error(self, df_players):
        with pytest.raises(ValueError, match="joueurs correspondent"):
            fiche_joueur(df_players, "name", "a")  # matches multiple players

    def test_col_labels_applied(self, df_players):
        result = fiche_joueur(
            df_players, "name", "Magnus",
            col_labels={"federation": "Fédération", "rating": "Elo"}
        )
        assert "Fédération" in result.columns
        assert "Elo" in result.columns

    def test_nan_becomes_na_string(self):
        df = pd.DataFrame([{"name": "Player X", "score": float("nan")}])
        result = fiche_joueur(df, "name", "Player X")
        assert result.iloc[0]["score"] == "N/A"

    def test_date_column_formatted(self):
        df = pd.DataFrame([{"name": "Player Y", "dob": "1990-05-20"}])
        result = fiche_joueur(df, "name", "Player Y", cols_dates=["dob"])
        assert result.iloc[0]["dob"] == "20/05/1990"

    def test_returns_single_row(self, df_players):
        result = fiche_joueur(df_players, "name", "Magnus Carlsen")
        assert len(result) == 1



class TestListerJoueurs:
    @pytest.fixture
    def df_players(self):
        return pd.DataFrame([
            {"name": "Carlos Alcaraz", "team": "ESP", "age": 21},
            {"name": "Novak Djokovic", "team": "SRB", "age": 37},
            {"name": "Jannik Sinner", "team": "ITA", "age": 23},
        ])

    def test_sorted_by_name(self, df_players):
        result = lister_joueurs(df_players, col_nom="name")
        names = list(result["name"])
        assert names == sorted(names)

    def test_index_starts_at_1(self, df_players):
        result = lister_joueurs(df_players, col_nom="name")
        assert result.index[0] == 1

    def test_includes_equipe_column(self, df_players):
        result = lister_joueurs(df_players, col_nom="name", col_equipe="team")
        assert "team" in result.columns

    def test_col_labels_applied(self, df_players):
        result = lister_joueurs(
            df_players, col_nom="name", col_equipe="team",
            col_labels={"name": "Joueur", "team": "Équipe"}
        )
        assert "Joueur" in result.columns
        assert "Équipe" in result.columns

    def test_row_count(self, df_players):
        result = lister_joueurs(df_players, col_nom="name")
        assert len(result) == 3

    def test_only_name_and_team_columns(self, df_players):
        result = lister_joueurs(df_players, col_nom="name", col_equipe="team")
        assert set(result.columns) == {"name", "team"}

    def test_without_equipe_col(self, df_players):
        result = lister_joueurs(df_players, col_nom="name")
        assert "team" not in result.columns
        assert "age" not in result.columns

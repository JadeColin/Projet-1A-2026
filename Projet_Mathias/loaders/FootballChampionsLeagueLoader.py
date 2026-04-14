from pathlib import Path

import pandas as pd


class FootballChampionsLeagueLoader:
    """
    Charge les données de la base Football Champions League (UEFA).

    Fichiers sources :
        - player.csv : statistiques individuelles des joueurs (751 joueurs)
        - team.csv   : équipes participantes (32 équipes)
        - match.csv  : matchs de la compétition (125 matchs)

    Exemple d'utilisation :
        loader = FootballChampionsLeagueLoader()
        players = loader.load_players()
        matches = loader.load_matches()
        players, teams, matches = loader.load_all()
    """

    ROOT = Path(__file__).parent.parent.parent / "Base_de_données" / "football_champions_league"

    def load_players(self) -> pd.DataFrame:
        """
        Charge et nettoie les statistiques joueurs de la Ligue des Champions.

        Colonnes principales : player_name, club, position, assists, goals,
        goals_right_foot, goals_left_foot, goals_headers, minutes_played,
        pass_attempted, pass_completed, tackles_won, fouls_committed, yellow, red,
        saved, conceded, cleansheets, distance_covered.

        Note : le fichier source contient deux colonnes 'match_played' ;
               la première (par position) est renommée 'match_played_field'
               (stats de champ), la seconde 'match_played' (total).
               Typos conservés depuis la source : 'balls_recoverd',
               'cross_complted', 'punches made'.
        """
        df = pd.read_csv(self.ROOT / "player.csv")
        # La colonne dupliquée est automatiquement renommée 'match_played.1' par pandas
        df = df.rename(columns={"match_played": "match_played_field", "match_played.1": "match_played"})
        return df

    def load_teams(self) -> pd.DataFrame:
        """
        Charge les équipes de la Ligue des Champions.

        Colonnes : full_name, short_name, year_founded, country, league, city
        """
        return pd.read_csv(self.ROOT / "team.csv")

    def load_matches(self) -> pd.DataFrame:
        """
        Charge et nettoie les matchs de la Ligue des Champions.

        Colonnes : date, phase, round, matchday, group, team_home, team_away,
                   score_team_home, score_team_away

        Colonnes ajoutées :
            - date : converti en datetime
        """
        df = pd.read_csv(self.ROOT / "match.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les trois tables en une seule fois.

        Renvoie :
            players, teams, matches
        """
        return self.load_players(), self.load_teams(), self.load_matches()

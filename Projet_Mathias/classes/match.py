"""
Classes génériques pour représenter un match et une collection de matchs.

Conçues pour être compatibles avec tous les sports du projet :

    - Basketball (NBA)   : col_equipe1='team_id_home', col_equipe2='team_id_away',
                           col_score1='pts_home', col_score2='pts_away',
                           col_date='game_date'
    - Football (Europ.)  : col_equipe1='home_team_api_id', col_equipe2='away_team_api_id',
                           col_score1='home_team_goal', col_score2='away_team_goal',
                           col_date='date'
    - Tennis (ATP/WTA)   : col_equipe1='winner_id', col_equipe2='loser_id',
                           col_gagnant='winner_id', col_date='tourney_date'
                           (pas de score numérique — score en texte dans 'score')
    - LoL (EMEA)         : col_equipe1='team_blue', col_equipe2='team_red',
                           col_gagnant='winner', col_date='date'
    - Volleyball         : col_equipe1='country_code_1', col_equipe2='country_code_2',
                           col_score1='set_country_1', col_score2='set_country_2',
                           col_gagnant='winner', col_date='date'
"""

from __future__ import annotations

import pandas as pd


class Match:
    """Représente un match individuel à partir d'une ligne de DataFrame."""

    def __init__(
        self,
        data: pd.Series,
        col_id: str | None = None,
        col_date: str | None = None,
        col_equipe1: str | None = None,
        col_equipe2: str | None = None,
        col_score1: str | None = None,
        col_score2: str | None = None,
        col_gagnant: str | None = None,
    ) -> None:
        self._data = data
        self._col_id = col_id
        self._col_date = col_date
        self._col_equipe1 = col_equipe1
        self._col_equipe2 = col_equipe2
        self._col_score1 = col_score1
        self._col_score2 = col_score2
        self._col_gagnant = col_gagnant

    # ------------------------------------------------------------------ #
    #  Propriétés principales                                              #
    # ------------------------------------------------------------------ #

    @property
    def id(self):
        """Identifiant du match."""
        if self._col_id is None:
            return None
        return self._data.get(self._col_id)

    @property
    def date(self) -> pd.Timestamp | None:
        """Date du match."""
        if self._col_date is None:
            return None
        val = self._data.get(self._col_date)
        if pd.isna(val):
            return None
        return pd.Timestamp(val)

    @property
    def equipe_1(self):
        """Identifiant ou nom de l'équipe 1 (domicile / bleue / winner selon sport)."""
        if self._col_equipe1 is None:
            return None
        return self._data.get(self._col_equipe1)

    @property
    def equipe_2(self):
        """Identifiant ou nom de l'équipe 2 (extérieur / rouge / loser selon sport)."""
        if self._col_equipe2 is None:
            return None
        return self._data.get(self._col_equipe2)

    @property
    def score_1(self):
        """Score/points de l'équipe 1."""
        if self._col_score1 is None:
            return None
        val = self._data.get(self._col_score1)
        return None if pd.isna(val) else val

    @property
    def score_2(self):
        """Score/points de l'équipe 2."""
        if self._col_score2 is None:
            return None
        val = self._data.get(self._col_score2)
        return None if pd.isna(val) else val

    @property
    def gagnant(self):
        """
        Retourne l'identifiant/nom du gagnant.

        Priorité :
            1. Colonne col_gagnant si elle est configurée.
            2. Déduction automatique depuis col_score1 et col_score2.
            3. None si égalité ou données manquantes.
        """
        if self._col_gagnant is not None:
            val = self._data.get(self._col_gagnant)
            if not pd.isna(val):
                return val

        s1, s2 = self.score1, self.score2
        if s1 is not None and s2 is not None:
            if s1 > s2:
                return self.equipe1
            if s2 > s1:
                return self.equipe2
        return None

    @property
    def est_nul(self) -> bool:
        """True si le match s'est terminé sur un score égal."""
        s1, s2 = self.score1, self.score2
        if s1 is None or s2 is None:
            return False
        return s1 == s2

    # ------------------------------------------------------------------ #
    #  Accès brut                                                          #
    # ------------------------------------------------------------------ #

    def __getitem__(self, colonne: str):
        """Accès direct à n'importe quelle colonne brute : match['surface']."""
        return self._data[colonne]

    def to_dict(self) -> dict:
        """Retourne toutes les données brutes sous forme de dictionnaire."""
        return self._data.to_dict()

    def __repr__(self) -> str:
        e1, e2 = self.equipe1, self.equipe2
        date = self.date.date() if self.date else "?"
        s1, s2 = self.score1, self.score2
        score = f" {s1}-{s2}" if s1 is not None else ""
        return f"Match({e1!r} vs {e2!r}{score}, date={date})"


# --------------------------------------------------------------------------- #


class Matchs:
    """
    Collection de matchs wrappant un DataFrame pandas.

    Paramètres de mapping (noms des colonnes dans le DataFrame source) :
        col_id       : identifiant unique du match (optionnel)
        col_date     : date du match (optionnel)
        col_equipe1  : équipe 1 (domicile / bleue / winner…)
        col_equipe2  : équipe 2 (extérieur / rouge / loser…)
        col_score1   : score numérique de l'équipe 1 (optionnel)
        col_score2   : score numérique de l'équipe 2 (optionnel)
        col_gagnant  : colonne contenant directement le gagnant (optionnel)

    Exemple — Volleyball :
        matchs = Matchs(
            df_men,
            col_date='date',
            col_equipe1='country_code_1',
            col_equipe2='country_code_2',
            col_score1='set_country_1',
            col_score2='set_country_2',
            col_gagnant='winner',
        )
        print(matchs.bilan('USA'))

    Exemple — LoL :
        matchs = Matchs(
            df_matches,
            col_date='date',
            col_equipe1='team_blue',
            col_equipe2='team_red',
            col_gagnant='winner',
        )
        print(matchs.victoires('TH'))
    """

    def __init__(
        self,
        df: pd.DataFrame,
        col_id: str | None = None,
        col_date: str | None = None,
        col_equipe1: str | None = None,
        col_equipe2: str | None = None,
        col_score1: str | None = None,
        col_score2: str | None = None,
        col_gagnant: str | None = None,
    ) -> None:
        self._df = df.copy()
        self._col_id = col_id
        self._col_date = col_date
        self._col_equipe1 = col_equipe1
        self._col_equipe2 = col_equipe2
        self._col_score1 = col_score1
        self._col_score2 = col_score2
        self._col_gagnant = col_gagnant

    # ------------------------------------------------------------------ #
    #  Filtres                                                             #
    # ------------------------------------------------------------------ #

    def get_par_equipe(self, equipe_id) -> "Matchs":
        """Retourne tous les matchs impliquant l'équipe donnée (domicile ou extérieur)."""
        if self._col_equipe1 is None or self._col_equipe2 is None:
            raise ValueError("col_equipe1 et col_equipe2 doivent être configurées.")
        mask = (
            (self._df[self._col_equipe1] == equipe_id)
            | (self._df[self._col_equipe2] == equipe_id)
        )
        return self._copie(self._df[mask])

    def get_par_date(
        self,
        debut: str | pd.Timestamp,
        fin: str | pd.Timestamp | None = None,
    ) -> "Matchs":
        """
        Filtre les matchs dans un intervalle de dates.

        debut : borne inférieure incluse (ex: '2024-01-01')
        fin   : borne supérieure incluse (défaut = aujourd'hui)
        """
        if self._col_date is None:
            raise ValueError("col_date non configurée.")
        dates = pd.to_datetime(self._df[self._col_date], errors="coerce")
        debut_ts = pd.Timestamp(debut)
        fin_ts = pd.Timestamp(fin) if fin is not None else pd.Timestamp.today()
        mask = (dates >= debut_ts) & (dates <= fin_ts)
        return self._copie(self._df[mask])

    def get_par_saison(self, saison: str, col_saison: str = "season") -> "Matchs":
        """Filtre par saison (ex : '2022-2023')."""
        mask = self._df[col_saison] == saison
        return self._copie(self._df[mask])

    def filtrer(self, **kwargs) -> "Matchs":
        """
        Filtre générique sur n'importe quelle colonne brute.

        Exemple : matchs.filtrer(surface='Clay')
        """
        df = self._df
        for col, val in kwargs.items():
            df = df[df[col] == val]
        return self._copie(df)

    # ------------------------------------------------------------------ #
    #  Statistiques par équipe                                             #
    # ------------------------------------------------------------------ #

    def victoires(self, equipe_id) -> int:
        """Nombre de victoires de l'équipe dans cette collection."""
        gagnants = self._serie_gagnants()
        return int((gagnants == equipe_id).sum())

    def defaites(self, equipe_id) -> int:
        """Nombre de défaites de l'équipe dans cette collection."""
        matchs_equipe = self.get_par_equipe(equipe_id)
        return len(matchs_equipe) - matchs_equipe.victoires(equipe_id) - matchs_equipe.nuls()

    def nuls(self) -> int:
        """Nombre de matchs nuls dans la collection (score égal)."""
        if self._col_score1 is None or self._col_score2 is None:
            return 0
        return int((self._df[self._col_score1] == self._df[self._col_score2]).sum())

    def bilan(self, equipe_id) -> dict:
        """
        Retourne un dictionnaire {victoires, defaites, nuls, joues} pour l'équipe.

        Exemple :
            {'victoires': 5, 'defaites': 2, 'nuls': 1, 'joues': 8}
        """
        matchs_equipe = self.get_par_equipe(equipe_id)
        v = matchs_equipe.victoires(equipe_id)
        n = matchs_equipe.nuls()
        d = len(matchs_equipe) - v - n
        return {"victoires": v, "defaites": d, "nuls": n, "joues": len(matchs_equipe)}

    def score_moyen(self) -> dict:
        """
        Score moyen des deux équipes sur tous les matchs de la collection.

        Retourne {'equipe1': float, 'equipe2': float}.
        """
        if self._col_score1 is None or self._col_score2 is None:
            raise ValueError("col_score1 et col_score2 doivent être configurées.")
        return {
            "equipe1": round(self._df[self._col_score1].mean(), 2),
            "equipe2": round(self._df[self._col_score2].mean(), 2),
        }

    def classement(self) -> pd.DataFrame:
        """
        Calcule un classement simplifié (victoires, défaites, nuls) pour toutes les
        équipes présentes dans la collection.

        Retourne un DataFrame trié par victoires décroissantes.
        Colonnes : equipe, victoires, defaites, nuls, joues.
        """
        if self._col_equipe1 is None or self._col_equipe2 is None:
            raise ValueError("col_equipe1 et col_equipe2 doivent être configurées.")

        equipes = set(self._df[self._col_equipe1].dropna()) | set(
            self._df[self._col_equipe2].dropna()
        )
        rows = []
        for equipe in sorted(equipes):
            b = self.bilan(equipe)
            rows.append({"equipe": equipe, **b})

        return (
            pd.DataFrame(rows)
            .sort_values(["victoires", "joues"], ascending=[False, True])
            .reset_index(drop=True)
        )

    # ------------------------------------------------------------------ #
    #  Interface Python standard                                           #
    # ------------------------------------------------------------------ #

    def to_dataframe(self) -> pd.DataFrame:
        """Retourne le DataFrame brut sous-jacent (copie)."""
        return self._df.copy()

    def __len__(self) -> int:
        return len(self._df)

    def __iter__(self):
        for _, row in self._df.iterrows():
            yield self._make_match(row)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self._make_match(self._df.iloc[idx])
        return self._copie(self._df.iloc[idx])

    def __repr__(self) -> str:
        e1 = self._col_equipe1 or "?"
        e2 = self._col_equipe2 or "?"
        return f"Matchs({len(self)} matchs | {e1} vs {e2})"

    # ------------------------------------------------------------------ #
    #  Helpers internes                                                    #
    # ------------------------------------------------------------------ #

    def _serie_gagnants(self) -> pd.Series:
        """
        Construit une Series avec le gagnant de chaque match.

        Logique :
            1. col_gagnant renseignée → utilise directement cette colonne.
            2. Sinon, déduit depuis col_score1 > col_score2.
        """
        if self._col_gagnant is not None and self._col_gagnant in self._df.columns:
            return self._df[self._col_gagnant]

        if self._col_score1 is None or self._col_score2 is None:
            raise ValueError(
                "Impossible de déterminer le gagnant : configurez col_gagnant "
                "ou col_score1 + col_score2."
            )

        s1 = self._df[self._col_score1]
        s2 = self._df[self._col_score2]
        gagnants = pd.Series(index=self._df.index, dtype=object)
        gagnants[s1 > s2] = self._df.loc[s1 > s2, self._col_equipe1]
        gagnants[s2 > s1] = self._df.loc[s2 > s1, self._col_equipe2]
        return gagnants

    def _make_match(self, row: pd.Series) -> Match:
        return Match(
            row,
            self._col_id,
            self._col_date,
            self._col_equipe1,
            self._col_equipe2,
            self._col_score1,
            self._col_score2,
            self._col_gagnant,
        )

    def _copie(self, df: pd.DataFrame) -> "Matchs":
        return Matchs(
            df,
            self._col_id,
            self._col_date,
            self._col_equipe1,
            self._col_equipe2,
            self._col_score1,
            self._col_score2,
            self._col_gagnant,
        )

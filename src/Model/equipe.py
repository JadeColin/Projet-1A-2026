"""
Classes génériques pour représenter une équipe et une collection d'équipes.

Conçues pour être compatibles avec tous les sports du projet :
    - Basketball (NBA)   : col_id='id', col_nom='full_name', col_abrev='abbreviation',
                           col_ville='city'
    - Football           : équipes référencées via home_team_api_id / away_team_api_id
                           (pas de table d'équipes directe dans les données nettoyées)
    - LoL (EMEA)         : col_id='team', col_nom='team', col_abrev='team_abbreviation',
                           col_ville='location'
    - Volleyball         : équipes = pays, col_id='code', col_nom='country'
"""

from __future__ import annotations

import pandas as pd

from .joueur import Joueurs


class Equipe:
    """Représente une équipe individuelle à partir d'une ligne de DataFrame."""

    def __init__(
        self,
        data: pd.Series,
        col_id: str = "id",
        col_nom: str = "nom",
        col_abrev: str | None = None,
        col_ville: str | None = None,
    ) -> None:
        self._data = data
        self._col_id = col_id
        self._col_nom = col_nom
        self._col_abrev = col_abrev
        self._col_ville = col_ville

    # ------------------------------------------------------------------ #
    #  Propriétés principales                                              #
    # ------------------------------------------------------------------ #

    @property
    def id(self):
        """Identifiant de l'équipe."""
        return self._data.get(self._col_id)

    @property
    def nom(self) -> str | None:
        """Nom de l'équipe."""
        return self._data.get(self._col_nom)

    @property
    def abreviation(self) -> str | None:
        """Abréviation de l'équipe (ex : 'BOS', 'TH')."""
        if self._col_abrev is None:
            return None
        return self._data.get(self._col_abrev)

    @property
    def ville(self) -> str | None:
        """Ville ou localisation de l'équipe."""
        if self._col_ville is None:
            return None
        return self._data.get(self._col_ville)

    # ------------------------------------------------------------------ #
    #  Relations                                                           #
    # ------------------------------------------------------------------ #

    def get_joueurs(self, joueurs: Joueurs) -> Joueurs:
        """
        Retourne les joueurs de cette équipe depuis une collection Joueurs.

        Nécessite que Joueurs ait été configuré avec col_equipe.
        """
        return joueurs.get_par_equipe(self.id)

    # ------------------------------------------------------------------ #
    #  Accès brut                                                          #
    # ------------------------------------------------------------------ #

    def __getitem__(self, colonne: str):
        """Accès direct à n'importe quelle colonne brute."""
        return self._data[colonne]

    def to_dict(self) -> dict:
        """Retourne toutes les données brutes sous forme de dictionnaire."""
        return self._data.to_dict()

    def __repr__(self) -> str:
        abrev = f", abrev={self.abreviation!r}" if self.abreviation else ""
        return f"Equipe({self.nom!r}{abrev})"


# --------------------------------------------------------------------------- #


class Equipes:
    """
    Collection d'équipes wrappant un DataFrame pandas.

    Paramètres de mapping (noms des colonnes dans le DataFrame source) :
        col_id    : identifiant unique de l'équipe
        col_nom   : nom de l'équipe
        col_abrev : abréviation (optionnel)
        col_ville : ville/localisation (optionnel)

    Exemple — Basketball :
        equipes = Equipes(
            df_teams,
            col_id='id',
            col_nom='full_name',
            col_abrev='abbreviation',
            col_ville='city',
        )
        celtics = equipes.get_par_nom("Celtics")[0]
        print(celtics.get_joueurs(joueurs))

    Exemple — LoL :
        equipes = Equipes(
            df_teams,
            col_id='team',
            col_nom='team',
            col_abrev='team_abbreviation',
            col_ville='location',
        )
    """

    def __init__(
        self,
        df: pd.DataFrame,
        col_id: str = "id",
        col_nom: str = "nom",
        col_abrev: str | None = None,
        col_ville: str | None = None,
    ) -> None:
        self._df = df.copy()
        self._col_id = col_id
        self._col_nom = col_nom
        self._col_abrev = col_abrev
        self._col_ville = col_ville

    # ------------------------------------------------------------------ #
    #  Filtres                                                             #
    # ------------------------------------------------------------------ #

    def get_par_id(self, equipe_id) -> Equipe | None:
        """Retourne l'Equipe correspondant à l'identifiant, ou None."""
        mask = self._df[self._col_id] == equipe_id
        rows = self._df[mask]
        if rows.empty:
            return None
        return self._make_equipe(rows.iloc[0])

    def get_par_nom(self, nom: str, exact: bool = False) -> "Equipes":
        """
        Filtre par nom.

        exact=False (défaut) : recherche partielle insensible à la casse.
        exact=True           : correspondance exacte insensible à la casse.
        """
        if exact:
            mask = self._df[self._col_nom].str.lower() == nom.lower()
        else:
            mask = self._df[self._col_nom].str.contains(nom, case=False, na=False)
        return self._copie(self._df[mask])

    def filtrer(self, **kwargs) -> "Equipes":
        """
        Filtre générique sur n'importe quelle colonne brute.

        Exemple : equipes.filtrer(region='EMEA')
        """
        df = self._df
        for col, val in kwargs.items():
            df = df[df[col] == val]
        return self._copie(df)

    # ------------------------------------------------------------------ #
    #  Relations                                                           #
    # ------------------------------------------------------------------ #

    def get_joueurs(self, joueurs: Joueurs) -> Joueurs:
        """
        Retourne tous les joueurs appartenant à l'une des équipes de la collection.

        Utile pour obtenir les joueurs d'un sous-ensemble d'équipes filtrées.
        Nécessite que Joueurs ait été configuré avec col_equipe.
        """
        if self._df.empty:
            return joueurs.filtrer(**{joueurs._col_equipe: None})  # collection vide
        ids = self._df[self._col_id].tolist()
        mask = joueurs.to_dataframe()[joueurs._col_equipe].isin(ids)
        return joueurs._copie(joueurs.to_dataframe()[mask])

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
            yield self._make_equipe(row)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self._make_equipe(self._df.iloc[idx])
        return self._copie(self._df.iloc[idx])

    def __repr__(self) -> str:
        return f"Equipes({len(self)} équipes | id='{self._col_id}', nom='{self._col_nom}')"

    # ------------------------------------------------------------------ #
    #  Helpers internes                                                    #
    # ------------------------------------------------------------------ #

    def _make_equipe(self, row: pd.Series) -> Equipe:
        return Equipe(row, self._col_id, self._col_nom, self._col_abrev, self._col_ville)

    def _copie(self, df: pd.DataFrame) -> "Equipes":
        return Equipes(df, self._col_id, self._col_nom, self._col_abrev, self._col_ville)

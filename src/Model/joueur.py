"""
Classes génériques pour représenter un joueur et une collection de joueurs.

Conçues pour être compatibles avec tous les sports du projet :
    - Basketball (NBA)   : col_id='person_id', col_nom='full_name', col_naissance='birthdate',
                           col_equipe='team_id', col_taille='height_cm'
    - Tennis (ATP/WTA)   : col_id='player_id', col_nom='full_name', col_naissance='dob',
                           col_taille='height'  (pas d'équipe)
    - LoL (EMEA)         : col_id='pseudo', col_nom='name', col_naissance='birthdate',
                           col_equipe='team'
    - Volleyball         : col_id='name', col_nom='name', col_naissance='birth_date',
                           col_equipe='country_code', col_taille='height'
"""

from __future__ import annotations

import pandas as pd


class Joueur:
    """Représente un joueur individuel à partir d'une ligne de DataFrame."""

    def __init__(
        self,
        data: pd.Series,
        col_id: str = "id",
        col_nom: str = "nom",
        col_naissance: str | None = None,
        col_equipe: str | None = None,
        col_taille: str | None = None,
    ) -> None:
        self._data = data
        self._col_id = col_id
        self._col_nom = col_nom
        self._col_naissance = col_naissance
        self._col_equipe = col_equipe
        self._col_taille = col_taille

    # ------------------------------------------------------------------ #
    #  Propriétés principales                                              #
    # ------------------------------------------------------------------ #

    @property
    def id(self):
        """Identifiant du joueur."""
        return self._data.get(self._col_id)

    @property
    def nom(self) -> str | None:
        """Nom complet du joueur."""
        return self._data.get(self._col_nom)

    @property
    def naissance(self) -> pd.Timestamp | None:
        """Date de naissance (Timestamp) ou None si non configurée."""
        if self._col_naissance is None:
            return None
        val = self._data.get(self._col_naissance)
        if pd.isna(val):
            return None
        return pd.Timestamp(val)

    @property
    def age(self) -> float | None:
        """Âge en années (arrondi à 1 décimale) calculé à aujourd'hui."""
        dob = self.naissance
        if dob is None:
            return None
        return round((pd.Timestamp.today() - dob).days / 365.25, 1)

    @property
    def equipe(self):
        """Identifiant ou nom de l'équipe du joueur."""
        if self._col_equipe is None:
            return None
        return self._data.get(self._col_equipe)

    @property
    def taille(self) -> float | None:
        """Taille du joueur (en cm selon la source)."""
        if self._col_taille is None:
            return None
        val = self._data.get(self._col_taille)
        return None if pd.isna(val) else val

    # ------------------------------------------------------------------ #
    #  Accès brut                                                          #
    # ------------------------------------------------------------------ #

    def __getitem__(self, colonne: str):
        """Accès direct à n'importe quelle colonne brute : joueur['position']."""
        return self._data[colonne]

    def to_dict(self) -> dict:
        """Retourne toutes les données brutes sous forme de dictionnaire."""
        return self._data.to_dict()

    def __repr__(self) -> str:
        return f"Joueur({self.nom!r}, id={self.id!r})"


# --------------------------------------------------------------------------- #


class Joueurs:
    """
    Collection de joueurs wrappant un DataFrame pandas.

    Paramètres de mapping (noms des colonnes dans le DataFrame source) :
        col_id         : identifiant unique du joueur
        col_nom        : nom complet
        col_naissance  : date de naissance (optionnel)
        col_equipe     : identifiant/nom de l'équipe (optionnel)
        col_taille     : taille en cm (optionnel)

    Exemple — Basketball :
        joueurs = Joueurs(
            df_players,
            col_id='person_id',
            col_nom='full_name',
            col_naissance='birthdate',
            col_equipe='team_id',
            col_taille='height_cm',
        )
        print(joueurs.get_par_nom("LeBron"))
        print(joueurs.age_moyen())
    """

    def __init__(
        self,
        df: pd.DataFrame,
        col_id: str = "id",
        col_nom: str = "nom",
        col_naissance: str | None = None,
        col_equipe: str | None = None,
        col_taille: str | None = None,
    ) -> None:
        self._df = df.copy()
        self._col_id = col_id
        self._col_nom = col_nom
        self._col_naissance = col_naissance
        self._col_equipe = col_equipe
        self._col_taille = col_taille

    # ------------------------------------------------------------------ #
    #  Filtres                                                             #
    # ------------------------------------------------------------------ #

    def get_par_id(self, joueur_id) -> Joueur | None:
        """Retourne le Joueur correspondant à l'identifiant, ou None."""
        mask = self._df[self._col_id] == joueur_id
        rows = self._df[mask]
        if rows.empty:
            return None
        return self._make_joueur(rows.iloc[0])

    def get_par_nom(self, nom: str, exact: bool = False) -> "Joueurs":
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

    def get_par_equipe(self, equipe_id) -> "Joueurs":
        """Retourne les joueurs appartenant à l'équipe donnée."""
        if self._col_equipe is None:
            raise ValueError(
                "col_equipe non configurée — précisez col_equipe à l'initialisation."
            )
        mask = self._df[self._col_equipe] == equipe_id
        return self._copie(self._df[mask])

    def filtrer(self, **kwargs) -> "Joueurs":
        """
        Filtre générique sur n'importe quelle colonne brute.

        Exemple : joueurs.filtrer(position='Center', height_cm=210)
        """
        df = self._df
        for col, val in kwargs.items():
            df = df[df[col] == val]
        return self._copie(df)

    # ------------------------------------------------------------------ #
    #  Statistiques                                                        #
    # ------------------------------------------------------------------ #

    def ages(self, date_ref: pd.Timestamp | None = None) -> pd.Series:
        """
        Série des âges (en années) pour chaque joueur.

        date_ref : date de référence (aujourd'hui par défaut).
        """
        if self._col_naissance is None:
            raise ValueError(
                "col_naissance non configurée — précisez col_naissance à l'initialisation."
            )
        if date_ref is None:
            date_ref = pd.Timestamp.today()
        naissances = pd.to_datetime(self._df[self._col_naissance], errors="coerce")
        return ((date_ref - naissances).dt.days / 365.25).round(1)

    def age_moyen(self, date_ref: pd.Timestamp | None = None) -> float:
        """Âge moyen de la collection."""
        return round(self.ages(date_ref).mean(), 1)

    def taille_moyenne(self) -> float | None:
        """Taille moyenne en cm."""
        if self._col_taille is None:
            raise ValueError(
                "col_taille non configurée — précisez col_taille à l'initialisation."
            )
        return round(self._df[self._col_taille].mean(), 1)

    def resume(self) -> pd.DataFrame:
        """
        Tableau de synthèse avec les colonnes configurées uniquement.

        Colonnes affichées : id, nom, et toutes les colonnes optionnelles configurées.
        """
        cols = [self._col_id, self._col_nom]
        for col in (self._col_naissance, self._col_equipe, self._col_taille):
            if col is not None:
                cols.append(col)
        cols_present = [c for c in cols if c in self._df.columns]
        return self._df[cols_present].reset_index(drop=True)

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
            yield self._make_joueur(row)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self._make_joueur(self._df.iloc[idx])
        return self._copie(self._df.iloc[idx])

    def __repr__(self) -> str:
        return f"Joueurs({len(self)} joueurs | id='{self._col_id}', nom='{self._col_nom}')"

    # ------------------------------------------------------------------ #
    #  Helpers internes                                                    #
    # ------------------------------------------------------------------ #

    def _make_joueur(self, row: pd.Series) -> Joueur:
        return Joueur(
            row,
            self._col_id,
            self._col_nom,
            self._col_naissance,
            self._col_equipe,
            self._col_taille,
        )

    def _copie(self, df: pd.DataFrame) -> "Joueurs":
        return Joueurs(
            df,
            self._col_id,
            self._col_nom,
            self._col_naissance,
            self._col_equipe,
            self._col_taille,
        )

"""
Classe de base pour tous les loaders de sports.

Chaque loader hérite de BaseLoader et déclare simplement SPORT_FOLDER.
La mécanique commune (chemin racine, lecture CSV, parsing des dates) est
centralisée ici.

Pour ajouter un nouveau sport :
    1. Créer MonSportLoader(BaseLoader) avec SPORT_FOLDER = "mon_sport"
    2. Implémenter les méthodes load_X() en appelant self._load_csv(...)
    3. L'enregistrer dans load.py

Exemple minimal :
    class BadmintonLoader(BaseLoader):
        SPORT_FOLDER = "badminton"

        def load_players(self):
            return self._load_csv("player.csv")

        def load_matches(self):
            return self._load_csv("match.csv", date_cols=["date"])
"""

from abc import ABC
from pathlib import Path

import pandas as pd


class BaseLoader(ABC):
    """
    Infrastructure commune à tous les loaders de sports.

    Attributs de classe à définir dans chaque sous-classe :
        SPORT_FOLDER : str
            Nom du dossier dans Base_de_données/ (ex: "Basketball", "tennis").
    """

    _DATA_ROOT: Path = Path(__file__).parent.parent.parent / "data"
    SPORT_FOLDER: str = ""

    @property
    def root(self) -> Path:
        """Chemin absolu vers le dossier de données du sport."""
        return self._DATA_ROOT / self.SPORT_FOLDER

    def _load_csv(
        self,
        filename: str,
        dtype: dict | None = None,
        date_cols: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Charge un fichier CSV depuis le dossier du sport.

        Paramètres :
            filename  : nom du fichier (ex: "player.csv")
            dtype     : dictionnaire de types pour pd.read_csv (optionnel)
            date_cols : colonnes à convertir en datetime (optionnel)

        Retourne :
            DataFrame pandas prêt à l'emploi.
        """
        df = pd.read_csv(self.root / filename, dtype=dtype or {})
        for col in (date_cols or []):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

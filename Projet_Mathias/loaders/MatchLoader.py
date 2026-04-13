from pathlib import Path

import pandas as pd

from .TennisLoader import TennisLoader
from .BasketballLoader import BasketballLoader
from .FootballLoader import FootballLoader
from .LolLoader import LolLoader
from .VolleyballLoader import VolleyballLoader


class MatchLoader:
    """
    Charge les matchs d'un sport donné en s'appuyant sur les loaders dédiés.

    Sports supportés : 'tennis', 'basketball', 'football', 'lol', 'volleyball'

    Exemple d'utilisation :
        loader = MatchLoader("tennis")
        matchs = loader.load_all_matches()
        print(matchs.head())

        loader = MatchLoader("volleyball")
        matchs = loader.load_all_matches()
    """

    _SPORTS_VALIDES = {"tennis", "basketball", "football", "lol", "volleyball"}

    def __init__(self, sport: str) -> None:
        sport = sport.lower()
        if sport not in self._SPORTS_VALIDES:
            raise ValueError(
                f"Sport inconnu : {sport!r}. Sports valides : {self._SPORTS_VALIDES}"
            )
        self.sport = sport

    def load_all_matches(self) -> pd.DataFrame:
        """
        Retourne un DataFrame pandas de tous les matchs pour le sport configuré.

        Tennis      → fusion ATP + WTA, colonne 'circuit' ajoutée ('ATP' ou 'WTA')
        Basketball  → matchs NBA (load_matches)
        Football    → matchs des ligues européennes (load_games)
        LoL         → matchs EMEA (load_matches)
        Volleyball  → fusion hommes + femmes, colonne 'genre' ajoutée ('M' ou 'F')
        """
        if self.sport == "tennis":
            loader = TennisLoader()
            atp = loader.load_atp_matches()
            wta = loader.load_wta_matches()
            atp["circuit"] = "ATP"
            wta["circuit"] = "WTA"
            return pd.concat([atp, wta], ignore_index=True)

        elif self.sport == "basketball":
            return BasketballLoader().load_matches()

        elif self.sport == "football":
            return FootballLoader().load_games()

        elif self.sport == "lol":
            return LolLoader().load_matches()

        elif self.sport == "volleyball":
            loader = VolleyballLoader()
            hommes = loader.load_matches_men()
            femmes = loader.load_matches_women()
            hommes["genre"] = "M"
            femmes["genre"] = "F"
            return pd.concat([hommes, femmes], ignore_index=True)

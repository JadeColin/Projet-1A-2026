"""
Classe de base abstraite pour les modules analytiques sport.

Définit le contrat commun que tout module sport doit respecter pour s'intégrer
au menu terminal générique. Ajouter un nouveau sport = créer une classe qui
hérite de StatsSport et implémente ses méthodes abstraites.

Méthodes obligatoires (à implémenter dans chaque sport) :
    - classement(n)       : top N ranking (équipes ou joueurs selon le sport)
    - nb_joueurs()        : nombre de participants dans la base
    - nb_matchs()         : nombre de matchs dans la base
    - stats_entite(nom)   : stats détaillées d'une équipe ou d'un joueur

Méthodes optionnelles (à surcharger pour les sports collectifs) :
    - roster(nom_equipe)  : liste des joueurs d'une équipe

Méthodes concrètes (fournies, ne pas surcharger sauf cas spécifique) :
    - resume()            : dictionnaire de synthèse {joueurs, matchs}
    - est_collectif()     : True si le sport supporte la fonctionnalité roster

Exemple d'implémentation — Basketball :

    class BasketballStats(StatsSport):

        def __init__(self):
            loader = BasketballLoader()
            self._players, self._teams, self._matches = loader.load_all()

        def classement(self, n=10):
            return classement_points()

        def nb_joueurs(self):
            return len(self._players)

        def nb_matchs(self):
            return len(self._matches)

        def stats_entite(self, nom):
            return stats_equipe(nom)

        def roster(self, nom_equipe):
            return roster_equipe(nom_equipe)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class StatsSport(ABC):
    """
    Interface commune pour tous les modules analytiques sport.

    Garantit qu'un menu terminal peut interroger n'importe quel sport
    via les mêmes méthodes, sans connaître les détails de chaque base.

    Sports couverts (à titre d'exemple) :
        Collectifs  : Basketball, LoL, CS2, Football CL, Volleyball
        Individuels : Tennis, Échecs, Badminton, StarCraft II
    """


    @abstractmethod
    def classement(self, n: int = 10) -> pd.DataFrame:
        """
        Classement principal du sport par victoires (top N).

        - Sports collectifs  : une ligne = une équipe.
        - Sports individuels : une ligne = un joueur.

        Colonnes minimales attendues : entité (équipe ou joueur), Victoires.
        Le DataFrame doit être trié par Victoires décroissantes.
        """
        ...

    @abstractmethod
    def nb_joueurs(self) -> int:
        """Nombre total de joueurs/participants dans la base de données."""
        ...

    @abstractmethod
    def nb_matchs(self) -> int:
        """Nombre total de matchs dans la base de données."""
        ...

    @abstractmethod
    def stats_entite(self, nom: str) -> pd.DataFrame:
        """
        Statistiques détaillées pour une entité nommée.

        - Sports collectifs  : statistiques moyennes par match d'une équipe.
        - Sports individuels : statistiques sur la saison d'un joueur.

        Paramètre :
            nom : nom (ou sous-chaîne) de l'équipe ou du joueur à rechercher.

        Lève ValueError si l'entité n'est pas trouvée.
        """
        ...

    def roster(self, nom_equipe: str) -> pd.DataFrame:
        """
        Roster d'une équipe : liste des joueurs (et staff si disponible).

        Disponible uniquement pour les sports collectifs.
        Par défaut lève NotImplementedError — surcharger dans les sports
        collectifs (Basketball, LoL, CS2…).

        Paramètre :
            nom_equipe : nom (ou sous-chaîne) de l'équipe.

        Lève ValueError si l'équipe n'est pas trouvée.
        """
        raise NotImplementedError(
            f"{type(self).__name__} ne supporte pas la fonctionnalité 'roster' "
            f"(sport individuel ou données non disponibles)."
        )


    def resume(self) -> dict:
        """
        Résumé général de la base de données du sport.

        Retourne un dictionnaire avec les clés :
            - 'joueurs' : nombre de joueurs/participants (int)
            - 'matchs'  : nombre de matchs (int)

        Exemple :
            {'joueurs': 539, 'matchs': 1230}
        """
        return {
            "joueurs": self.nb_joueurs(),
            "matchs": self.nb_matchs(),
        }

    def est_collectif(self) -> bool:
        """
        Indique si ce sport supporte la fonctionnalité roster().

        Retourne True si la méthode roster() a été surchargée dans la
        sous-classe (i.e. ce n'est plus la version par défaut qui lève
        NotImplementedError).

        Utilisation typique dans le menu :
            if sport.est_collectif():
                print("3. Roster d'une équipe")
        """
        return type(self).roster is not StatsSport.roster

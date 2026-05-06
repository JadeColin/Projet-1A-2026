"""
Application de statistiques sportives — interface en ligne de commande.

Lancement :
    python -m Projet_Mathias.app.main
"""

from src.Model.sport import (
    TypeSport,
    CategorieSport,
    TypeCompetition,
    filtrer,
)


# ── Configuration des stats par sport ────────────────────────────────────────


def _make_sports_config() -> dict:
    """Retourne la configuration complète de chaque sport."""
    import src.Analysis.basketball as bk
    import src.Analysis.lol as lol
    import src.Analysis.football_cl as fcl
    import src.Analysis.tennis as tn
    import src.Analysis.chess as ch
    import src.Analysis.volleyball as vb

    return {
        "Basketball": {
            "stats": [
                {
                    "label": "Classement équipes",
                    "fn": bk.classement_points,
                    "inputs": [],
                },
                {
                    "label": "Top équipes offensives",
                    "fn": bk.top_equipes_offensives,
                    "inputs": [],
                },
                {
                    "label": "Stats d'une équipe",
                    "fn": bk.stats_equipe,
                    "inputs": [{"key": "team_name", "label": "Nom / abrév. équipe"}],
                },
                {
                    "label": "Roster d'une équipe",
                    "fn": bk.roster_equipe,
                    "inputs": [{"key": "team_name", "label": "Nom / abrév. équipe"}],
                },
            ]
        },
        "League of Legends": {
            "stats": [
                {
                    "label": "Classement EMEA",
                    "fn": lol.classement_points,
                    "inputs": [],
                },
                {
                    "label": "Stats d'une équipe",
                    "fn": lol.stats_equipe,
                    "inputs": [{"key": "team_name", "label": "Nom équipe"}],
                },
                {
                    "label": "Champions pickés / bannés",
                    "fn": lol.champions_picks_bans,
                    "inputs": [],
                },
                {
                    "label": "Durée moyenne des parties",
                    "fn": lol.duree_moyenne_parties,
                    "inputs": [],
                },
            ]
        },
        "Football Champions L.": {
            "stats": [
                {
                    "label": "Meilleurs buteurs",
                    "fn": fcl.meilleurs_buteurs,
                    "inputs": [],
                },
                {
                    "label": "Meilleurs passeurs",
                    "fn": fcl.meilleurs_passeurs,
                    "inputs": [],
                },
                {
                    "label": "Stats d'une équipe",
                    "fn": fcl.stats_equipe,
                    "inputs": [{"key": "team_name", "label": "Nom équipe"}],
                },
                {
                    "label": "Résultats par phase",
                    "fn": fcl.resultats_par_phase,
                    "inputs": [],
                },
            ]
        },
        "Tennis": {
            "stats": [
                {
                    "label": "Classement ATP (victoires)",
                    "fn": lambda: tn.classement_victoires("ATP"),
                    "inputs": [],
                },
                {
                    "label": "Classement WTA (victoires)",
                    "fn": lambda: tn.classement_victoires("WTA"),
                    "inputs": [],
                },
                {
                    "label": "Stats d'un joueur ATP",
                    "fn": lambda player_name: tn.stats_joueur(player_name, "ATP"),
                    "inputs": [{"key": "player_name", "label": "Nom joueur"}],
                },
                {
                    "label": "Stats d'une joueuse WTA",
                    "fn": lambda player_name: tn.stats_joueur(player_name, "WTA"),
                    "inputs": [{"key": "player_name", "label": "Nom joueuse"}],
                },
                {
                    "label": "Résultats par surface (ATP)",
                    "fn": lambda: tn.resultats_par_surface("ATP"),
                    "inputs": [],
                },
                {
                    "label": "Résultats par surface (WTA)",
                    "fn": lambda: tn.resultats_par_surface("WTA"),
                    "inputs": [],
                },
                {
                    "label": "Stats par tournoi (ATP)",
                    "fn": lambda: tn.stats_par_tournoi("ATP"),
                    "inputs": [],
                },
                {
                    "label": "Stats par tournoi (WTA)",
                    "fn": lambda: tn.stats_par_tournoi("WTA"),
                    "inputs": [],
                },
            ]
        },
        "Échecs": {
            "stats": [
                {
                    "label": "Classement Elo Standard",
                    "fn": lambda: ch.classement_elo("standard"),
                    "inputs": [],
                },
                {
                    "label": "Classement Elo Rapid",
                    "fn": lambda: ch.classement_elo("rapid"),
                    "inputs": [],
                },
                {
                    "label": "Classement Elo Blitz",
                    "fn": lambda: ch.classement_elo("blitz"),
                    "inputs": [],
                },
                {
                    "label": "Bilan d'un joueur",
                    "fn": ch.bilan_joueur,
                    "inputs": [{"key": "player_name", "label": "Nom joueur"}],
                },
                {
                    "label": "Stats par titre FIDE",
                    "fn": ch.stats_par_titre,
                    "inputs": [],
                },
            ]
        },
        "Volleyball": {
            "stats": [
                {
                    "label": "Classement Hommes",
                    "fn": lambda: vb.classement("hommes"),
                    "inputs": [],
                },
                {
                    "label": "Classement Femmes",
                    "fn": lambda: vb.classement("femmes"),
                    "inputs": [],
                },
                {
                    "label": "Bilan équipe Hommes",
                    "fn": lambda team_code: vb.bilan_equipe(team_code, "hommes"),
                    "inputs": [{"key": "team_code", "label": "Code pays (ex : FRA)"}],
                },
                {
                    "label": "Bilan équipe Femmes",
                    "fn": lambda team_code: vb.bilan_equipe(team_code, "femmes"),
                    "inputs": [{"key": "team_code", "label": "Code pays (ex : FRA)"}],
                },
                {
                    "label": "Joueurs d'un pays (H)",
                    "fn": lambda country_code: vb.stats_joueurs_par_pays(country_code, "hommes"),
                    "inputs": [{"key": "country_code", "label": "Code pays (ex : FRA)"}],
                },
                {
                    "label": "Joueuses d'un pays (F)",
                    "fn": lambda country_code: vb.stats_joueurs_par_pays(country_code, "femmes"),
                    "inputs": [{"key": "country_code", "label": "Code pays (ex : FRA)"}],
                },
            ]
        },
    }


# ── Affichage ─────────────────────────────────────────────────────────────────

_SEP = "─" * 54


def _titre(texte: str) -> None:
    print(f"\n{_SEP}")
    print(f"  {texte}")
    print(_SEP)


def _option(num, texte: str) -> None:
    print(f"  [{num}]  {texte}")


def _nav(peut_reculer: bool = True, peut_avancer: bool = False) -> None:
    parts = []
    if peut_reculer:
        parts.append("[-] Retour")
    if peut_avancer:
        parts.append("[+] Suivant")
    parts.append("[q] Quitter")
    print(f"\n  {' | '.join(parts)}")


def _lire(prompt: str = "Votre choix : ") -> str:
    return input(f"\n  {prompt}").strip()


def _afficher_resultat(result) -> None:
    """Affiche un résultat : DataFrame retourné ou impression directe déjà faite."""
    import pandas as pd
    if isinstance(result, pd.DataFrame):
        if result.empty:
            print("  (aucun résultat)")
        else:
            print(result.to_string(index=False))


# ── Moteur de navigation ──────────────────────────────────────────────────────
#
# Chaque "page" est un callable() → str | callable | None
#   callable  → naviguer vers cette nouvelle page
#   'back'    → reculer dans l'historique
#   'forward' → avancer dans l'historique
#   'quit'    → quitter l'application
#   None      → rester sur la page (réafficher)
#


class CLI:
    def __init__(self):
        self._back: list = []
        self._fwd: list = []
        self._filters: dict = {
            "type_sport": None,        # TypeSport | None
            "categorie": None,         # CategorieSport | None
            "type_competition": None,  # TypeCompetition | None
        }
        self._config: dict | None = None

    # ── Boucle principale ─────────────────────────────────────────────────────

    def run(self) -> None:
        self._config = _make_sports_config()
        current = self._page_accueil
        while current is not None:
            result = current()
            if result == "quit":
                print("\n  Au revoir !\n")
                break
            elif result == "back":
                if self._back:
                    self._fwd.append(current)
                    current = self._back.pop()
                else:
                    print("  (déjà au début de la navigation)")
            elif result == "forward":
                if self._fwd:
                    self._back.append(current)
                    current = self._fwd.pop()
                else:
                    print("  (déjà à la fin de la navigation)")
            elif callable(result):
                self._back.append(current)
                self._fwd.clear()
                current = result
            # None → rester sur la page courante (réafficher)

    # ── Utilitaires ───────────────────────────────────────────────────────────

    def _sports_visibles(self) -> list:
        """Retourne les sports filtrés ET disponibles dans la config."""
        sports = filtrer(
            type_sport=self._filters["type_sport"],
            categorie=self._filters["categorie"],
            type_competition=self._filters["type_competition"],
        )
        return [s for s in sports if s.nom in self._config]

    def _filtres_str(self) -> str:
        vals = [str(v) for v in self._filters.values() if v is not None]
        return ", ".join(vals) if vals else "Aucun"

    # ── Page : accueil ────────────────────────────────────────────────────────

    def _page_accueil(self):
        sports = self._sports_visibles()
        _titre("Stats Sports — Menu principal")
        print(f"  Filtres actifs : {self._filtres_str()}")
        print()
        _option(0, "Filtres")
        for i, sport in enumerate(sports, 1):
            _option(i, sport.nom)
        _nav(peut_reculer=False, peut_avancer=bool(self._fwd))

        choix = _lire()

        if choix == "q":
            return "quit"
        if choix == "+":
            return "forward"
        if choix == "0":
            return self._page_filtres
        if choix.isdigit():
            idx = int(choix) - 1
            if 0 <= idx < len(sports):
                return self._make_page_sport(sports[idx])
            print("  Numéro invalide.")
        else:
            print("  Commande non reconnue.")
        return None

    # ── Page : filtres ────────────────────────────────────────────────────────

    def _page_filtres(self):
        f = self._filters

        def coche(condition: bool) -> str:
            return " [✓]" if condition else ""

        _titre("Filtres — logique ET (combinez librement)")

        print("  Format :")
        _option(1, f"Collectif{coche(f['type_sport'] == TypeSport.COLLECTIF)}")
        _option(2, f"Individuel{coche(f['type_sport'] == TypeSport.INDIVIDUEL)}")
        _option(3, "Réinitialiser format")

        print("\n  Discipline :")
        _option(4, f"Sport{coche(f['categorie'] == CategorieSport.SPORT)}")
        _option(5, f"E-sport{coche(f['categorie'] == CategorieSport.ESPORT)}")
        _option(6, "Réinitialiser discipline")

        print("\n  Compétition :")
        _option(7, f"Par points{coche(f['type_competition'] == TypeCompetition.POINTS)}")
        _option(8, f"Éliminatoire{coche(f['type_competition'] == TypeCompetition.ELIMINATOIRE)}")
        _option(9, f"Mixte{coche(f['type_competition'] == TypeCompetition.MIXTE)}")
        _option(10, "Réinitialiser compétition")

        _nav(peut_avancer=bool(self._fwd))

        choix = _lire()

        _MAP = {
            "1":  ("type_sport",       TypeSport.COLLECTIF),
            "2":  ("type_sport",       TypeSport.INDIVIDUEL),
            "3":  ("type_sport",       None),
            "4":  ("categorie",        CategorieSport.SPORT),
            "5":  ("categorie",        CategorieSport.ESPORT),
            "6":  ("categorie",        None),
            "7":  ("type_competition", TypeCompetition.POINTS),
            "8":  ("type_competition", TypeCompetition.ELIMINATOIRE),
            "9":  ("type_competition", TypeCompetition.MIXTE),
            "10": ("type_competition", None),
        }

        if choix == "q":
            return "quit"
        if choix == "-":
            return "back"
        if choix == "+":
            return "forward"
        if choix in _MAP:
            cle, val = _MAP[choix]
            self._filters[cle] = val
            # Rester sur la page pour permettre de combiner plusieurs filtres
        else:
            print("  Commande non reconnue.")
        return None

    # ── Page : sport ──────────────────────────────────────────────────────────

    def _make_page_sport(self, sport):
        config = self._config[sport.nom]

        def page():
            _titre(sport.nom)
            stats = config["stats"]
            for i, stat in enumerate(stats, 1):
                _option(i, stat["label"])
            _nav(peut_avancer=bool(self._fwd))

            choix = _lire()

            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix == "+":
                return "forward"
            if choix.isdigit():
                idx = int(choix) - 1
                if 0 <= idx < len(stats):
                    return self._make_page_stat(stats[idx])
                print("  Numéro invalide.")
            else:
                print("  Commande non reconnue.")
            return None

        return page

    # ── Page : stat ───────────────────────────────────────────────────────────

    def _make_page_stat(self, stat):
        def page():
            _titre(stat["label"])

            kwargs = {}
            for inp in stat["inputs"]:
                val = input(f"  {inp['label']} : ").strip()
                if not val:
                    print("  Saisie annulée.")
                    return "back"
                kwargs[inp["key"]] = val

            print()
            try:
                result = stat["fn"](**kwargs)
                _afficher_resultat(result)
            except ValueError as e:
                print(f"  Erreur : {e}")
            except Exception as e:
                print(f"  Erreur inattendue : {e}")

            print(f"\n{_SEP}")
            _nav(peut_avancer=bool(self._fwd))

            choix = _lire()
            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix == "+":
                return "forward"
            return None

        return page


# ── Point d'entrée ────────────────────────────────────────────────────────────


def main() -> None:
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()

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
    import src.Analysis.cs2 as cs2
    import src.Analysis.starcraft2 as sc2
    import src.Analysis.badminton as bad

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
                    "inputs": [],
                    "selector": {
                        "key": "team_name",
                        "label": "Sélectionnez une équipe",
                        "options_fn": lambda: (bk._load(), bk._teams.sort_values("full_name")["full_name"].tolist())[1],
                    },
                },
                {
                    "label": "Roster d'une équipe",
                    "fn": bk.roster_equipe,
                    "inputs": [],
                    "selector": {
                        "key": "team_name",
                        "label": "Sélectionnez une équipe",
                        "options_fn": lambda: (bk._load(), bk._teams.sort_values("full_name")["full_name"].tolist())[1],
                    },
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
                    "inputs": [],
                    "selector": {
                        "key": "team_name",
                        "label": "Sélectionnez une équipe",
                        "options_fn": lambda: (lol._load(), sorted(set(lol._matches["team_blue"].dropna().tolist() + lol._matches["team_red"].dropna().tolist())))[1],
                    },
                },
                {
                    "label": "Champions pickés / bannés",
                    "fn": lol.champions_picks_bans,
                    "inputs": [],
                },
                {
                    "label": "Roster d'une équipe",
                    "fn": lol.roster_equipe,
                    "inputs": [],
                    "selector": {
                        "key": "team_name",
                        "label": "Sélectionnez une équipe",
                        "options_fn": lambda: (lol._load(), lol._players["team"].dropna().sort_values().unique().tolist())[1],
                    },
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
                    "inputs": [],
                    "selector": {
                        "key": "team_name",
                        "label": "Sélectionnez une équipe",
                        "options_fn": lambda: (fcl._load(), fcl._players["club"].dropna().sort_values().unique().tolist())[1],
                    },
                },
                {
                    "label": "Roster d'un club",
                    "fn": lambda club: fcl.liste_joueurs(club=club),
                    "inputs": [],
                    "selector": {
                        "key": "club",
                        "label": "Sélectionnez un club",
                        "options_fn": lambda: (fcl._load(), fcl._players["club"].dropna().sort_values().unique().tolist())[1],
                    },
                },
                {
                    "label": "Bracket",
                    "fn": fcl.bracket,
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
                    "inputs": [],
                    "selector": {
                        "key": "player_name",
                        "label": "Sélectionnez un joueur",
                        "options_fn": lambda: (tn._load(), tn._atp_players["full_name"].dropna().sort_values().tolist())[1],
                    },
                },
                {
                    "label": "Stats d'une joueuse WTA",
                    "fn": lambda player_name: tn.stats_joueur(player_name, "WTA"),
                    "inputs": [],
                    "selector": {
                        "key": "player_name",
                        "label": "Sélectionnez une joueuse",
                        "options_fn": lambda: (tn._load(), tn._wta_players["full_name"].dropna().sort_values().tolist())[1],
                    },
                },
                {
                    "label": "Bracket ATP (Grand Chelem)",
                    "fn": lambda tourney_name: tn.bracket(tourney_name, "ATP"),
                    "inputs": [],
                    "selector": {
                        "key": "tourney_name",
                        "label": "Sélectionnez un tournoi",
                        "options_fn": lambda: (tn._load(), sorted(tn._atp_matches[tn._atp_matches["tourney_level"] == "G"]["tourney_name"].unique().tolist()))[1],
                    },
                },
                {
                    "label": "Bracket WTA (Grand Chelem)",
                    "fn": lambda tourney_name: tn.bracket(tourney_name, "WTA"),
                    "inputs": [],
                    "selector": {
                        "key": "tourney_name",
                        "label": "Sélectionnez un tournoi",
                        "options_fn": lambda: (tn._load(), sorted(tn._wta_matches[tn._wta_matches["tourney_level"] == "G"]["tourney_name"].unique().tolist()))[1],
                    },
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
                    "inputs": [],
                    "selector": {
                        "key": "player_name",
                        "label": "Sélectionnez un joueur",
                        "options_fn": lambda: (ch._load(), ch._players["name"].dropna().sort_values().tolist())[1],
                    },
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
                    "inputs": [],
                    "selector": {
                        "key": "team_code",
                        "label": "Sélectionnez un pays",
                        "options_fn": lambda: (vb._load(), sorted(set(vb._matches_men["country_code_1"].dropna().tolist() + vb._matches_men["country_code_2"].dropna().tolist())))[1],
                    },
                },
                {
                    "label": "Bilan équipe Femmes",
                    "fn": lambda team_code: vb.bilan_equipe(team_code, "femmes"),
                    "inputs": [],
                    "selector": {
                        "key": "team_code",
                        "label": "Sélectionnez un pays",
                        "options_fn": lambda: (vb._load(), sorted(set(vb._matches_women["country_code_1"].dropna().tolist() + vb._matches_women["country_code_2"].dropna().tolist())))[1],
                    },
                },
                {
                    "label": "Joueurs d'un pays (H)",
                    "fn": lambda country_code: vb.liste_joueurs(genre="hommes", equipe=country_code),
                    "inputs": [],
                    "selector": {
                        "key": "country_code",
                        "label": "Sélectionnez un pays",
                        "options_fn": lambda: (vb._load(), vb._players_men["country_code"].dropna().sort_values().unique().tolist())[1],
                    },
                },
                {
                    "label": "Joueuses d'un pays (F)",
                    "fn": lambda country_code: vb.liste_joueurs(genre="femmes", equipe=country_code),
                    "inputs": [],
                    "selector": {
                        "key": "country_code",
                        "label": "Sélectionnez un pays",
                        "options_fn": lambda: (vb._load(), vb._players_women["country_code"].dropna().sort_values().unique().tolist())[1],
                    },
                },
            ]
        },
        "CS2": {
            "stats": [
                {
                    "label": "Classement stages",
                    "fn": cs2.classement_stages,
                    "inputs": [],
                },
                {
                    "label": "Bracket",
                    "fn": cs2.bracket,
                    "inputs": [],
                },
                {
                    "label": "Stats d'une équipe",
                    "fn": cs2.stats_equipe,
                    "inputs": [],
                    "selector": {
                        "key": "team_name",
                        "label": "Sélectionnez une équipe",
                        "options_fn": lambda: (cs2._load(), cs2._players["team"].dropna().sort_values().unique().tolist())[1],
                    },
                },
                {
                    "label": "Roster d'une équipe",
                    "fn": cs2.roster_equipe,
                    "inputs": [],
                    "selector": {
                        "key": "team_name",
                        "label": "Sélectionnez une équipe",
                        "options_fn": lambda: (cs2._load(), cs2._players["team"].dropna().sort_values().unique().tolist())[1],
                    },
                },
            ]
        },
        "StarCraft II": {
            "stats": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": lambda nom: sc2.fiche_joueur_sc2(nom),
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur",
                        "options_fn": lambda: (sc2._load(), sc2._players["name"].dropna().sort_values().tolist())[1],
                    },
                },
            ]
        },
        "Badminton": {
            "stats": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": lambda nom: bad.fiche_joueur_badminton(nom),
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur",
                        "options_fn": lambda: (bad._load(), bad._players["name"].dropna().sort_values().tolist())[1],
                    },
                },
                {
                    "label": "Bracket",
                    "fn": bad.bracket,
                    "inputs": [],
                    "selector": {
                        "key": "tournament_name",
                        "label": "Sélectionnez un tournoi",
                        "options_fn": lambda: (bad._load(), sorted(bad._matches[bad._matches["round"] == "Final"]["tournament"].dropna().unique().tolist()))[1],
                    },
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

            # Sélecteur numéroté (liste d'options prédéfinies)
            sel = stat.get("selector")
            if sel:
                try:
                    options = sel["options_fn"]()
                except Exception as e:
                    print(f"  Erreur lors du chargement des options : {e}")
                    return "back"

                print(f"  {sel['label']} :\n")
                for i, opt in enumerate(options, 1):
                    _option(i, opt)
                _nav(peut_avancer=bool(self._fwd))

                choix = _lire()
                if choix == "q":
                    return "quit"
                if choix == "-":
                    return "back"
                if choix == "+":
                    return "forward"
                if not choix.isdigit() or not (1 <= int(choix) <= len(options)):
                    print("  Numéro invalide.")
                    return None
                kwargs[sel["key"]] = options[int(choix) - 1]

            # Champs libres
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

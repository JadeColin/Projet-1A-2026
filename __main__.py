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
#
# Chaque sport possède :
#   collectif : bool  — True → propose Équipe / Joueurs
#   genre     : bool  — True → propose Hommes / Femmes en premier
#
# Pour un sport collectif sans genre :
#   {"collectif": True, "genre": False, "equipe": [...], "joueurs": [...]}
#
# Pour un sport collectif avec genre :
#   {"collectif": True, "genre": True,
#    "hommes": {"equipe": [...], "joueurs": [...]},
#    "femmes": {"equipe": [...], "joueurs": [...]}}
#
# Pour un sport individuel sans genre :
#   {"collectif": False, "genre": False, "stats": [...]}
#
# Pour un sport individuel avec genre :
#   {"collectif": False, "genre": True, "hommes": [...], "femmes": [...]}
#


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
            "collectif": True,
            "genre": False,
            "equipe": [
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
            ],
            "joueurs": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": bk.fiche_joueur_basketball,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (Basketball)",
                        "options_df_fn": lambda: (
                            bk._load(),
                            bk._players[["full_name", "team_id", "birthdate"]].merge(
                                bk._teams[["id", "full_name"]].rename(
                                    columns={"id": "team_id", "full_name": "Équipe"}
                                ),
                                on="team_id", how="left",
                            )[["full_name", "Équipe", "birthdate"]]
                        )[1],
                        "col_display": "full_name",
                        "filters": [
                            {"label": "Équipe",    "col": "Équipe",    "type": "category"},
                            {"label": "Naissance", "col": "birthdate", "type": "year"},
                        ],
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
            ],
        },
        "League of Legends": {
            "collectif": True,
            "genre": False,
            "equipe": [
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
            ],
            "joueurs": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": lol.fiche_joueur_lol,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (LoL)",
                        "options_df_fn": lambda: (
                            lol._load(),
                            lol._players[["name", "team", "country_of_birth", "birthdate"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Équipe",    "col": "team",             "type": "category"},
                            {"label": "Pays",      "col": "country_of_birth", "type": "category"},
                            {"label": "Naissance", "col": "birthdate",        "type": "year"},
                        ],
                    },
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
            ],
        },
        "Football Champions L.": {
            "collectif": True,
            "genre": False,
            "equipe": [
                {
                    "label": "Bracket",
                    "fn": fcl.bracket,
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
            ],
            "joueurs": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": fcl.fiche_joueur_fcl,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (Football CL)",
                        "options_df_fn": lambda: (
                            fcl._load(),
                            fcl._players[["player_name", "club"]]
                        )[1],
                        "col_display": "player_name",
                        "filters": [
                            {"label": "Club", "col": "club", "type": "category"},
                        ],
                    },
                },
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
                    "label": "Roster d'un club",
                    "fn": lambda club: fcl.liste_joueurs(club=club),
                    "inputs": [],
                    "selector": {
                        "key": "club",
                        "label": "Sélectionnez un club",
                        "options_fn": lambda: (fcl._load(), fcl._players["club"].dropna().sort_values().unique().tolist())[1],
                    },
                },
            ],
        },
        "Tennis": {
            "collectif": False,
            "genre": True,
            "hommes": [
                {
                    "label": "Classement ATP (victoires)",
                    "fn": lambda: tn.classement_victoires("ATP"),
                    "inputs": [],
                },
                {
                    "label": "Fiche d'un joueur",
                    "fn": lambda nom: tn.fiche_joueur_tennis(nom, "ATP"),
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (Tennis ATP)",
                        "options_df_fn": lambda: (
                            tn._load(),
                            tn._atp_players[["full_name", "ioc", "dob"]]
                        )[1],
                        "col_display": "full_name",
                        "filters": [
                            {"label": "Pays (IOC)", "col": "ioc", "type": "category"},
                            {"label": "Naissance",  "col": "dob", "type": "year"},
                        ],
                    },
                },
                {
                    "label": "Stats d'un joueur",
                    "fn": lambda player_name: tn.stats_joueur(player_name, "ATP"),
                    "inputs": [],
                    "selector": {
                        "key": "player_name",
                        "label": "Sélectionnez un joueur (Tennis ATP)",
                        "options_df_fn": lambda: (
                            tn._load(),
                            tn._atp_players[["full_name", "ioc", "dob"]]
                        )[1],
                        "col_display": "full_name",
                        "filters": [
                            {"label": "Pays (IOC)", "col": "ioc", "type": "category"},
                            {"label": "Naissance",  "col": "dob", "type": "year"},
                        ],
                    },
                },
                {
                    "label": "Bracket (Grand Chelem)",
                    "fn": lambda tourney_name: tn.bracket(tourney_name, "ATP"),
                    "inputs": [],
                    "selector": {
                        "key": "tourney_name",
                        "label": "Sélectionnez un tournoi",
                        "options_fn": lambda: (tn._load(), sorted(tn._atp_matches[tn._atp_matches["tourney_level"] == "G"]["tourney_name"].unique().tolist()))[1],
                    },
                },
            ],
            "femmes": [
                {
                    "label": "Classement WTA (victoires)",
                    "fn": lambda: tn.classement_victoires("WTA"),
                    "inputs": [],
                },
                {
                    "label": "Fiche d'une joueuse",
                    "fn": lambda nom: tn.fiche_joueur_tennis(nom, "WTA"),
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez une joueuse (Tennis WTA)",
                        "options_df_fn": lambda: (
                            tn._load(),
                            tn._wta_players[["full_name", "ioc", "dob"]]
                        )[1],
                        "col_display": "full_name",
                        "filters": [
                            {"label": "Pays (IOC)", "col": "ioc", "type": "category"},
                            {"label": "Naissance",  "col": "dob", "type": "year"},
                        ],
                    },
                },
                {
                    "label": "Stats d'une joueuse",
                    "fn": lambda player_name: tn.stats_joueur(player_name, "WTA"),
                    "inputs": [],
                    "selector": {
                        "key": "player_name",
                        "label": "Sélectionnez une joueuse (Tennis WTA)",
                        "options_df_fn": lambda: (
                            tn._load(),
                            tn._wta_players[["full_name", "ioc", "dob"]]
                        )[1],
                        "col_display": "full_name",
                        "filters": [
                            {"label": "Pays (IOC)", "col": "ioc", "type": "category"},
                            {"label": "Naissance",  "col": "dob", "type": "year"},
                        ],
                    },
                },
                {
                    "label": "Bracket (Grand Chelem)",
                    "fn": lambda tourney_name: tn.bracket(tourney_name, "WTA"),
                    "inputs": [],
                    "selector": {
                        "key": "tourney_name",
                        "label": "Sélectionnez un tournoi",
                        "options_fn": lambda: (tn._load(), sorted(tn._wta_matches[tn._wta_matches["tourney_level"] == "G"]["tourney_name"].unique().tolist()))[1],
                    },
                },
            ],
        },
        "Échecs": {
            "collectif": False,
            "genre": False,
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
                    "label": "Fiche d'un joueur",
                    "fn": ch.fiche_joueur_chess,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (Échecs)",
                        "options_df_fn": lambda: (
                            ch._load(),
                            ch._players[["name", "federation", "birth_year"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Fédération", "col": "federation",  "type": "category"},
                            {"label": "Naissance",  "col": "birth_year",  "type": "year"},
                        ],
                    },
                },
                {
                    "label": "Bilan d'un joueur",
                    "fn": ch.bilan_joueur,
                    "inputs": [],
                    "selector": {
                        "key": "player_name",
                        "label": "Sélectionnez un joueur (Échecs)",
                        "options_df_fn": lambda: (
                            ch._load(),
                            ch._players[["name", "federation", "birth_year"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Fédération", "col": "federation",  "type": "category"},
                            {"label": "Naissance",  "col": "birth_year",  "type": "year"},
                        ],
                    },
                },
                {
                    "label": "Stats par titre FIDE",
                    "fn": ch.stats_par_titre,
                    "inputs": [],
                },
            ],
        },
        "Volleyball": {
            "collectif": True,
            "genre": True,
            "hommes": {
                "equipe": [
                    {
                        "label": "Classement",
                        "fn": lambda: vb.classement("hommes"),
                        "inputs": [],
                    },
                    {
                        "label": "Bilan d'une équipe",
                        "fn": lambda team_code: vb.bilan_equipe(team_code, "hommes"),
                        "inputs": [],
                        "selector": {
                            "key": "team_code",
                            "label": "Sélectionnez un pays",
                            "options_fn": lambda: (vb._load(), sorted(set(vb._matches_men["country_code_1"].dropna().tolist() + vb._matches_men["country_code_2"].dropna().tolist())))[1],
                        },
                    },
                ],
                "joueurs": [
                    {
                        "label": "Fiche d'un joueur",
                        "fn": lambda nom: vb.fiche_joueur_volleyball(nom, "hommes"),
                        "inputs": [],
                        "selector": {
                            "key": "nom",
                            "label": "Sélectionnez un joueur (Volleyball Hommes)",
                            "options_df_fn": lambda: (
                                vb._load(),
                                vb._players_men[["name", "country_code", "birth_date"]]
                            )[1],
                            "col_display": "name",
                            "filters": [
                                {"label": "Pays",      "col": "country_code", "type": "category"},
                                {"label": "Naissance", "col": "birth_date",   "type": "year"},
                            ],
                        },
                    },
                    {
                        "label": "Joueurs d'un pays",
                        "fn": lambda country_code: vb.liste_joueurs(genre="hommes", equipe=country_code),
                        "inputs": [],
                        "selector": {
                            "key": "country_code",
                            "label": "Sélectionnez un pays",
                            "options_fn": lambda: (vb._load(), vb._players_men["country_code"].dropna().sort_values().unique().tolist())[1],
                        },
                    },
                ],
            },
            "femmes": {
                "equipe": [
                    {
                        "label": "Classement",
                        "fn": lambda: vb.classement("femmes"),
                        "inputs": [],
                    },
                    {
                        "label": "Bilan d'une équipe",
                        "fn": lambda team_code: vb.bilan_equipe(team_code, "femmes"),
                        "inputs": [],
                        "selector": {
                            "key": "team_code",
                            "label": "Sélectionnez un pays",
                            "options_fn": lambda: (vb._load(), sorted(set(vb._matches_women["country_code_1"].dropna().tolist() + vb._matches_women["country_code_2"].dropna().tolist())))[1],
                        },
                    },
                ],
                "joueurs": [
                    {
                        "label": "Fiche d'une joueuse",
                        "fn": lambda nom: vb.fiche_joueur_volleyball(nom, "femmes"),
                        "inputs": [],
                        "selector": {
                            "key": "nom",
                            "label": "Sélectionnez une joueuse (Volleyball Femmes)",
                            "options_df_fn": lambda: (
                                vb._load(),
                                vb._players_women[["name", "country_code", "birth_date"]]
                            )[1],
                            "col_display": "name",
                            "filters": [
                                {"label": "Pays",      "col": "country_code", "type": "category"},
                                {"label": "Naissance", "col": "birth_date",   "type": "year"},
                            ],
                        },
                    },
                    {
                        "label": "Joueuses d'un pays",
                        "fn": lambda country_code: vb.liste_joueurs(genre="femmes", equipe=country_code),
                        "inputs": [],
                        "selector": {
                            "key": "country_code",
                            "label": "Sélectionnez un pays",
                            "options_fn": lambda: (vb._load(), vb._players_women["country_code"].dropna().sort_values().unique().tolist())[1],
                        },
                    },
                ],
            },
        },
        "CS2": {
            "collectif": True,
            "genre": False,
            "equipe": [
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
            ],
            "joueurs": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": cs2.fiche_joueur_cs2,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (CS2)",
                        "options_df_fn": lambda: (
                            cs2._load(),
                            cs2._players[["name", "team", "nationality", "birthdate"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Équipe",      "col": "team",        "type": "category"},
                            {"label": "Nationalité", "col": "nationality", "type": "category"},
                            {"label": "Naissance",   "col": "birthdate",   "type": "year"},
                        ],
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
            ],
        },
        "StarCraft II": {
            "collectif": False,
            "genre": False,
            "stats": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": sc2.fiche_joueur_sc2,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (StarCraft II)",
                        "options_df_fn": lambda: (
                            sc2._load(),
                            sc2._players[["name", "team", "nationality", "birthdate"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Équipe",      "col": "team",        "type": "category"},
                            {"label": "Nationalité", "col": "nationality", "type": "category"},
                            {"label": "Naissance",   "col": "birthdate",   "type": "year"},
                        ],
                    },
                },
                {
                    "label": "Bilan d'un joueur",
                    "fn": sc2.bilan_joueur_sc2,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (StarCraft II)",
                        "options_df_fn": lambda: (
                            sc2._load(),
                            sc2._players[["name", "team", "nationality", "birthdate"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Équipe",      "col": "team",        "type": "category"},
                            {"label": "Nationalité", "col": "nationality", "type": "category"},
                            {"label": "Naissance",   "col": "birthdate",   "type": "year"},
                        ],
                    },
                },
            ],
        },
        "Badminton": {
            "collectif": False,
            "genre": False,
            "stats": [
                {
                    "label": "Fiche d'un joueur",
                    "fn": bad.fiche_joueur_badminton,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (Badminton)",
                        "options_df_fn": lambda: (
                            bad._load(),
                            bad._players[["name", "country"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Pays", "col": "country", "type": "category"},
                        ],
                    },
                },
                {
                    "label": "Bilan d'un joueur",
                    "fn": bad.bilan_joueur_badminton,
                    "inputs": [],
                    "selector": {
                        "key": "nom",
                        "label": "Sélectionnez un joueur (Badminton)",
                        "options_df_fn": lambda: (
                            bad._load(),
                            bad._players[["name", "country"]]
                        )[1],
                        "col_display": "name",
                        "filters": [
                            {"label": "Pays", "col": "country", "type": "category"},
                        ],
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
            ],
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


def _extract_year(val) -> int | None:
    """Extrait l'année depuis différents formats : datetime, int YYYYMMDD, int année, str."""
    import pandas as pd
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(val, "year"):          # datetime / Timestamp
        return val.year
    if isinstance(val, (int, float)):
        v = int(val)
        if v > 19_000_000:            # format YYYYMMDD
            return v // 10_000
        return v                      # déjà une année
    s = str(val).strip()
    if len(s) >= 4:
        try:
            return int(s[:4])
        except ValueError:
            pass
    return None


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
        else:
            print("  Commande non reconnue.")
        return None

    # ── Page : sport (routeur) ────────────────────────────────────────────────

    def _make_page_sport(self, sport):
        config = self._config[sport.nom]
        collectif = config.get("collectif", False)
        genre = config.get("genre", False)

        if genre:
            return self._make_page_genre(sport.nom, config)
        elif collectif:
            return self._make_page_cat(sport.nom, config["equipe"], config["joueurs"])
        else:
            return self._make_page_stats(sport.nom, config["stats"])

    # ── Page : sélection du genre ─────────────────────────────────────────────

    def _make_page_genre(self, titre, config):
        collectif = config.get("collectif", False)

        def page():
            _titre(titre)
            _option(1, "Hommes")
            _option(2, "Femmes")
            _nav(peut_avancer=bool(self._fwd))

            choix = _lire()
            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix == "+":
                return "forward"
            if choix == "1":
                genre_data = config["hommes"]
                label_genre = "Hommes"
            elif choix == "2":
                genre_data = config["femmes"]
                label_genre = "Femmes"
            else:
                print("  Commande non reconnue.")
                return None

            if collectif:
                return self._make_page_cat(
                    f"{titre} — {label_genre}",
                    genre_data["equipe"],
                    genre_data["joueurs"],
                )
            else:
                return self._make_page_stats(f"{titre} — {label_genre}", genre_data)

        return page

    # ── Page : sélection Équipe / Joueurs ─────────────────────────────────────

    def _make_page_cat(self, titre, stats_equipe, stats_joueurs):
        def page():
            _titre(titre)
            _option(1, "Équipe")
            _option(2, "Joueurs")
            _nav(peut_avancer=bool(self._fwd))

            choix = _lire()
            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix == "+":
                return "forward"
            if choix == "1":
                return self._make_page_stats(f"{titre} — Équipe", stats_equipe)
            if choix == "2":
                return self._make_page_stats(f"{titre} — Joueurs", stats_joueurs)
            print("  Commande non reconnue.")
            return None

        return page

    # ── Page : liste des fonctionnalités ──────────────────────────────────────

    def _make_page_stats(self, titre, stats):
        def page():
            _titre(titre)
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

    # ── Page : exécution d'une stat ───────────────────────────────────────────

    def _make_page_stat(self, stat):
        # Si le sélecteur utilise un DataFrame (pagination + filtres), déléguer
        sel = stat.get("selector")
        if sel and "options_df_fn" in sel:
            return self._make_page_selector_paged(sel, stat)

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

            result = None
            print()
            try:
                result = stat["fn"](**kwargs)
                _afficher_resultat(result)
            except ValueError as e:
                print(f"  Erreur : {e}")
            except Exception as e:
                print(f"  Erreur inattendue : {e}")

            return self._attendre_apres_resultat(result, stat["label"])

        return page


    # ── Page : sélecteur paginé avec filtres ──────────────────────────────────

    def _make_page_selector_paged(self, sel, stat):
        """
        Remplace _make_page_stat pour les sélecteurs avec options_df_fn.

        Affiche une liste paginée (20 items/page) avec filtres optionnels.
        Quand l'utilisateur choisit un item, exécute la stat et affiche le résultat.
        """
        PAGE_SIZE = 20
        state: dict = {"page": 0, "filters": {}, "df": None, "_filter_applied": False}
        col = sel["col_display"]
        # Filtre recherche par nom toujours disponible en tête de liste
        filters_cfg = [
            {"label": "Recherche par nom", "col": "__search__", "type": "search"},
        ] + sel.get("filters", [])

        def _apply_filters(df):
            filtered = df.copy()
            # Recherche textuelle : préfixe sur chaque mot du nom affiché
            if "__search__" in state["filters"]:
                term = state["filters"]["__search__"].lower()
                import pandas as pd
                mask = filtered[col].apply(
                    lambda name: pd.notna(name) and any(
                        word.lower().startswith(term)
                        for word in str(name).split()
                    )
                )
                filtered = filtered[mask]
            for fkey, fval in state["filters"].items():
                if fkey == "__search__":
                    continue
                if fkey.startswith("__year__"):
                    src_col = fkey[len("__year__"):]
                    years = filtered[src_col].apply(_extract_year)
                    if isinstance(fval, tuple):
                        mask = years.apply(
                            lambda y: y is not None and fval[0] <= y <= fval[1]
                        )
                    else:
                        mask = years.apply(lambda y: y == fval)
                    filtered = filtered[mask]
                else:
                    filtered = filtered[
                        filtered[fkey].astype(str) == str(fval)
                    ]
            return filtered

        def _filtres_str():
            parts = []
            for fkey, fval in state["filters"].items():
                label = next(
                    (f["label"] for f in filters_cfg
                     if f["col"] == fkey or f"__year__{f['col']}" == fkey),
                    fkey,
                )
                if isinstance(fval, tuple):
                    parts.append(f"{label}: {fval[0]}-{fval[1]}")
                else:
                    parts.append(f"{label}: {fval}")
            return " | ".join(parts)

        def page():
            # Chargement unique du DataFrame
            if state["df"] is None:
                try:
                    state["df"] = sel["options_df_fn"]()
                except Exception as e:
                    print(f"  Erreur lors du chargement : {e}")
                    return "back"

            df = state["df"]
            filtered = _apply_filters(df)
            items = filtered[col].dropna().sort_values().tolist()
            total = len(items)
            n_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            state["page"] = max(0, min(state["page"], n_pages - 1))
            start = state["page"] * PAGE_SIZE
            page_items = items[start:start + PAGE_SIZE]

            _titre(sel["label"])

            if state["filters"]:
                print(f"  Filtres actifs : {_filtres_str()}")
            print(f"  {total} résultat{'s' if total != 1 else ''}"
                  f" — Page {state['page'] + 1}/{n_pages}\n")

            for i, item in enumerate(page_items, 1):
                _option(i, item)

            nav_parts = []
            if state["page"] > 0:
                nav_parts.append("[<] Préc.")
            if state["page"] < n_pages - 1:
                nav_parts.append("[>] Suiv.")
            if filters_cfg:
                nav_parts.append("[f] Filtrer")
            if state["filters"]:
                nav_parts.append("[r] Reset")
            nav_parts += ["[-] Retour", "[q] Quitter"]
            print(f"\n  {' | '.join(nav_parts)}")

            choix = _lire()

            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix == "<" and state["page"] > 0:
                state["page"] -= 1
                return None
            if choix == ">" and state["page"] < n_pages - 1:
                state["page"] += 1
                return None
            if choix == "r":
                state["filters"].clear()
                state["page"] = 0
                return None
            if choix == "f" and filters_cfg:
                return self._make_page_filter(state, filters_cfg, df)
            if choix.isdigit():
                idx = int(choix) - 1
                if 0 <= idx < len(page_items):
                    value = page_items[idx]
                    kwargs = {sel["key"]: value}
                    for inp in stat.get("inputs", []):
                        v = input(f"  {inp['label']} : ").strip()
                        if not v:
                            print("  Saisie annulée.")
                            return None
                        kwargs[inp["key"]] = v
                    result = None
                    print()
                    try:
                        result = stat["fn"](**kwargs)
                        _afficher_resultat(result)
                    except ValueError as e:
                        print(f"  Erreur : {e}")
                    except Exception as e:
                        print(f"  Erreur inattendue : {e}")
                    return self._attendre_apres_resultat(result, stat["label"])
                print("  Numéro invalide.")
            else:
                print("  Commande non reconnue.")
            return None

        return page

    # ── Page : choix du filtre ─────────────────────────────────────────────────

    def _make_page_filter(self, state, filters_cfg, df):
        """Page listant les filtres disponibles. Retourne automatiquement après application."""

        def page():
            # Retour automatique après application d'un filtre (catégorie ou année)
            if state.get("_filter_applied"):
                state["_filter_applied"] = False
                return "back"

            _titre("Filtrer")

            if state["filters"]:
                print("  Filtres actifs :")
                for fkey, fval in state["filters"].items():
                    label = next(
                        (f["label"] for f in filters_cfg
                         if f["col"] == fkey or f"__year__{f['col']}" == fkey),
                        fkey,
                    )
                    val_str = (f"{fval[0]}-{fval[1]}"
                               if isinstance(fval, tuple) else str(fval))
                    print(f"    {label} : {val_str}")
                print()

            print("  Choisir un filtre :")
            for i, f in enumerate(filters_cfg, 1):
                _option(i, f["label"])
            _nav(peut_avancer=bool(self._fwd))

            choix = _lire()
            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix.isdigit():
                fi = int(choix) - 1
                if 0 <= fi < len(filters_cfg):
                    fconf = filters_cfg[fi]
                    if fconf["type"] == "search":
                        sinput = _lire(
                            "Premières lettres d'un prénom ou nom : "
                        ).strip()
                        if sinput:
                            state["filters"]["__search__"] = sinput.lower()
                        else:
                            state["filters"].pop("__search__", None)
                        state["page"] = 0
                        state["_filter_applied"] = True
                        return None  # prochain appel détecte _filter_applied
                    elif fconf["type"] == "category":
                        return self._make_page_filter_category(state, fconf, df)
                    elif fconf["type"] == "year":
                        yinput = _lire(
                            f"{fconf['label']} (ex: 1990 ou 1990-2000) : "
                        ).strip()
                        if not yinput:
                            return None
                        fkey = f"__year__{fconf['col']}"
                        if "-" in yinput:
                            parts = yinput.split("-", 1)
                            try:
                                state["filters"][fkey] = (
                                    int(parts[0]), int(parts[1])
                                )
                                state["page"] = 0
                                state["_filter_applied"] = True
                            except ValueError:
                                print("  Format invalide (ex: 1990-2000).")
                        else:
                            try:
                                state["filters"][fkey] = int(yinput)
                                state["page"] = 0
                                state["_filter_applied"] = True
                            except ValueError:
                                print("  Format invalide (ex: 1990).")
                        return None  # prochain appel détecte _filter_applied
                print("  Numéro invalide.")
            else:
                print("  Commande non reconnue.")
            return None

        return page

    # ── Page : sélection d'une valeur catégorielle ────────────────────────────

    def _make_page_filter_category(self, state, fconf, df):
        """Page paginée pour sélectionner une valeur de filtre catégoriel."""
        PAGE_SIZE = 20
        cat_state: dict = {"page": 0}

        def page():
            unique_vals = sorted(
                df[fconf["col"]].dropna().astype(str).unique().tolist()
            )
            total = len(unique_vals)
            n_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            cat_state["page"] = max(0, min(cat_state["page"], n_pages - 1))
            start = cat_state["page"] * PAGE_SIZE
            page_vals = unique_vals[start:start + PAGE_SIZE]

            _titre(f"Filtrer par {fconf['label']}")
            print(f"  {total} valeur{'s' if total != 1 else ''}"
                  f" — Page {cat_state['page'] + 1}/{n_pages}\n")

            for i, v in enumerate(page_vals, 1):
                _option(i, v)

            nav_parts = []
            if cat_state["page"] > 0:
                nav_parts.append("[<] Préc.")
            if cat_state["page"] < n_pages - 1:
                nav_parts.append("[>] Suiv.")
            nav_parts += ["[-] Retour", "[q] Quitter"]
            print(f"\n  {' | '.join(nav_parts)}")

            choix = _lire()
            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix == "<" and cat_state["page"] > 0:
                cat_state["page"] -= 1
                return None
            if choix == ">" and cat_state["page"] < n_pages - 1:
                cat_state["page"] += 1
                return None
            if choix.isdigit():
                vi = int(choix) - 1
                if 0 <= vi < len(page_vals):
                    state["filters"][fconf["col"]] = page_vals[vi]
                    state["page"] = 0
                    state["_filter_applied"] = True
                    return "back"  # revient sur filter_choice → auto-back → selector
                print("  Numéro invalide.")
            else:
                print("  Commande non reconnue.")
            return None

        return page

    # ── Export CSV ────────────────────────────────────────────────────────────

    def _attendre_apres_resultat(self, result, stat_label: str):
        """
        Affiche la barre de navigation après un résultat.

        Propose [e] Exporter CSV si le résultat est un DataFrame non vide.
        Boucle jusqu'à ce que l'utilisateur choisisse de naviguer (back/forward/quit).
        """
        import pandas as pd

        peut_exporter = isinstance(result, pd.DataFrame) and not result.empty
        print(f"\n{_SEP}")

        while True:
            nav_parts = []
            if peut_exporter:
                nav_parts.append("[e] Exporter CSV")
            if self._fwd:
                nav_parts.append("[+] Suivant")
            nav_parts += ["[-] Retour", "[q] Quitter"]
            print(f"\n  {' | '.join(nav_parts)}")

            choix = _lire()
            if choix == "q":
                return "quit"
            if choix == "-":
                return "back"
            if choix == "+":
                return "forward"
            if choix == "e" and peut_exporter:
                self._exporter_csv(result, stat_label)
            else:
                print("  Commande non reconnue.")

    def _exporter_csv(self, df, stat_label: str) -> None:
        """Sauvegarde un DataFrame dans un fichier CSV choisi par l'utilisateur."""
        import re
        from datetime import datetime

        clean = re.sub(r"[^a-z0-9]+", "_", stat_label.lower()).strip("_")
        horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
        default = f"{clean}_{horodatage}.csv"

        nom = _lire(f"Nom du fichier [{default}] : ").strip()
        if not nom:
            nom = default
        if not nom.endswith(".csv"):
            nom += ".csv"

        try:
            df.to_csv(nom, index=True, encoding="utf-8-sig")
            print(f"  Exporté : {nom}")
        except Exception as e:
            print(f"  Erreur lors de l'export : {e}")


# ── Point d'entrée ────────────────────────────────────────────────────────────


def main() -> None:
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()

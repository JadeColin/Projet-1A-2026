"""
Application de statistiques sportives — interface Tkinter.

Lancement :
    python -m Projet_Mathias.app.main
    # ou depuis le dossier Projet-1A-2026 :
    python -m Projet_Mathias.app.main
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

# ── Palette de couleurs ──────────────────────────────────────────────────────
BG_DARK   = "#1e1e2e"
BG_PANEL  = "#2a2a3e"
BG_CARD   = "#313145"
FG_TEXT   = "#cdd6f4"
FG_MUTED  = "#6c7086"
ACCENT    = "#89b4fa"
ACCENT2   = "#cba6f7"
SUCCESS   = "#a6e3a1"
WARNING   = "#f9e2af"
DANGER    = "#f38ba8"

SPORT_COLORS = {
    "Basketball":            "#f9a825",
    "League of Legends":     "#8e24aa",
    "Football Champions L.": "#1565c0",
    "Tennis":                "#2e7d32",
    "Échecs":                "#4e342e",
    "Volleyball":            "#d84315",
}

FONT_TITLE  = ("Segoe UI", 16, "bold")
FONT_SPORT  = ("Segoe UI", 11, "bold")
FONT_BTN    = ("Segoe UI", 10)
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)


# ── Configuration des sports ─────────────────────────────────────────────────

def _make_sports_config():
    """Retourne la configuration complète de chaque sport."""
    import Projet_Mathias.app.sports.basketball  as bk
    import Projet_Mathias.app.sports.lol         as lol
    import Projet_Mathias.app.sports.football_cl as fcl
    import Projet_Mathias.app.sports.tennis      as tn
    import Projet_Mathias.app.sports.chess       as ch
    import Projet_Mathias.app.sports.volleyball  as vb

    return {
        "Basketball": {
            "stats": [
                {
                    "label": "Classement équipes",
                    "fn": bk.classement_equipes,
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
                    "fn": lol.classement_emea,
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
                    "fn": lambda name: tn.stats_joueur(name, "ATP"),
                    "inputs": [{"key": "player_name", "label": "Nom joueur"}],
                },
                {
                    "label": "Stats d'une joueuse WTA",
                    "fn": lambda name: tn.stats_joueur(name, "WTA"),
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
                    "fn": lambda code: vb.bilan_equipe(code, "hommes"),
                    "inputs": [{"key": "team_code", "label": "Code pays (ex : FRA)"}],
                },
                {
                    "label": "Bilan équipe Femmes",
                    "fn": lambda code: vb.bilan_equipe(code, "femmes"),
                    "inputs": [{"key": "team_code", "label": "Code pays (ex : FRA)"}],
                },
                {
                    "label": "Joueurs d'un pays (H)",
                    "fn": lambda code: vb.stats_joueurs_par_pays(code, "hommes"),
                    "inputs": [{"key": "country_code", "label": "Code pays (ex : FRA)"}],
                },
                {
                    "label": "Joueuses d'un pays (F)",
                    "fn": lambda code: vb.stats_joueurs_par_pays(code, "femmes"),
                    "inputs": [{"key": "country_code", "label": "Code pays (ex : FRA)"}],
                },
            ]
        },
    }


# ── Widgets utilitaires ───────────────────────────────────────────────────────

class ScrollableTreeview(tk.Frame):
    """Treeview avec scrollbars horizontal et vertical."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_DARK)
        self.tree = ttk.Treeview(self, **kwargs)
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def load_dataframe(self, df):
        """Charge un DataFrame pandas dans le Treeview."""
        # Vider
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=str(col))
            width = max(len(str(col)) * 9, 80)
            self.tree.column(col, width=width, anchor="center")

        for _, row in df.iterrows():
            values = [str(v) if str(v) != "nan" else "" for v in row]
            self.tree.insert("", "end", values=values)


# ── Application principale ───────────────────────────────────────────────────

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Stats Sports")
        self.geometry("1200x750")
        self.minsize(900, 600)
        self.configure(bg=BG_DARK)

        self._sports_config = None
        self._current_sport = None
        self._current_stat  = None

        self._apply_styles()
        self._build_ui()

    # ── Styles ttk ────────────────────────────────────────────────────────────

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Treeview",
            background=BG_CARD, foreground=FG_TEXT,
            fieldbackground=BG_CARD, rowheight=24,
            font=FONT_SMALL,
        )
        style.configure("Treeview.Heading",
            background=BG_PANEL, foreground=ACCENT,
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Treeview", background=[("selected", ACCENT)])
        style.configure("Vertical.TScrollbar",   background=BG_PANEL, troughcolor=BG_DARK)
        style.configure("Horizontal.TScrollbar", background=BG_PANEL, troughcolor=BG_DARK)

    # ── Construction de l'interface ───────────────────────────────────────────

    def _build_ui(self):
        # Barre de titre
        header = tk.Frame(self, bg=BG_PANEL, height=50)
        header.pack(fill="x", side="top")
        tk.Label(
            header, text="  Stats Sports",
            bg=BG_PANEL, fg=ACCENT, font=FONT_TITLE,
        ).pack(side="left", padx=16, pady=10)

        # Corps principal : sidebar + contenu
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        # Sidebar sports
        self._sidebar = tk.Frame(body, bg=BG_PANEL, width=200)
        self._sidebar.pack(fill="y", side="left")
        self._sidebar.pack_propagate(False)

        tk.Label(
            self._sidebar, text="Sports",
            bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 9, "bold"),
        ).pack(pady=(16, 4), padx=12, anchor="w")

        self._sport_buttons = {}
        for sport in [
            "Basketball", "League of Legends", "Football Champions L.",
            "Tennis", "Échecs", "Volleyball"
        ]:
            btn = tk.Button(
                self._sidebar, text=sport,
                bg=BG_PANEL, fg=FG_TEXT, font=FONT_SPORT,
                relief="flat", anchor="w", padx=14,
                activebackground=BG_CARD, activeforeground=ACCENT,
                cursor="hand2",
                command=lambda s=sport: self._select_sport(s),
            )
            btn.pack(fill="x", pady=1)
            self._sport_buttons[sport] = btn

        # Zone de contenu
        self._content = tk.Frame(body, bg=BG_DARK)
        self._content.pack(fill="both", expand=True, padx=0)

        self._show_welcome()

    # ── Écran d'accueil ───────────────────────────────────────────────────────

    def _show_welcome(self):
        self._clear_content()
        frame = tk.Frame(self._content, bg=BG_DARK)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(frame, text="Bienvenue", bg=BG_DARK, fg=ACCENT, font=("Segoe UI", 28, "bold")).pack()
        tk.Label(
            frame,
            text="Sélectionnez un sport dans la barre latérale\npour accéder aux statistiques.",
            bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 13),
            justify="center",
        ).pack(pady=12)

    # ── Sélection d'un sport ──────────────────────────────────────────────────

    def _select_sport(self, sport: str):
        # Mettre à jour l'apparence des boutons
        for s, btn in self._sport_buttons.items():
            color = SPORT_COLORS.get(s, ACCENT)
            if s == sport:
                btn.configure(bg=BG_CARD, fg=color)
            else:
                btn.configure(bg=BG_PANEL, fg=FG_TEXT)

        self._current_sport = sport
        self._current_stat  = None

        # Charger la config au premier accès
        if self._sports_config is None:
            self._sports_config = _make_sports_config()

        self._build_sport_view(sport)

    # ── Vue d'un sport ────────────────────────────────────────────────────────

    def _build_sport_view(self, sport: str):
        self._clear_content()
        config = self._sports_config[sport]
        color  = SPORT_COLORS.get(sport, ACCENT)

        # En-tête du sport
        header = tk.Frame(self._content, bg=BG_PANEL)
        header.pack(fill="x")
        tk.Label(
            header, text=f"  {sport}",
            bg=BG_PANEL, fg=color, font=FONT_TITLE,
        ).pack(side="left", padx=16, pady=10)

        # Barre de stats (boutons horizontaux)
        stat_bar = tk.Frame(self._content, bg=BG_CARD)
        stat_bar.pack(fill="x", pady=1)

        self._stat_buttons = {}
        for stat in config["stats"]:
            btn = tk.Button(
                stat_bar, text=stat["label"],
                bg=BG_CARD, fg=FG_TEXT, font=FONT_BTN,
                relief="flat", padx=10, pady=8,
                activebackground=BG_PANEL, activeforeground=color,
                cursor="hand2",
                command=lambda s=stat: self._select_stat(s, color),
            )
            btn.pack(side="left", padx=2, pady=4)
            self._stat_buttons[stat["label"]] = btn

        # Zone de saisie (masquée par défaut)
        self._input_frame = tk.Frame(self._content, bg=BG_DARK)
        self._input_frame.pack(fill="x", padx=16, pady=6)

        # Zone de résultats
        result_frame = tk.Frame(self._content, bg=BG_DARK)
        result_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._table = ScrollableTreeview(result_frame)
        self._table.pack(fill="both", expand=True)

        # Label de statut
        self._status_var = tk.StringVar(value="← Choisissez une statistique")
        self._status_lbl = tk.Label(
            self._content, textvariable=self._status_var,
            bg=BG_DARK, fg=FG_MUTED, font=FONT_SMALL,
        )
        self._status_lbl.pack(pady=4)

    # ── Sélection d'une stat ──────────────────────────────────────────────────

    def _select_stat(self, stat: dict, color: str):
        # Mettre en valeur le bouton actif
        for lbl, btn in self._stat_buttons.items():
            if lbl == stat["label"]:
                btn.configure(bg=BG_PANEL, fg=color)
            else:
                btn.configure(bg=BG_CARD, fg=FG_TEXT)

        self._current_stat = stat
        self._build_input_area(stat, color)

        # Si aucune saisie requise, lancer directement
        if not stat["inputs"]:
            self._run_stat(stat, {})

    # ── Zone de saisie dynamique ──────────────────────────────────────────────

    def _build_input_area(self, stat: dict, color: str):
        for w in self._input_frame.winfo_children():
            w.destroy()

        if not stat["inputs"]:
            return

        self._entries = {}
        for inp in stat["inputs"]:
            tk.Label(
                self._input_frame, text=inp["label"] + " :",
                bg=BG_DARK, fg=FG_TEXT, font=FONT_BODY,
            ).pack(side="left", padx=(0, 6))

            entry = tk.Entry(
                self._input_frame,
                bg=BG_CARD, fg=FG_TEXT, font=FONT_BODY,
                insertbackground=FG_TEXT, relief="flat", width=24,
            )
            entry.pack(side="left", padx=(0, 10))
            entry.bind("<Return>", lambda e, s=stat: self._run_stat_from_ui(s))
            self._entries[inp["key"]] = entry

        tk.Button(
            self._input_frame, text="Rechercher",
            bg=color, fg=BG_DARK, font=("Segoe UI", 10, "bold"),
            relief="flat", padx=12, pady=4, cursor="hand2",
            command=lambda s=stat: self._run_stat_from_ui(s),
        ).pack(side="left")

    # ── Exécution d'une stat ──────────────────────────────────────────────────

    def _run_stat_from_ui(self, stat: dict):
        kwargs = {key: entry.get().strip() for key, entry in self._entries.items()}
        if any(not v for v in kwargs.values()):
            messagebox.showwarning("Saisie manquante", "Veuillez remplir tous les champs.")
            return
        self._run_stat(stat, kwargs)

    def _run_stat(self, stat: dict, kwargs: dict):
        self._status_var.set("Chargement…")
        self._table.load_dataframe(__import__("pandas").DataFrame())

        def worker():
            try:
                df = stat["fn"](**kwargs)
                self.after(0, lambda: self._display_result(df, stat["label"]))
            except ValueError as e:
                self.after(0, lambda: self._show_error(str(e)))
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Erreur : {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _display_result(self, df, label: str):
        self._table.load_dataframe(df)
        self._status_var.set(f"{label}  —  {len(df)} ligne(s)")

    def _show_error(self, msg: str):
        self._status_var.set(f"Erreur")
        messagebox.showerror("Erreur", msg)

    # ── Utilitaires ───────────────────────────────────────────────────────────

    def _clear_content(self):
        for widget in self._content.winfo_children():
            widget.destroy()


# ── Point d'entrée ───────────────────────────────────────────────────────────

def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

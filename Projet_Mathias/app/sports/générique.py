"""
Fonctionnalités génériques applicables à tous les sports collectifs.

Fonctions disponibles :
    - formater_roster : formate le roster d'une équipe selon la spec standard
                        (Rôle | Nom complet | Pseudo* | Nationalité | Date de naissance)
                        *Pseudo uniquement pour les sports e-sport.

Usage depuis un module sport :

    from Projet_Mathias.app.sports.générique import formater_roster

    # Basketball (sport classique, pas de pseudo, pas de nationalité dans les données)
    formater_roster(
        df_joueurs=roster_df,
        col_nom="full_name",
        col_naissance="birthdate",
        est_esport=False,
    )

    # LoL (e-sport, avec pseudo, coachs disponibles)
    formater_roster(
        df_joueurs=players_df,
        col_nom="name",
        col_pseudo="pseudo",
        col_nationalite="country_of_birth",
        col_naissance="birthdate",
        df_coachs=coaches_df,
        est_esport=True,
    )
"""

from __future__ import annotations

import pandas as pd


def formater_roster(
    df_joueurs: pd.DataFrame,
    col_nom: str,
    col_pseudo: str | None = None,
    col_nationalite: str | None = None,
    col_naissance: str | None = None,
    df_coachs: pd.DataFrame | None = None,
    est_esport: bool = False,
) -> pd.DataFrame:
    """
    Formate le roster d'une équipe selon la spec standard.

    Colonnes produites (dans cet ordre) :
        Rôle | Nom complet | Pseudo (e-sport uniquement) | Nationalité | Date de naissance

    Les coachs apparaissent en tête de liste, puis les joueurs.
    Les colonnes absentes des données sont affichées comme « N/A ».
    Les dates sont formatées en JJ/MM/AAAA.

    Paramètres
    ----------
    df_joueurs      : DataFrame des joueurs de l'équipe (déjà filtré sur l'équipe).
    col_nom         : Colonne contenant le nom complet du joueur.
    col_pseudo      : Colonne contenant le pseudo/surnom en jeu (optionnel).
    col_nationalite : Colonne contenant la nationalité (optionnel).
    col_naissance   : Colonne contenant la date de naissance (optionnel).
    df_coachs       : DataFrame des coachs de l'équipe (optionnel).
    est_esport      : True pour inclure la colonne Pseudo dans le résultat.

    Retourne
    --------
    pd.DataFrame trié coachs → joueurs, indexé à partir de 1.
    """

    def _extraire(df: pd.DataFrame, role: str) -> pd.DataFrame:
        """Construit un DataFrame normalisé à partir d'un groupe (joueurs ou coachs)."""
        df = df.reset_index(drop=True)
        out = pd.DataFrame(index=df.index)

        out["Rôle"] = role

        out["Nom complet"] = (
            df[col_nom] if col_nom in df.columns else "N/A"
        )

        if est_esport and col_pseudo and col_pseudo in df.columns:
            out["Pseudo"] = df[col_pseudo]

        out["Nationalité"] = (
            df[col_nationalite]
            if col_nationalite and col_nationalite in df.columns
            else "N/A"
        )

        if col_naissance and col_naissance in df.columns:
            out["Date de naissance"] = (
                pd.to_datetime(df[col_naissance], errors="coerce")
                .dt.strftime("%d/%m/%Y")
            )
        else:
            out["Date de naissance"] = "N/A"

        return out

    # Construire les blocs coachs + joueurs
    parts: list[pd.DataFrame] = []
    if df_coachs is not None and not df_coachs.empty:
        parts.append(_extraire(df_coachs, "Coach"))
    parts.append(_extraire(df_joueurs, "Joueur"))

    result = pd.concat(parts, ignore_index=True)

    # Ordonner les colonnes selon la spec
    cols = ["Rôle", "Nom complet"]
    if est_esport and "Pseudo" in result.columns:
        cols.append("Pseudo")
    cols += ["Nationalité", "Date de naissance"]

    result = result[cols].reset_index(drop=True)
    result.index += 1
    return result


# ---------------------------------------------------------------------------
# Bracket d'élimination
# ---------------------------------------------------------------------------

_VERT = "\033[32m"
_RESET = "\033[0m"
_LARGEUR_EQUIPE = 25  # largeur fixe pour l'affichage d'un nom d'équipe


class ResultatMatch:
    """
    Détermine le gagnant d'un match à partir des scores.

    Paramètres
    ----------
    equipe1, equipe2 : noms des deux équipes
    score1, score2   : scores respectifs (peuvent être NaN si non joué)

    Attributs
    ---------
    gagnant  : nom de l'équipe gagnante, ou None si match non joué / égalité
    perdant  : nom de l'équipe perdante, ou None
    joue     : True si le match a un résultat
    """

    def __init__(
        self,
        equipe1: str,
        equipe2: str,
        score1: float | int | None,
        score2: float | int | None,
    ) -> None:
        self.equipe1 = equipe1
        self.equipe2 = equipe2
        self.score1 = score1
        self.score2 = score2
        self.joue = (
            score1 is not None
            and score2 is not None
            and not (isinstance(score1, float) and score1 != score1)
            and not (isinstance(score2, float) and score2 != score2)
        )
        if self.joue:
            if score1 > score2:
                self.gagnant = equipe1
                self.perdant = equipe2
            elif score2 > score1:
                self.gagnant = equipe2
                self.perdant = equipe1
            else:
                self.gagnant = None
                self.perdant = None
        else:
            self.gagnant = None
            self.perdant = None

    def label_equipe(self, equipe: str) -> str:
        """Retourne 'score1-score2' si joué, sinon '???'."""
        if not self.joue:
            return "???"
        if equipe == self.equipe1:
            return f"{int(self.score1)}-{int(self.score2)}"
        return f"{int(self.score2)}-{int(self.score1)}"


def _agreger_deux_manches(
    df: pd.DataFrame,
    col_equipe1: str,
    col_equipe2: str,
    col_score1: str,
    col_score2: str,
    col_round: str,
) -> pd.DataFrame:
    """
    Agrège les matchs aller/retour en un seul résultat par confrontation.

    Pour chaque paire de teams (indépendamment de l'ordre domicile/extérieur),
    additionne les scores des deux manches et renvoie une ligne par confrontation.
    """
    rows = []
    df = df.copy()
    df["_paire"] = df.apply(
        lambda r: tuple(sorted([r[col_equipe1], r[col_equipe2]])), axis=1
    )
    for (round_, paire), group in df.groupby([col_round, "_paire"]):
        eq1, eq2 = paire
        score_eq1 = 0
        score_eq2 = 0
        for _, row in group.iterrows():
            if row[col_equipe1] == eq1:
                score_eq1 += row[col_score1]
                score_eq2 += row[col_score2]
            else:
                score_eq1 += row[col_score2]
                score_eq2 += row[col_score1]
        rows.append({
            col_round: round_,
            col_equipe1: eq1,
            col_equipe2: eq2,
            col_score1: score_eq1,
            col_score2: score_eq2,
        })
    return pd.DataFrame(rows)


def afficher_bracket(
    df: pd.DataFrame,
    col_equipe1: str,
    col_equipe2: str,
    col_score1: str,
    col_score2: str,
    col_round: str,
    ordre_rounds: list[str],
    deux_manches: bool = False,
) -> None:
    """
    Affiche un bracket d'élimination directe en ASCII dans le terminal.

    Les noms de rounds sont affichés en en-tête.
    Le chemin du gagnant (lignes de connexion + nom) est colorié en vert.
    Les équipes non encore qualifiées sont affichées '???'.

    Paramètres
    ----------
    df            : DataFrame contenant les matchs de la phase éliminatoire.
    col_equipe1   : Colonne du nom de l'équipe 1.
    col_equipe2   : Colonne du nom de l'équipe 2.
    col_score1    : Colonne du score de l'équipe 1.
    col_score2    : Colonne du score de l'équipe 2.
    col_round     : Colonne identifiant le round (ex: 'RO8', 'RO4', 'RO2').
    ordre_rounds  : Liste des rounds dans l'ordre chronologique,
                    du premier tour jusqu'à la finale.
                    Exemple : ["RO8", "RO4", "RO2"]
    deux_manches  : Si True, agrège les matchs aller/retour avant affichage.
    """
    if deux_manches:
        df = _agreger_deux_manches(df, col_equipe1, col_equipe2, col_score1, col_score2, col_round)

    # Construire la liste des matchups par round (ResultatMatch)
    rounds: dict[str, list[ResultatMatch]] = {}
    for r in ordre_rounds:
        df_r = df[df[col_round] == r]
        matchups = []
        for _, row in df_r.iterrows():
            matchups.append(ResultatMatch(
                equipe1=str(row[col_equipe1]),
                equipe2=str(row[col_equipe2]),
                score1=row[col_score1],
                score2=row[col_score2],
            ))
        rounds[r] = matchups

    # Compléter les rounds avec des matchups vides si données absentes
    nb_matchups_attendus = 2 ** (len(ordre_rounds) - 1)
    for i, r in enumerate(ordre_rounds):
        attendu = nb_matchups_attendus // (2 ** i)
        while len(rounds[r]) < attendu:
            rounds[r].append(ResultatMatch("???", "???", None, None))

    # -------------------------------------------------------------------------
    # Rendu ASCII ligne par ligne
    # La hauteur d'un matchup dans le premier round = 3 lignes
    # (ligne equipe1, ligne séparateur, ligne equipe2)
    # Entre deux matchups du même round : 1 ligne vide
    # Chaque round suivant double l'espacement vertical
    # -------------------------------------------------------------------------

    nb_rounds = len(ordre_rounds)
    # Hauteur totale en lignes pour le premier round
    n_matchups_r0 = len(rounds[ordre_rounds[0]])
    # Chaque matchup = 3 lignes, séparé par (espacement - 1) lignes vides
    # espacement entre matchups du round 0 = 1 ligne
    espacement_0 = 1
    hauteur_matchup = 3
    hauteur_totale = n_matchups_r0 * hauteur_matchup + (n_matchups_r0 - 1) * espacement_0

    L = _LARGEUR_EQUIPE

    def _tronquer(nom: str) -> str:
        return nom[:L - 1] + "…" if len(nom) >= L else nom

    def _ligne_equipe(equipe: str, score_label: str, est_gagnant: bool) -> str:
        nom = _tronquer(equipe)
        texte = f"{nom:<{L}} {score_label}"
        if est_gagnant:
            return f"{_VERT}{texte}{_RESET}"
        return texte

    # Construire une grille : liste de lignes (strings)
    grille: list[list[str]] = []  # grille[col_round][ligne] = texte de la colonne

    for i, r in enumerate(ordre_rounds):
        matchups = rounds[r]
        n = len(matchups)
        col_lines: list[str] = [""] * hauteur_totale

        # espacement entre matchups à ce round
        esp = espacement_0 * (2 ** i)
        # hauteur totale occupée par un groupe (matchup + séparateur)
        pas = hauteur_matchup + esp

        for j, m in enumerate(matchups):
            # Position de départ (ligne du haut du matchup)
            debut = j * pas + (esp // 2) * (1 if i > 0 else 0)
            # Centrage vertical du matchup dans son slot
            slot = hauteur_totale // n
            debut = j * slot + (slot - hauteur_matchup) // 2

            est_g1 = m.joue and m.gagnant == m.equipe1
            est_g2 = m.joue and m.gagnant == m.equipe2

            score1 = m.label_equipe(m.equipe1)
            score2 = m.label_equipe(m.equipe2)

            if debut < hauteur_totale:
                col_lines[debut] = _ligne_equipe(m.equipe1, score1, est_g1)
            if debut + 1 < hauteur_totale:
                col_lines[debut + 1] = "─" * (L + 6)
            if debut + 2 < hauteur_totale:
                col_lines[debut + 2] = _ligne_equipe(m.equipe2, score2, est_g2)

        grille.append(col_lines)

    # Construire les colonnes de connexion entre rounds
    # Pour chaque paire de rounds consécutifs, on trace une colonne de connecteurs
    connecteurs: list[list[str]] = []
    for i in range(nb_rounds - 1):
        matchups_gauche = rounds[ordre_rounds[i]]
        matchups_droite = rounds[ordre_rounds[i + 1]]
        conn_lines: list[str] = ["   "] * hauteur_totale

        slot_g = hauteur_totale // len(matchups_gauche)
        slot_d = hauteur_totale // len(matchups_droite)

        for j, m_d in enumerate(matchups_droite):
            # Les deux matchups qui alimentent ce slot de droite
            idx_g1 = j * 2
            idx_g2 = j * 2 + 1

            m_g1 = matchups_gauche[idx_g1] if idx_g1 < len(matchups_gauche) else None
            m_g2 = matchups_gauche[idx_g2] if idx_g2 < len(matchups_gauche) else None

            # Lignes centrales des matchups gauches
            centre_g1 = idx_g1 * slot_g + slot_g // 2
            centre_g2 = idx_g2 * slot_g + slot_g // 2
            centre_d = j * slot_d + slot_d // 2

            # Gagnant du matchup de gauche
            gagnant_g1 = m_g1.gagnant if m_g1 else None
            gagnant_g2 = m_g2.gagnant if m_g2 else None

            # Tracer les lignes horizontales et verticales
            for ligne in range(hauteur_totale):
                # Branche haute : du centre_g1 jusqu'au centre_d
                if centre_g1 <= ligne <= centre_d or centre_d <= ligne <= centre_g1:
                    est_vert = (gagnant_g1 is not None and m_d.joue and
                                (m_d.equipe1 == gagnant_g1 or m_d.equipe2 == gagnant_g1))
                    symbole = f"{_VERT}│{_RESET}" if est_vert else "│"
                    if ligne == centre_g1:
                        symbole = f"{_VERT}─┤{_RESET}" if est_vert else "─┤"
                    elif ligne == centre_d and centre_g1 < centre_d:
                        symbole = f"{_VERT}├─{_RESET}" if est_vert else "├─"
                    conn_lines[ligne] = symbole

                # Branche basse : du centre_g2 jusqu'au centre_d
                if centre_g2 >= ligne >= centre_d or centre_d >= ligne >= centre_g2:
                    est_vert = (gagnant_g2 is not None and m_d.joue and
                                (m_d.equipe1 == gagnant_g2 or m_d.equipe2 == gagnant_g2))
                    symbole = f"{_VERT}│{_RESET}" if est_vert else "│"
                    if ligne == centre_g2:
                        symbole = f"{_VERT}─┤{_RESET}" if est_vert else "─┤"
                    elif ligne == centre_d and centre_g2 > centre_d:
                        symbole = f"{_VERT}├─{_RESET}" if est_vert else "├─"
                    conn_lines[ligne] = symbole

        connecteurs.append(conn_lines)

    # Affichage final
    # En-têtes
    en_tetes = []
    for r in ordre_rounds:
        en_tetes.append(f"{r:^{L + 8}}")
    print("  ".join(en_tetes))
    print("─" * (len(ordre_rounds) * (L + 10)))

    # Lignes
    for ligne in range(hauteur_totale):
        segments = []
        for i, r in enumerate(ordre_rounds):
            cell = grille[i][ligne] if grille[i][ligne] else " " * (L + 6)
            segments.append(cell)
            if i < nb_rounds - 1:
                conn = connecteurs[i][ligne] if connecteurs[i][ligne].strip() else "   "
                segments.append(conn)
        print("  ".join(segments))

    print()


# ---------------------------------------------------------------------------
# Agenda des matchs récents
# ---------------------------------------------------------------------------

_COLS_AGENDA = ["Sport", "Date", "Équipe 1", "Équipe 2", "Score 1", "Score 2"]


def agenda_recents(sources: list[pd.DataFrame], n: int = 10) -> pd.DataFrame:
    """
    Retourne les n matchs les plus récents toutes sources confondues.

    Chaque source doit être un DataFrame avec exactement les colonnes :
        Sport | Date | Équipe 1 | Équipe 2 | Score 1 | Score 2

    La colonne Date doit être parseable par pd.to_datetime.
    Les lignes sans date valide sont ignorées.

    Paramètres
    ----------
    sources : liste de DataFrames standardisés, un par sport.
              Chaque module sport expose une fonction get_agenda_data()
              qui renvoie un DataFrame dans ce format.
    n       : nombre de matchs à retourner (défaut : 10).

    Retourne
    --------
    pd.DataFrame trié du plus récent au plus ancien, indexé à partir de 1.
    """
    if not sources:
        return pd.DataFrame(columns=_COLS_AGENDA)

    combined = pd.concat(sources, ignore_index=True)
    combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce")
    combined = (
        combined
        .dropna(subset=["Date"])
        .sort_values("Date", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    combined["Date"] = combined["Date"].dt.strftime("%d/%m/%Y")
    combined.index += 1
    return combined[_COLS_AGENDA]

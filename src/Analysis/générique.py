"""
Fonctionnalités génériques applicables à tous les sports collectifs.

Fonctions disponibles :
    - formater_roster : formate le roster d'une équipe selon la spec standard
                        (Rôle | Nom complet | Pseudo* | Nationalité | Date de naissance)
                        *Pseudo uniquement pour les sports e-sport.

Usage depuis un module sport :

    from src.Analysis.générique import formater_roster

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



def _calculer_classement(
    df: pd.DataFrame,
    col_equipe1: str,
    col_equipe2: str,
    col_score1: str,
    col_score2: str,
) -> pd.DataFrame:
    """
    Calcule le classement par points à partir d'un DataFrame de matchs.

    Règles : 3 pts victoire, 1 pt nul, 0 pt défaite.
    Tri : Points décroissants, puis différence décroissante.
    Rang : classement standard (ex-æquo = même rang, le suivant saute des places).

    Retourne un DataFrame avec les colonnes :
        Rang | Équipe | MJ | V | N | D | Pts | Diff
    """
    teams: dict[str, dict] = {}
    for eq in pd.concat([df[col_equipe1], df[col_equipe2]]).unique():
        teams[eq] = {"MJ": 0, "V": 0, "N": 0, "D": 0, "Pts": 0, "Diff": 0}

    for _, row in df.iterrows():
        m = ResultatMatch(
            equipe1=str(row[col_equipe1]),
            equipe2=str(row[col_equipe2]),
            score1=row[col_score1],
            score2=row[col_score2],
        )
        if not m.joue:
            continue
        eq1, eq2 = m.equipe1, m.equipe2
        teams[eq1]["MJ"] += 1
        teams[eq2]["MJ"] += 1
        diff = int(m.score1) - int(m.score2)
        teams[eq1]["Diff"] += diff
        teams[eq2]["Diff"] -= diff
        if m.gagnant == eq1:
            teams[eq1]["V"] += 1
            teams[eq1]["Pts"] += 3
            teams[eq2]["D"] += 1
        elif m.gagnant == eq2:
            teams[eq2]["V"] += 1
            teams[eq2]["Pts"] += 3
            teams[eq1]["D"] += 1
        else:
            teams[eq1]["N"] += 1
            teams[eq2]["N"] += 1
            teams[eq1]["Pts"] += 1
            teams[eq2]["Pts"] += 1

    result = (
        pd.DataFrame.from_dict(teams, orient="index")
        .reset_index()
        .rename(columns={"index": "Équipe"})
        .sort_values(["Pts", "Diff"], ascending=[False, False])
        .reset_index(drop=True)
    )
    result["Rang"] = result["Pts"].rank(method="min", ascending=False).astype(int)
    result["Winrate"] = (result["V"] / result["MJ"].replace(0, pd.NA) * 100).round(1)
    result["Winrate"] = result["Winrate"].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
    )
    return result[["Rang", "Équipe", "MJ", "V", "N", "D", "Pts", "Diff", "Winrate"]]


def _afficher_table_classement(
    df: pd.DataFrame,
    top_qualifies: int | None = None,
    titre: str | None = None,
) -> None:
    """Affiche un tableau de classement avec séparateur optionnel après top_qualifies."""
    if titre:
        print(f"\n{'═' * 70}")
        print(f"  {titre}")
        print(f"{'═' * 70}")

    lines = df.to_string(index=False).split("\n")
    header_line = lines[0]
    data_lines = lines[1:]
    width = max(len(header_line), 40)

    print(header_line)

    if top_qualifies is None:
        for line in data_lines:
            print(line)
    else:
        n_top = len(df[df["Rang"] <= top_qualifies])
        sep_label = f" TOP {top_qualifies} "
        sep_line = sep_label.center(width, "─")
        for i, line in enumerate(data_lines):
            print(line)
            if i == n_top - 1 and n_top < len(data_lines):
                print(sep_line)

    print()


def afficher_classement(
    df: pd.DataFrame,
    col_equipe1: str,
    col_equipe2: str,
    col_score1: str,
    col_score2: str,
    col_groupe: str | None = None,
    top_qualifies: int | None = None,
) -> None:
    """
    Affiche le classement d'une compétition par points dans le terminal.

    Si la compétition comporte des groupes (col_groupe renseigné), un tableau
    de classement est affiché pour chaque groupe.
    Sinon, un seul tableau global est affiché.

    Le chemin de qualification est matérialisé par une ligne séparatrice
    après les top_qualifies premières équipes (si renseigné).

    Règles de points : 3 pts victoire, 1 pt nul, 0 pt défaite.
    Départage : différence de buts/scores.
    Rang : standard (ex-æquo → même rang, suivant saute des places).

    Paramètres
    ----------
    df            : DataFrame des matchs.
    col_equipe1   : Colonne du nom de l'équipe 1.
    col_equipe2   : Colonne du nom de l'équipe 2.
    col_score1    : Colonne du score de l'équipe 1.
    col_score2    : Colonne du score de l'équipe 2.
    col_groupe    : Colonne identifiant le groupe (optionnel).
                    Si fournie, un tableau par groupe est affiché.
    top_qualifies : Nombre d'équipes qui se qualifient (optionnel).
                    Une ligne séparatrice est insérée après ce rang.
    """
    if col_groupe is not None and col_groupe in df.columns:
        for groupe in sorted(df[col_groupe].dropna().unique()):
            df_groupe = df[df[col_groupe] == groupe]
            classement = _calculer_classement(
                df_groupe, col_equipe1, col_equipe2, col_score1, col_score2
            )
            _afficher_table_classement(
                classement, top_qualifies, titre=f"Groupe {groupe}"
            )
    else:
        classement = _calculer_classement(
            df, col_equipe1, col_equipe2, col_score1, col_score2
        )
        _afficher_table_classement(classement, top_qualifies)



def fiche_joueur(
    df_joueurs: pd.DataFrame,
    col_nom: str,
    nom_joueur: str,
    col_labels: dict[str, str] | None = None,
    cols_dates: list[str] | None = None,
) -> pd.DataFrame:
    """
    Retourne la fiche complète d'un joueur sous forme de tableau Statistique | Valeur.

    Toutes les colonnes disponibles dans df_joueurs sont affichées.
    La recherche est insensible à la casse et accepte des noms partiels.

    Paramètres
    ----------
    df_joueurs  : DataFrame contenant les joueurs du sport.
    col_nom     : Colonne utilisée pour la recherche par nom.
    nom_joueur  : Nom (ou partie du nom) du joueur recherché.
    col_labels  : Dictionnaire optionnel {nom_colonne: label_affiché} pour
                  renommer les colonnes en labels lisibles.
                  Les colonnes absentes du dict conservent leur nom d'origine.
    cols_dates  : Liste de colonnes à formater en date (dd/mm/yyyy).

    Retourne
    --------
    pd.DataFrame à deux colonnes : "Statistique" | nom du joueur
        Chaque ligne correspond à une information disponible.

    Lève
    ----
    ValueError si aucun joueur ne correspond à la recherche.
    ValueError si plusieurs joueurs correspondent (liste des correspondances incluse).
    """
    mask = df_joueurs[col_nom].astype(str).str.contains(
        nom_joueur, case=False, na=False
    )
    correspondances = df_joueurs[mask]

    if correspondances.empty:
        raise ValueError(f"Aucun joueur trouvé pour : '{nom_joueur}'")

    if len(correspondances) > 1:
        noms = correspondances[col_nom].tolist()
        raise ValueError(
            f"{len(noms)} joueurs correspondent à '{nom_joueur}' : "
            + ", ".join(str(n) for n in noms)
            + ". Précisez la recherche."
        )

    joueur = correspondances.iloc[0]
    nom_label = str(joueur[col_nom])

    # Formatage des dates
    if cols_dates:
        joueur = joueur.copy()
        for col in cols_dates:
            if col in joueur.index and pd.notna(joueur[col]):
                try:
                    joueur[col] = pd.to_datetime(joueur[col]).strftime("%d/%m/%Y")
                except Exception:
                    pass

    # Construction du tableau large : 1 ligne = 1 joueur, 1 colonne = 1 variable
    labels = col_labels or {}
    data = {}
    for col in joueur.index:
        label = labels.get(col, col)
        valeur = joueur[col]
        if pd.isna(valeur) if not isinstance(valeur, str) else False:
            valeur = "N/A"
        data[label] = valeur

    result = pd.DataFrame([data])
    result.index = pd.Index([nom_label])
    result.index.name = None
    return result


def lister_joueurs(
    df_joueurs: pd.DataFrame,
    col_nom: str,
    col_equipe: str | None = None,
    col_labels: dict[str, str] | None = None,
) -> pd.DataFrame:
    """
    Retourne la liste de tous les joueurs disponibles dans un sport.

    Utilisée pour les sports individuels (affiche tous les sportifs)
    ou pour les sports collectifs quand on souhaite voir tous les joueurs
    indépendamment de leur équipe.

    Paramètres
    ----------
    df_joueurs  : DataFrame contenant les joueurs.
    col_nom     : Colonne du nom du joueur.
    col_equipe  : Colonne de l'équipe (optionnel, affichée si fournie).
    col_labels  : Dictionnaire optionnel {nom_colonne: label_affiché}.

    Retourne
    --------
    pd.DataFrame avec au minimum les colonnes Nom (et Équipe si fournie),
    trié par nom, indexé à partir de 1.
    """
    labels = col_labels or {}
    cols = [col_nom]
    if col_equipe and col_equipe in df_joueurs.columns:
        cols.append(col_equipe)

    result = df_joueurs[cols].copy().sort_values(col_nom).reset_index(drop=True)
    result = result.rename(columns={c: labels.get(c, c) for c in cols})
    result.index += 1
    return result

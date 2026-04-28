from Projet_Mathias.classes.sport import Sport, SPORTS
from Projet_fouad.visualize import CompetitionVisualizer, EventVisualizer
from Projet_fouad.visualizeMatch import MatchVisualizer


# ── Liste des sports disponibles ────────────────────────────────────────────
supported_sports = SPORTS

print("\nSports disponibles :")
for s in supported_sports:
    print(f"  - {s.nom}")

selected_sport_name = input("\nSélectionnez un sport : ").strip().lower()

matched_sport = next((s for s in supported_sports if s.nom.lower() == selected_sport_name), None)
if matched_sport is None:
    raise ValueError(
        f"Sport '{selected_sport_name}' non supporté. "
        f"Choix possibles : {[s.nom for s in supported_sports]}"
    )
selected_sport = matched_sport


# ── Compétitions ────────────────────────────────────────────────────────────
competitions = CompetitionVisualizer.display_all_competitions(selected_sport)
if not competitions:
    raise ValueError(f"Aucune compétition trouvée pour le sport '{selected_sport.nom}'.")

print(f"\nCompétitions disponibles pour {selected_sport.nom} :")
for i, c in enumerate(competitions, 1):
    print(f"  {i}. {c}")

selected_competition_name = input("\nSélectionnez une compétition (nom exact) : ").strip()
matched_competition = next((c for c in competitions if str(c) == selected_competition_name), None)
if matched_competition is None:
    raise ValueError(
        f"Compétition '{selected_competition_name}' introuvable. "
        f"Choix possibles : {[str(c) for c in competitions]}"
    )
selected_competition = matched_competition


# ── Événements ──────────────────────────────────────────────────────────────
events = EventVisualizer.display_all_events(selected_competition)
if not events:
    raise ValueError(f"Aucun événement trouvé pour la compétition '{selected_competition}'.")

print(f"\nÉvénements disponibles dans '{selected_competition}' :")
for i, e in enumerate(events, 1):
    print(f"  {i}. {e}")

selected_event_name = input("\nSélectionnez un événement (nom exact) : ").strip()
matched_event = next((e for e in events if str(e) == selected_event_name), None)
if matched_event is None:
    raise ValueError(
        f"Événement '{selected_event_name}' introuvable. "
        f"Choix possibles : {[str(e) for e in events]}"
    )
selected_event = matched_event


# ── Matchs ──────────────────────────────────────────────────────────────────
matches = selected_event.matchs
if not matches:
    raise ValueError(f"Aucun match trouvé pour l'événement '{selected_event}'.")

print(f"\nMatchs disponibles pour '{selected_event}' :")
for i, m in enumerate(matches, 1):
    print(f"  {i}. {m}")

selected_match_str = input("\nSélectionnez un match (nom exact, ex: Équipe A vs Équipe B) : ").strip()
matched_match = next((m for m in matches if str(m) == selected_match_str), None)
if matched_match is None:
    raise ValueError(
        f"Match '{selected_match_str}' introuvable. "
        f"Choix possibles : {[str(m) for m in matches]}"
    )
selected_match = matched_match


# ── Joueurs / Participations ────────────────────────────────────────────────
print(f"\nParticipations pour le match sélectionné :")
for p in selected_match.participations:
    print(f"  - {p}")
from pathlib import Path
import pandas as pd


df = pd.read_csv("wta_players_2024.csv")

ROOT = Path("Base_de_données")
sport_1 = "Basketball"
sport_2 = "Football"
sport_3 = "Lol"
sport_4 = "tennis"
sport_5 = "volleyball"

# Tennis
joueuse_tennis = ROOT / sport_4 / "wta_players_2024.csv"
joueur_tennis = ROOT / sport_4 / "atp_players_2024.csv"
matchs_femme_tennis = ROOT / sport_4 / "wta_matches_2024.csv"
matchs_homme_tennis = ROOT / sport_4 / "atp_matches_2024.csv"

df_joueuse_tennis = pd.read_csv(joueuse_tennis)
df_joueur_rennis = pd.read_csv(joueur_tennis)
df_matchs_femme_tennis = pd.read_csv(matchs_femme_tennis)
df_matchs_homme_tennis = pd.read_csv(matchs_homme_tennis)

# Basketball
joueur_basket = ROOT / sport_1 / "player.csv"
matchs_basket = ROOT / sport_1 / "match.csv"
equipe_basket = ROOT / sport_1 / "team.csv"

df_joueur_basket = pd.read_csv(joueur_basket)
df_matchs_basket = pd.read_csv(matchs_basket)
df_equipe_basket = pd.read_csv(equipe_basket)

# Football
pays_foot = ROOT / sport_2 / "country.csv"
matchs_foot = ROOT / sport_2 / "game.csv"
ligue_foot = ROOT / sport_2 / "league.csv"

df_pays_foot = pd.read_csv(pays_foot)
df_matchs_foot = pd.read_csv(matchs_foot)
df_ligue_foot = pd.read_csv(ligue_foot)

# Lol
coachs_lol = ROOT / sport_3 / "coach.csv"
matchs_lol = ROOT / sport_3 / "match.csv"
joueurs_lol = ROOT / sport_3 / "player.csv"
equipe_lol = ROOT / sport_3 / "team.csv"

df_coachs_lol = pd.read_csv(coachs_lol)
df_matchs_lol = pd.read_csv(matchs_lol)
df_joueurs_lol = pd.read_csv(joueurs_lol)
df_equipe_lol = pd.read_csv(equipe_lol)

# Volleyball
coachs_homme_volley = ROOT / sport_5 / "coach_men.csv"
coachs_femme_volley = ROOT / sport_5 / "coach_women.csv"
pays_volley = ROOT / sport_5 / "country.csv"
matchs_homme_volley = ROOT / sport_5 / "match_men.csv"
matchs_femme_volley = ROOT / sport_5 / "match_women.csv"
joueurs_femme_volley = ROOT / sport_5 / "player_women.csv"
joueurs_homme_volley = ROOT / sport_5 / "player_men.csv"

df_coachs_homme_volley = pd.read_csv(coachs_homme_volley)
df_coachs_femme_volley = pd.read_csv(coachs_femme_volley)
df_pays_volley = pd.read_csv(pays_volley)
df_matchs_homme_volley = pd.read_csv(matchs_homme_volley)
df_matchs_femme_volley = pd.read_csv(matchs_femme_volley)
df_joueurs_homme_volley = pd.read_csv(joueurs_homme_volley)
df_joueurs_femme_volley = pd.read_csv(joueurs_femme_volley)
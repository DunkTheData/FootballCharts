import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import re
from bs4 import BeautifulSoup

features_def = {'player',
                'comp_level',
                'squad',
                'position',
                'age',
                'birth_year',
                'minutes_90s',
                'tackles',
                'tackles_won',
                'pressures',
                'pressure_regains',
                'pressures_def_3rd',
                'pressures_mid_3rd',
                'pressures_att_3rd',
                'blocks',
                'interceptions',
                'clearances'}

features_misc = {'player',
                 'comp_level',
                 'squad',
                 'position',
                 'minutes_90s',
                 'cards_yellow',
                 'cards_red',
                 'fouls',
                 'fouled',
                 'offsides',
                 'crosses',
                 'pens_conceded',
                 'own_goals',
                 'ball_recoveries',
                 'aerials_won',
                 'aerials_lost',
                 'aerials_won_pct'}

features_poss = {'player',
                 'comp_level',
                 'squad',
                 'position',
                 'minutes_90s',
                 'touches',
                 'touches_def_pen_area',
                 'touches_def_3rd',
                 'touches_mid_3rd',
                 'touches_att_3rd',
                 'touches_att_pen_area',
                 'dribbles_completed',
                 'dribbles',
                 'dribbles_completed_pct',
                 'carries',
                 'carry_distance',
                 'carry_progressive_distance',
                 'pass_targets',
                 'passes_received',
                 'miscontrols',
                 'dispossessed',
                 'progressive_carries'}

features_pass = {'player',
                 'comp_level',
                 'squad',
                 'position',
                 'minutes_90s',
                 'passes_pct',
                 'passes_total_distance',
                 'passes_progressive_distance',
                 'passes_completed_long',
                 'passes_pct_long',
                 'assists',
                 'xa',
                 'assisted_shots',
                 'passes_into_final_third',
                 'passes_into_penalty_area',
                 'crosses_into_penalty_area',
                 'progressive_passes'}

features_shot = {'player',
                 'comp_level',
                 'squad',
                 'position',
                 'minutes_90s',
                 'goals',
                 'shots_total',
                 'shots_on_target',
                 'goals_per_shot',
                 'goals_per_shot_on_target',
                 'average_shot_distance',
                 'shots_free_kicks',
                 'pens_made',
                 'pens_att',
                 'npxg',
                 'npxg_per_shot'}

features_gk = {'player',
               'comp_level',
               'squad',
               'position',
               'minutes_90s',
               'shots_on_target_against',
               'saves',
               'clean_sheets_pct',
               'pens_save_pct'}

features_gk_adv = {'player',
                   'comp_level',
                   'squad',
                   'position',
                   'minutes_90s',
                   'psxg_gk',
                   'psnpxg_per_shot_on_target_against',
                   'passes_completed_launched_gk',
                   'passes_pct_launched_gk',
                   'goal_kick_length_avg',
                   'crosses_stopped_pct_gk',
                   'def_actions_outside_pen_area_gk',
                   'avg_distance_def_actions_gk'}

dict_labels = {
    'tackles': 'Tackles',
    'tackles_won': 'Tackles won',
    'pressures': 'Pressures',
    'pressure_regains': 'Pressure regains',
    'pressures_def_3rd': 'Pressure defensive 3rd',
    'pressures_mid_3rd': 'Pressure mid 3rd',
    'pressures_att_3rd': 'Pressure attacking 3rd',
    'blocks': 'Blocks',
    'interceptions': 'Interceptions',
    'clearances': 'Clearances',
    'cards_yellow': 'Yellow cards',
    'cards_red': 'Red cards',
    'fouls': 'Fouls committed',
    'fouled': 'Fouls drawn',
    'offsides': 'Offsides',
    'crosses': 'Crosses',
    'pens_conceded': 'Penalty conceded',
    'own_goals': 'Own goals',
    'ball_recoveries': 'Ball recoveries',
    'aerials_won': 'Aerials won',
    'aerials_lost': 'Aerials lost',
    'aerials_won_pct': 'Aerials win%',
    'touches': 'Touches',
    'touches_def_pen_area': 'Touches own penalty box',
    'touches_def_3rd': 'Touches defensive 3rd',
    'touches_mid_3rd': 'Touches mid 3rd',
    'touches_att_3rd': 'Touches attacking 3rd',
    'touches_att_pen_area': 'Touches opponent box',
    'dribbles_completed': 'Dribbles completed',
    'dribbles': 'Dribble attempts',
    'dribbles_completed_pct': 'Dribbles %',
    'carries': 'Carries',
    'carry_distance': 'Carry distance',
    'carry_progressive_distance': 'Carry progressive distance',
    'pass_targets': 'Targeted from passes',
    'passes_received': 'Passes received',
    'miscontrols': 'Miscontrols',
    'dispossessed': 'Dispossessed',
    'progressive_carries': 'Progressive carries',
    'passes_pct': 'Passing %',
    'passes_total_distance': 'Passes total distance',
    'passes_progressive_distance': 'Passes progressive distance',
    'passes_completed_long': 'Long passes completed',
    'passes_pct_long': 'Long passes completion%',
    'assists': 'Assists',
    'xa': 'xA',
    'assisted_shots': 'Key passes',
    'passes_into_final_third': 'Passes into final 3rd',
    'passes_into_penalty_area': 'Passes into box',
    'crosses_into_penalty_area': 'Crosses into box',
    'progressive_passes': 'Progressive passes',
    'goals': 'Goals',
    'shots_total': 'Shots',
    'shots_on_target': 'Shots on target',
    'goals_per_shot': 'Goals per shot',
    'goals_per_shot_on_target': 'Goals per shot on target',
    'average_shot_distance': 'Average shot distance',
    'shots_free_kicks': 'Shots from free kicks',
    'pens_made': 'Penalty scored',
    'pens_att': 'Penalty attempts',
    'npxg': 'npxG',
    'npxg_per_shot': 'npxG per shot',
    'shots_on_target_against': 'Shots on target faced',
    'saves': 'Saves',
    'clean_sheets_pct': 'Clean sheet %',
    'pens_save_pct': 'Penalty save%',
    'psxg_gk': 'PSxG',
    'psnpxg_per_shot_on_target_against': 'PSxG per shot on target',
    'passes_completed_launched_gk': 'Launched passes completed',
    'passes_pct_launched_gk': 'Launched passing %',
    'goal_kick_length_avg': 'Goal Kick average length',
    'crosses_stopped_pct_gk': 'Crosses stopped %',
    'def_actions_outside_pen_area_gk': 'Defensive actions out of box',
    'avg_distance_def_actions_gk': 'Average distance of defensive actions'
}


def get_soup(url):
    """
    :param url: a web URL
    :return: soup of the parsed url
    """
    res = requests.get(url)
    ## The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml')

    return soup


def get_player_table(soup):
    """
    :param soup:
    :return: player table
    """
    all_tables = soup.findAll("tbody")
    player_table = all_tables[1]

    return player_table


def get_final_data_per90(player_table, features_wanted):
    """
    :param player_table:
    :param features_wanted: features we need (tackles, goals etc...)
    :param min_numb_game: threshold for number of game played
    :return: df: dataframe with stats selected per 90 minutes
    """
    pre_df_player = dict()

    rows_squad = player_table.find_all('tr')
    for row in rows_squad:
        if (row.find('th', {"scope": "row"}) != None):
            for f in features_wanted:
                cell = row.find("td", {"data-stat": f})
                a = cell.text.strip().encode()
                text = a.decode("utf-8")
                if f in pre_df_player:
                    pre_df_player[f].append(text)
                else:
                    pre_df_player[f] = [text]

                if f == 'player':
                    link = 'https://fbref.com' + str(
                        cell.findAll('a', attrs={'href': re.compile("/en")})[0].get('href'))
                    if 'UrlFBref' in pre_df_player:
                        pre_df_player["UrlFBref"].append(link)
                    else:
                        pre_df_player["UrlFBref"] = [link]

    df = pd.DataFrame.from_dict(pre_df_player)

    for var in features_wanted:
        if var not in ['player', 'comp_level', 'squad', 'position', 'age', 'birth_year', 'minutes_90s']:
            if 'pct' not in var or 'avg' not in var:
                df[var] = df[var].replace('', 0).astype('float64') / df['minutes_90s'].astype('float64')
            else:
                df[var] = df[var].replace('', 0).astype('float64')

    return df

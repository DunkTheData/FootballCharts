import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import get_data
from get_data import features_def, features_misc, features_poss, features_pass, features_shot, features_gk, \
    features_gk_adv, dict_labels
from plot import templates, roles_templates_dict
import time


def app():
    st.title('Player comparator')
    st.write("Here you can make a comparison between 2 players")

    @st.cache(suppress_st_warning=True, show_spinner=False)
    def create_data():
        """
        Create the final Datarame with all the stats we need. The function is cached to improve user experience.

        Parameters
        ----------

        Returns
        -------
        df: Pandas DataFrame
        """
        with st.spinner('Gathering the data, please wait'):
            # Init a progress bar
            my_bar = st.progress(0)

            soup_def = get_data.get_soup('https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats')
            time.sleep(2)
            table_def = get_data.get_player_table(soup_def)
            df_def = get_data.get_final_data_per90(table_def, features_def)

            my_bar.progress(10)
            soup_misc = get_data.get_soup('https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats')
            time.sleep(2)
            table_misc = get_data.get_player_table(soup_misc)
            df_misc = get_data.get_final_data_per90(table_misc, features_misc)

            my_bar.progress(20)
            soup_poss = get_data.get_soup(
                'https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats')
            time.sleep(2)
            table_poss = get_data.get_player_table(soup_poss)
            df_poss = get_data.get_final_data_per90(table_poss, features_poss)

            my_bar.progress(30)
            soup_pass = get_data.get_soup(
                'https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats')
            time.sleep(2)
            table_pass = get_data.get_player_table(soup_pass)
            df_pass = get_data.get_final_data_per90(table_pass, features_pass)

            my_bar.progress(40)
            soup_shot = get_data.get_soup(
                'https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats')
            time.sleep(2)
            table_shot = get_data.get_player_table(soup_shot)
            df_shot = get_data.get_final_data_per90(table_shot, features_shot)

            my_bar.progress(50)
            soup_gk = get_data.get_soup(
                'https://fbref.com/en/comps/Big5/keepers/players/Big-5-European-Leagues-Stats')
            time.sleep(2)
            table_gk = get_data.get_player_table(soup_gk)
            df_gk = get_data.get_final_data_per90(table_gk, features_gk)

            my_bar.progress(60)
            soup_gk_adv = get_data.get_soup(
                'https://fbref.com/en/comps/Big5/keepersadv/players/Big-5-European-Leagues-Stats')
            time.sleep(2)
            table_gk_adv = get_data.get_player_table(soup_gk_adv)
            df_gk_adv = get_data.get_final_data_per90(table_gk_adv, features_gk_adv)

            my_bar.progress(80)

            # Merge all sub dataframes
            df = df_def.merge(df_misc,
                              on=['player', 'comp_level', 'squad', 'minutes_90s', 'position', 'UrlFBref']).merge(
                df_poss, on=['player', 'comp_level', 'squad', 'minutes_90s', 'position', 'UrlFBref']).merge(
                df_pass, on=['player', 'comp_level', 'squad', 'minutes_90s', 'position', 'UrlFBref']).merge(
                df_shot, on=['player', 'comp_level', 'squad', 'minutes_90s', 'position', 'UrlFBref']).merge(
                df_gk, on=['player', 'comp_level', 'squad', 'minutes_90s', 'position', 'UrlFBref'], how='outer').merge(
                df_gk_adv, on=['player', 'comp_level', 'squad', 'minutes_90s', 'position', 'UrlFBref'], how='outer')

            my_bar.progress(90)

            # Filter on players who did not play enough minutes
            min_threshold = float(0.3*df.minutes_90s.astype('float64').max())
            df = df.loc[df.minutes_90s.astype('float64') >= min_threshold].reset_index(drop=True)

            df['comp_level'] = df.comp_level.replace(
                ['eng Premier League', 'fr Ligue 1', 'de Bundesliga', 'it Serie A', 'es La Liga'],
                ['Premier League', 'Ligue 1', 'Bundesliga', 'Serie A', 'La Liga'])
            my_bar.progress(100)

        return df

    data = create_data()

    # Get the role of every player using an available dataset from @jaseziv
    roles = pd.read_csv(
        'https://raw.githubusercontent.com/JaseZiv/worldfootballR_data/master/raw-data/fbref-tm-player-mapping/output/fbref_to_tm_mapping.csv',
        encoding='unicode-escape')

    df = data.merge(roles[['UrlFBref', 'TmPos']], on=['UrlFBref'])
    df['position'] = df.TmPos.map(roles_templates_dict)

    # Select boxes for League, Team and Player choices
    leagues = df['comp_level'].drop_duplicates()
    league_choice = st.selectbox('Select a league:', leagues, key="1")

    col1, col2 = st.columns(2)

    with col1:
        teams = df["squad"].loc[df["comp_level"] == league_choice].drop_duplicates()
        team_choice = st.selectbox('Select a team', teams, key="2")
        players = df["player"].loc[df["squad"] == team_choice]
        player_choice = st.selectbox('Select a player', players, key="3")

    with col2:
        teams = df["squad"].loc[df["comp_level"] == league_choice].drop_duplicates()
        team_choice2 = st.selectbox('Select a team', teams, key="5")
        players = df["player"].loc[df["squad"] == team_choice2]
        player_choice2 = st.selectbox('Select a player', players, key="6")

    player = df.loc[df.player == player_choice].reset_index(drop=True)
    player2 = df.loc[df.player == player_choice2].reset_index(drop=True)

    # Use a variable that will be used for a test
    var_GK = 0
    if player.position.item() == 'Goalkeeper' and player2.position.item() != 'Goalkeeper':
        var_GK = 1
        st.warning('Goalkeepers can only be compared with each other.')
    elif player2.position.item() == 'Goalkeeper' and player.position.item() != 'Goalkeeper':
        var_GK = 1
        st.warning('Goalkeepers can only be compared with each other.')

    st.write('Select between three and ten variables:')

    choices = st.multiselect('Stats selected', sorted(dict_labels.values()))

    # Tests
    if len(choices) < 3:
        st.warning('You have to select minimum 3 variables.')
    elif len(choices) > 10:
        st.warning('You can select maximum 10 variables.')

    if not st.button('Done', key='Done2'):
        return

    if player_choice == player_choice2:
        st.warning('You must select 2 different players')
        return
    elif var_GK != 0:
        st.warning('Goalkeepers can only be compared with each other.')
        return

    # Inverse the dict with labels to get the correct columns names for the dataframe
    inv_dict_labels = {v: k for k, v in dict_labels.items()}
    options = [inv_dict_labels.get(f) for f in choices]

    # Values off the players
    values = player[options].values.flatten().tolist()
    values2 = player2[options].values.flatten().tolist()

    # Normalize [0-1]
    max_values = [df.loc[df.comp_level == league_choice][v].max() for v in options]
    min_values = [df.loc[df.comp_level == league_choice][v].min() for v in options]

    # Graph
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[round((x - m) / (M - m), 2) for M, m, x in zip(max_values, min_values, values)],
        theta=choices,
        customdata=values,
        line_color='#DFC27D',
        fill='toself',
        name=player_choice,
        hovertemplate=
        '<b>Value: %{customdata:.2f}</b>' +
        '<br><i>%{theta}</i> <br><extra></extra>',
    ))
    fig.add_trace(go.Scatterpolar(
        r=[round((x - m) / (M - m), 2) for M, m, x in zip(max_values, min_values, values2)],
        theta=choices,
        customdata=values2,
        line_color='#35978F',
        fill='toself',
        name=player_choice2,
        hovertemplate=
        '<b>Value: %{customdata:.2f}</b>' +
        '<br><i>%{theta}</i> <br><extra></extra>',
    ))

    fig.update_layout(
        height=800,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        template=None
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add a table with values of player and League average
    dict_table = dict()
    dict_table['Team'] = [team_choice, team_choice2]
    dict_table['Position'] = [player.position.item(), player2.position.item()]

    for i in range(len(options)):
        dict_table[dict_labels.get(options[i])] = [round(values[i], 2), round(values2[i], 2)]

    table = pd.DataFrame(dict_table, index=[player_choice, player_choice2])

    # Put the max value in blue
    st.write(
        table.style.format(formatter='{:.2f}', subset=list(table.columns)[3:]).highlight_max(
            subset=list(table.columns)[3:], color='skyblue', axis=0))

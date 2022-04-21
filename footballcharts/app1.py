import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import get_data
from scipy import stats
from get_data import features_def, features_misc, features_poss, features_pass, features_shot, features_gk, \
    features_gk_adv, dict_labels
from plot import templates, roles_templates_dict
import time


def app():
    st.title('Player bar chart')
    st.write("Here you can see the performances of a player compared to its peers")

    def get_quantile(vec, value):  # get color depending on value
        """
        Return a color depending on the dispersion of the value within a set of values

        Parameters
        ----------
        vec: Pandas series
        value: float

        Returns
        -------
        color: HEX color string
        """
        if value >= vec.quantile(0.9):
            color = '#2CBD42'
        elif value < vec.quantile(0.9) and value >= vec.quantile(0.6):
            color = '#9CE057'
        elif value < vec.quantile(0.6) and value >= vec.quantile(0.5):
            color = '#E3E349'
        elif value < vec.quantile(0.5) and value >= vec.quantile(0.4):
            color = '#E3E349'
        elif value < vec.quantile(0.4) and value >= vec.quantile(0.1):
            color = '#E4A759'
        elif value < vec.quantile(0.1):
            color = '#E84848'

        return color

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

    # Make select boxes for League, Team and Player choices
    leagues = df['comp_level'].drop_duplicates()
    league_choice = st.selectbox('Select a league:', leagues, key="1")
    teams = df["squad"].loc[df["comp_level"] == league_choice].drop_duplicates()
    team_choice = st.selectbox('Select a team', teams, key="2")
    players = df["player"].loc[df["squad"] == team_choice]
    player_choice = st.selectbox('Select a player', players, key="3")

    # Go button
    if not st.button('Go !'):
        return

    player_role = str(list(df.loc[df.player == player_choice].position.unique())[0])

    # Dataframe with only the needed columns
    plot_features = templates.get(player_role)
    final_df = df[['player', 'comp_level', 'squad', 'position'] + plot_features].dropna()

    # Player and League data that will be used for the graph'
    player = final_df.loc[final_df.player == player_choice].reset_index(drop=True)
    data = final_df.loc[(final_df.comp_level == league_choice) & (
            final_df.position == str(player.position[0]))].reset_index(drop=True)

    # List of player values
    values = player[plot_features].values.flatten().tolist()

    # Labels for the bar chart
    labels = [dict_labels.get(f) for f in plot_features]

    # Graph
    title = "{} compared to {} {}s".format(player_choice, league_choice, player_role)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=labels,
        x=[stats.percentileofscore(-1 * data[v], -1 * x) if v in ['dispossessed', 'fouls'] else stats.percentileofscore(data[v], x) for v, x in zip(plot_features, values)],
        customdata=values,
        hovertemplate=
        '<b>Value</b>: %{customdata:.2f}' +
        '<br><i>Percentile</i>: %{x:.0f} %<br><extra></extra>',
        orientation='h',
        showlegend=False,
        marker=dict(
            color=[get_quantile(data[v], x) for v, x in zip(plot_features, values)]
        )
    ))

    mean_values = [data[v].mean() for v in plot_features]
    means = [stats.percentileofscore(-1 * data[v], -1 * data[v].mean()) if v in ['dispossessed', 'fouls'] else stats.percentileofscore(data[v], data[v].mean()) for v in plot_features]

    for i in range(len(means)):
        fig2.add_shape(type='line',
                       yref="y",
                       xref="x",
                       x0=means[i],
                       y0=-0.4 + i,
                       x1=means[i],
                       y1=0.4 + i,
                       line=dict(color='black', width=2, dash='dot'))

    fig2.update_layout(
        title=title,
        xaxis_title="Percentile",
        yaxis_automargin=True,
        font=dict(
            family="Courier New, monospace"),
        width=9000,
        height=800,
        hovermode="closest",
        template=None
    )

    # Legend
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                              marker=dict(size=15, color='#2CBD42', symbol='square'), showlegend=True, name='Top 10%'))
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                              marker=dict(size=15, color='#9CE057', symbol='square'), showlegend=True, name='Top 40%'))
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                              marker=dict(size=15, color='#E3E349', symbol='square'), showlegend=True, name='Median'))
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                              marker=dict(size=15, color='#E4A759', symbol='square'), showlegend=True,
                              name='Bottom 40%'))
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                              marker=dict(size=15, color='#E84848', symbol='square'), showlegend=True,
                              name='Bottom 10%'))

    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                              line=dict(color='black', width=2, dash='dot'), showlegend=True,
                              name=f'League average {player_role}'))

    st.plotly_chart(fig2, use_container_width=True)

    # Add a table with values of player and League average
    dict_table = dict()
    dict_table['Team'] = [team_choice, '-']
    dict_table['Position'] = [str(player.position[0])] * 2

    for i in range(len(labels)):
        dict_table[labels[i]] = [round(values[i], 2), round(mean_values[i], 2)]

    table = pd.DataFrame(dict_table, index=[player_choice, 'League average'])

    # Put the max value in blue
    st.write(
        table.style.format(formatter='{:.2f}', subset=list(table.columns)[3:]).highlight_max(
            subset=list(table.columns)[3:], color='skyblue', axis=0))

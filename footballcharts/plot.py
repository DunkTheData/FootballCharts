templates = {
    'Goalkeeper': ['def_actions_outside_pen_area_gk', 'passes_completed_launched_gk', 'passes_pct_launched_gk',
           'crosses_stopped_pct_gk', 'shots_on_target_against', 'psnpxg_per_shot_on_target_against', 'psxg_gk',
           'clean_sheets_pct', 'saves'],

    'Full Back': ['tackles_won', 'interceptions', 'aerials_won_pct', 'carry_progressive_distance', 'dribbles_completed',
           'crosses', 'passes_into_final_third', 'assisted_shots', 'xa', 'assists'],

    'Central Back': ['passes_pct', 'passes_completed_long', 'passes_progressive_distance', 'aerials_won_pct', 'aerials_won',
           'fouls', 'pressures', 'clearances', 'interceptions', 'tackles_won'],

    'Defensive Midfielder': ['fouls', 'pressures', 'clearances', 'interceptions', 'tackles_won', 'aerials_won', 'carries',
           'carry_progressive_distance', 'progressive_passes', 'passes_pct'],

    'Midfielder': ['fouls', 'pressure_regains', 'interceptions', 'aerials_won', 'carries', 'carry_progressive_distance',
            'xa', 'assisted_shots', 'progressive_passes', 'passes_into_final_third', 'passes_pct'],

    'Winger': ['pressure_regains', 'dispossessed', 'fouled', 'dribbles_completed', 'xa', 'crosses', 'passes_pct',
           'touches_att_pen_area', 'npxg', 'shots_total'],

    'Advanced Midfielder': ['pressure_regains', 'dispossessed', 'fouled', 'dribbles_completed', 'xa', 'assisted_shots',
           'progressive_passes', 'passes_pct', 'touches_att_pen_area', 'npxg', 'shots_total'],

    'Striker': ['pressure_regains', 'aerials_won_pct', 'aerials_won', 'xa', 'assisted_shots', 'touches_att_pen_area',
           'npxg_per_shot', 'npxg', 'shots_on_target', 'shots_total']
}

roles_templates_dict = {
    'Goalkeeper': 'Goalkeeper',
    'Left-Back': 'Full Back',
    'Right-Back': 'Full Back',
    'Centre-Back': 'Central Back',
    'Defensive Midfield': 'Defensive Midfielder',
    'Left Midfield': 'Midfielder',
    'Central Midfield': 'Midfielder',
    'Right Midfield': 'Midfielder',
    'Left Winger': 'Winger',
    'Right Winger': 'Winger',
    'Attacking Midfield': 'Advanced Midfielder',
    'Centre-Forward': 'Striker',
    'Second Striker': 'Striker'
}

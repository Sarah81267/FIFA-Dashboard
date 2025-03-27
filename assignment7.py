# Published dashboard link: [Your Render Link Here]
# Password (if applicable): [Your Password Here]

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Dataset setup (same as before)
data = {
    'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 
             1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
    'Winner': ['Uruguay', 'Italy', 'Italy', 'Uruguay', 'Germany', 'Brazil', 'Brazil', 
               'England', 'Brazil', 'Germany', 'Argentina', 'Italy', 'Argentina', 
               'Germany', 'Brazil', 'France', 'Brazil', 'Italy', 'Spain', 'Germany', 'France', 'Argentina'],
    'Runner-up': ['Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary', 
                  'Sweden', 'Czechoslovakia', 'Germany', 'Italy', 'Netherlands', 
                  'Netherlands', 'Germany', 'Germany', 'Argentina', 'Italy', 
                  'Brazil', 'Germany', 'France', 'Netherlands', 'Argentina', 'Croatia', 'France'],
    'Host': ['Uruguay', 'Italy', 'France', 'Brazil', 'Switzerland', 'Sweden', 
             'Chile', 'England', 'Mexico', 'Germany', 'Argentina', 'Spain', 
             'Mexico', 'Italy', 'United States', 'France', 'South Korea/Japan', 
             'Germany', 'South Africa', 'Brazil', 'Russia', 'Qatar']
}

df = pd.DataFrame(data)
df.replace('West Germany', 'Germany', inplace=True)

country_codes = {
    'Argentina': 'ARG', 'Brazil': 'BRA', 'Chile': 'CHL', 'Croatia': 'HRV',
    'Czechoslovakia': 'CZE', 'England': 'GBR', 'France': 'FRA', 'Germany': 'DEU',
    'Hungary': 'HUN', 'Italy': 'ITA', 'Mexico': 'MEX', 'Netherlands': 'NLD',
    'Qatar': 'QAT', 'Russia': 'RUS', 'South Africa': 'ZAF', 'South Korea/Japan': 'KOR',
    'Spain': 'ESP', 'Sweden': 'SWE', 'Switzerland': 'CHE', 'United States': 'USA',
    'Uruguay': 'URY'
}

winners_count = df['Winner'].value_counts().reset_index()
winners_count.columns = ['Country', 'Wins']
winners_count['Code'] = winners_count['Country'].map(country_codes)

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    html.H1("FIFA World Cup Winners Dashboard", style={'textAlign': 'center', 'color': '#00529F'}),
    
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='World Cup Winners Map', value='tab-1'),
        dcc.Tab(label='Country Performance', value='tab-2'),
        dcc.Tab(label='Tournament Details', value='tab-3'),
    ]),
    html.Div(id='tabs-content', style={'margin': '20px'})
])

# Tab content callback
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        fig = px.choropleth(
            winners_count,
            locations="Code",
            color="Wins",
            hover_name="Country",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Number of World Cup Wins by Country",
            projection="natural earth"
        )
        fig.update_geos(showcountries=True, countrycolor="black")
        return html.Div([dcc.Graph(figure=fig, style={'height': '70vh'})])
    
    elif tab == 'tab-2':
        return html.Div([
            html.H3("Select a country:", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df['Winner'].unique())],
                value='Brazil',
                style={'width': '60%', 'margin': '20px auto'}
            ),
            html.Div(id='country-output')
        ])
    
    elif tab == 'tab-3':
        return html.Div([
            html.H3("Select a year:", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(y), 'value': y} for y in sorted(df['Year'], reverse=True)],
                value=2022,
                style={'width': '60%', 'margin': '20px auto'}
            ),
            html.Div(id='year-output')
        ])

# Country performance with star timeline
@app.callback(
    Output('country-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_output(selected_country):
    wins = df[df['Winner'] == selected_country].copy()
    runner_ups = df[df['Runner-up'] == selected_country].copy()
    
    # Create star-marked timeline
    fig = go.Figure()
    
    if len(wins) > 0:
        fig.add_trace(go.Scatter(
            x=wins['Year'],
            y=['Winner']*len(wins),
            mode='markers+text',
            marker=dict(size=16, color='gold', symbol='star'),
            name='Winner',
            text=[f"Won {y}" for y in wins['Year']],
            textposition='top center'
        ))
    
    if len(runner_ups) > 0:
        fig.add_trace(go.Scatter(
            x=runner_ups['Year'],
            y=['Runner-up']*len(runner_ups),
            mode='markers+text',
            marker=dict(size=16, color='silver', symbol='star'),
            name='Runner-up',
            text=[f"Runner-up {y}" for y in runner_ups['Year']],
            textposition='top center'
        ))
    
    fig.update_layout(
        title=f"{selected_country}'s World Cup Performance",
        xaxis_title="Year",
        yaxis=dict(showgrid=False),
        height=400
    )
    
    return html.Div([
        html.Div([
            html.Div([
                html.H4("Total Wins:", style={'color': 'gold'}),
                html.H2(len(wins), style={'textAlign': 'center'})
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                html.H4("Runner-up Finishes:", style={'color': 'silver'}),
                html.H2(len(runner_ups), style={'textAlign': 'center'})
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
        ], style={'textAlign': 'center'}),
        
        dcc.Graph(figure=fig)
    ])

# Tournament details (unchanged)
# Tournament details callback with white background
@app.callback(
    Output('year-output', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_output(selected_year):
    year_data = df[df['Year'] == selected_year].iloc[0]
    return html.Div([
        html.Div([  # Added container div with white background
            html.H4(f"{selected_year} World Cup Results", style={'marginTop': '0'}),
            html.P(f"🏆 Winner: {year_data['Winner']}"),
            html.P(f"🥈 Runner-up: {year_data['Runner-up']}"),
            html.P(f"🏟️ Host: {year_data['Host']}")
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        })
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
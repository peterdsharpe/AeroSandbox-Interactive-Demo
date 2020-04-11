import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sub
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import aerosandbox as asb
import lorem
from airplane import *

app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])


app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                html.H1("Aircraft Design with Dash"),
                html.H5("Peter Sharpe"),
            ], width=True),
            dbc.Col([
                html.Img(src="assets/MIT-logo-red-gray-72x38.svg", alt="MIT Logo", height="30px"),
            ], width=1)
        ], align="end"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Key Parameters"),
                    html.P("Wing Span [m]:"),
                    dcc.Input(id='span', value="37.5", type="text"),
                ]),
                html.Hr(),
                html.Div([
                    html.H5("Commands"),
                    # html.Div([
                    #     html.Button("Display Geometry")
                    # ], style={"padding": 10}),
                    # html.Div([
                    #     html.Button("Run Analysis"),
                    # ], style={"padding": 10}),
                    dbc.Button("Display Geometry", id="draw", color="primary", style={"margin": "5px"}),
                    dbc.Button("Run Analysis", id="analyze", color="secondary", style={"margin": "5px"}),
                ]),
                html.Hr(),
                html.Div([
                    html.H5("Aerodynamic Performance"),
                    html.P(id='output')
                ])
            ], width=5),
            dbc.Col([
                # html.Div(id='display')
                dcc.Graph(id='display', style={'height': '80vh'})
            ], width=True)
        ])
    ],
    fluid=True
)

@app.callback(
    Output(component_id='display', component_property='figure'),
    [Input(component_id='span', component_property='value')]
)
def update_display(input_value):
    figure = make_airplane_figure(wing_span=eval(input_value))
    figure.update_layout(
        autosize=True,
        # width=1000,
        # height=700,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
        )
    )
    return figure

try:  # wrapping this, since a forum post said it may be deprecated at some point.
    app.title = "Aircraft Design with Dash"
except:
    print("Could not set the page title!")
app.run_server(debug=True)

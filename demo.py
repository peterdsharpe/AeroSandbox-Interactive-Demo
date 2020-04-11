import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sub
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import aerosandbox as asb
import casadi as cas
from airplane import *

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                html.H1("Solar Aircraft Design with AeroSandbox and Dash"),
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
                    dcc.Input(id='wing_span', value=43, type="number"),
                    html.P("Angle of Attack [deg]:"),
                    dcc.Input(id='alpha', value=7.0, type="number"),
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
                    dbc.Button("Display Geometry", id="display_geometry", color="primary", style={"margin": "5px"}),
                    dbc.Button("Run Analysis", id="run_analysis", color="secondary", style={"margin": "5px"}),
                ]),
                html.Hr(),
                html.Div([
                    html.H5("Aerodynamic Performance"),
                    html.P(id='output')
                ])
            ], width=3),
            dbc.Col([
                # html.Div(id='display')
                dbc.Spinner(
                    dcc.Graph(id='display', style={'height': '80vh'}),
                    color="primary"
                )
            ], width=True)
        ])
    ],
    fluid=True
)
display_geometry_n_clicks_last = [0]
run_analysis_n_clicks_last = [0]


@app.callback(
    [Output('display', 'figure'),
     Output('output', 'children')
     ],
    [
        Input('display_geometry', 'n_clicks'),
        Input('run_analysis', 'n_clicks'),
    ],
    [
        State('wing_span', 'value'),
        State('alpha', 'value'),
    ]
)
def display_geometry(
        display_geometry_n_clicks,
        run_analysis_n_clicks,
        wing_span,
        alpha,
):
    airplane = make_airplane(
        wing_span=wing_span
    )
    op_point = asb.OperatingPoint(
        density=0.10,
        velocity=20,
        alpha=alpha,
    )
    if not display_geometry_n_clicks == display_geometry_n_clicks_last[0]:
        display_geometry_n_clicks_last[0] = display_geometry_n_clicks
        # Display the geometry
        figure = airplane.draw(show=False)
        output = ""
    elif not run_analysis_n_clicks == run_analysis_n_clicks_last[0]:
        run_analysis_n_clicks_last[0] = run_analysis_n_clicks
        # Run an analysis
        opti = cas.Opti()  # Initialize an analysis/optimization environment
        # airplane.fuselages=[]
        ap = asb.Casll1(
            airplane=airplane,
            op_point=op_point,
            opti=opti
        )
        # Solver options
        p_opts = {}
        s_opts = {}
        # s_opts["mu_strategy"] = "adaptive"
        opti.solver('ipopt', p_opts, s_opts)
        # Solve
        try:
            sol = opti.solve()
        except RuntimeError:
            sol = opti.debug
            raise Exception("An error occurred!")
        # Postprocess
        ap.substitute_solution(sol)

        figure = ap.draw(show=False)  # Generates
        output = []
        o = lambda x: output.extend([x, html.Br()])
        tab = "..." * 4
        o("CL: %.4f" % ap.CL)
        o("CD: %.4f" % ap.CD)
        o(tab + "CDi: %.4f" % ap.CDi)
        o(tab + "CDp: %.4f" % ap.CDp)
        o("L/D: %.3f" % (ap.CL / ap.CD))
        output = html.P(output)
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
    camera = dict
    return (figure, output)


try:  # wrapping this, since a forum post said it may be deprecated at some point.
    app.title = "Aircraft Design with Dash"
except:
    print("Could not set the page title!")
app.run_server(debug=False)

import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sub
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import aerosandbox as asb
import numpy as np
import pandas as pd

from airplane import make_airplane

app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                html.H2("Solar Aircraft Design with AeroSandbox and Dash"),
                html.H5("Peter Sharpe"),
            ], width=True),
            # dbc.Col([
            #     html.Img(src="assets/MIT-logo-red-gray-72x38.svg", alt="MIT Logo", height="30px"),
            # ], width=1)
        ], align="end"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Key Parameters"),
                    html.P("Number of booms:"),
                    dcc.Slider(
                        id='n_booms',
                        min=1,
                        max=3,
                        step=1,
                        value=1,
                        marks={
                            1: "1",
                            2: "2",
                            3: "3",
                        }
                    ),
                    html.P("Wing Span [m]:"),
                    dcc.Input(id='wing_span', value=43, type="number"),
                    html.P("Angle of Attack [deg]:"),
                    dcc.Input(id='alpha', value=7.0, type="number"),
                ]),
                html.Hr(),
                html.Div([
                    html.H5("Commands"),
                    dbc.Button("Display (1s)", id="display_geometry", color="primary", style={"margin": "5px"},
                               n_clicks_timestamp='0'),
                    dbc.Button("LL Analysis (3s)", id="run_ll_analysis", color="secondary", style={"margin": "5px"},
                               n_clicks_timestamp='0'),
                    dbc.Button("VLM Analysis (15s)", id="run_vlm_analysis", color="secondary",
                               style={"margin": "5px"}, n_clicks_timestamp='0'),
                ]),
                html.Hr(),
                html.Div([
                    html.H5("Aerodynamic Performance"),
                    dbc.Spinner(
                        html.P(id='output'),
                        color="primary",
                    )
                ])
            ], width=3),
            dbc.Col([
                # html.Div(id='display')
                dbc.Spinner(
                    dcc.Graph(id='display', style={'height': '80vh'}),
                    color="primary"
                )
            ], width=True)
        ]),
        html.Hr(),
        html.P([
            html.A("Source code", href="https://github.com/peterdsharpe/AeroSandbox-Interactive-Demo"),
            ". Aircraft design tools powered by ",
            html.A("AeroSandbox", href="https://peterdsharpe.github.com/AeroSandbox"),
            ". Build beautiful UIs for your scientific computing apps with ",
            html.A("Plot.ly ", href="https://plotly.com/"),
            "and ",
            html.A("Dash", href="https://plotly.com/dash/"),
            "!",
        ]),
    ],
    fluid=True
)


def make_table(dataframe):
    return dbc.Table.from_dataframe(
        dataframe,
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        style={

        }
    )


@app.callback(
    [Output('display', 'figure'),
     Output('output', 'children')
     ],
    [
        Input('display_geometry', 'n_clicks_timestamp'),
        Input('run_ll_analysis', 'n_clicks_timestamp'),
        Input('run_vlm_analysis', 'n_clicks_timestamp'),
    ],
    [
        State('n_booms', 'value'),
        State('wing_span', 'value'),
        State('alpha', 'value'),
    ]
)
def display_geometry(
        display_geometry,
        run_ll_analysis,
        run_vlm_analysis,
        n_booms,
        wing_span,
        alpha,
):
    ### Figure out which button was clicked
    try:
        button_pressed = np.argmax(np.array([
            float(display_geometry),
            float(run_ll_analysis),
            float(run_vlm_analysis),
        ]))
        assert button_pressed is not None
    except:
        button_pressed = 0

    ### Make the airplane
    airplane = make_airplane(
        n_booms=n_booms,
        wing_span=wing_span,
    )
    if button_pressed == 0:
        # Display the geometry
        figure = airplane.draw(show=False, backend='plotly')
        output = "Please run an analysis to display the data."
    elif button_pressed == 1:
        # Run an analysis
        opti = asb.Opti()  # Initialize an analysis/optimization environment

        ap, result = analyse_ll(
            my_airplane=airplane,
            ms_velocity=20,
            angle_of_attack=alpha,
            angle_of_sideslip=0,
        )
        # Solver options
        p_opts = {}
        s_opts = {}
        s_opts["max_iter"] = 50
        # s_opts["mu_strategy"] = "adaptive"
        opti.solver('ipopt', p_opts, s_opts)
        # Solve
        try:
            sol = opti.solve()
            output = make_table(pd.DataFrame(
                {
                    "Figure": [
                        "CL",
                        "CD",
                        "L/D"
                    ],
                    "Value" : [
                        sol.value(result["CL"]),
                        sol.value(result["CD"]),
                        sol.value(result["CL"] / result["CD"]),
                    ]
                }
            ))
        except RuntimeError as e:
            sol = opti.debug
            output = html.P(
                "Aerodynamic analysis failed! Most likely the airplane is stalled at this flight condition."
            )
            print(e)

        figure = ap.draw(show=False, backend='plotly')

    elif button_pressed == 2:
        # Run an analysis
        opti = asb.Opti()  # Initialize an analysis/optimization environment
        ap, result = analyse_vlm(
            my_airplane=airplane,
            ms_velocity=20,
            angle_of_attack=alpha,
            angle_of_sideslip=0,
        )
        # Solver options
        p_opts = {}
        s_opts = {}
        s_opts["max_iter"] = 50
        # s_opts["mu_strategy"] = "adaptive"
        opti.solver('ipopt', p_opts, s_opts)
        # Solve
        try:
            sol = opti.solve()
            output = make_table(pd.DataFrame(
                {
                    "Figure": [
                        "CL",
                        "CD",
                        "L/D"
                    ],
                    "Value" : [
                        sol.value(result["CL"]),
                        sol.value(result["CD"]),
                        sol.value(result["CL"] / result["CD"]),
                    ]
                }
            ))
        except RuntimeError as e:
            sol = opti.debug
            output = html.P(
                "Aerodynamic analysis failed! Most likely the airplane is stalled at this flight condition."
            )
            print(e)

        figure = ap.draw(show=False, backend='plotly')  # Generates figure

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

    return (figure, output)

# Analysis type: Vortex Lattice Method
def analyse_vlm(
        my_airplane,
        ms_velocity,
        angle_of_attack,
        angle_of_sideslip,
):

    op_point=asb.OperatingPoint(
        atmosphere=asb.Atmosphere(altitude=0),
        velocity=ms_velocity,  # airspeed, m/s
        alpha=angle_of_attack,  # angle of attack, deg
        beta=angle_of_sideslip,  # sideslip angle, deg
        p=0,  # x-axis rotation rate, rad/sec
        q=0,  # y-axis rotation rate, rad/sec
        r=0,  # z-axis rotation rate, rad/sec
    )

    xyz_ref = [
        my_airplane.wings[0].aerodynamic_center(chord_fraction=0.35)[0],
        0,
        0
    ]

    analysis = asb.VortexLatticeMethod(
        airplane=my_airplane,
        op_point=op_point,
        xyz_ref=xyz_ref,
    )
    result = analysis.run()

    return (analysis, result)

# Analysis type: LiftingLine
def analyse_ll(
        my_airplane,
        ms_velocity,
        angle_of_attack,
        angle_of_sideslip,
):

    op_point = asb.OperatingPoint(
            atmosphere=asb.Atmosphere(altitude=0),
            velocity=ms_velocity,  # airspeed, m/s
            alpha=angle_of_attack,  # angle of attack, deg
            beta=angle_of_sideslip,  # sideslip angle, deg
            p=0,  # x-axis rotation rate, rad/sec
            q=0,  # y-axis rotation rate, rad/sec
            r=0,  # z-axis rotation rate, rad/sec
        )

    xyz_ref = [
        my_airplane.wings[0].aerodynamic_center(chord_fraction=0.35)[0],
        0,
        0
    ]

    analysis = asb.LiftingLine(
        airplane=my_airplane,
        op_point=op_point,
        xyz_ref=xyz_ref,
    )
    result = analysis.run()

    return (analysis, result)

if __name__ == '__main__':
    app.run(debug=False)

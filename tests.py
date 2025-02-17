import aerosandbox as asb
from airplane import make_airplane


def test_lifting_line():
    n_booms = 3
    wing_span = 40
    alpha = 5

    airplane = make_airplane(
        n_booms=n_booms,
        wing_span=wing_span,
    )

    op_point = asb.OperatingPoint(
        velocity=20,
        alpha=alpha,
    )

    ### LL
    # Run an analysis
    opti = asb.Opti()  # Initialize an analysis/optimization environment
    # airplane.fuselages=[]
    ap = asb.LiftingLine(
        airplane=airplane,
        op_point=op_point,
    )
    result = ap.run()
    # Solver options
    p_opts = {}
    s_opts = {}
    # s_opts["mu_strategy"] = "adaptive"
    opti.solver("ipopt", p_opts, s_opts)
    # Solve
    try:
        sol = opti.solve()
    except RuntimeError:
        sol = opti.debug
        raise Exception("An error occurred!")
    # Postprocess
    # ap.substitute_solution(sol)
    ap.draw(show=False, backend="plotly").show()


if __name__ == "__main__":
    test_lifting_line()

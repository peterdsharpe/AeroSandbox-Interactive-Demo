import aerosandbox as asb
import casadi as cas
from airplane import make_airplane

wing_span = 40
alpha = 5

airplane = make_airplane(
    wing_span=wing_span
)
op_point = asb.OperatingPoint(
    density=0.10,
    velocity=20,
    alpha=alpha,
)

### LL
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
# ap.substitute_solution(sol)
ap.draw()
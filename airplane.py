import aerosandbox as asb
import numpy as np
import copy

naca0008 = asb.Airfoil(name="naca0008")
e216 = asb.Airfoil(name="e216")

def make_airplane(
        n_booms=1,
        wing_span=43,
)-> asb.Airplane:

    # boom length
    boom_length = 6.181

    # wing
    # wing_span = 37.126
    wing_root_chord = 2.316
    wing_x_quarter_chord = -0.1

    # hstab
    hstab_span = 2.867
    hstab_chord = 1.085
    hstab_twist_angle = -4

    # vstab
    vstab_span = 2.397
    vstab_chord = 1.134

    wing = asb.Wing(
        name="Main Wing",
        # x_le=-0.05 * wing_root_chord,  # Coordinates of the wing's leading edge # TODO make this a free parameter?
        #x_le=wing_x_quarter_chord,  # Coordinates of the wing's leading edge # TODO make this a free parameter?
        symmetric=True,
        xsecs=[  # The wing's cross ("X") sections
            asb.WingXSec(  # Root
                # Coordinates of the XSec's leading edge, relative to the wing's leading edge.
                xyz_le=[-wing_root_chord / 4, 0, 0],
                chord=wing_root_chord,
                twist=0,  # degrees
                airfoil=e216,  # Airfoils are blended between a given XSec and the next one.
                control_surface_type='symmetric',
                # Flap # Control surfaces are applied between a given XSec and the next one.
                control_surface_deflection=0,  # degrees
                spanwise_panels=30
            ),
            asb.WingXSec(  # Tip
                #z_le=0,  # wing_span / 2 * cas.pi / 180 * 5,
                xyz_le=[-wing_root_chord * 0.5 / 4, wing_span / 2, 0],
                chord=wing_root_chord * 0.5,
                twist=0,
                airfoil=e216,
            ),
        ]
    ).translate([-0.05 * wing_root_chord, 0, 0])

    hstab = asb.Wing(
        name="Horizontal Stabilizer",
        symmetric=True,
        xsecs=[  # The wing's cross ("X") sections
            asb.WingXSec(  # Root
                # Coordinates of the XSec's leading edge, relative to the wing's leading edge.
                xyz_le=[0, 0, 0],
                chord=hstab_chord,
                twist=hstab_twist_angle,  # degrees # TODO fix
                airfoil=naca0008,  # Airfoils are blended between a given XSec and the next one.
                control_surface_type='symmetric',
                # Flap # Control surfaces are applied between a given XSec and the next one.
                control_surface_deflection=0,  # degrees
                spanwise_panels=8
            ),
            asb.WingXSec(  # Tip
                xyz_le=[0, hstab_span / 2, 0],
                chord=hstab_chord,
                twist=hstab_twist_angle,  # TODO fix
                airfoil=naca0008,
            ),
        ]
    ).translate([boom_length - vstab_chord * 0.75 - hstab_chord, 0, 0]) # Coordinates of the wing's leading edge

    vstab = asb.Wing(
        name="Vertical Stabilizer",
        symmetric=False,
        xsecs=[  # The wing's cross ("X") sections
            asb.WingXSec(  # Root
                #xyz_le Coordinates of the XSec's leading edge, relative to the wing's leading edge.
                xyz_le=[0, 0, 0],
                chord=vstab_chord,
                twist=0,  # degrees
                airfoil=naca0008,  # Airfoils are blended between a given XSec and the next one.
                control_surface_type='symmetric',
                # Flap # Control surfaces are applied between a given XSec and the next one.
                control_surface_deflection=0,  # degrees
                spanwise_panels=8
            ),
            asb.WingXSec(  # Tip
                xyz_le=[0, 0, vstab_span],
                chord=vstab_chord,
                twist=0,
                airfoil=naca0008,
            ),
        ]
    ).translate([boom_length - vstab_chord * 0.75, 0, -vstab_span / 2 + vstab_span * 0.15]) # Coordinates of the wing's leading edge

    ### Build the fuselage geometry
    # boom_length = 6.181
    # nose_length = 1.5
    # fuse_diameter = 0.6
    # boom_diameter = 0.2
    #
    # wing_x_quarter_chord
    fuse = build_fuse(
        boom_length = boom_length,
        nose_length = 1.5,
        fuse_diameter = 0.6,
        boom_diameter = 0.2,
        wing_x_quarter_chord = wing_x_quarter_chord,
        wing_root_chord = wing_root_chord,
    )

    # Assemble the airplane
    fuses = []
    hstabs = []
    vstabs = []
    if n_booms == 1:
        fuses.append(fuse)
        hstabs.append(hstab)
        vstabs.append(vstab)
    elif n_booms == 2:
        boom_location = 0.40  # as a fraction of the half-span
        left_coordinates = [0, -wing_span / 2 * boom_location, 0]
        right_coordinates = [0, wing_span / 2 * boom_location, 0]

        left_fuse_clone = copy.deepcopy(fuse)
        right_fuse_clone = copy.deepcopy(fuse)
        left_fuse = left_fuse_clone.translate(left_coordinates)
        right_fuse = right_fuse_clone.translate(right_coordinates)
        fuses.extend([left_fuse, right_fuse])

        left_hstab_clone = copy.deepcopy(hstab)
        right_hstab_clone = copy.deepcopy(hstab)
        left_hstab = left_hstab_clone.translate(left_coordinates)
        right_hstab = right_hstab_clone.translate(right_coordinates)
        hstabs.extend([left_hstab, right_hstab])

        left_vstab_clone = copy.deepcopy(vstab)
        right_vstab_clone = copy.deepcopy(vstab)
        left_vstab = left_vstab_clone.translate(left_coordinates)
        right_vstab = right_vstab_clone.translate(right_coordinates)
        vstabs.extend([left_vstab, right_vstab])

    elif n_booms == 3:
        boom_location = 0.57  # as a fraction of the half-span
        left_coordinates = [0, -wing_span / 2 * boom_location, 0]
        right_coordinates = [0, wing_span / 2 * boom_location, 0]

        left_fuse_clone = copy.deepcopy(fuse)
        center_fuse = copy.deepcopy(fuse)
        right_fuse_clone = copy.deepcopy(fuse)
        left_fuse = left_fuse_clone.translate(left_coordinates)
        right_fuse = right_fuse_clone.translate(right_coordinates)
        fuses.extend([left_fuse, center_fuse, right_fuse])

        left_hstab_clone = copy.deepcopy(hstab)
        center_hstab = copy.deepcopy(hstab)
        right_hstab_clone = copy.deepcopy(hstab)
        left_hstab = left_hstab_clone.translate(left_coordinates)
        right_hstab = right_hstab_clone.translate(right_coordinates)
        hstabs.extend([left_hstab, center_hstab, right_hstab])

        left_vstab_clone = copy.deepcopy(vstab)
        center_vstab = copy.deepcopy(vstab)
        right_vstab_clone = copy.deepcopy(vstab)
        left_vstab = left_vstab_clone.translate(left_coordinates)
        right_vstab = right_vstab_clone.translate(right_coordinates)
        vstabs.extend([left_vstab, center_vstab, right_vstab])

    else:
        raise ValueError("Bad value of n_booms!")

    airplane = asb.Airplane(
        name="Solar1",
        xyz_ref=[0.5, 0, 0],
        s_ref=9,
        c_ref=0.9,
        b_ref=10,
        wings=[wing] + hstabs + vstabs,
        fuselages=fuses,
    )

    return airplane


def build_fuse(
    boom_length,
    nose_length,
    fuse_diameter,
    boom_diameter,
    wing_x_quarter_chord,
    wing_root_chord,
):
    blend = lambda x: (1 - np.cos(np.pi * x)) / 2
    fuse_x_c = []
    fuse_z_c = []
    fuse_radius = []
    fuse_resolution = 10
    # Nose geometry
    fuse_nose_theta = np.linspace(0, np.pi / 2, fuse_resolution)
    fuse_x_c.extend([
        (wing_x_quarter_chord - wing_root_chord / 4) - nose_length * np.cos(theta) for theta in fuse_nose_theta
    ])
    fuse_z_c.extend([-fuse_diameter / 2] * fuse_resolution)
    fuse_radius.extend([
        fuse_diameter / 2 * np.sin(theta) for theta in fuse_nose_theta
    ])
    # Taper
    fuse_taper_x_nondim = np.linspace(0, 1, fuse_resolution)
    fuse_x_c.extend([
        0.0 * boom_length + (0.6 - 0.0) * boom_length * x_nd for x_nd in fuse_taper_x_nondim
    ])
    fuse_z_c.extend([
        -fuse_diameter / 2 * blend(1 - x_nd) - boom_diameter / 2 * blend(x_nd) for x_nd in fuse_taper_x_nondim
    ])
    fuse_radius.extend([
        fuse_diameter / 2 * blend(1 - x_nd) + boom_diameter / 2 * blend(x_nd) for x_nd in fuse_taper_x_nondim
    ])
    # Tail
    # fuse_tail_x_nondim = np.linspace(0, 1, fuse_resolution)[1:]
    # fuse_x_c.extend([
    #     0.9 * boom_length + (1 - 0.9) * boom_length * x_nd for x_nd in fuse_taper_x_nondim
    # ])
    # fuse_z_c.extend([
    #     -boom_diameter / 2 * blend(1 - x_nd) for x_nd in fuse_taper_x_nondim
    # ])
    # fuse_radius.extend([
    #     boom_diameter / 2 * blend(1 - x_nd) for x_nd in fuse_taper_x_nondim
    # ])
    fuse_straight_resolution = 4
    fuse_x_c.extend([
        0.6 * boom_length + (1 - 0.6) * boom_length * x_nd for x_nd in np.linspace(0, 1, fuse_straight_resolution)[1:]
    ])
    fuse_z_c.extend(
        [-boom_diameter / 2] * (fuse_straight_resolution - 1)
    )
    fuse_radius.extend(
        [boom_diameter / 2] * (fuse_straight_resolution - 1)
    )

    fuse = asb.Fuselage(
        name="Fuselage",
        xsecs=[
            asb.FuselageXSec(
                xyz_c=[fuse_x_c[i], 0, fuse_z_c[i]],
                radius=fuse_radius[i]
            ) for i in range(len(fuse_x_c))
        ]
    )

    return fuse

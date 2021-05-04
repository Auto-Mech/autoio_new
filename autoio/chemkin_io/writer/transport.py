"""
 Writes the string for a Chemkin transport file
"""

from chemkin_io.writer import _util as util

# conversion factors
CM2K = 1.438776877
BOHR2ANG = 0.529177
BOHR2ANG_3 = BOHR2ANG**3


def properties(spc_trans_dct):
    """ Writes the string in containing data from several mechanism species
        used in calculating transport properties during Chemkin simulations.

        :param spc_trans_dct:
        :type spc_trans_dict: {spc_name:
            {'shape_idx': 0 for atomic, 1 for linear, 2 for non-linear,
             'epsilon': Lennard-Jones well depth epsilon/k_B (Kelvins),
             'sigma': Lennard-Jones collision diameter (angstroms),
             'dipole_moment': dipole moment (Debyes),
             'polarizability': polarizability (angstroms^3),
             'zrot': rotational relaxation collision number at 298 K
            }
        }
        :return: chemkin_str: Chemkin string with transport data
        :rtype: str
    """

    # Initialize string with common header
    chemkin_str = util.CKIN_TRANS_HEADER_STR
    chemkin_str += '\n'

    # Add the headers for each of the columns
    chemkin_str += (
        '{0:20s}'.format('! Species') +
        '{0:>5s}'.format('Shape') +
        '{0:>12s}'.format('Epsilon') +
        '{0:>8s}'.format('Sigma') +
        '{0:>8s}'.format('Mu') +
        '{0:>8s}'.format('Alpha') +
        '{0:>8s}'.format('Z_Rot')
    )
    chemkin_str += '\n'

    # Add the values to the string
    for name, dct in spc_trans_dct.items():
        shape_idx = dct.get('shape_idx', 2)
        eps = dct.get('epsilon', 0.00) * CM2K
        sig = dct.get('sigma', 0.00) * BOHR2ANG
        dmom = dct.get('dipole_moment', 0.00)
        polar = dct.get('polarizability', 0.00) * BOHR2ANG_3
        zrot = dct.get('zrot', 1.00)

        chemkin_str += (
            '{0:20s}'.format(name) +
            '{0:>5d}'.format(shape_idx) +
            '{0:>12.3f}'.format(eps) +
            '{0:>8.3f}'.format(sig) +
            '{0:>8.3f}'.format(dmom) +
            '{0:>8.3f}'.format(polar) +
            '{0:>8.3f}'.format(zrot)
        )
        chemkin_str += '\n'

    return chemkin_str

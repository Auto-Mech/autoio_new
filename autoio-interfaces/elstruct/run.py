""" core run function
"""

from autorun import from_input_string
import automol
import ase
from ase.units import Hartree

def direct(input_writer, script_str, run_dir, prog,
           geo, charge, mult, method, basis, **kwargs):
    """ Generates an input file for an electronic structure job and
        runs it directly.

        :param input_writer: elstruct writer module function for desired job
        :type input_writer: elstruct function
        :param script_str: string of bash script that contains
            execution instructions electronic structure job
        :type script_str: str
        :param run_dir: name of directory to run electronic structure job
        :type run_dir: str
        :param prog: electronic structure program to run
        :type prog: str
        :param geo: cartesian or z-matrix geometry
        :type geo: tuple
        :param charge: molecular charge
        :type charge: int
        :param mult: spin multiplicity
        :type mult: int
        :param method: electronic structure method
        :type method: str
        :returns: the input string, the output string, and the run directory
        :rtype: (str, str)
    """
    if prog.startswith('ase'):
        atoms = geom_to_atoms(geo)
        tokens = prog.split('_')
        if len(tokens) > 1:
            calculator = tokens[1]
        else:
            pass
        if calculator == 'psi4':
            from ase.calculators.psi4 import Psi4
            calc = Psi4()
            calc.parameters['basis'] = basis
            calc.parameters['method'] = method
            calc.parameters['multiplicity'] = mult
            atoms.calc = calc
            atoms.get_potential_energy()
            version_str = f'ase_{ase.__version__}-psi4_{calc.psi4.__version__}'
            calc.results['version'] = version_str
            calc.results['energy'] = calc.results['energy'] / Hartree
            input_str = str(calc.parameters)
            output_str = str(calc.results)
    else:
        input_str = input_writer(
            prog=prog,
            geo=geo, charge=charge, mult=mult, method=method, basis=basis,
            **kwargs)

        output_strs = from_input_string(script_str, run_dir, input_str)
        output_str = output_strs[0]

    return input_str, output_str


def geom_to_atoms(geo):
    from ase import Atoms
    if automol.zmat.is_valid(geo):
        geo = automol.zmat.geometry(geo)
    atoms = Atoms(symbols = automol.geom.symbols(geo), positions = automol.geom.coordinates(geo, angstrom=True) )
    return atoms


def atoms_to_geom(atoms):
    pass

from elstruct.reader._ase.status import has_normal_exit_message, check_convergence_messages
from ase.units import Hartree
import ase
from ase.calculators.psi4 import Psi4

def program_version(out_str):
    import ast
    results = ast.literal_eval(out_str)
    return results['version']

def energy(method, out_str):
    import ast
    results = ast.literal_eval(out_str)
    return results['energy'] / Hartree

__all__ = [

    'has_normal_exit_message',
    'check_convergence_messages',   
'program_version'
]

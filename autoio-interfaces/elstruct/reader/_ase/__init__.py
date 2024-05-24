from elstruct.reader._ase.status import has_normal_exit_message, check_convergence_messages

def program_version(out_str):
    import ast
    results = ast.literal_eval(out_str)
    return results['version']

def energy(method, out_str):
    import ast
    results = ast.literal_eval(out_str)
    return results['energy'] 

__all__ = [

    'has_normal_exit_message',
    'check_convergence_messages',   
'program_version'
]

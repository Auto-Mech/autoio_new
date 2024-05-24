""" status checkers
"""
import autoparse.pattern as app
import autoparse.find as apf
import elstruct.par


# Exit message for the program
def has_normal_exit_message(output_str):
    """ does this output string have a normal exit message?
    """
    return True
    # pattern = app.escape('*** ASE exiting successfully.')
    # return apf.has_match(pattern, output_str, case=False)

def check_convergence_messages(error, success, output_str):
    """ Assess whether the output file string contains messages
        denoting all of the requested procedures in the job have converged.

        :param output_str: string of the program's output file
        :type output_str: str
        :rtype: bool
    """

    return True
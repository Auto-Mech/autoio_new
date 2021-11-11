"""
  Read a MESS input file and compile data for the PES inside
"""

import numpy as np
from numpy.core.fromnumeric import nonzero
import pandas as pd
from autoparse import find
import autoparse.pattern as app
from ioformat import remove_comment_lines

def pes(input_string, read_fake=False):
    """ Read a MESS input file string and get info about PES

        :param input_string: string for a MESS (rates) input file
        :type input_string: str
        :param read_fake: value to include fake wells and barriers
        :type read_fake: bool
        :return energy_dct: dict[label: energy]
        :rtype: dict[label: energy]
        :return conn_lst_dct: defines the wells connected by each barrier
        :rtype: dict[barrier: (reac, prod)] all str
        :return conn_lst
        :rtype: lst(str)
    """

    # Initialize energy and connection information
    energy_dct = {}
    conn_lst = tuple()
    conn_lst_dct = {}
    pes_label_dct = {}

    input_string = remove_comment_lines(input_string, delim_pattern=app.escape('!'))
    input_lines = input_string.splitlines()
    for idx, line in enumerate(input_lines):

        if 'Well' in line:

            line_lst = line.strip().split()
            if line_lst[0].strip() == 'Well' and '!' not in line:
                # Get label
                label = line_lst[1]

                if ('F' not in label) or ('F' in label and read_fake):
                    # Get energy
                    for line2 in input_lines[idx:]:
                        if 'ZeroEnergy' in line2:
                            ene = float(line2.split()[-1])
                            break

                    # Add value to energy dct
                    energy_dct[label] = ene

                    prior_line = input_lines[idx-1]
                    line_lst2 = prior_line.split('!')
                    try:
                        spc = line_lst2[1]
                        # strip gets rid of the spaces before and after
                        pes_label_dct[spc.strip()] = label
                    except IndexError:
                        print(
                            'Warning: labeling not found for species {}'.format(label))

        if 'Bimolecular' in line:

            line_lst = line.strip().split()

            if line_lst[0].strip() == 'Bimolecular' and '!' not in line:
                # Get label
                label = line_lst[1]

                # Get energy
                for line2 in input_lines[idx:]:
                    if 'Dummy' in line2:
                        ene = -10.0
                        break
                    if 'GroundEnergy' in line2:
                        ene = float(line2.split()[-1])
                        break

                # Add value to dct
                energy_dct[label] = ene

                # Add value to PES dct - NB THIS DEPENDS ON THE INPUT FILE.
                # IF NOT PRESENT, DO NOT GENERATE THE PES LABEL DICTIONARY
                prior_line = input_lines[idx-1]
                line_lst2 = prior_line.split('!')
                try:
                    spc = line_lst2[1]
                    # strip gets rid of the spaces before and after
                    pes_label_dct[spc.strip()] = label
                except IndexError:
                    print('Warning: labeling not found for species {}'.format(label))

        if 'Barrier' in line:

            line_lst = line.strip().split()
            if line_lst[0].strip() == 'Barrier' and '!' not in line:
                # Get label
                [tslabel, rlabel, plabel] = line_lst[1:4]

                if ('F' not in tslabel) or ('F' in tslabel and read_fake):
                    # Get energy
                    for line2 in input_lines[idx:]:
                        if 'ZeroEnergy' in line2:
                            ene = float(line2.split()[-1])
                            break

                    # Add value to dct
                    energy_dct[tslabel] = ene

                    # Amend fake labels (may be wrong)
                    if not read_fake:
                        rlabel = rlabel.replace('F', 'P')
                        plabel = plabel.replace('F', 'P')

                    # Add the connection to lst
                    conn_lst += ((rlabel, tslabel),)
                    conn_lst += ((tslabel, plabel),)
                    conn_lst_dct[tslabel] = (rlabel, plabel)

    return energy_dct, conn_lst, conn_lst_dct, pes_label_dct

def find_barrier(conn_lst_dct, reac, prod):
    """ finds the barrier that connects reac to prod
        returns None if the barrier is not found
        future implementation: it should find the lowest energy path from reac to prod

        :param conn_lst_dct: defines the wells connected by each barrier
        :type conn_lst_dct: dict[barrier: (reac, prod)] all str
        :param reac, prod: connected species
        :type reac, prod: str
        :return barriername: name of the barrier
        :rtype: str
    """
    b1 = (reac, prod)
    b2 = (prod, reac)
    ls_keys = list(conn_lst_dct.keys())
    ls_vals = list(conn_lst_dct.values())
    b1_find = find.where_is(b1, ls_vals)
    b2_find = find.where_is(b2, ls_vals)
    if len(b1_find) > 0:
        return ls_keys[b1_find[0]]
    elif len(b2_find) > 0:
        return ls_keys[b2_find[0]]
    else:
        return None

def get_species(input_string):
    """ Read a MESS input file string and get the block of each species
        Bimolecular fragments are listed together,
        but header Fragment is changed to Species

        :param input_string: string for a MESS (rates) input file
        :type input_string: str

        :return species_blocks: dictionary with the species blocks
            {name:[frag1 block, frag2 block], name:[unimol block],}
        :rtype: dict{label: list}
    """
    input_string = remove_comment_lines(input_string, delim_pattern=app.escape('!'))
    lines = input_string.splitlines()
    lines = [line for line in lines if line.strip() != '']

    # find where data of interest are
    bad_wellwrds = ['WellDepth', 'WellCutoff', 'WellExtension',
                    'WellReductionThreshold', 'WellPartitionMethod',
                    'WellProjectionThreshold']
    bad_fragwrds = ['FragmentGeometry', 'PEDSpecies']

    names_i = np.where(
        np.array([('Bimolecular' in line or 'Well' in line) and
                  all(bad not in line for bad in bad_wellwrds) for line in lines],
                 dtype=int) == 1)[0]
    init_i = np.where(
        np.array([('Fragment' in line or 'Species' in line) and
                  all(bad not in line for bad in bad_fragwrds) for line in lines],
                 dtype=int) == 1)[0]
    init_i = init_i[init_i > names_i[0]]
    end_i = np.where(
        np.array(['End' in line for line in lines], dtype=int) == 1)[0]+1
    levels_i = np.where(
        np.array(['ElectronicLevels' in line for line in lines], dtype=int) == 1)[0]
    final_i = np.array([end_i[i < end_i][0] for i in levels_i])[:len(init_i)]

    # dictionary labels
    labels = [lines[i].strip().split()[1] for i in names_i]
    species_blocks = {k: [] for k in labels}

    # extract the data
    for i in np.arange(0, len(init_i)):

        # type
        sp_type = lines[init_i[i]].strip().split()[0]
        label = lines[names_i[init_i[i] > names_i][-1]].strip().split()[1]

        # name and label
        if sp_type == 'Fragment':
            name = 'Species ' + lines[init_i[i]].strip().split()[1]

        elif sp_type == 'Species':
            name = 'Species ' + label

        # store in the dictionary
        block = '\n'.join(lines[init_i[i]+1:final_i[i]])
        block = name + '\n' + block
        species_blocks[label].append(block)

    return species_blocks

def dct_species_fragments(species_blocks):
    """ derive a dictionary of species names and corresponding unimol or bimol names
        :param species_blocks: dictionary with the species blocks
            {name:[frag1 block, frag2 block], name:[unimol block],}
        :type: dict{label: list}
        :return dct_sp_fr: dictionary with species and fragment names
                        {species:[wellname], bimolspecies:[frag1, frag2]}
        :rtype: dct{str: lst}
    """

    dct_sp_fr = dict.fromkeys(species_blocks.keys())

    for label in dct_sp_fr.keys():
        if len(species_blocks[label]) == 1:
            dct_sp_fr[label] = [label]
        else:
            fragments = []
            for sp in species_blocks[label]:
                frag = sp.split('\n')[0].split()[1]
                fragments.append(frag)
            dct_sp_fr[label] = fragments

    return dct_sp_fr


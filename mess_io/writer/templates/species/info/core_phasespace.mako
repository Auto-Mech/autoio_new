  Stoichiometry  ${stoich}
  Core PhaseSpaceTheory
% for geo, natom in zip(geos, natoms):
    FragmentGeometry[angstrom]    ${natom}
${geo}
% endfor
    SymmetryFactor                  ${sym_factor}   
    PotentialPrefactor[au]          ${pot_prefactor}
    PotentialPowerExponent          ${pot_exp}
    TSTLevel ${tstlvl}
  End  ! Core

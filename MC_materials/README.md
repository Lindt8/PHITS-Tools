# Monte Carlo materials

[![Documentation](https://img.shields.io/badge/Documentation-brightgreen)](https://lindt8.github.io/PHITS-Tools/docs/manage_mc_materials.html)

The `manage_mc_materials.py` submodule of PHITS Tools can be used to create 
new materials database files and to add/edit materials in existing ones. 
See the [**`PHITS_tools.manage_mc_materials` submodule documentation**](https://lindt8.github.io/PHITS-Tools/docs/manage_mc_materials.html) 
for details on managing the materials database.

Within the main `PHITS Tools` Python module, the [`fetch_MC_material()`](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.fetch_MC_material) 
function can be used to access these material compositions within a Python script.

These files were assembled from a variety of sources over time;
they just seek to compile information for materials to be used in Monte Carlo 
particle transport calculations in an easily accessible plain-text format. 
The first 372 entries are from the Compendium of Material Composition Data for
Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the
Pacific Northwest National Laboratory.  That document can be found at:
https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf
The sources for other entries are specified.

The files named `"MC_materials_by_*_fraction_for_*.txt"` contain the full
collection of materials already formatted for use in the PHITS and MCNP
Monte Carlo particle transport codes, ready to be copy/pasted into an input file and used.
Choice between atom and weight fraction is up to the user, as one may be 
preferable to the other if one wishes to make any compositional modifications
to any of the materials.  The "for_photons" files contain materials 
specified by their elemental composition, assuming natural isotopic abundances.
The "for_neutrons" files instead substitute some of the natural element
specifications for the individual most naturally abundant isotopes for 
those elements and also manually specify isotopic distributions for 
specific materials.

The MC materials database consists of named "materials sets" (`SET_NAME` = `'Compiled_MC_materials'` and `'PNNL_materials_compendium'`
as the defaults included with PHITS Tools) each with the following files for each set:

- `SET_NAME.json` = This is the main database file containing all the information for each material and is what is used 
    by PHITS Tools and this submodule for extracting/adding/modifying materials database information.
- `SET_NAME.txt` = A human-readable plaintext file containing all the information in `SET_NAME.json`
- `SET_NAME_index.txt` = A text file listing all materials contained in the set, along with their ID numbers and data source
- `SET_NAME_by_*_for_*.txt` = Text files providing PHITS/MCNP-formatted materials cards for all materials in the set:
    - `SET_NAME_by_atom_fraction_for_neutrons.txt` = compositions by atom fraction with specific isotopes listed
    - `SET_NAME_by_atom_fraction_for_photons.txt` = compositions by atom fraction with only elements listed (natural abundances assumed)
    - `SET_NAME_by_weight_fraction_for_neutrons.txt` = compositions by weight fraction with specific isotopes listed
    - `SET_NAME_by_weight_fraction_for_photons.txt` = compositions by weight fraction with only elements listed (natural abundances assumed)
- `SET_NAME_general.txt` = A composite of the four `SET_NAME_by_*_for_*.txt` files where each material's entry is selected
    following a fairly simple set of rules outlined in the [`write_general_mc_file`](https://lindt8.github.io/PHITS-Tools/docs/manage_mc_materials.html#manage_mc_materials.write_general_mc_file) 
    function's documentation.




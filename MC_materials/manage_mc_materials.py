r'''

This submodule is used for managing the MC materials database found in the "MC_materials" directory, which is located 
in the same directory as PHITS_tools.py.  The MC materials database consists of a list of materials with the necessary
compositional information needed for particle transport simulations, and it uses the PNNL 
Compendium of Material Composition Data for Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, document as
its foundational source, on top of which additional materials can be added freely.

The MC materials database files created and managed by this module's functions are also those retrieved by the 
[`fetch_MC_material()`](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.fetch_MC_material) function in PHITS Tools.
Assuming you have installed PHITS Tools via `pip`, you may access the functions within this submodule in your 
Python scripts with `from PHITS_tools.manage_mc_materials import *` or `import PHITS_tools.manage_mc_materials as mcmats` 
(or "as" whatever alias you wish to give it in your programs); otherwise, you can just import this module as you would 
any other local module.

### **MC materials database structure**

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
    following a fairly simple set of rules outlined in the `write_general_mc_file` function's documentation.

### **Updating/creating MC materials databases**

The main function of this submodule is `update_materials_database_files`; while the other functions in this submodule 
can be used independently, most can be called automatically within `update_materials_database_files`. This function can 
be used to updated all of the files of an existing database or to create a new database based off of an existing one.
Executing `update_materials_database_files` with information with a new material to be added (or modified) will do the following:

1. (if `prefer_user_data_folder=True`) `setup_local_mc_materials_directory` is executed, doing the following:
    - Confirmation of existence of a local `MC_materials` directory; if not found:
    - Creation of local `MC_materials` directory:
        - In the same directory as `PHITS_tools.py` (or one directory higher) is a `MC_materials` directory. If it does 
            not exist already, a new local directory, outside the PHITS Tools installation, will be created at 
            [`pathlib.Path.home()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.home)` / '.PHITS-Tools' / 'MC_materials'`.
            - On Windows, this defaults to `C:\Users\USERNAME\.PHITS-Tools\MC_materials`
            - On MacOS and Linux, this defaults to `/home/USERNAME/.PHITS-Tools/MC_materials`
        - The contents of the original `MC_materials` directory are copied to this new local directory. 
    - This directory will be used as the data source for not only `update_materials_database_files` but also as the new 
        default data source for the [`fetch_MC_material()`](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.fetch_MC_material) function in PHITS Tools.
    - This local directory is created to allow creation and curation of user MC materials databases locally without fear
        of being overwritten/deleted when updating PHITS Tools to a new version via `pip install PHITS-Tools --upgrade`.
2. The JSON database file will be updated with the new/updated materials information provided to the function.
    - If `new_database_base_name` is not left as `None`, instead of updating the existing database, a new databased using 
        `new_database_base_name` as its "`SET_NAME`" is created from the existing database, applying the specified 
        materials addition/updates to it too.  This new database is then used for the remaining operations.
    - If `save_backup_list=True`, a timestamped copy of the updated/new JSON file is placed in the `MC_materials/backup_lists/` directory.
3. (if `update_MC_formated_files=True`) `write_descriptive_file()` is called, updating/creating `SET_NAME.txt` and `SET_NAME_index.txt`
4. (if `update_descriptive_file=True`) `write_mc_formated_files()` is called, updating/creating the four `SET_NAME_by_*_for_*.txt` files
5. (if `update_general_MC_file=True`) `write_general_mc_file()` is called, updating/creating `SET_NAME_general.txt`


### **Main function for updating MC materials database files**

- `update_materials_database_files` : add/modify materials entries, create new database files

### **Additional helper functions**

- `setup_local_mc_materials_directory` : on first run, creates copy of MC materials outside the PHITS Tools install
- `pnnl_lib_csv_to_dict_list`       : converts the PNNL materials_compendium.csv file to a list of dictionaries
- `materials_dict_list_to_json`     : save a list of dictionaries to a JSON file
- `materials_json_to_dict_list`     : read a JSON file into a list of dictionaries
- `write_descripive_material_entry` : write a plaintext material entry for a material's dictionary object
- `write_mc_material_entry`         : write a PHITS/MCNP-formatted text entry for a material's dictionary object
- `write_descriptive_file`          : write a file of plaintext material entries for all material dictionaries in a list
- `write_mc_formated_files`         : write 4 files of PHITS/MCNP-formatted materials for all material dictionaries in a list
- `write_general_mc_file`           : write a file of PHITS/MCNP-formatted materials (choosing "most sensible" of 4 for each)

### **Usage examples**



To create a new database from an existing one, one can use `update_materials_database_files` as follows, in this case 
showing how the `'Compiled_MC_materials'` materials set files were initially created from the `PNNL_materials_compendium.json` file 
with the addition of a material for the atmospheric composition on Mars.

```python
from PHITS_tools.manage_mc_materials import *

# Using the PNNL compendium as a base, create and add to the "Compiled_MC_materials" database
json_filepath = 'PNNL_materials_compendium'
name = 'Martian Atmosphere'
mat_str = '6000 -2.62E-01  8000 -7.00E-01 18000 -1.93E-02 7000 -1.89E-02'
update_materials_database_files(json_filepath,
                                name,
                                mat_str,
                                matid=None,
                                density='function of altitude and time',
                                source='Mahaffy 2013, DOI: 10.1126/science.1237966',
                                source_short='Mahaffy 2013',
                                formula=None,
                                molecular_weight=None,
                                total_atom_density=None,
                                new_database_base_name="Compiled_MC_materials",
                                update_descriptive_file=True,
                                update_MC_formated_files=True,
                                update_general_MC_file=True,
                                save_backup_list=True,
                                prefer_user_data_folder=True)
```

To just add a new material to an existing database, in this case adding Martian regolith to 
`Compiled_MC_materials.json` and its text files, one can use `update_materials_database_files` as follows:

```python
from PHITS_tools.manage_mc_materials import *

# Update the existing "Compiled_MC_materials" database
json_filepath = "Compiled_MC_materials"
name = 'Martian Regolith'
mat_str = '1000 0.151069196 11000 0.033300262 12000 0.016650131 13000 0.033300262 14000 0.156699215 18000 0.537611902 19000 0.033300262 20000 0.016650131 26000 0.021418638'
update_materials_database_files(json_filepath,
                                name,
                                mat_str,
                                matid=None,
                                density=1.7,
                                source='McKenna-Lawlor 2012, DOI: 10.1016/j.icarus.2011.04.004',
                                source_short='McKenna-Lawlor 2012',
                                formula=None,
                                molecular_weight=None,
                                total_atom_density=None,
                                new_database_base_name=None,
                                update_descriptive_file=True,
                                update_MC_formated_files=True,
                                update_general_MC_file=True,
                                save_backup_list=True,
                                prefer_user_data_folder=True)
```

And, finally, if you wish to recreate the JSON file and text files for the initial PNNL database `'PNNL_materials_compendium'`, 
which uses a [CSV file of the PNNL data from PYNE](https://github.com/pyne/pyne/blob/develop/pyne/dbgen/materials_compendium.csv)
as its initial source of data (as may be useful if another such PNNL database is published in the future), 
this can be done as follows: 

```python
from pathlib import Path
from PHITS_tools.manage_mc_materials import *

# Generate the JSON file and descriptive text file for the PNNL library
mat_list = pnnl_lib_csv_to_dict_list()
materials_dict_list_to_json(mat_list,json_filepath=Path(Path.cwd(),'PNNL_materials_compendium.json'))
header_text  = 'This file was assembled from the Compendium of Material Composition Data for' + '\n'
header_text += 'Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the' + '\n'
header_text += 'Pacific Northwest National Laboratory.' + '\n'
header_text += 'This file seeks to just compile the core information of the compendium in an' + '\n'
header_text += 'easily accessible plain-text format.  The full document can be found at: ' + '\n'
header_text += r'https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf' + '\n'
write_descriptive_file(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium.txt'),header_text=header_text)
write_mc_formated_files(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium.txt'),header_text=header_text)
write_general_mc_file(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium_general.txt'),header_text=header_text)
```


'''


import re
import os
import csv
import sys
import json
from pathlib import Path
#from PHITS_tools import Element_Z_to_Sym, Element_Sym_to_Z, fetch_MC_material, nuclide_plain_str_to_ZZZAAAM


def update_materials_database_files(json_filepath,name,mat_str,matid=None,density=None,source=None,
                                    source_short=None,formula=None,molecular_weight=None,total_atom_density=None,
                                    new_database_base_name=None,update_descriptive_file=True,
                                    update_MC_formated_files=True,update_general_MC_file=True,
                                    save_backup_list=True,prefer_user_data_folder=True):
    '''
    Description:
    
        Add or modify a material in a MC materials database JSON file (optionally updating text files too).

    Inputs:
        (required)
        
        - `json_filepath` = string or Path object denoting the path to the JSON materials file. If a string is provided 
                that does not end in `'.json'`, this function will search to see if a JSON file of the same basename exists
                in a directory called "MC_materials" located in
            - if `prefer_user_data_folder=True`: your local [`"$HOME`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.home)`/.PHITS-Tools/"` 
                    directory, creating it and copying the distributed MC_materials data to it if not yet existing via 
                    the `setup_local_mc_materials_directory` function.
            - if `prefer_user_data_folder=False`: the same directory as the PHITS_tools.py module (or one directory up), 
                    which requires either PHITS Tools to be installed via `pip` or locatable within your PYTHONPATH system variable).
                The JSON libraries that are shipped with PHITS Tools by default are titled `'Compiled_MC_materials'` 
                and `'PNNL_materials_compendium'`.
        - `name` = string of the name of the material to be added / updated.  See the "Notes" section further below for 
                more information on how entry identification is handled.
        - `mat_str` = string designating the composition of the material.  This should be provided as a series of 
                alternating nuclide IDs and concentrations. 
                Valid nuclide ID's include ZZZAAA values (1000*Z + A) or any format supported by [nuclide_plain_str_to_ZZZAAAM()](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.nuclide_plain_str_to_ZZZAAAM) (no spaces permitted).
                Concentrations can be provided as either mass fractions (negative) or atom fractions (positive).
                If they do not sum to unity, they will be automatically normalized such that they will.
                An example for water: `"1000 2 8000 1"` or `"H 2 O 1"` or `"1000 0.66666 8000 0.33333"`
        
    Inputs:
        (optional)
        
        - `matid` = (D=`None`) integer denoting material number in the materials database. If left as default `None`, 
                this function will nominally assume that a new material is being added to the database.
                If an integer is provided, the function will assume the intent is to overwrite an existing entry.
                See the "Notes" section further below for more information on how entry identification is handled.
        - `density` = (D=`None`) a float denoting the density of the material in g/cm3 (can be a string if variable)
        - `source` = (D=`None`) a string denoting the data source, e.g., `'PNNL'`, `'NIST'`, `'Mahaffy 2013, DOI: 10.1126/science.1237966'`, etc. [STRONGLY ENCOURAGED]
        - `source_short` = (D=`None`) a string denoting the data source in shorter/abbreviated form, e.g., `'Mahaffy 2013'`
        - `formula` = (D=`None`) a string denoting a material's chemical formula
        - `molecular_weight` = (D=`None`) a float denoting the molecular weight in g/mole
        - `total_atom_density` = (D=`None`) a float denoting the total atom density in atoms/(barn-cm)
        - `new_database_base_name` = (D=`None`) a string specifying the base database name to be used for all files written 
                by this function. If left as default `None`, the base name from `json_filepath` will be used.  Otherwise, 
                this can be used to create new database files, rather than rewriting existing ones.
        - `update_descriptive_file` = (D=`True`) Boolean denoting whether the descriptive file for the database, 
                as generated by `write_descriptive_file()`, should be updated/(re)written.
        - `update_MC_formated_files` = (D=`True`) Boolean denoting whether the four MCNP/PHITS-formatted files for the database, 
                as generated by `write_mc_formated_files()`, should be updated/(re)written.
        - `update_general_MC_file` = (D=`True`) Boolean denoting whether the updated descriptive file for the database, 
                as generated by `write_general_mc_file()`, should be updated/(re)written.
        - `save_backup_list` = (D=`True`) Boolean denoting whether an extra (timestamped) copy of the produced JSON 
                materials list database file should also be saved separately in a "backup_lists" directory located in 
                the same directory as `json_filepath`.
        - `prefer_user_data_folder` = (D=`True`) Boolean denoting whether this function should prioritize the local 
                MC materials databases in your local [`"$HOME`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.home)`/.PHITS-Tools/"` 
                directory over those in the PHITS Tools distribution. If the local user directory does not yet exist, 
                setting this to `True` will cause it to be created with a call of `setup_local_mc_materials_directory`.
                This local directory is created to allow creation and curation of user MC materials databases locally without fear
                of being overwritten/deleted when updating PHITS Tools to a new version via `pip install PHITS-Tools --upgrade`.

    Outputs:
    
        - `None`; the materials data from `json_filepath` will be updated with the provided new material (or written to 
                a new JSON database named with `new_database_base_name`), and derived text files are optionally updated 
                too as designated by `update_descriptive_file`, `update_MC_formated_files`, and `update_general_MC_file`.
    
    Notes:
        
        Entries in the database are uniquely identified by their `matid` or the combination of `name` and `source`.
        If provided with a `matid` or `name` and `source` combination already present within the database, a prompt
        window, as pictured below (in this case, with `matid` specified), will appear showing both the old and new versions 
        of the entry and asking for confirmation on whether the existing entry should be overwritten with the new one.
        
        ![](https://github.com/Lindt8/PHITS-Tools/blob/main/docs/update_MC_material_window.png?raw=true "Overwrite MC materials confirmation window")
        
    '''
    import datetime
    import tkinter
    from tkinter import messagebox
    from PHITS_tools import Element_Z_to_Sym, Element_Sym_to_Z, nuclide_plain_str_to_ZZZAAAM
    
    add_new_material = True
    rewrite_existing_material = False
    rewrite_matid = None  # material ID (=index + 1) to overwrite
    if matid is not None:
        rewrite_matid = matid
        rewrite_existing_material = True
        add_new_material = False
    
    # Ensure specified JSON database exists
    if prefer_user_data_folder and isinstance(json_filepath, str):
        json_filepath = setup_local_mc_materials_directory() / (json_filepath + '.json')
    elif isinstance(json_filepath, str) and (len(json_filepath) <= 5 or (len(json_filepath) > 5 and json_filepath.lower()[:-5] != '.json')):
        # basename is provided, need to find location of PHITS_tools.py and MC_materials/
        database_filename = json_filepath + '.json'
        import pkgutil
        lib_file = None
        try:
            try: # First, check MC_materials folder distributed with PHITS Tools
                phits_tools_module_path = pkgutil.get_loader("PHITS_tools").get_filename()
                mc_materials_dir_path = Path(Path(phits_tools_module_path).parent, 'MC_materials/')
                mc_materials_updir_path = Path(Path(phits_tools_module_path).parent, '..', 'MC_materials/')
                if mc_materials_dir_path.exists():
                    lib_file = Path(mc_materials_dir_path,database_filename)
                elif mc_materials_updir_path.exists():
                    lib_file = Path(mc_materials_updir_path, database_filename)
                else:
                    print('Could not find the "MC_materials/" directory via pkgutil.get_loader("PHITS_tools").')
                    raise FileNotFoundError(mc_materials_dir_path)
            except: # Failing that, check PYTHONPATH
                user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
                for i in user_paths:  # first try looking explicitly for MC_materials dir in PYTHONPATH
                    if 'MC_materials' in i:
                        lib_file = Path(i, database_filename)
                if lib_file is None:  # check for PHITS Tools in general
                    for i in user_paths:
                        if 'phits_tools' in i.lower() or 'phits-tools' in i.lower():
                            lib_file = Path(i, 'MC_materials', database_filename)
                if lib_file is None:
                    print('Could not find "PHITS-Tools", "PHITS_tools", nor "MC_materials" folders in PYTHONPATH; this folder contains the vital "MC_materials/" directory where the JSON libraries are stored.')
                    raise FileNotFoundError('$PYTHONPATH/PHITS-Tools/MC_materials/'+database_filename+
                                            ' nor '+'$PYTHONPATH/PHITS_tools/MC_materials/'+database_filename+
                                            ' nor '+'$PYTHONPATH/MC_materials/'+database_filename)
        except:
            print('Failed to locate "MC_materials/" directory.')
            print('ERROR: If PHITS Tools is not installed with pip, the PYTHONPATH environmental variable must be defined and contain the path to the directory holding "MC_materials/*.json" files')
            return None
        json_filepath = lib_file
    else:
        json_filepath = Path(json_filepath)
    if not json_filepath.exists():
        json_filepath_caps = json_filepath.parent / (json_filepath.stem + '.JSON')
        if json_filepath_caps.exists():
            json_filepath = json_filepath_caps
        else:
            print('Specified materials library could not be located at:', lib_file)
            raise FileNotFoundError(json_filepath)
            return None
    
    # load in the materials dictionary list
    all_mats_list = materials_json_to_dict_list(json_filepath=json_filepath)
    
    # If requested, use new name for database
    if new_database_base_name is not None:
        json_filepath = Path(json_filepath.parent, new_database_base_name + '.json')
    
    
    def Element_ZorSym_to_mass(Z):
        '''
        Description:
            Returns an element's average atomic mass provided its atomic number Z or elemental symbol
    
        Inputs:
            - `Z` = string of elemental symbol or atomic number Z
    
        Outputs:
            - `A_avg` = average atomic mass
        '''
        average_atomic_masses = [1.008664,1.007,4.002602,6.941,9.012182,10.811,12.0107,14.0067,15.9994,18.9984032,
                                 20.1797,22.98976928,24.305,26.9815386,28.0855,30.973762,32.065,35.453,39.948,39.0983,
                                 40.078,44.955912,47.867,50.9415,51.9961,54.938045,55.845,58.933195,58.6934,63.546,65.38,
                                 69.723,72.63,74.9216,78.96,79.904,83.798,85.4678,87.62,88.90585,91.224,92.90638,95.96,98,
                                 101.07,102.9055,106.42,107.8682,112.411,114.818,118.71,121.76,127.6,126.90447,131.293,
                                 132.9054519,137.327,138.90547,140.116,140.90765,144.242,145,150.36,151.964,157.25,
                                 158.92535,162.5,164.93032,167.259,168.93421,173.054,174.9668,178.49,180.94788,183.84,
                                 186.207,190.23,192.217,195.084,196.966569,200.59,204.3833,207.2,208.9804,209,210,222,
                                 223,226,227,232.03806,231.03588,238.02891,237,244,243,247,247,251,252,257,258,259,
                                 266,267,268,269,270,277,278,281,282,285,286,289,290,293,294,294]
        try:
            zi = int(Z)
        except:
            zi = Element_Sym_to_Z(Z)
        return average_atomic_masses[zi]
    
    
    if add_new_material:
        override_duplicate_name = True
        # First, check existing list to see if there are any conflicting materials
        duplicate_entry_found = False
        duplicate_entry_index = None
        if any([all_mats_list[i]['name'] == name for i in range(len(all_mats_list))]):
            print("Found this material name in the database already:")
            for i in range(len(all_mats_list)):
                if all_mats_list[i]['name'] == name:
                    print('\tentry number {} from source = {}'.format(str(i + 1), all_mats_list[i]['source']))
                    if all_mats_list[i]['source'] == source or all_mats_list[i]['source_short'] == source_short:
                        print('\tMultiple materials with identical names and sources not allowed!')
                        duplicate_entry_found = True
                        duplicate_entry_index = i
                        if not override_duplicate_name:
                            print('\tIf your intent is to overwrite that existing entry, please set "override_duplicate_name = True"')
                            sys.exit()
                        else:
                            print('\tOverwriting existing entry with new one, if "Yes" is selected.')
                    else:
                        if not override_duplicate_name:
                            print('\tNo sources conflict with this one, but stopping anyways.  Override this option by setting "override_duplicate_name = True"')
                            sys.exit()
                        else:
                            print('\tNo sources conflict with this one, so this entry will be written separately as a new entry.')
    if rewrite_existing_material:
        if rewrite_matid > len(all_mats_list):
            print('Invalid rewrite_matid {} entered; valid entries are integers from 1 to {}'.format(str(rewrite_matid), str(len(all_mats_list))))
            sys.exit()

    new_mat = {}
    new_mat.update({'name': name})
    new_mat.update({'density': density})
    if source:
        new_mat.update({'source': source})
    if source_short:
        new_mat.update({'source_short': source})
    else:
        new_mat.update({'source': '-'})
    if formula:
        new_mat.update({'formula': formula})
    else:
        new_mat.update({'formula': '-'})
    if molecular_weight:
        new_mat.update({'molecular weight': molecular_weight})
    else:
        new_mat.update({'molecular weight': '-'})
    if total_atom_density:  # else part taken care of later since this is calculated from normal density
        new_mat.update({'total atom density': total_atom_density})

    # process mat_str
    mat_elements = mat_str.split()
    ZZZAAA_ids = []
    concentrations = []
    for i in range(len(mat_elements)):
        mel = mat_elements[i]
        if i % 2 == 0:  # ZA part
            try:
                ZZZAAA = int(mel)
            except:
                # contains characters, must be converted
                if mel.isalpha():  # only element symbol is listed
                    Z = Element_Sym_to_Z(mel)
                    ZZZAAA = 1000 * Z
                else:
                    ZZZAAA = int(nuclide_plain_str_to_ZZZAAAM(mel) / 10)
            ZZZAAA_ids.append(ZZZAAA)
        else:  # concentration part
            concentrations.append(float(mel))

    # reorder to be in order of increasing ZZZAAA
    z1 = [x for x, _ in sorted(zip(ZZZAAA_ids, concentrations))]
    z2 = [x for _, x in sorted(zip(ZZZAAA_ids, concentrations))]
    ZZZAAA_ids = z1
    concentrations = z2

    avg_masses = []
    # normalize concentrations
    con_sum = sum(concentrations)
    for i in range(len(concentrations)):
        concentrations[i] = concentrations[i] / abs(con_sum)

    if con_sum < 0:
        provided_mass_fracs = True
        mass_fracs = concentrations
        # must calculate atom fractions
        atom_fracs = []
        for i in range(len(mass_fracs)):
            A = int(str(ZZZAAA_ids[i])[-3:])
            if A == 0:
                A = Element_ZorSym_to_mass(int(str(ZZZAAA_ids[i])[:-3]))
            atom_fracs.append(mass_fracs[i] / A)
            avg_masses.append(A)
        sum_fracs = sum(atom_fracs)
        # now renormalize
        for i in range(len(mass_fracs)):
            atom_fracs[i] = atom_fracs[i] / sum_fracs

    else:
        provided_mass_fracs = False  # atom fracs instead
        atom_fracs = concentrations
        # must calculate atom fractions
        mass_fracs = []
        for i in range(len(atom_fracs)):
            A = int(str(ZZZAAA_ids[i])[-3:])
            if A == 0:
                A = Element_ZorSym_to_mass(int(str(ZZZAAA_ids[i])[:-3]))
            mass_fracs.append(atom_fracs[i] * A)
            avg_masses.append(A)
        sum_fracs = sum(mass_fracs)
        # now renormalize
        for i in range(len(atom_fracs)):
            mass_fracs[i] = -1 * mass_fracs[i] / sum_fracs

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    # calculate atom densities if provided numerical density
    atom_densities = []
    if density and isfloat(density):
        # calculate mass of 1 unit of the material
        Av = 6.02214076e23
        tot_atom_density = 0.0  # g/molecule
        for i in range(len(mass_fracs)):
            atom_densities.append(float(density) * Av * abs(mass_fracs[i]) / (avg_masses[i] * (1e24)))  # in atoms/b-cm
            tot_atom_density += abs(atom_densities[-1])
    else:
        for i in range(len(mass_fracs)):
            atom_densities.append(0.0)

    # generate summary information which is by element
    Z_list = []
    sym_list = []
    summary_mf = []
    summary_af = []
    summary_ad = []
    photon_ZZZAAA_ids = []
    elm_ZA_list = []
    for i in range(len(ZZZAAA_ids)):
        Z = int(str(ZZZAAA_ids[i])[:-3])
        photon_ZZZAAA_ids.append(1000 * Z)
        if Z not in Z_list:
            Z_list.append(Z)
            elm_ZA_list.append(1000 * Z)
            sym_list.append(Element_Z_to_Sym(Z))
            summary_mf.append(mass_fracs[i])
            summary_af.append(atom_fracs[i])
            summary_ad.append(atom_densities[i])
        else:
            zi = Z_list.index(Z)
            summary_mf[zi] += mass_fracs[i]
            summary_af[zi] += atom_fracs[i]
            summary_ad[zi] += atom_densities[i]

    # compile into dictionary
    new_mat.update({'summary': {'element': sym_list, 'neutron ZA': elm_ZA_list, 'photon ZA': elm_ZA_list,
                                'weight fraction': summary_mf, 'atom fraction': summary_af,
                                'atom density': summary_ad}})
    if not total_atom_density:
        if density and isfloat(density):
            new_mat.update({'total atom density': tot_atom_density})
        else:
            new_mat.update({'total atom density': '-'})

    pars = ['neutrons', 'photons']
    par_ZAs = [ZZZAAA_ids, photon_ZZZAAA_ids]
    for pi in range(len(pars)):
        par = pars[pi]
        ZA_list = par_ZAs[pi]
        new_mat.update({par: {'weight fraction': {'ZA': ZA_list, 'value': mass_fracs},
                              'atom fraction': {'ZA': ZA_list, 'value': atom_fracs},
                              'atom density': {'ZA': ZA_list, 'value': atom_densities}}})

    # With GUI, ask user to confirm overwriting of existing material
    if rewrite_existing_material or (add_new_material and duplicate_entry_found and override_duplicate_name):
        if rewrite_existing_material:
            this_matid = rewrite_matid
        else:
            this_matid = duplicate_entry_index+1
        existing_mat_str = write_descripive_material_entry(all_mats_list[this_matid - 1], this_matid)
        new_mat_str = write_descripive_material_entry(new_mat, this_matid)
        r = tkinter.Tk()
        r.title("Overwrite existing entry in "+str(json_filepath)+" ?")
        l1 = tkinter.Label(r, text="Would you like to overwrite the old entry (left) with the new entry (right)?")
        l1.grid(row=0, column=0, sticky=tkinter.W, padx=10, pady=10)

        def clickButton1():
            global yn_response
            yn_response = True
            r.destroy()
            return yn_response

        def clickButton2():
            global yn_response
            yn_response = False
            r.destroy()
            return yn_response

        f1 = tkinter.Frame(r)
        # button widget 
        b1 = tkinter.Button(f1, text="Yes", command=clickButton1)
        b2 = tkinter.Button(f1, text="No", command=clickButton2)

        # arranging button widgets 
        f1.grid(row=0, column=1, padx=10, pady=10, sticky=tkinter.W)
        b1.pack(side="left", padx=10)
        b2.pack(side="right", padx=10)

        # Text of old and new entries
        old_entry = tkinter.Label(r, text=existing_mat_str)
        new_entry = tkinter.Label(r, text=new_mat_str)  # , justify='left'

        old_entry.grid(row=1, column=0, sticky=tkinter.W + tkinter.N, padx=10, pady=10)
        new_entry.grid(row=1, column=1, sticky=tkinter.W + tkinter.N, padx=10, pady=10)

        # b1.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = tkinter.E) 
        # b2.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tkinter.W) 

        # infinite loop which can be terminated  
        # by keyboard or mouse interrupt 

        tkinter.mainloop()

        # r.option_add('*Dialog.msg.font', 'Courier New 16')
        # response = messagebox.askyesno(r,"Python - material overwrite","Would you like to overwrite the following entry:\n"+'\nwith the new one below?\n')
        if not yn_response:
            sys.exit()

    if add_new_material:
        # add the new material to the library list
        if duplicate_entry_found:
            if override_duplicate_name:
                all_mats_list[duplicate_entry_index] = new_mat
        else:
            all_mats_list.append(new_mat)
    elif rewrite_existing_material:
        all_mats_list[rewrite_matid - 1] = new_mat

    # Save new materials list
    materials_dict_list_to_json(all_mats_list, json_filepath=json_filepath)
    
    # Update text files
    if update_descriptive_file:
        lib_filepath = Path(json_filepath.parent, json_filepath.stem + '.txt')
        write_descriptive_file(all_mats_list, lib_filepath=lib_filepath)
    if update_MC_formated_files:
        lib_filepath = Path(json_filepath.parent, json_filepath.stem + '.txt')
        write_mc_formated_files(all_mats_list, lib_filepath=lib_filepath)
    if update_general_MC_file:
        lib_filepath = Path(json_filepath.parent, json_filepath.stem + '_general.txt')
        write_general_mc_file(all_mats_list, lib_filepath=lib_filepath)

    if save_backup_list:
        def time_stamped(fname, fmt='{fname}_%Y-%m-%d-%H%M'):
            '''
            requires import datetime
            '''
            return datetime.datetime.now().strftime(fmt).format(fname=fname)
        backup_lib_filename = Path(json_filepath.parent, 'backup_lists/', time_stamped(json_filepath.stem) + '.json')
        backup_lib_filename.parent.mkdir(parents=True, exist_ok=True) # create backup_lists directory if it doesn't already exist
        materials_dict_list_to_json(all_mats_list, json_filepath=backup_lib_filename)
        
    return None




def setup_local_mc_materials_directory(phits_tools_module_path=None):
    r'''
    Description:
        This function copies the "MC_materials" directory distributed with PHITS Tools to a different local directory 
        (outside of the "PHITS-Tools" directory created when installing PHITS Tools via `pip`); specifically, 
         it does the following:
         
        - Confirmation of existence of a local `MC_materials` directory; if not found:
        - Creation of local `MC_materials` directory:
            - In the same directory as `PHITS_tools.py` (or one directory up) is a `MC_materials/` directory. If it does
                not exist already, a new local directory, outside the PHITS Tools installation, will be created at 
                [`pathlib.Path.home()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.home)` / '.PHITS-Tools' / 'MC_materials'`.
                - On Windows, this defaults to `C:\Users\USERNAME\.PHITS-Tools\MC_materials`
                - On MacOS and Linux, this defaults to `/home/USERNAME/.PHITS-Tools/MC_materials`
            - The contents of the original [distributed `MC_materials` directory](https://github.com/Lindt8/PHITS-Tools/tree/main/MC_materials) 
                are copied to this new local directory. 
        - This directory will be used as the data source for not only `update_materials_database_files` but also as the new 
            default data source for the [`fetch_MC_material()`](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.fetch_MC_material) function in PHITS Tools.
        - This local directory is created to allow creation and curation of user MC materials databases locally without fear
            of being overwritten/deleted when updating PHITS Tools to a new version via `pip install PHITS-Tools --upgrade`.

    Inputs:
        - `phits_tools_module_path` = string or Path object denoting the path to the `PHITS_tools.py` Python module file.
            If this is left as `None`, an attempt will be made to find it automatically via [`pkgutil.get_loader`](https://docs.python.org/3/library/pkgutil.html#pkgutil.get_loader)`("PHITS_tools").get_filename()`.

    Outputs:
        - `user_data_dir` = Path object pointing to the found existing or newly created local `MC_materials` directory
    '''
    user_data_dir = Path.home() / '.PHITS-Tools' / 'MC_materials/'
    if not user_data_dir.exists():
        import pkgutil
        import shutil
        # First check to see if MC_materials distributed directory exists (this script should be sitting in it...)
        if phits_tools_module_path is None:
            phits_tools_module_path = pkgutil.get_loader("PHITS_tools").get_filename()
        mc_materials_dist_path = Path(Path(phits_tools_module_path).parent, 'MC_materials/')
        if not mc_materials_dist_path.exists():
            mc_materials_dist_path = Path(Path(phits_tools_module_path).parent, '..', 'MC_materials/')
        if mc_materials_dist_path.exists():
            # Need to create initial local user data directory
            #user_data_dir.mkdir(parents=True, exist_ok=True)
            # and then copy contents of the distributed MC_materials directory into it
            shutil.copytree(mc_materials_dist_path, user_data_dir, ignore=shutil.ignore_patterns('__*__'))
            print('Copied contents of', mc_materials_dist_path, 'to new local directory', user_data_dir)
            
            # With only JSON files distributed, go ahead and create the text files for the local database
            print('Creating local .txt versions of default MC materials databases...')
            # PNNL base library
            #mat_list = pnnl_lib_csv_to_dict_list(path_to_materials_compendium_csv=mc_materials_dist_path/'materials_compendium.csv')
            #materials_dict_list_to_json(mat_list, json_filepath=mc_materials_dist_path/'PNNL_materials_compendium.json')
            mat_list = materials_json_to_dict_list(json_filepath=user_data_dir/'PNNL_materials_compendium.json')
            header_text = 'This file was assembled from the Compendium of Material Composition Data for' + '\n'
            header_text += 'Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the' + '\n'
            header_text += 'Pacific Northwest National Laboratory.' + '\n'
            header_text += 'This file seeks to just compile the core information of the compendium in an' + '\n'
            header_text += 'easily accessible plain-text format.  The full document can be found at: ' + '\n'
            header_text += r'https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf' + '\n'
            if not (user_data_dir/'PNNL_materials_compendium.txt').exists():
                write_descriptive_file(mat_list, lib_filepath=user_data_dir/'PNNL_materials_compendium.txt', header_text=header_text)
            if not (user_data_dir / 'PNNL_materials_compendium_by_atom_fraction_for_neutrons.txt').exists():
                write_mc_formated_files(mat_list, lib_filepath=user_data_dir/'PNNL_materials_compendium.txt', header_text=header_text)
            if not (user_data_dir / 'PNNL_materials_compendium_general.txt').exists():
                write_general_mc_file(mat_list, lib_filepath=user_data_dir/'PNNL_materials_compendium_general.txt', header_text=header_text)
            # User-customized library
            mat_list = materials_json_to_dict_list(json_filepath=user_data_dir/'Compiled_MC_materials.json')
            if not (user_data_dir/'Compiled_MC_materials.txt').exists():
                write_descriptive_file(mat_list, lib_filepath=user_data_dir/'Compiled_MC_materials.txt')
            if not (user_data_dir / 'Compiled_MC_materials_by_atom_fraction_for_neutrons.txt').exists():
                write_mc_formated_files(mat_list, lib_filepath=user_data_dir/'Compiled_MC_materials.txt')
            if not (user_data_dir / 'Compiled_MC_materials_general.txt').exists():
                write_general_mc_file(mat_list, lib_filepath=user_data_dir/'Compiled_MC_materials_general.txt')
    return user_data_dir


def pnnl_lib_csv_to_dict_list(path_to_materials_compendium_csv=(Path.cwd()/'materials_compendium.csv')):
    '''
    Description:
        This function converts a CSV file of the PNNL
        Compendium of Material Composition Data for Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, 
        to a Python dictionary object.
        The PNNL library's CSV file was obtained from PYNE:
        https://github.com/pyne/pyne/blob/develop/pyne/dbgen/materials_compendium.csv

    Inputs:
        - `path_to_materials_compendium_csv` = string or Path object denoting the path to the "materials_compendium.csv" file

    Outputs:
        - `mat_list` = a list of dictionary objects of the extracted materials information
    '''

    def is_line_not_empty(line):
        if any([i != '' for i in line]):
            return True
        return False

    f = open(path_to_materials_compendium_csv, 'r', newline='', encoding="utf-8")
    csv_reader = csv.reader(f, delimiter=',', quotechar='"')
    lines = list(filter(is_line_not_empty, csv_reader))
    f.close()

    # isolate just the lines we care about
    mat_dict_list = []
    matno = 1
    in_core_lines = False
    in_element_section = False
    in_mcnp_neutrons = False
    in_mcnp_photons = False

    for line in lines:
        nostr = (str(matno) + '.')
        if nostr in line[0][:len(nostr)]:
            mat = {}
            mat.update({'PNNL_number': int(line[0].replace('.', ''))})
            mat.update({'name': line[1]})
            mat.update({'source': 'PNNL-15870 Rev. 1'})
            mat.update({'source_short': 'PNNL'})
            matno += 1
            in_core_lines = True
        elif line[0] == 'Formula =':
            mat.update({'formula': line[1]})
            mat.update({'molecular weight': line[6]})
        elif line[0] == 'Density (g/cm3) =':
            mat.update({'density': line[2]})
            mat.update({'total atom density': line[6]})

        elif line[0] == 'Element':
            in_element_section = True
            mat.update({'summary': {'element': [], 'neutron ZA': [], 'photon ZA': [], 'weight fraction': [],
                                    'atom fraction': [], 'atom density': []}})
            continue
        elif in_element_section:
            if line[0] == 'Total':
                in_element_section = False

        elif line[0] == 'MCNP Form':
            in_mcnp_section = True

        elif line[0] == 'Neutrons' and in_mcnp_section:
            in_mcnp_neutrons = True
            mat.update({'neutrons': {'weight fraction': {'ZA': [], 'value': []},
                                     'atom fraction': {'ZA': [], 'value': []},
                                     'atom density': {'ZA': [], 'value': []}}})

        if in_element_section:
            mat['summary']['element'].append(line[0])
            mat['summary']['neutron ZA'].append(line[1])
            mat['summary']['photon ZA'].append(line[2])
            mat['summary']['weight fraction'].append(line[3])
            mat['summary']['atom fraction'].append(line[4])
            mat['summary']['atom density'].append(line[5])

        if in_mcnp_neutrons:
            if line[0] == 'Photons':
                in_mcnp_neutrons = False
                in_mcnp_photons = True
                mat.update({'photons': {'weight fraction': {'ZA': [], 'value': []},
                                        'atom fraction': {'ZA': [], 'value': []},
                                        'atom density': {'ZA': [], 'value': []}}})
            else:
                mat['neutrons']['weight fraction']['ZA'].append(line[1])
                mat['neutrons']['weight fraction']['value'].append(line[2])
                mat['neutrons']['atom fraction']['ZA'].append(line[3])
                mat['neutrons']['atom fraction']['value'].append(line[4])
                mat['neutrons']['atom density']['ZA'].append(line[5])
                mat['neutrons']['atom density']['value'].append(line[6])

        if in_mcnp_photons:
            if line[0] == 'CEPXS Form:':
                in_mcnp_photons = False
                in_mcnp_section = False
                # wrap up entry
                mat_dict_list.append(mat)
            else:
                mat['photons']['weight fraction']['ZA'].append(line[1])
                mat['photons']['weight fraction']['value'].append(line[2])
                mat['photons']['atom fraction']['ZA'].append(line[3])
                mat['photons']['atom fraction']['value'].append(line[4])
                mat['photons']['atom density']['ZA'].append(line[5])
                mat['photons']['atom density']['value'].append(line[6])
    
    return mat_dict_list

def materials_dict_list_to_json(mat_list,json_filepath=(Path.cwd()/'materials_compendium.json')):
    '''
    Description:
        This function converts the materials list of dictionaries into a JSON file.
    
    Inputs:
        - `mat_dict_list` = a list of dictionary objects of the extracted materials information
        - `json_filepath` = string or Path object denoting the path to the JSON materials file to be written

    Outputs:
        - `None`; the materials data will be saved to `json_filepath`.
    '''
    with open(json_filepath, 'w') as f:
        json.dump(mat_list, f)
    print('Materials library file written:', json_filepath)
    return None

def materials_json_to_dict_list(json_filepath=(Path.cwd()/'materials_compendium.json')):
    '''
    Description:
        This function converts the materials list of dictionaries into a JSON file.
    
    Inputs:
        - `json_filepath` = string or Path object denoting the path to the JSON materials file

    Outputs:
        - `mat_list` = a list of dictionary objects of the extracted materials information
    '''
    with open(json_filepath, "r") as f:
        mat_list = json.load(f)
    return mat_list


def write_descripive_material_entry(mat,mati):
    '''
    Description:
        Generate a descriptive text block for a material dictionary object.

    Inputs:
        - `mat` = a dictionary object formatted like all entries in the library
        - `mati` = integer specifying material number within the database

    Outputs:
        - `entry_text` = a string of formatted text with all information about the material
    '''
    banner_width = 80

    if 'PNNL_number' in mat:  # entries are strings already
        summary_table_format_string = '  {:9} {:12} {:12} {:13} {:13} {:13} \n'
        mcnp_table_format_string = '     {:7} {:13} {:7} {:13} {:7} {:13} \n'
    else:  # entries are ints/floats
        summary_table_format_string = '  {:9} {:<12d} {:<12d} {:<13.6f} {:<13.6f} {:<13.6f} \n'
        mcnp_table_format_string = '     {:<7d} {:<13.6f} {:<7d} {:<13.6f} {:<7d} {:<13.6f} \n'

    entry_text = '\n' + '*' * banner_width + '\n'
    entry_text += '  {:<3d} : {} \n'.format(mati, mat['name'])
    entry_text += '  Source = {} \n'.format(mat['source'])
    entry_text += '  Formula = {} \n'.format(mat['formula'])
    entry_text += '  Molecular weight (g/mole) = {} \n'.format(mat['molecular weight'])
    entry_text += '  Density (g/cm3) = {} \n'.format(mat['density'])
    if isinstance(mat['total atom density'], str):
        entry_text += '  Total atom density (atoms/b-cm) = {} \n'.format(mat['total atom density'])
    else:
        entry_text += '  Total atom density (atoms/b-cm) = {:<13.4E} \n'.format(mat['total atom density'])
    entry_text += '-' * banner_width + '\n'
    entry_text += '  Elemental composition \n'
    entry_text += '  {:9} {:12} {:12} {:13} {:13} {:13} \n'.format("Element", "Neutron ZA", "Photon ZA", "Weight frac.",
                                                                   "Atom frac.", "Atom density")
    for j in range(len(mat['summary']['element'])):
        entry_text += summary_table_format_string.format(mat['summary']['element'][j], mat['summary']['neutron ZA'][j],
                                                         mat['summary']['photon ZA'][j],
                                                         mat['summary']['weight fraction'][j],
                                                         mat['summary']['atom fraction'][j],
                                                         mat['summary']['atom density'][j])
    pars = ['neutrons', 'photons']
    for pi in range(len(pars)):
        par = pars[pi]
        entry_text += '-' * banner_width + '\n'
        entry_text += '  PHITS/MCNP formatted ({}) \n'.format(par)
        entry_text += '     {:^17}     {:^17}     {:^17} \n'.format("Weight Fractions", "Atom Fractions",
                                                                    "Atom Densities")
        for j in range(len(mat[par]['weight fraction']['ZA'])):
            entry_text += mcnp_table_format_string.format(mat[par]['weight fraction']['ZA'][j],
                                                          mat[par]['weight fraction']['value'][j],
                                                          mat[par]['atom fraction']['ZA'][j],
                                                          mat[par]['atom fraction']['value'][j],
                                                          mat[par]['atom density']['ZA'][j],
                                                          mat[par]['atom density']['value'][j])
    entry_text += '*' * banner_width + '\n'
    return entry_text

def write_mc_material_entry(mat,mati,particle_format='neutrons',concentration_format='weight fraction',comment_char='$'):
    '''
    Description:
        Generate a MCNP/PHITS-formatted text block for a material dictionary object.

    Inputs:
        - `mat` = a dictionary object formatted like all entries in the library
        - `mati` = integer specifying material number within the database
        - `particle_format` = (D=`'neutrons'`) string denoting how material compositions are formatted; select `'neutrons'`
             for full isotopic composition or `'photons'` for just elemental compositions (natural abundances)
        - `concentration_format` = (D=`'weight fraction'`) string denoting how material concentrations are formatted; 
             select either `'weight fraction'` or `'atom fraction'`.
        - `comment_char` = (D=`'$'`) string denoting the comment character to use (Note: `'$'` works for both PHITS and MCNP.)

    Outputs:
        - `entry_text` = a string of MCNP/PHITS-formatted text with material composition information
    '''
    from PHITS_tools import Element_Z_to_Sym
    concentration_formats = ['atom fraction', 'weight fraction']
    particle_formats = ['neutrons', 'photons']
    par = particle_format
    conctype = concentration_format
    if conctype not in concentration_formats:
        raise ValueError("Invalid concentration format. Expected `conctype` to be one of: %s" % concentration_formats)
    if par not in particle_formats:
        raise ValueError("Invalid particle format. Expected `par` to be one of: %s" % particle_formats)
    cc = comment_char
    #mati = i + 1  # counting number for material
    banner_width = 60

    entry_text = '\n' + cc + '*' * banner_width + '\n'
    entry_text += cc + '  {:<3d} : {} \n'.format(mati, mat['name'])
    if mat['source'] and mat['source'] != '-':
        entry_text += cc + '  Source = {} \n'.format(mat['source'])
    if mat['formula'] and mat['formula'] != '-':
        entry_text += cc + '  Formula = {} \n'.format(mat['formula'])
    if mat['molecular weight'] and mat['molecular weight'] != '-':
        entry_text += cc + '  Molecular weight (g/mole) = {} \n'.format(mat['molecular weight'])
    if mat['density'] and mat['density'] != '-':
        entry_text += cc + '  Density (g/cm3) = {} \n'.format(mat['density'])
    if mat['total atom density'] and mat['total atom density'] != '-':
        if isinstance(mat['total atom density'], str):
            entry_text += cc + '  Total atom density (atoms/b-cm) = {} \n'.format(mat['total atom density'])
        else:
            entry_text += cc + '  Total atom density (atoms/b-cm) = {:<13.4E} \n'.format(mat['total atom density'])
    entry_text += cc + '  Composition by {} \n'.format(conctype)

    for j in range(len(mat[par][conctype]['ZA'])):

        if isinstance(mat[par][conctype]['value'][j], str):
            entry_format = '{:4}    {:>7}  {:13}   ' + cc + '  {}' + '\n'
        else:
            entry_format = '{:4}    {:>7d}  {:<13.6f}   ' + cc + '  {}' + '\n'

        if j == 0:
            mstr = 'M{:<3}'.format(mati)
        else:
            mstr = ' ' * 4

        ZZZAAA = mat[par][conctype]['ZA'][j]
        if ZZZAAA == '-':
            ZZZAAA = mat['photons'][conctype]['ZA'][j]

        Z = int(str(ZZZAAA)[:-3])
        A = str(ZZZAAA)[-3:]
        sym = Element_Z_to_Sym(Z)
        if A != '000':
            isotope = sym + '-' + A.lstrip('0')
        else:
            isotope = sym

        entry_text += entry_format.format(mstr, ZZZAAA, mat[par][conctype]['value'][j], isotope)

    entry_text += cc + '*' * banner_width + '\n'
    return entry_text


def write_descriptive_file(mat_list,lib_filepath=Path(Path.cwd(),'MC_materials.txt'),header_text='',write_index_file=True):
    '''
    Description:
        Generates a text file of descriptive text blocks for a list of material dictionary objects.

    Inputs:
        - `mat_list` = a list of dictionary objects of the extracted materials information
        - `lib_filepath` = string or Path object denoting the path to the materials library text file to be saved
        - `header_text` = a string of text appearing at the very top of the output text file
             If left blank (`''`), a default header string as defined at the start of this function will be used.
        - `write_index_file` = (D=`True`) Boolean specifying if an index file, just listing the materials contained 
             in the outputted file along with their ID number and data source (tab delimited), should also be written. 
             If `True`, this file will have the same filepath as `lib_filepath` but with `'_index'` appended to its basename. 
    
    Outputs:
        - `None`; the materials text data will be saved to `lib_filepath`.
    '''
    lib_text = ''
    if header_text=='':
        header_text = '  ' + 'This file was assembled from a variety of sources over time;' + '\n'
        header_text += '  ' + 'it just seeks to compile information for materials to be used in Monte Carlo ' + '\n'
        header_text += '  ' + 'particle transport calculations in an easily accessible plain-text format. ' + '\n'
        header_text += '  ' + 'The first 372 entries are from the Compendium of Material Composition Data for' + '\n'
        header_text += '  ' + 'Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the' + '\n'
        header_text += '  ' + 'Pacific Northwest National Laboratory.  That document can be found at:' + '\n'
        header_text += '  ' + r'https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf' + '\n'
        header_text += '  ' + 'The sources for other entries are specified.' + '\n'
    lib_text += header_text
    for i in range(len(mat_list)):
        mat = mat_list[i]
        mati = i + 1
        entry_text = write_descripive_material_entry(mat, mati)
        lib_text += entry_text
    
    # save file
    f = open(lib_filepath, 'w+')
    f.write(lib_text)
    f.close()
    print('Materials library file written:', lib_filepath)

    # Make an index
    if write_index_file:
        index_text = 'ID\tName\tSource\n'
        for i in range(len(mat_list)):
            mat = mat_list[i]
            index_text += '{}\t{}\t{}\n'.format(str(i + 1), mat['name'], mat['source'])
        lib_filepath = Path(lib_filepath)
        fpath = Path(lib_filepath.parent, lib_filepath.stem + '_index' + lib_filepath.suffix)
        f = open(fpath, 'w+')
        f.write(index_text)
        f.close()
    return None

def write_mc_formated_files(mat_list, lib_filepath=(Path.cwd()/'MC_materials.txt'), comment_char='$', header_text=''):
    '''
    Description:
        Generates four text files of MCNP/PHITS-formatted materials section text blocks for a list of material dictionary objects.
        The four files cover every combination of concentration formats `['atom fraction', 'weight fraction']` and 
        particle formats `['neutrons', 'photons']`.

    Inputs:
        - `mat_list` = a list of dictionary objects of the extracted materials information
        - `lib_filepath` = string or Path object denoting the basic path to the materials library text files to be saved
        - `comment_char` = (D=`'$'`) string denoting the comment character to use (Note: `'$'` works for both PHITS and MCNP.)
        - `header_text` = a string of text appearing at the very top of the output text files. 
            If left blank (`''`), a default header string as defined at the start of this function will be used.
        
    Outputs:
        - `None`; the materials text data will be saved to four files at `lib_filepath` with 
            `_by_[atom/weight]_fraction_for_[neutrons/photons]` appended to the end of the filename.
    '''
    cc = comment_char 
    if header_text=='':
        header_text = cc + '  ' + 'This file was assembled from a variety of sources over time;' + '\n'
        header_text += cc + '  ' + 'it just seeks to compile information for materials to be used in Monte Carlo ' + '\n'
        header_text += cc + '  ' + 'particle transport calculations in an easily accessible plain-text format. ' + '\n'
        header_text += cc + '  ' + 'The first 372 entries are from the Compendium of Material Composition Data for' + '\n'
        header_text += cc + '  ' + 'Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the' + '\n'
        header_text += cc + '  ' + 'Pacific Northwest National Laboratory.  That document can be found at:' + '\n'
        header_text += cc + '  ' + r'https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf' + '\n'
        header_text += cc + '  ' + 'The sources for other entries are specified.' + '\n'
    lib_filepath = Path(lib_filepath)
    concentration_formats = ['atom fraction', 'weight fraction']
    particle_formats = ['neutrons', 'photons']
    for cfi in range(len(concentration_formats)):
        for pfi in range(len(particle_formats)):
            conctype = concentration_formats[cfi]
            par = particle_formats[pfi]
            lib_text = header_text
            for i in range(len(mat_list)):
                mat = mat_list[i]
                mati = i + 1
                entry_text = write_mc_material_entry(mat,mati,particle_format=par,concentration_format=conctype,comment_char=cc)
                lib_text += entry_text
            # save file
            fpath = Path(lib_filepath.parent, lib_filepath.stem + '_by_' + conctype.replace(' ', '_') + '_for_' + par + lib_filepath.suffix)
            f = open(fpath, 'w+')
            f.write(lib_text)
            f.close()
            print('Materials library file written:', fpath)
    return None


def write_general_mc_file(mat_list,lib_filepath=Path(Path.cwd(),'MC_materials_general.txt'),comment_char='$',header_text=''):
    '''
    Description:
        Generates a text file of MCNP/PHITS-formatted materials section text blocks for a list of material dictionary objects.
        This single file is a mix of concentration and particle formats as automatically selected for most general situations.
        If a material entry contains a chemical formula, its concentration will be specified by atom fraction; otherwise, 
        weight fraction will be used.  If any of the "neutron keywords" (`['depleted', 'enriched', ' heu', ' leu', 'uranium', 'plutonium', 'uranyl']`)
        appear in a material's name (case insensitive), the "neutrons" particle-formatted data is used (isotopic compositions specified); 
        otherwise, the "photons" particle format (natural abundances for elements) is used.
        
    Inputs:
        - `mat_list` = a list of dictionary objects of the extracted materials information
        - `lib_filepath` = string or Path object denoting the basic path to the materials library text file to be saved
        - `comment_char` = (D=`'$'`) string denoting the comment character to use (Note: `'$'` works for both PHITS and MCNP.)
        - `header_text` = a string of text appearing at the very top of the output text files. 
            If left blank (`''`), a default header string as defined at the start of this function will be used.
        
    Outputs:
        - `None`; the materials text data will be saved to `lib_filepath`.
    '''
    from PHITS_tools import fetch_MC_material
    cc = comment_char 
    if header_text=='':
        header_text = cc + '  ' + 'This file was assembled from a variety of sources over time;' + '\n'
        header_text += cc + '  ' + 'it just seeks to compile information for materials to be used in Monte Carlo ' + '\n'
        header_text += cc + '  ' + 'particle transport calculations in an easily accessible plain-text format. ' + '\n'
        header_text += cc + '  ' + 'The first 372 entries are from the Compendium of Material Composition Data for' + '\n'
        header_text += cc + '  ' + 'Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the' + '\n'
        header_text += cc + '  ' + 'Pacific Northwest National Laboratory.  That document can be found at:' + '\n'
        header_text += cc + '  ' + r'https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf' + '\n'
        header_text += cc + '  ' + 'The sources for other entries are specified.' + '\n'
    lib_text = header_text
    for i in range(len(mat_list)):
        lib_text += fetch_MC_material(i + 1, matdict=mat_list[i])
    # save file
    f = open(lib_filepath, 'w+')
    f.write(lib_text)
    f.close()
    print('Materials library file written:', lib_filepath)
    return None




'''
# Generate the JSON file and descriptive text file for the PNNL library
mat_list = pnnl_lib_csv_to_dict_list()
materials_dict_list_to_json(mat_list,json_filepath=Path(Path.cwd(),'PNNL_materials_compendium.json'))
header_text  = 'This file was assembled from the Compendium of Material Composition Data for' + '\n'
header_text += 'Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the' + '\n'
header_text += 'Pacific Northwest National Laboratory.' + '\n'
header_text += 'This file seeks to just compile the core information of the compendium in an' + '\n'
header_text += 'easily accessible plain-text format.  The full document can be found at: ' + '\n'
header_text += r'https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf' + '\n'
write_descriptive_file(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium.txt'),header_text=header_text)
write_mc_formated_files(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium.txt'),header_text=header_text)
write_general_mc_file(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium_general.txt'),header_text=header_text)
'''

'''
# Using the PNNL compendium as a base, create and add to the "Compiled_MC_materials" database
json_filepath = 'PNNL_materials_compendium'
name = 'Martian Atmosphere'
mat_str = '6000 -2.62E-01  8000 -7.00E-01 18000 -1.93E-02 7000 -1.89E-02'
update_materials_database_files(json_filepath,
                                name,
                                mat_str,
                                matid=None,
                                density='function of altitude and time',
                                source='Mahaffy 2013, DOI: 10.1126/science.1237966',
                                source_short='Mahaffy 2013',
                                formula=None,
                                molecular_weight=None,
                                total_atom_density=None,
                                new_database_base_name="Compiled_MC_materials",
                                update_descriptive_file=True,
                                update_MC_formated_files=True,
                                update_general_MC_file=True,
                                save_backup_list=True,
                                prefer_user_data_folder=True
                                )
'''

'''
# Update the existing "Compiled_MC_materials" database
json_filepath = "Compiled_MC_materials"
name = 'Martian Regolith'
mat_str = '1000 0.151069196 11000 0.033300262 12000 0.016650131 13000 0.033300262 14000 0.156699215 18000 0.537611902 19000 0.033300262 20000 0.016650131 26000 0.021418638'
update_materials_database_files(json_filepath,
                                name,
                                mat_str,
                                matid=None,
                                density=1.7,
                                source='McKenna-Lawlor 2012, DOI: 10.1016/j.icarus.2011.04.004',
                                source_short='McKenna-Lawlor 2012',
                                formula=None,
                                molecular_weight=None,
                                total_atom_density=None,
                                new_database_base_name=None,
                                update_descriptive_file=True,
                                update_MC_formated_files=True,
                                update_general_MC_file=True,
                                save_backup_list=True,
                                prefer_user_data_folder=True)
'''

'''
# Update the existing "Compiled_MC_materials" database
json_filepath = "Compiled_MC_materials"
name = 'Wood (Southern Pine, DOUBLE DENSITY) '
mat_str = '1001  -0.059642 6000  -0.497018 7014  -0.004970 8016  -0.427435 12000  -0.001988 16000  -0.004970 19000  -0.001988 20000  -0.001988'
update_materials_database_files(json_filepath,
                                name,
                                mat_str,
                                matid=359,
                                density=2*0.64,
                                source='DEMONSTRATION OF CHANGED MATERIAL ENTRY',
                                source_short='TEST_DEMO',
                                formula=None,
                                molecular_weight=None,
                                total_atom_density=None,
                                new_database_base_name=None,
                                update_descriptive_file=True,
                                update_MC_formated_files=True,
                                update_general_MC_file=True,
                                save_backup_list=True,
                                prefer_user_data_folder=True)
'''
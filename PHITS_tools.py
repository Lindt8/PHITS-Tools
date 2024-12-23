'''

This module contains a variety of tools used for parsing PHITS output files.

Specifically, it seeks to be a (nearly) universal PHITS output parser, supporting output from
all tallies, both normal "standard" output as well as dump file outputs (in ASCII and binary formats).
It is also capable of automatically parsing all such PHITS output files in a directory.
If a DCHAIN input file (output from the [T-Dchain] tally) or DCHAIN output `*.act` file is provided
to the main tally output processing function, an attempt will be made to import the [DCHAIN Tools module](https://github.com/Lindt8/DCHAIN-Tools)
and process the found DCHAIN output files too.

The functions contained in this module and brief descriptions of their functions are included below.
However, provided first is a description of the three different ways one can use and interface with this module.

### **How to use the PHITS_tools.py module**

There are three main ways one can use this Python module:

 1. As an **imported Python module**
      - In your own Python scripts, you can import this module as `from PHITS_tools import *` and call its main functions,
         which are listed in the next section below, or any of its other functions documented here.
 2. As a **command line interface (CLI)**
      - This module can be ran on the command line with the individual PHITS output file to be parsed (or a directory
          containing multiple files to be parsed) as the required argument.
          Execute `python PHITS_tools.py --help` to see all of the different options that can be used with this module
          to parse standard or dump PHITS output files (individually and directories containing them) via the CLI.
 3. As a **graphical user interface (GUI)**
      - When the module is executed without any additional arguments, `python PHITS_tools.py`, (or with the `--GUI` or `-g` flag in the CLI)
          a GUI will be launched to step you through selecting what "mode" you would like to run PHITS Tools in (`STANDARD`, `DUMP`, or `DIRECTORY`),
          selecting a file to be parsed (or a directory containing multiple files to be parsed), and the various options for each mode.

The CLI and GUI options result in the parsed file's contents being saved to a pickle (or dill) file, which can be reopened
and used later in a Python script.  When using the main functions below within a Python script which has imported the PHITS_tools
module, you can optionally choose not to save the pickle files (if desired) and only have the tally output/dump parsing
functions return the data objects they produce for your own further analyses.

### **Main PHITS Output Parsing Functions**

- `parse_tally_output_file`         : general parser for standard output files for all PHITS tallies
- `parse_tally_dump_file`           : parser for dump files from "dump" flag in PHITS [T-Cross], [T-Time], and [T-Track] tallies
- `parse_all_tally_output_in_dir`   : run `parse_tally_output_file()` over all standard output files in a directory (and, optionally, `parse_tally_dump_file()` over all dump files too)

### General Purpose Functions

- `fetch_MC_material`               : returns a string of a formatted material for PHITS or MCNP
- `tally`                           : tally/histogram values (and their indices) falling within a desired binning structure
- `rebinner`                        : rebin a set of y-data to a new x-binning structure (edges not necessarily preserved)
- `is_number`                       : returns Boolean denoting whether provided string is that of a number
- `ZZZAAAM_to_nuclide_plain_str`    : returns a nuclide plaintext string for a given "ZZZAAAM" number (1000Z+10A+M)
- `nuclide_plain_str_to_latex_str`  : convert a plaintext string for a nuclide to a LaTeX formatted raw string
- `Element_Z_to_Sym`                : return an elemental symbol string given its proton number Z
- `Element_Sym_to_Z`                : returns an atomic number Z provided the elemental symbol
- `find`                            : return index of the first instance of a value in a list
- `ICRP116_effective_dose_coeff`    : returns effective dose of a mono-energetic particle of some species and some geometry

### Subfunctions for PHITS output parsing
(These are meant as dependencies more so than for standalone usage.)

- `split_into_header_and_content`   : initial reading of PHITS tally output, dividing it into header and "content" sections
- `extract_data_from_header_line`   : extract metadata key/value pairs from tally output header lines
- `data_row_to_num_list`            : extract numeric values from a line in the tally content section
- `parse_group_string`              : split a string containing "groups" (e.g., regions) into a list of them
- `parse_tally_header`              : extract metadata from tally output header section
- `initialize_tally_array`          : initialize NumPy array for storing tally results
- `calculate_tally_absolute_errors` : calculate absolute uncertainties from read values and relative errors
- `split_str_of_equalities`         : split a string containing equalities (e.g., `reg = 100`) into a list of them
- `parse_tally_content`             : extract tally results/values from tally content section
- `build_tally_Pandas_dataframe`    : make Pandas dataframe from the main results NumPy array and the metadata
- `search_for_dump_parameters`      : attempt to auto find "dump" parameters via possible standard tally output file
- `determine_PHITS_output_file_type` : determine if a file is standard tally output or ASCII/binary dump file

'''
'''
Each function beings with a comment block containing the following sections:

    Description:


    Dependencies:


    Inputs:


    Outputs:

("Dependencies:" is omitted when there are none.)        
'''

import sys
import os
import numpy as np
from munch import *
from pathlib import Path


# default program settings
launch_GUI = False
run_with_CLI_inputs = False
in_debug_mode = False # toggles printing of debug messages throughout the code
#in_debug_mode = True # toggles printing of debug messages throughout the code
test_explicit_files_dirs = False # used for testing specific files at the bottom of this file
#test_explicit_files_dirs = True

if __name__ == "__main__":
    #in_debug_mode = True

    if test_explicit_files_dirs:
        in_debug_mode = True
        pass
    elif len(sys.argv) == 1:
        launch_GUI = True
    else:
        if '-g' in sys.argv or '--GUI' in sys.argv:
            launch_GUI = True
        else:
            run_with_CLI_inputs = True
            # CLI for PHITS Tools
            import argparse


if in_debug_mode:
    import pprint
    import time
    # Timer start
    start = time.time()



# use Path, get extension, check for existence of filename_err.extension


def parse_tally_output_file(tally_output_filepath, make_PandasDF = True, calculate_absolute_errors = True,
                            save_output_pickle = True, prefer_reading_existing_pickle = False):
    '''
    Description:
        Parse any PHITS tally output file, returning tally metadata and an array of its values (and optionally
        this data inside of a Pandas dataframe too).  Note the separate `parse_tally_dump_file` function for
        parsing PHITS dump files.  If a DCHAIN input file (output from the [T-Dchain] tally) or DCHAIN output
        `*.act` file is provided, an attempt will be made to import the [DCHAIN Tools module](https://github.com/Lindt8/DCHAIN-Tools) and process the found
        DCHAIN output files, returning the output dictionary object and (optionally) saving it to a pickle file.

    Dependencies:
        - `import numpy as np`
        - `import pandas as pd` (if `make_PandasDF = True`)
        - `import pickle` (if `save_output_pickle = True`)
        - `from munch import *`
        - `from pathlib import Path`

    Inputs:
       (required)

        - `tally_output_filepath` = file or filepath to the tally output file to be parsed

    Inputs:
       (optional)

       - `make_PandasDF` = A Boolean determining whether a Pandas dataframe of the tally data array will be made (D=`True`)
       - `calculate_absolute_errors` = A Boolean determining whether the absolute uncertainty of each tally output value
                      is to be calculated (simply as the product of the value and relative error); if `False`, the final
                      dimension of `tally_data`, `ierr`, will be of length-2 rather than length-3 (D=`True`)
       - `save_output_pickle` = A Boolean determining whether the `tally_output` dictionary object is saved as a pickle file;
                      if `True`, the file will be saved with the same path and name as the provided PHITS tally output file
                      but with the .pickle extension. (D=`True`)
       - `prefer_reading_existing_pickle` = A Boolean determining what this function does if the pickle file this function
                      seeks to generate already exists.  If `False` (default behavior), this function will parse the PHITS
                      output files as usual and overwrite the existing pickle file.  If `True`, this function will instead
                      simply just read the existing found pickle file and return its stored `tally_output` contents. (D=`False`)

    Output:
        - `tally_output` = a dictionary object with the below keys and values:
            - `'tally_data'` = a 10-dimensional NumPy array containing all tally results, explained in more detail below
            - `'tally_metadata'` = a dictionary/Munch object with various data extracted from the tally output file, such as axis binning and units
            - `'tally_dataframe'` = (optionally included if setting `make_PandasDF = True`) a Pandas dataframe version of `tally_data`


    Notes:

       Many quantities can be scored across the various tallies in the PHITS code.  This function outputs a "universal"
       array `tally_data` that can accomodate all of the different scoring geometry meshes, physical quantities with
       assigned meshes, and output axes provided within PHITS.  This is achieved with a 10-dimensional array accessible as

       `tally_data[ ir, iy, iz, ie, it, ia, il, ip, ic, ierr ]`, with indices explained below:

       Tally data indices and corresponding mesh/axis:

        - `0` | `ir`, Geometry mesh: `reg` / `x` / `r` / `tet` ([T-Cross] `ir surf` if `mesh=r-z` with `enclos=0`)
        - `1` | `iy`, Geometry mesh:  `1` / `y` / `1`
        - `2` | `iz`, Geometry mesh:  `1` / `z` / `z` ([T-Cross] `iz surf` if `mesh=xyz` or `mesh=r-z` with `enclos=0`)
        - `3` | `ie`, Energy mesh: `eng` ([T-Deposit2] `eng1`)
        - `4` | `it`, Time mesh
        - `5` | `ia`, Angle mesh
        - `6` | `il`, LET mesh
        - `7` | `ip`, Particle type (`part = `)
        - `8` | `ic`, Special: [T-Deposit2] `eng2`; [T-Yield] `mass`, `charge`, `chart`; [T-Interact] `act`
        - `9` | `ierr = 0/1/2`, Value / relative uncertainty / absolute uncertainty (expanded to `3/4/5`, or `2/3` if
        `calculate_absolute_errors = False`, for [T-Cross] `mesh=r-z` with `enclos=0` case; see notes further below)

       -----

       By default, all array dimensions are length-1 (except `ierr`, which is length-3).  These dimensions are set/corrected
       automatically when parsing the tally output file.  Thus, for very simple tallies, most of these indices will be
       set to 0 when accessing tally results, e.g. `tally_data[2,0,0,:,0,0,0,:,0,:]` to access the full energy spectrum
       in the third region for all scored particles / particle groups with the values and uncertainties.

       The output `tally_metadata` dictionary contains all information needed to identify every bin along every
       dimension: region numbers/groups, particle names/groups, bin edges and midpoints for all mesh types
       (x, y, z, r, energy, angle, time, and LET) used in the tally.

       The `tally_dataframe` Pandas dataframe output functions as normal.  Note that a dictionary containing supplemental
       information that is common to all rows of the dataframe can be accessed with `tally_dataframe.attrs`.

       -----

       **Unsupported tallies and DCHAIN**

       At present, the following tallies are NOT supported by this function: [T-WWG], [T-WWBG], [T-Volume],
       [T-Userdefined], [T-Gshow], [T-Rshow], [T-3Dshow], [T-4Dtrack], and [T-Dchain]&dagger;.

       &dagger;If provided with the output file of [T-Dchain] (the input file for the DCHAIN code) or the `*.act` main
       output file produced by the DCHAIN code, this function will attempt to import the [DCHAIN Tools module](https://github.com/Lindt8/DCHAIN-Tools)
       and process the found DCHAIN output files, returning the output dictionary object and (optionally) saving it to a pickle file.
       Otherwise, for [T-Dchain] or [T-Yield] with `axis = dchain`, you can manually use the separate suite of parsing
       functions included in the [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools) module.

       -----

       **[T-Cross] special case**

       The [T-Cross] tally is unique (scoring across region boundaries rather than within regions), creating some
       additional challenges.
       In the `mesh = reg` case, much is the same except each region number is composed of the `r-from` and `r-to` values, e.g. `'100 - 101'`.

       For `xyz` and `r-z` meshes, an additional parameter is at play: `enclos`.
       By default, `enclos=0`.
       In the event `enclos=1` is set, the total number of geometric regions is still either `nx*ny*nz` or `nr*nz` for
       `xyz` and `r-z` meshes, respectively.
       For `enclos=0` in the `mesh = xyz` case, the length of the z dimension (`iz` index) is instead equal to `nzsurf`,
       which is simply one greater than `nz` (# regions = `nx*ny*(nz+1)`).

       For `enclos=0` in the `mesh = r-z` case, this is much more complicated as PHITS will output every combination of
       `nr*nzsurf` AND `nrsurf*nz`, noting `nzsurf=nz+1` and `nrsurf=nr+1` (or `nrsurf=nr` if the first radius bin edge
       is `r=0.0`).
       The solution implemented here is to, for only this circumstance (in only the `enclos=0 mesh=r-z` case),
       set the length of the `ir` and `iz` dimensions to `nrsurf` and `nzsurf`, respectively, and also
       to expand the length of the final dimension of `tally_data` from 3 to 6 (or from 2 to 4 if `calculate_absolute_errors=False`), where:

        - `ierr = 0/1/2` refer to the combinations of `nr` and `nzsurf` (or `0/1` if `calculate_absolute_errors=False`)
        - `ierr = 3/4/5` refer to the combinations of `nrsurf` and `nz` (or `2/3` if `calculate_absolute_errors=False`)

       In this case, the Pandas dataframe, if enabled, will contain 3 (or 2) extra columns `value2` and `rel.err.2` [and `abs.err.2`],
       which correspond to the combinations of `nrsurf` and `nz` (while the original columns without the "2" refer to
       values for combinations of and `nr` and `nzsurf`).

       -----

       **[T-Yield] special case**

       [T-Yield] is also a bit exceptional.  When setting the `axis` parameter equal to `charge`, `mass`, or `chart`,
       the `ic` dimension of `tally_data` is used for each entry of charge (proton number, Z), mass (A), or
       isotope/isomer, respectively.

       In the case of `axis = charge` or `axis = mass`, the value of `ic` refers to the actual charge/proton number Z
       or mass number A when accessing `tally_data`; for instance, `tally_data[:,:,:,:,:,:,:,:,28,:]`
       references results from nuclei with Z=28 if `axis = charge` or A=28 if `axis = mass`.  The length of the `ic`
       dimension is initialized as 130 or 320 but is later reduced to only just include the highest charge or mass value.

       In the case of `axis = chart`, the length of the `ic` dimension is initially set equal to the `mxnuclei` parameter
       in the [T-Yield] tally.  If `mxnuclei = 0` is set, then the length of the `ic` dimension is initially set to 10,000.
       This `ic` dimension length is later reduced to the total number of unique nuclides found in the output.
       Owing to the huge number of possible nuclides, a list of found nuclides with nonzero yield is assembled and
       added to `tally_metadata` under the keys `nuclide_ZZZAAAM_list` and `nuclide_isomer_list`, i.e.
       `tally_metadata['nuclide_ZZZAAAM_list']` and `tally_metadata['nuclide_isomer_list']`.
       These lists should be referenced to see what nuclide each of index `ic` refers to.
       The entries of the ZZZAAAM list are intergers calculated with the formula 10000\*Z + 10\*A + M, where M is the
       metastable state of the isomer (0 = ground state, 1 = 1st metastable/isomeric state, etc.).  The entries
       of the isomer list are these same nuclides in the same order but written as plaintext strings, e.g. `'Al-28'` and `'Xe-133m1'`.
       The lists are ordered in the same order nuclides are encountered while parsing the output file.
       Thus, to sensibly access the yield of a specific nuclide, one must first find its index `ic` in one of the two
       metadata lists of ZZZAAAM values or isomer names and then use that to access `tally_data`.  For example, to get
       the yield results of production of carbon-14 (C-14), one would use the following code:

       `ic = tally_metadata['nuclide_ZZZAAAM_list'].index(60140)`

       OR

       `ic = tally_metadata['nuclide_isomer_list'].index('C-14')`

       then

       `my_yield_values = tally_data[:,:,:,:,:,:,:,:,ic,:]`


    '''

    '''
    The old [T-Cross] mesh=r-z enclos=0 solution is written below:
        The solution implemented here uses `ir` to iterate `nr`, `iy` to iterate `nrsurf`, `iz` to
        iterate `nz`, and `ic` to iterate `nzsurf`.  Since only `rsurf*z [iy,iz]` and `r*zsurf [ir,ic]` pairs exist,
        when one pair is being written, the other will be `[-1,-1]`, thus the lengths of these dimensions for the array
        are increased by an extra 1 to prevent an overlap in the data written.
    '''
    pickle_filepath = Path(tally_output_filepath.parent, tally_output_filepath.stem + '.pickle')
    if prefer_reading_existing_pickle and os.path.isfile(pickle_filepath):
        import pickle
        print('Reading found pickle file: ', pickle_filepath)
        with open(pickle_filepath, 'rb') as handle:
            tally_output = pickle.load(handle)
        return tally_output

    # main toggled settings
    #calculate_absolute_errors = True
    construct_Pandas_frame_from_array = make_PandasDF
    #process_all_tally_out_files_in_directory = False
    save_pickle_files_of_output = save_output_pickle  # save metadata, array, and Pandas frame in a pickled dictionary object

    if construct_Pandas_frame_from_array: import pandas as pd

    # Check if is _err or _dmp file (or normal value file)
    is_val_file = False
    is_err_file = False
    is_dmp_file = False
    if tally_output_filepath.stem[-4:] == '_err':
        is_err_file = True
    elif tally_output_filepath.stem[-4:] == '_dmp':
        is_dmp_file = True
    else:
        is_val_file = True

    if is_dmp_file:
        print('ERROR: The provided file is a "dump" output file. Use the function titled "parse_tally_dump_file" to process it instead.')
        return None

    if is_err_file:
        print('WARNING: Provided file contains just relative uncertainties.',str(tally_output_filepath))
        potential_val_file = Path(tally_output_filepath.parent, tally_output_filepath.stem.replace('_err','') + tally_output_filepath.suffix)
        if potential_val_file.is_file():
            print('\t Instead, both it and the file with tally values will be parsed.')
            potential_err_file = tally_output_filepath
            tally_output_filepath = potential_val_file
            is_val_file = True
            is_err_file = False
        else:
            print('\t The corresponding file with tally values could not be found, so only these uncertainties will be parsed.')

    # Split content of output file into header and content
    if in_debug_mode: print("\nSplitting output into header and content...   ({:0.2f} seconds elapsed)".format(time.time() - start))
    tally_header, tally_content = split_into_header_and_content(tally_output_filepath)
    if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))
    # print(len(tally_content))

    # Check if *_err file exists
    potential_err_file = Path(tally_output_filepath.parent, tally_output_filepath.stem + '_err' + tally_output_filepath.suffix)
    is_err_in_separate_file = potential_err_file.is_file()  # for some tallies/meshes, uncertainties are stored in a separate identically-formatted file

    # Extract tally metadata
    if in_debug_mode: print("\nExtracting tally metadata...   ({:0.2f} seconds elapsed)".format(time.time() - start))
    tally_metadata = parse_tally_header(tally_header, tally_content)
    if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))
    if in_debug_mode: pprint.pp(dict(tally_metadata))
    # Check if tally_type is among those supported.
    unsupported_tally_types = ['[T-WWG]', '[T-WWBG]', '[T-Volume]', '[T-Userdefined]', '[T-Gshow]', '[T-Rshow]',
                               '[T-3Dshow]', '[T-4Dtrack]', '[T-Dchain]', 'UNKNOWN']
    if tally_metadata['tally_type'] in unsupported_tally_types:
        print('ERROR! tally type',tally_metadata['tally_type'],'is not supported by this function!')
        if tally_metadata['tally_type'] == '[T-Dchain]' or tally_output_filepath.suffix == '.act':
            print('Instead, the DCHAIN Tools module is used to process the DCHAIN output files with the same basename of the provided file.')
            dchain_tools_url = 'github.com/Lindt8/DCHAIN-Tools'
            dchain_tools_go_to_github_str = 'The DCHAIN Tools module ( '+dchain_tools_url+' ) is capable of parsing all DCHAIN-related output.'
            if tally_output_filepath.suffix != '.act':
                act_filepath = Path(tally_output_filepath.parent, tally_output_filepath.stem + '.act')
                if not act_filepath.is_file():
                    # DCHAIN output is not present in directory
                    print('Failed to find the main DCHAIN *.act output file:',act_filepath)
                    print('Aborting this process...')
                    return None
            try:
                from dchain_tools import process_dchain_simulation_output
            except:
                print('Failed to import the DCHAIN Tools module; to parse DCHAIN output via PHITS Tools, please install DCHAIN Tools and configure it in your Python environment')
                return None
            simulation_folder_path = str(Path(tally_output_filepath.parent)) + '\\'
            simulation_basename = str(tally_output_filepath.stem)
            dchain_output = process_dchain_simulation_output(simulation_folder_path,simulation_basename,process_DCS_file=True)
            if save_output_pickle:
                import pickle
                path_to_pickle_file = Path(tally_output_filepath.parent, tally_output_filepath.stem + '.pickle')
                if in_debug_mode: print("\nWriting output to pickle file...   ({:0.2f} seconds elapsed)".format(time.time() - start))
                with open(path_to_pickle_file, 'wb') as handle:
                    pickle.dump(dchain_output, handle, protocol=pickle.HIGHEST_PROTOCOL)
                    print('Pickle file written:', path_to_pickle_file, '\n')
                if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))
            return dchain_output
        else:
            return None
    if tally_metadata['tally_type'] == '[T-Yield]' and tally_metadata['axis'] == 'dchain':
        dchain_tools_url = 'github.com/Lindt8/DCHAIN-Tools'
        print('This function does not support [T-Yield] with setting "axis = dchain".')
        print('However, the DCHAIN Tools module (', dchain_tools_url, ') is capable of parsing all DCHAIN-related output.')
        return None

    # Initialize tally data array with zeros
    tally_data = initialize_tally_array(tally_metadata, include_abs_err=calculate_absolute_errors)

    # Parse tally data
    if is_val_file:
        err_mode = False
    else: # if is_err_file
        err_mode = True
    if in_debug_mode: print("\nParsing tally data...   ({:0.2f} seconds elapsed)".format(time.time() - start))
    if tally_metadata['tally_type']=='[T-Yield]' and tally_metadata['axis'] in ['chart','charge','mass']: # need to update metadata too
        tally_data, tally_metadata = parse_tally_content(tally_data, tally_metadata, tally_content, is_err_in_separate_file, err_mode=err_mode)
    else:
        tally_data = parse_tally_content(tally_data, tally_metadata, tally_content, is_err_in_separate_file, err_mode=err_mode)
    if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))
    err_data_found = True
    if tally_metadata['axis_dimensions'] == 2 and tally_metadata['2D-type'] != 4:
        if is_err_file:
            err_data_found = False
        elif is_err_in_separate_file:
            err_tally_header, err_tally_content = split_into_header_and_content(potential_err_file)
            if in_debug_mode: print("\nParsing tally error...   ({:0.2f} seconds elapsed)".format(time.time() - start))
            if tally_metadata['tally_type'] == '[T-Yield]' and tally_metadata['axis'] in ['chart','charge','mass']:  # need to update metadata too
                tally_data, tally_metadata = parse_tally_content(tally_data, tally_metadata, err_tally_content, is_err_in_separate_file,err_mode=True)
            else:
                tally_data = parse_tally_content(tally_data, tally_metadata, err_tally_content, is_err_in_separate_file, err_mode=True)
            if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))
        else:
            print('WARNING: A separate file ending in "_err" containing uncertainties should exist but was not found.')
            err_data_found = False
    if calculate_absolute_errors:
        if err_data_found:
            if in_debug_mode: print("\nCalculating absolute errors...   ({:0.2f} seconds elapsed)".format(time.time() - start))
            tally_data = calculate_tally_absolute_errors(tally_data)
            if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))
        elif is_err_file:
            print('WARNING: Absolute errors not calculated since the main tally values file was not found.')
        else:
            print('WARNING: Absolute errors not calculated since the _err file was not found.')
    # Generate Pandas dataframe of tally results
    if construct_Pandas_frame_from_array:
        if in_debug_mode: print("\nConstructing Pandas dataframe...   ({:0.2f} seconds elapsed)".format(time.time() - start))
        tally_Pandas_df = build_tally_Pandas_dataframe(tally_data, tally_metadata)
        if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))
    else:
        tally_Pandas_df = None

    tally_output = {
        'tally_data': tally_data,
        'tally_metadata': tally_metadata,
        'tally_dataframe': tally_Pandas_df,
    }

    if save_output_pickle:
        import pickle
        path_to_pickle_file = Path(tally_output_filepath.parent, tally_output_filepath.stem + '.pickle')
        if in_debug_mode: print("\nWriting output to pickle file...   ({:0.2f} seconds elapsed)".format(time.time() - start))
        with open(path_to_pickle_file, 'wb') as handle:
            pickle.dump(tally_output, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print('Pickle file written:', path_to_pickle_file, '\n')
        if in_debug_mode: print("\tComplete!   ({:0.2f} seconds elapsed)".format(time.time() - start))

    return tally_output



def parse_tally_dump_file(path_to_dump_file, dump_data_number=None , dump_data_sequence=None, return_directional_info=False,
                          use_degrees=False,max_entries_read=None,return_namedtuple_list=True,
                          return_Pandas_dataframe=True, save_namedtuple_list=False, save_Pandas_dataframe=False):
    '''
    Description:
        Parses the dump file of a [T-Cross], [T-Product], or [T-Time] tally generated by PHITS, in ASCII or binary format.

    Dependencies:
        - `from collections import namedtuple`
        - `from scipy.io import FortranFile`
        - `import pandas as pd` (if `return_Pandas_dataframe = True`)
        - `import dill` (if `save_namedtuple_list = True`)
        - `import lzma` (if `save_namedtuple_list = True`)

    Inputs:
       (required)

        - `path_to_dump_file` = string or Path object denoting the path to the dump tally output file to be parsed
        - `dump_data_number` = integer number of data per row in dump file, binary if >0 and ASCII if <0.
                 This should match the value following `dump=` in the tally creating the dump file. (D=`None`)
                 If not specified, the search_for_dump_parameters() function will attempt to find it automatically.
        - `dump_data_sequence` = string or list of integers with the same number of entries as `dump_data_number`,
                 mapping each column in the dump file to their physical quantities.  (D=`None`)
                 This should match the line following the `dump=` line in the tally creating the dump file.
                 See PHITS manual section "6.7.22 dump parameter" for further explanations of these values.
                 If not specified, the search_for_dump_parameters() function will attempt to find it automatically.

    Inputs:
       (optional)

        - `return_directional_info` = (optional, D=`False`) Boolean designating whether extra directional information
                 should be calculated and returned; these include: radial distance `r` from the origin in cm,
                 radial distance `rho` from the z-axis in cm,
                 polar angle `theta` between the direction vector and z-axis in radians [0,pi] (or degrees), and
                 azimuthal angle `phi` of the direction vector in radians [-pi,pi] (or degrees).
                 Note: This option requires all position and direction values [x,y,z,u,v,w] to be included in the dump file.
        - `use_degrees` = (optional, D=`False`) Boolean designating whether angles `theta` and `phi` are returned
                 in units of degrees. Default setting is to return angles in radians.
        - `max_entries_read` = (optional, D=`None`) integer number specifying the maximum number of entries/records
                 of the dump file to be read.  By default, all records in the dump file are read.
        - `return_namedtuple_list` = (optional, D=`True`) Boolean designating whether `dump_data_list` is returned.
        - `return_Pandas_dataframe` = (optional, D=`True`) Boolean designating whether `dump_data_frame` is returned.
        - `save_namedtuple_list` = (optional, D=`False`) Boolean designating whether `dump_data_list` is saved to a dill file,
                which will be compressed with LZMA (built-in with Python)
                (for complicated reasons, objects containing namedtuples cannot be easily saved with pickle but can with dill).
                This *.dill.xz file can then be opened (after importing `dill` and `lzma`) as:
                `with lzma.open(path_to_dillxz_file, 'rb') as file: dump_data_list = dill.load(file)`
        - `save_Pandas_dataframe` = (optional, D=`False`) Boolean designating whether `dump_data_frame` is saved to a pickle
                file (via Pandas .to_pickle()).

    Outputs:
        - `dump_data_list` = List of length equal to the number of records contained in the file. Each entry in the list
                 is a namedtuple containing all of the physical information in the dump file for a given particle event,
                 in the same order as specified in `dump_data_sequence` and using the same naming conventions for keys as
                 described in the PHITS manual section "6.7.22 dump parameter"
                 (`kf`, `x`, `y`, `z`, `u`, `v`, `w`, `e`, `wt`, `time`, `c1`, `c2`, `c3`, `sx`, `sy`, `sz`, `name`, `nocas`, `nobch`, `no`).
                 If `return_directional_info = True`, `r`, `rho`, `theta`, and `phi` are appended to the end of this namedtuple, in that order.
        - `dump_data_frame` = A Pandas dataframe created from `dump_data_list` with columns for each physical quantity
                 and rows for each record included in the dump file.
    '''

    from collections import namedtuple
    from typing import NamedTuple
    from scipy.io import FortranFile
    if return_Pandas_dataframe or save_Pandas_dataframe:
        import pandas as pd
    if save_Pandas_dataframe or save_namedtuple_list:
        #import pickle
        import dill

    if not return_namedtuple_list and not return_Pandas_dataframe and not save_namedtuple_list and not save_Pandas_dataframe:
        raise ValueError('ERROR: All "return_namedtuple_list", "return_Pandas_dataframe", "save_namedtuple_list", and "save_Pandas_dataframe" are False. Enable at least one to use this function.')

    if dump_data_number == None or dump_data_sequence == None:
        dump_data_number, dump_data_sequence = search_for_dump_parameters(path_to_dump_file)
    if dump_data_number == None or dump_data_sequence == None:
        raise ValueError("Please manually specify 'dump_data_number' and 'dump_data_sequence'; these were not inputted and could not be automatically found from an origin tally standard output file.")
        #return None

    if isinstance(dump_data_sequence, str):
        dump_data_sequence = dump_data_sequence.split()
        dump_data_sequence = [int(i) for i in dump_data_sequence]
    dump_file_is_binary = True if (dump_data_number > 0) else False  # if not binary, file will be ASCII
    data_values_per_line = abs(dump_data_number)
    if data_values_per_line != len(dump_data_sequence):
        raise ValueError('ERROR: Number of values in "dump_data_sequence" is not equal to "dump_data_number"')

    # Generate NamedTuple for storing record information
    # See PHITS manual section "6.7.22 dump parameter" for descriptions of these values
    dump_quantities = ['kf', 'x', 'y', 'z', 'u', 'v', 'w', 'e', 'wt', 'time', 'c1', 'c2', 'c3', 'sx', 'sy', 'sz',
                       'name', 'nocas', 'nobch', 'no']
    ordered_record_entries_list = [dump_quantities[i - 1] for i in dump_data_sequence]
    rawRecord = namedtuple('rawRecord', ordered_record_entries_list)
    if return_directional_info:
        ordered_record_entries_list += ['r', 'rho', 'theta', 'phi']
        angle_units_mult = 1
        if use_degrees: angle_units_mult = 180 / np.pi
    Record = namedtuple('Record', ordered_record_entries_list)

    records_list = []
    if dump_file_is_binary:
        # Read binary dump file; extract each record (particle)
        file_size_bytes = os.path.getsize(path_to_dump_file)
        record_size_bytes = (data_values_per_line + 1) * 8  # each record has 8 bytes per data value plus an 8-byte record end
        num_records = int(file_size_bytes / record_size_bytes)
        if max_entries_read != None:
            if max_entries_read < num_records:
                num_records = max_entries_read
        # print(num_records)
        current_record_count = 0
        if return_directional_info:
            with FortranFile(path_to_dump_file, 'r') as f:
                while current_record_count < num_records:
                    current_record_count += 1
                    raw_values = f.read_reals(float)
                    rawrecord = rawRecord(*raw_values)
                    # calculate r, rho, theta (w.r.t. z-axis), and phi (w.r.t. x axis)
                    r = np.sqrt(rawrecord.x ** 2 + rawrecord.y ** 2 + rawrecord.z ** 2)
                    rho = np.sqrt(rawrecord.x ** 2 + rawrecord.y ** 2)
                    dir_vector = [rawrecord.u, rawrecord.v, rawrecord.w]
                    theta = np.arccos(np.clip(np.dot(dir_vector, [0, 0, 1]), -1.0, 1.0)) * angle_units_mult
                    phi = np.arctan2(rawrecord.y, rawrecord.x) * angle_units_mult
                    record = Record(*raw_values, r, rho, theta, phi)
                    records_list.append(record)
        else: # just return data in dump file
            with FortranFile(path_to_dump_file, 'r') as f:
                while current_record_count < num_records:
                    current_record_count += 1
                    raw_values = f.read_reals(float)
                    record = Record(*raw_values)
                    records_list.append(record)
    else: # file is ASCII
        if max_entries_read == None:
            max_entries_read = np.inf
        if return_directional_info:
            with open(path_to_dump_file, 'r') as f:
                current_record_count = 0
                for line in f:
                    current_record_count += 1
                    if current_record_count > max_entries_read: break
                    line_str_values = line.replace('D', 'E').split()
                    raw_values = [float(i) for i in line_str_values]
                    rawrecord = rawRecord(*raw_values)
                    # calculate r, rho, theta (w.r.t. z-axis), and phi (w.r.t. x axis)
                    r = np.sqrt(rawrecord.x ** 2 + rawrecord.y ** 2 + rawrecord.z ** 2)
                    rho = np.sqrt(rawrecord.x ** 2 + rawrecord.y ** 2)
                    dir_vector = [rawrecord.u, rawrecord.v, rawrecord.w]
                    theta = np.arccos(np.clip(np.dot(dir_vector, [0, 0, 1]), -1.0, 1.0)) * angle_units_mult
                    phi = np.arctan2(rawrecord.y, rawrecord.x) * angle_units_mult
                    record = Record(*raw_values, r, rho, theta, phi)
                    records_list.append(record)
        else: # just return data in dump file
            with open(path_to_dump_file, 'r') as f:
                current_record_count = 0
                for line in f:
                    current_record_count += 1
                    if current_record_count > max_entries_read: break
                    line_str_values = line.replace('D', 'E').split()
                    raw_values = [float(i) for i in line_str_values]
                    record = Record(*raw_values)
                    records_list.append(record)
    #print(record)

    if save_namedtuple_list:
        import lzma
        path_to_dump_file = Path(path_to_dump_file)
        pickle_path = Path(path_to_dump_file.parent, path_to_dump_file.stem + '_namedtuple_list.dill.xz')
        with lzma.open(pickle_path, 'wb') as handle:
            dill.dump(records_list, handle, protocol=dill.HIGHEST_PROTOCOL)
            print('Pickle file written:', pickle_path, '\n')

    if return_Pandas_dataframe or save_Pandas_dataframe:
        # Make Pandas dataframe from list of records
        records_df = pd.DataFrame(records_list, columns=Record._fields)
        if save_Pandas_dataframe:
            path_to_dump_file= Path(path_to_dump_file)
            pickle_path = Path(path_to_dump_file.parent, path_to_dump_file.stem + '_Pandas_df.pickle')
            records_df.to_pickle(pickle_path)
            #with open(pickle_path, 'wb') as handle:
            #    pickle.dump(records_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
            #    print('Pickle file written:', pickle_path, '\n')

    if return_namedtuple_list and return_Pandas_dataframe:
        return records_list, records_df
    elif return_namedtuple_list:
        return records_list
    elif return_Pandas_dataframe:
        return records_df
    else:
        return None




def parse_all_tally_output_in_dir(tally_output_dirpath, output_file_suffix = '.out', output_file_prefix = '',
                                  output_file_required_string='', include_subdirectories=False,  return_tally_output=False,
                                  make_PandasDF=True, calculate_absolute_errors=True,
                                  save_output_pickle=True, prefer_reading_existing_pickle=False,
                                  include_dump_files=False,
                                  dump_data_number=None , dump_data_sequence=None,
                                  dump_return_directional_info=False, dump_use_degrees=False,
                                  dump_max_entries_read=None,
                                  dump_save_namedtuple_list=True, dump_save_Pandas_dataframe=True
                                  ):
    '''
    Description:
        Parse all standard PHITS tally output files in a directory, returning either a list of dictionaries containing
        tally metadata and an array of values from each tally output (and optionally this data inside of a Pandas dataframe too)
        or a list of filepaths to pickle files containing these dictionaries, as created with the `parse_tally_output_file()` function.
        This function allows selective processing of files in the directory by specification of strings which must
        appear at the start, end, and/or anywhere within each filename.
        Even if a file satisfies all of these naming criteria, the function will also check the first line of the file
        to determine if it is a valid tally output file (meaning, it will skip files such as phits.out and batch.out).
        It will also skip over "_err" uncertainty files as these are automatically found by the `parse_tally_output_file()`
        function after it processes that tally's main output file.
        This function will mainly process standard tally output files, but it can optionally process tally "dump" files too,
        though it can only save the dump outputs to its dill/pickle files and not return the (quite large) dump data objects.
        The filenames of saved dump data will not be included in the returned list.

    Dependencies:
        - `import os`
        - `import numpy as np`
        - `import pandas as pd` (if `make_PandasDF = True`)
        - `import pickle` (if `save_output_pickle = True`)
        - `from munch import *`
        - `from pathlib import Path`

    Inputs:
       (required)

        - `tally_output_dirpath` = Path (string or path object) to the tally output directory to be searched and parsed

    Inputs:
       (optional)

       - `output_file_suffix` = A string specifying what characters processed filenames (including the file extension)
                      must end in to be included.  This condition is not enforced if set to an empty string `''`. (D=`'.out'`)
       - `output_file_prefix` = A string specifying what characters processed filenames (including the file extension)
                      must begin with to be included.  This condition is not enforced if set to an empty string `''`. (D=`''`)
       - `output_file_required_string` = A string which must be present anywhere within processed filenames (including the
                      file extension) to be included.  This condition is not enforced if set to an empty string `''`. (D=`''`)
       - `include_subdirectories` = A Boolean determining whether this function searches and processes all included
                      tally output files in this directory AND deeper subdirectories if set to `True`
                      or only the files directly within the provided directory `tally_output_dirpath` if set to `False` (D=`False`)
       - `return_tally_output` = A Boolean determining whether this function returns a list of `tally_output` dictionaries
                      if set to `True` or just a list of filepaths to the pickle files containing these dictionaries
                      if set to `False` (D=`False`)
       - `include_dump_files` = A Boolean determining whether dump files will be processed too or skipped. (D=`False`)
                      Settings to be applied to all encountered dump files can be specified per the optional inputs
                      detailed below which are simply passed to the `parse_tally_dump_file()` function.  Note that parameters
                      `return_namedtuple_list` and `return_Pandas_dataframe` will always be `False` when dump files are
                      processed in a directory with this function; instead, `save_namedtuple_list` and `save_Pandas_dataframe`
                      are by default set to `True` when parsing dump files in a directory with this function.  (Be warned,
                      if the dump file is large, the produced files from parsing them will be too.)

    Inputs:
       (optional, the same as in and directly passed to the `parse_tally_output_file()` function)

       - `make_PandasDF` = A Boolean determining whether a Pandas dataframe of the tally data array will be made (D=`True`)
       - `calculate_absolute_errors` = A Boolean determining whether the absolute uncertainty of each tally output value
                      is to be calculated (simply as the product of the value and relative error); if `False`, the final
                      dimension of `tally_data`, `ierr`, will be of length-2 rather than length-3 (D=`True`)
       - `save_output_pickle` = A Boolean determining whether the `tally_output` dictionary object is saved as a pickle file;
                      if `True`, the file will be saved with the same path and name as the provided PHITS tally output file
                      but with the .pickle extension. (D=`True`)
       - `prefer_reading_existing_pickle` = A Boolean determining what this function does if the pickle file this function
                      seeks to generate already exists.  If `False` (default behavior), this function will parse the PHITS
                      output files as usual and overwrite the existing pickle file.  If `True`, this function will instead
                      simply just read the existing found pickle file and return its stored `tally_output` contents. (D=`False`)

    Inputs:
       (optional, the same as in and directly passed to the `parse_tally_dump_file()` function)

       - `dump_data_number` = integer number of data per row in dump file, binary if >0 and ASCII if <0.
                This should match the value following `dump=` in the tally creating the dump file. (D=`None`)
                If not specified, the search_for_dump_parameters() function will attempt to find it automatically.
       - `dump_data_sequence` = string or list of integers with the same number of entries as `dump_data_number`,
                mapping each column in the dump file to their physical quantities.  (D=`None`)
                This should match the line following the `dump=` line in the tally creating the dump file.
                See PHITS manual section "6.7.22 dump parameter" for further explanations of these values.
                If not specified, the search_for_dump_parameters() function will attempt to find it automatically.
       - `dump_return_directional_info` = (optional, D=`False`) Boolean designating whether extra directional information
                should be calculated and returned; these include: radial distance `r` from the origin in cm,
                radial distance `rho` from the z-axis in cm,
                polar angle `theta` between the direction vector and z-axis in radians [0,pi] (or degrees), and
                azimuthal angle `phi` of the direction vector in radians [-pi,pi] (or degrees).
                Note: This option requires all position and direction values [x,y,z,u,v,w] to be included in the dump file.
       - `dump_use_degrees` = (optional, D=`False`) Boolean designating whether angles `theta` and `phi` are returned
                in units of degrees. Default setting is to return angles in radians.
       - `dump_max_entries_read` = (optional, D=`None`) integer number specifying the maximum number of entries/records
                of the dump file to be read.  By default, all records in the dump file are read.
       - `dump_save_namedtuple_list` = (optional, D=`True`) Boolean designating whether `dump_data_list` is saved to a dill file
               (for complicated reasons, objects containing namedtuples cannot be easily saved with pickle but can with dill).
       - `dump_save_Pandas_dataframe` = (optional, D=`True`) Boolean designating whether `dump_data_frame` is saved to a pickle
               file (via Pandas .to_pickle()).

    Output:
        - `tally_output_list` = a list of `tally_output` dictionary objects with the below keys and values / a list of
             file paths to pickle files containing `tally_output` dictionary objects:
            - `'tally_data'` = a 10-dimensional NumPy array containing all tally results, explained in more detail below
            - `'tally_metadata'` = a dictionary/Munch object with various data extracted from the tally output file, such as axis binning and units
            - `'tally_dataframe'` = (optionally included if setting `make_PandasDF = True`) a Pandas dataframe version of `tally_data`

    '''
    import os

    if not os.path.isdir(tally_output_dirpath):
        print('The provided path to "tally_output_dir" is not a directory:',tally_output_dirpath)
        if os.path.isfile(tally_output_dirpath):
            head, tail = os.path.split(tally_output_dirpath)
            tally_output_dirpath = head
            print('However, it is a valid path to a file; thus, its parent directory will be used:',tally_output_dirpath)
        else:
            print('Nor is it a valid path to a file. ERROR! Aborting...')
            return None

    if include_subdirectories:
        # Get paths to all files in this dir and subdirs
        files_in_dir = []
        for path, subdirs, files in os.walk(tally_output_dirpath):
            for name in files:
                files_in_dir.append(os.path.join(path, name))
    else:
        # Just get paths to files in this dir
        files_in_dir = [os.path.join(tally_output_dirpath, f) for f in os.listdir(tally_output_dirpath) if os.path.isfile(os.path.join(tally_output_dirpath, f))]

    # Determine which files should be parsed
    filepaths_to_process = []
    dump_filepaths_to_process = []
    len_suffix = len(output_file_suffix)
    len_prefix = len(output_file_prefix)
    len_reqstr = len(output_file_required_string)
    for f in files_in_dir:
        head, tail = os.path.split(f)
        if len_suffix > 0 and tail[-len_suffix:] != output_file_suffix: continue
        if len_prefix > 0 and tail[:len_prefix] != output_file_prefix: continue
        if len_reqstr > 0 and output_file_required_string not in tail: continue
        if tail[(-4-len_suffix):] == '_err' + output_file_suffix: continue
        with open(f) as ff:
            try:
                first_line = ff.readline().strip()
            except: # triggered if encountering binary / non ASCII or UTF-8 file
                if include_dump_files and tail[(-4-len_suffix):] == '_dmp' + output_file_suffix:
                    dump_filepaths_to_process.append(f)
                continue
            if len(first_line) == 0: continue
            if first_line[0] != '[' :
                if include_dump_files and tail[(-4-len_suffix):] == '_dmp' + output_file_suffix:
                    dump_filepaths_to_process.append(f)
                continue
        filepaths_to_process.append(f)

    tally_output_pickle_path_list = []
    tally_output_list = []
    for f in filepaths_to_process:
        f = Path(f)
        path_to_pickle_file = Path(f.parent, f.stem + '.pickle')
        tally_output_pickle_path_list.append(path_to_pickle_file)
        tally_output = parse_tally_output_file(f, make_PandasDF=make_PandasDF,
                                               calculate_absolute_errors=calculate_absolute_errors,
                                               save_output_pickle=save_output_pickle,
                                               prefer_reading_existing_pickle=prefer_reading_existing_pickle)
        if return_tally_output: tally_output_list.append(tally_output)

    if include_dump_files:
        for f in dump_filepaths_to_process:
            f = Path(f)
            parse_tally_dump_file(f, dump_data_number=dump_data_number, dump_data_sequence=dump_data_number,
                                  return_directional_info=dump_return_directional_info, use_degrees=dump_use_degrees,
                                  max_entries_read=dump_max_entries_read,
                                  return_namedtuple_list=False, return_Pandas_dataframe=False,
                                  save_namedtuple_list=dump_save_namedtuple_list,
                                  save_Pandas_dataframe=dump_save_Pandas_dataframe)

    if return_tally_output:
        return tally_output_list
    else:
        return tally_output_pickle_path_list


def fetch_MC_material(matid=None,matname=None,matsource=None,concentration_type=None,particle=None):
    '''
    Description:
        Returns a materials definition string formatted for use in PHITS or MCNP

    Dependencies:
        - `import os`
        - `import pickle`
        - PYTHONPATH environmental variable must be set and one entry must contain the directory
                which contains the vital "MC_materials/Compiled_MC_materials.pkl" file.

    Inputs:
       (required to enter `matid` OR `matname`, with `matid` taking priority if conflicting)

       - `matid` = ID number in the "Compiled_MC_materials" file
       - `matname` = exact name of material in "Compiled_MC_materials" file
       - `matsource` = exact source of material in "Compiled_MC_materials" file, only used when multiple
                materials have identical names
       - `concentration_type` = selection between `'weight fraction'` (default if no formula) and `'atom fraction'` (default if formula present) to be returned
       - `particle` = selection of whether natural (`'photons'`, default) or isotopic (`'neutrons'`) elements are used
                Note that if "enriched" or "depleted" appears in the material's name, particle=`'neutrons'` is set automatically.

    Outputs:
       - `mat_str` = string containing the material's information, ready to be inserted directly into a PHITS/MCNP input file
    '''
    import os
    import pickle
    if not matid and not matname:
        print('Either "matid" or "matname" MUST be defined')
        return None

    # First, locate and open materials library
    try:
        user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
        lib_file = None
        for i in user_paths:
            if 'phits_tools' in i.lower() or 'phits-tools' in i.lower():
                lib_file = i + r"\MC_materials\Compiled_MC_materials"
        if not lib_file:
            print('Could not find "PHITS_tools" folder in PYTHONPATH; this folder contains the vital "MC_materials/Compiled_MC_materials.pkl" file.')
    except KeyError:
        print('The PYTHONPATH environmental variable must be defined and contain the path to the directory holding "MC_materials/Compiled_MC_materials.pkl"')
        return None

    # Load materials library
    def load_obj(name ):
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)
    all_mats_list = load_obj(lib_file)

    if matid: # use mat ID number
        mi = int(matid)-1
        matname = all_mats_list[mi]['name']
    else: # use material name and possibly source too
        # determine material
        mi = None
        # first check for exact matches
        matching_mi = []
        for i in range(len(all_mats_list)):
            if all_mats_list[i]['name'].lower()==matname.lower():
                matching_mi.append(i)
        if len(matching_mi)==1:
            mi = matching_mi[0]
        elif len(matching_mi)>1:
            print('Found multiple materials with this identical matname value:')
            for mmi in matching_mi:
                print('\tmatid={}  matname="{}"  source="{}"'.format(str(mmi+1),all_mats_list[mmi]['name'],all_mats_list[mmi]['source']))
                if all_mats_list[mmi]['source'] and all_mats_list[mmi]['source']==matsource:
                    mi = mmi
                    print('\t\t^ matches inputed "matsource" and will be used')
            if mi==None:
                print('Please enter a "matsource" value identical to one of these two (or the matid).')
                return None
        else: # Exact material name not found
            # search for similar entries
            similar_mi = []
            for i in range(len(all_mats_list)):
                if matname.lower() in all_mats_list[i]['name'].lower():
                    similar_mi.append(i)
            if len(similar_mi)==0:
                print('No materials with that exact name or names containing "matname" were found.')
                return None
            elif len(similar_mi)==1:
                mi = similar_mi[0]
                print('Found one similar material (matid={}  matname="{}"  source="{}"); using it.'.format(str(mi+1),all_mats_list[mi]['name'],all_mats_list[mi]['source']))
            else:
                print('Found no material with exact "matname" but {} with similar names:'.format(len(similar_mi)))
                for smi in similar_mi:
                    print('\tmatid={}  matname="{}"  source="{}"'.format(str(smi+1),all_mats_list[smi]['name'],all_mats_list[smi]['source']))
                print('The first of these will be used.  If another material was desired, please enter its "matid" or exact "matname".')
                mi = similar_mi[0]

    # Now that material ID has been found, generate text entry
    mat = all_mats_list[mi]
    banner_width = 60
    cc = '$'  # comment character

    entry_text  = '\n'+cc+'*'*banner_width + '\n'
    entry_text += cc+'  {:<3d} : {} \n'.format(mi+1,mat['name'])
    if mat['source'] and mat['source']!='-':
        entry_text += cc+'  Source = {} \n'.format(mat['source'])
    if mat['formula'] and mat['formula']!='-':
        entry_text += cc+'  Formula = {} \n'.format(mat['formula'])
    if mat['molecular weight'] and mat['molecular weight']!='-':
        entry_text += cc+'  Molecular weight (g/mole) = {} \n'.format(mat['molecular weight'])
    if mat['density'] and mat['density']!='-':
        entry_text += cc+'  Density (g/cm3) = {} \n'.format(mat['density'])
    if mat['total atom density'] and mat['total atom density']!='-':
        if isinstance(mat['total atom density'],str):
            entry_text += cc+'  Total atom density (atoms/b-cm) = {} \n'.format(mat['total atom density'])
        else:
            entry_text += cc+'  Total atom density (atoms/b-cm) = {:<13.4E} \n'.format(mat['total atom density'])

    if concentration_type==None: # user did not select this, determine which is more appropriate automatically
        if mat['formula'] and mat['formula']!='-':
            concentration_type = 'atom fraction'
        else:
            concentration_type = 'weight fraction'

    entry_text += cc+'  Composition by {} \n'.format(concentration_type)

    # Determine if neutron or photon entry will be used
    neutron_keyword_list = ['depleted','enriched',' heu',' leu','uranium','plutonium','uranyl']
    if particle==None: # user did not select this, determine which is more appropriate automatically
        neutron_kw_found_in_name = False
        for nki in neutron_keyword_list:
            if nki in matname.lower():
                neutron_kw_found_in_name = True
        if neutron_kw_found_in_name:
            particle = 'neutrons'
        else:
            particle = 'photons'


    for j in range(len(mat[particle][concentration_type]['ZA'])):

        if isinstance(mat[particle][concentration_type]['value'][j],str):
            entry_format = '{:4}    {:>7}  {:13}   '+cc+'  {}'  + '\n'
        else:
            entry_format = '{:4}    {:>7d}  {:<13.6f}   '+cc+'  {}'  + '\n'

        if j==0:
            mstr = 'M{:<3}'.format(mi+1)
        else:
            mstr = ' '*4

        ZZZAAA = mat[particle][concentration_type]['ZA'][j]
        if ZZZAAA == '-':
            ZZZAAA = mat['photons'][concentration_type]['ZA'][j]

        Z = int(str(ZZZAAA)[:-3])
        A = str(ZZZAAA)[-3:]
        sym = Element_Z_to_Sym(Z)
        if A != '000':
            isotope = sym+'-'+A.lstrip('0')
        else:
            isotope = sym

        entry_text += entry_format.format(mstr,ZZZAAA,mat[particle][concentration_type]['value'][j],isotope)
    entry_text  += cc+'*'*banner_width + '\n'

    return entry_text

def tally(data, bin_edges=[], min_bin_left_edge=None, max_bin_right_edge=None, nbins=None, bin_width=None, divide_by_bin_width=False, normalization=None, scaling_factor=1, place_overflow_at_ends=True, return_uncertainties=False, return_event_indices_histogram=False):
    '''
    Description:
        Tally number of incidences of values falling within a desired binning structure

    Inputs:
        - `data` = list of values to be tallied/histogrammed
        - `bin_edges` = list of N+1 bin edge values for a tally of N bins
        - `min_bin_left_edge` = left/minimum edge value of the first bin
        - `max_bin_right_edge` = right/maximum edge value of the last bin
        - `nbins` = number of equally-sized bins to be created from `min_bin_left_edge` to `max_bin_right_edge`
        - `bin_width` = constant width of bins to be created from `min_bin_left_edge` to `max_bin_right_edge`
        - `divide_by_bin_width` = Boolean denoting whether final bin values are divided by their bin widths (D=`False`)
        - `normalization` = determine how the resulting histogram is normalized (D=`None`), options are:
                       `[None, 'unity-sum', 'unity-max-val']`.  If `None`, no additional normalization is done.
                       If `unity-sum`, the data is normalized such that its sum will be 1.  If `unity-max-val`, the
                       data is normalized such that the maximum value is 1.  The operation occurs after any bin
                       width normalization from `divide_by_bin_width` but before any scaling from `scaling_factor`.
        - `scaling_factor` = value which all final bins are multiplied/scaled by (D=`1`)
        - `place_overflow_at_ends` = handling of values outside of binning range (D=`True`); if `True` extreme
                       values are tallied in the first/last bin, if `False` extreme values are discarded
        - `return_uncertainties` = Boolean denoting if should return an extra N-length list whose elements
                       are the statistical uncertainties (square root w/ normalizations) of the tally bins (D=`False`)
        - `return_event_indices_histogram` = Boolean denoting if should return an extra N-length list whose elements
                       are each a list of the event indices corresponding to each bin (D=`False`)

    Notes:
        Regarding the binning structure, this function only needs to be provided `bin_edges` directly (takes priority)
        or the information needed to calculate `bin_edges`, that is: `min_bin_left_edge` and `max_bin_right_edge` and
        either `nbins` or `bin_width`.  (Priority is given to `nbins` if both are provided.)

    Outputs:
        - `tallied_hist` = N-length list of tallied data
        - `bin_edges` = list of N+1 bin edge values for a tally of N bins
        - `tallied_hist_err` = (optional) N-length list of statistical uncertainties of tallied data
        - `tallied_event_indicies` = (optional) N-length list of, for each bin, a list of the event indices populating it
    '''

    normalization_valid_entries = [None, 'unity-sum', 'unity-max-val']
    if normalization not in normalization_valid_entries:
        print("Entered normalization option of ",normalization," is not a valid option; please select from the following: [None, 'unity-sum', 'unity-max-val']".format())

    if len(bin_edges)!=0:
        bin_edges = np.array(bin_edges)
    else:
        if nbins != None:
            bin_edges = np.linspace(min_bin_left_edge,max_bin_right_edge,num=nbins+1)
        else:
            bin_edges = np.arange(min_bin_left_edge,max_bin_right_edge+bin_width,step=bin_width)

    nbins = len(bin_edges) - 1

    if return_event_indices_histogram:
        tallied_event_indicies = []
        tallied_hist = np.zeros(nbins)
        for i in range(nbins):
            tallied_event_indicies.append([])
        # events must be histogrammed manually
        for i, val in enumerate(data):
            if val < bin_edges[0]:
                if place_overflow_at_ends:
                    tallied_hist[0] += 1
                    tallied_event_indicies[0].append(i)
                continue
            if val > bin_edges[-1]:
                if place_overflow_at_ends:
                    tallied_hist[-1] += 1
                    tallied_event_indicies[-1].append(i)
                continue
            for j, be in enumerate(bin_edges):
                if be > val: # found right edge of bin containing val
                    tallied_hist[j-1] += 1
                    tallied_event_indicies[j-1].append(i)
                    break



    else:
        tallied_hist, bins = np.histogram(data,bins=bin_edges)

    if return_uncertainties:
        tallied_hist_err = np.sqrt(tallied_hist)
        if divide_by_bin_width: tallied_hist_err = tallied_hist_err/(bin_edges[1:]-bin_edges[:-1])
        if normalization=='unity-sum': tallied_hist_err = tallied_hist_err/np.sum(tallied_hist)
        if normalization=='unity-max-val': tallied_hist_err = tallied_hist_err/np.max(tallied_hist)
        if scaling_factor != 1: tallied_hist_err = tallied_hist_err*scaling_factor

    if divide_by_bin_width: tallied_hist = tallied_hist/(bin_edges[1:]-bin_edges[:-1])
    if normalization=='unity-sum': tallied_hist = tallied_hist/np.sum(tallied_hist)
    if normalization=='unity-max-val': tallied_hist = tallied_hist/np.max(tallied_hist)
    if scaling_factor != 1: tallied_hist = tallied_hist*scaling_factor

    if return_event_indices_histogram:
        if return_uncertainties:
            return tallied_hist,bin_edges,tallied_hist_err,tallied_event_indicies
        else:
            return tallied_hist,bin_edges,tallied_event_indicies
    else:
        if return_uncertainties:
            return tallied_hist,bin_edges,tallied_hist_err
        else:
            return tallied_hist,bin_edges





def rebinner(output_xbins,input_xbins,input_ybins):
    """
    Description:
        The purpose of this function is to rebin a set of y values corresponding to a set of x bins to a new set of x bins.
        The function seeks to be as generalized as possible, meaning bin sizes do not need to be consistent.

    Dependencies:
        `import numpy as np`

    Inputs:
      - `output_xbins` = output array containing bounds of x bins of length N; first entry is leftmost bin boundary
      - `input_xbins`  = input array containing bounds of x bins of length M; first entry is leftmost bin boundary
      - `input_ybins`  = input array containing y values of length M-1

    Outputs:
      - `output_ybins` = output array containing y values of length N-1
    """

    N = len(output_xbins)
    M = len(input_xbins)
    output_ybins = np.zeros(N-1)

    for i in range(0,N-1):
        # For each output bin
        lxo = output_xbins[i]   # lower x value of output bin
        uxo = output_xbins[i+1] # upper x value of output bin
        dxo = uxo - lxo         # width of current x output bin

        # Scan input x bins to see if any fit in this output bin
        for j in range(0,M-1):
            lxi = input_xbins[j]    # lower x value of input bin
            uxi = input_xbins[j+1]  # upper x value of input bin
            dxi = uxi - lxi         # width of current x input bin

            if uxi<lxo or lxi>uxo:
                # no bins are aligned
                continue
            elif lxi >= lxo and lxi < uxo:
                # start of an input bin occurs in this output bin
                if lxi >= lxo and uxi <= uxo:
                    # input bin completely encompassed by output bin
                    output_ybins[i] = output_ybins[i] + input_ybins[j]
                else:
                    # input bin spans over at least one output bin
                    # count fraction in current output x bin
                    f_in_dxo = (uxo-lxi)/dxi
                    output_ybins[i] = output_ybins[i] + f_in_dxo*input_ybins[j]
            elif lxi < lxo and uxi > uxo:
                # output bin is completely encompassed by input bin
                f_in_dxo = (uxo-lxo)/dxi
                output_ybins[i] = output_ybins[i] + f_in_dxo*input_ybins[j]
            elif lxi < lxo and uxi > lxo and uxi <= uxo:
                # tail of input bin is located in this output bin
                f_in_dxo = (uxi-lxo)/dxi
                output_ybins[i] = output_ybins[i] + f_in_dxo*input_ybins[j]

    return output_ybins

def is_number(n):
    '''
    Description:
        Determine if a string is that of a number or not.

    Inputs:
        - `n` = string to be tested

    Outputs:
        - `True` if value is a number (can be converted to float() without an error)
        - `False` otherwise
    '''
    try:
        float(n)
    except ValueError:
        return False
    return True


def ZZZAAAM_to_nuclide_plain_str(ZZZAAAM,include_Z=False,ZZZAAA=False,delimiter='-'):
    '''
    Description:
        Converts a plaintext string of a nuclide to an integer ZZZAAAM = 10000\*Z + 10\*A + M

    Dependencies:
        `Element_Z_to_Sym` (function within the "Hunter's tools" package)

    Input:
       - `ZZZAAAM` = integer equal to 10000*Z + 10*A + M, where M designates the metastable state (0=ground)
       - `include_Z` = Boolean denoting whether the Z number should be included in the output string (D=`False`)
       - `ZZZAAA` = Boolean denoting whether the input should be interpreted as a ZZZAAA value (1000Z+A) instead (D=`False`)
       - `delimiter` = string which will be used to separate elements of the output string (D=`-`)

    Output:
       - `nuc_str` = string describing the input nuclide formatted as [Z]-[Symbol]-[A][m]
    '''
    ZZZAAAM = int(ZZZAAAM)
    if ZZZAAA:
        ZZZAAAM = ZZZAAAM*10
    m = ZZZAAAM % 10
    A = (ZZZAAAM % 10000) // 10
    Z = ZZZAAAM // 10000
    symbol = Element_Z_to_Sym(Z)

    m_str = ''
    if m>0:
        m_str = 'm' + str(m)

    nuc_str = ''
    if include_Z:
        nuc_str += str(Z) + delimiter
    nuc_str += symbol + delimiter + str(A) + m_str

    return nuc_str


def nuclide_plain_str_to_latex_str(nuc_str,include_Z=False):
    '''
    Description:
        Converts a plaintext string of a nuclide to a LaTeX-formatted raw string
        Note: if you already have the Z, A, and isomeric state information determined, the "nuclide_to_Latex_form" function can be used instead

    Dependencies:
        - `Element_Z_to_Sym` (function within the "Hunter's tools" package) (only required if `include_Z = True`)

    Input:
        (required)

       - `nuc_str` = string to be converted; a huge variety of formats are supported, but they all must follow the following rules:
           + Isomeric/metastable state characters must always immediately follow the atomic mass characters.
               Isomeric state labels MUST either:
               - (1) be a single lower-case character OR
               - (2) begin with any non-numeric character and end with a number
           + Atomic mass numbers must be nonnegative integers OR the string `"nat"` (in which case no metastable states can be written)
           + Elemental symbols MUST begin with an upper-case character

    Input:
       (optional)

       - `include_Z` = `True`/`False` determining whether the nuclide's atomic number Z will be printed as a subscript beneath the atomic mass

    Output:
        - LaTeX-formatted raw string of nuclide
    '''
    tex_str = r''

    # remove unwanted characters from provided string
    delete_characters_list = [' ', '-', '_']
    for dc in delete_characters_list:
        nuc_str = nuc_str.replace(dc,'')

    # determine which characters are letters versus numbers
    isalpha_list = []
    isdigit_list = []
    for c in nuc_str:
        isalpha_list.append(c.isalpha())
        isdigit_list.append(c.isdigit())

    symbol = ''
    mass = ''
    isost = ''

    # string MUST begin with either mass number or elemental symbol
    if isdigit_list[0] or nuc_str[0:3]=='nat': # mass first
        mass_first = True
    else:
        mass_first = False

    if mass_first:
        if nuc_str[0:3]=='nat':
            mass = 'nat'
            ci = 3
        else:
            ci = 0
            while isdigit_list[ci]:
                mass += nuc_str[ci]
                ci += 1
            mass = str(int(mass)) # eliminate any extra leading zeros
            # encountered a non-numeric character, end of mass
            # now, determine if metastable state is listed or if element is listed next
            # first, check to see if any other numerals are in string
            lni = 0 # last numeral index
            for i in range(ci,len(nuc_str)):
                if isdigit_list[i]:
                    lni = i
            if lni != 0:
                # grab all characters between ci and last numeral as metastable state
                isost = nuc_str[ci:lni+1]
                ci = lni + 1
            else: # no more numerals in string, now check for single lower-case letter
                if isalpha_list[ci] and nuc_str[ci].islower():
                    isost = nuc_str[ci]
                    ci += 1

            # Now extract elemental symbol
            for i in range(ci,len(nuc_str)):
                if isalpha_list[i]:
                    symbol += nuc_str[i]

    else: # if elemental symbol is listed first
        if 'nat' in nuc_str:
            mass = 'nat'
            nuc_str = nuc_str.replace('nat','')

        ci = 0
        # Extract all characters before first number as the elemental symbol
        while nuc_str[ci].isalpha():
            symbol += nuc_str[ci]
            ci += 1

        # now, extract mass
        if mass != 'nat':
            while nuc_str[ci].isdigit():
                mass += nuc_str[ci]
                ci += 1
                if ci == len(nuc_str):
                    break

            # lastly, extract isomeric state, if present
            if ci != len(nuc_str):
                isost = nuc_str[ci:]

    # treating the cases of lowercase-specified particles (n, d, t, etc.)
    if symbol == '' and isost != '':
        symbol = isost
        isost = ''

    # Now assemble LaTeX string for nuclides
    if include_Z:
        if symbol == 'n':
            Z = 0
        elif symbol == 'p' or symbol == 'd' or symbol == 't':
            Z = 1
        else:
            Z = Element_Sym_to_Z(symbol)
        Z = str(int(Z))
        tex_str = r"$^{{{}{}}}_{{{}}}$".format(mass,isost,Z) + "{}".format(symbol)
    else:
        tex_str = r"$^{{{}{}}}$".format(mass,isost) + "{}".format(symbol)

    return tex_str


def Element_Z_to_Sym(Z):
    '''
    Description:
        Returns elemental symbol for a provided atomic number Z

    Inputs:
        - `Z` = atomic number

    Outputs:
        - `sym` = string of elemental symbol for element of atomic number Z
    '''
    elms = ["n ",\
            "H ","He","Li","Be","B ","C ","N ","O ","F ","Ne",\
            "Na","Mg","Al","Si","P ","S ","Cl","Ar","K ","Ca",\
            "Sc","Ti","V ","Cr","Mn","Fe","Co","Ni","Cu","Zn",\
            "Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y ","Zr",\
            "Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn",\
            "Sb","Te","I ","Xe","Cs","Ba","La","Ce","Pr","Nd",\
            "Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb",\
            "Lu","Hf","Ta","W ","Re","Os","Ir","Pt","Au","Hg",\
            "Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th",\
            "Pa","U ","Np","Pu","Am","Cm","Bk","Cf","Es","Fm",\
            "Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds",\
            "Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og"]
    i = int(Z)
    if i < 0 or i > len(elms):
        print('Z={} is not valid, please select a number from 0 to 118 (inclusive).'.format(str(Z)))
        return None
    return elms[i].strip()

def Element_Sym_to_Z(sym):
    '''
    Description:
        Returns atomic number Z for a provided elemental symbol

    Dependencies:
        `find` (function within the "Hunter's tools" package)

    Inputs:
        - `sym` = string of elemental symbol for element of atomic number Z

    Outputs:
        - `Z` = atomic number
    '''
    elms = ["n ",\
            "H ","He","Li","Be","B ","C ","N ","O ","F ","Ne",\
            "Na","Mg","Al","Si","P ","S ","Cl","Ar","K ","Ca",\
            "Sc","Ti","V ","Cr","Mn","Fe","Co","Ni","Cu","Zn",\
            "Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y ","Zr",\
            "Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn",\
            "Sb","Te","I ","Xe","Cs","Ba","La","Ce","Pr","Nd",\
            "Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb",\
            "Lu","Hf","Ta","W ","Re","Os","Ir","Pt","Au","Hg",\
            "Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th",\
            "Pa","U ","Np","Pu","Am","Cm","Bk","Cf","Es","Fm",\
            "Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds",\
            "Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og"]

    if len(sym.strip())>2:
        print('Please provide a valid elemental symbol (1 or 2 characters), {} is too long'.format(sym))
        return -1

    # handle exception for neutron first
    if sym.strip()=='XX':
        return 0

    # make sure string is formatted to match entries in elms list
    sym2 = sym.strip()
    if len(sym2)==1: sym2 += ' '
    sym2 = sym2[0].upper() + sym2[1].lower()

    Z = find(sym2,elms)

    if Z==None:
        print('Z could not be found for element "{}"; please make sure entry is correct.'.format(sym))
        return -1

    return Z

def find(target, myList):
    '''
    Description:
        Search for and return the index of the first occurance of a value in a list.

    Inputs:
        - `target` = value to be searched for
        - `myList` = list of values

    Output:
        - index of first instance of `target` in `myList`
    '''
    for i in range(len(myList)):
        if myList[i] == target:
            return i

def ICRP116_effective_dose_coeff(E=1.0,particle='photon',geometry='AP',interp_scale='log',interp_type='cubic',extrapolation_on=False):
    '''
    Description:
        For a given particle at a given energy in a given geometry, returns its
        effective dose conversion coefficient from ICRP 116

    Dependencies:
        - `import numpy as np`
        - `from scipy.interpolate import CubicSpline, lagrange, interp1d`
        - `find` (function within the "PHITS Tools" package)

    Inputs:
       - `E` = energy of the particle in MeV (D=`1`)
       - `particle` = select particle (D=`'photon'`, options include: `['photon', 'electron', 'positron' ,'neutron' ,'proton', 'negmuon', 'posmuon', 'negpion', 'pospion', 'He3ion']`)
       - `geometry` = geometric arrangement (D=`'AP'`, options include: `['AP', 'PA', 'LLAT', 'RLAT', 'ROT', 'ISO', 'H*(10)']` (`'LLAT'`,`'RLAT'`,`'ROT'` only available for photon, proton, and neutron))
              - Meanings:
               AP, antero-posterior; PA, postero-anterior; LLAT, left lateral; RLAT, right lateral; ROT, rotational; ISO, isotropic.
              - Note: `'H*(10)'` ambient dose equivalent is available for photons only
       - `interp_scale` = interpolation scale (D=`'log'` to interpolate on a log scale, options include: `['log','lin']`, ICRP 74/116 suggest log-log cubic interpolation)
       - `interp_type`  = interpolation method (D=`'cubic'` to interpolate with a cubic spline, options include: `['cubic','linear']`, ICRP 74/116 suggest log-log cubic interpolation)
                                              technically, any options available for scipy.interpolate.interp1d() can be used: `['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous']`
       - `extrapolation_on` = boolean designating whether values outside of the tabulated energies will be extrapolated (D=`False`)

             |                      |                                                                       |
             | -------------------- | --------------------------------------------------------------------- |
             | if False & E < E_min | f(E) = 0                                                              |
             | if False & E > E_max | f(E) = f(E_max)                                                       |
             | if True  & E < E_min | f(E) is linearly interpolated between (0,0) and (E_min,f(E_min))      |
             | if True  & E > E_max | f(E) is extrapolated using the specified interpolation scale and type |
    Outputs:
       - `f` = effective dose conversion coefficient in pSv*cm^2
    '''
    import numpy as np
    from scipy.interpolate import CubicSpline, lagrange, interp1d

    pars_list = ['photon','electron','positron','neutron','proton','negmuon','posmuon','negpion','pospion','He3ion']
    geo_list_all = ['AP','PA','LLAT','RLAT','ROT','ISO','H*(10)']
    geo_list_short = ['AP','PA','ISO']

    if particle not in pars_list or geometry not in geo_list_all:
        pstr = 'Please select a valid particle and geometry.\n'
        pstr += "Particle selected = {}, options include: ['photon','electron','positron','neutron','proton','negmuon','posmuon','negpion','pospion','He3ion']".format(particle)
        pstr += "Geometry selected = {}, options include: ['AP','PA','LLAT','RLAT','ROT','ISO'] ('LLAT','RLAT','ROT' only available for photon, proton, and neutron)"
        print(pstr)
        return None

    if (particle not in ['photon','neutron','proton'] and geometry in ['LLAT','RLAT','ROT']) or (particle!='photon' and geometry=='H*(10)'):
        if (particle!='photon' and geometry=='H*(10)'):
            pstr = "geometry = {} is only available for photons\n".format(geometry)
        else:
            pstr = "geometry = {} is only available for photon, neutron, and proton\n".format(geometry)
            pstr += "For selected particle = {}, please choose geometry from ['AP','PA','ISO']".format(particle)
        print(pstr)
        return None

    E_photon = [0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.511, 0.6, 0.662, 0.8, 1, 1.117, 1.33, 1.5, 2, 3, 4, 5, 6, 6.129, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    f_photon = [
    [0.0685, 0.156, 0.225, 0.313, 0.351, 0.37, 0.39, 0.413, 0.444, 0.519, 0.748, 1, 1.51, 2, 2.47, 2.52, 2.91, 3.17, 3.73, 4.49, 4.9, 5.59, 6.12, 7.48, 9.75, 11.7, 13.4, 15, 15.1, 17.8, 20.5, 26.1, 30.8, 37.9, 43.1, 47.1, 50.1, 54.5, 57.8, 63.3, 67.3, 72.3, 75.5, 77.5, 78.9, 80.5, 81.7, 83.8, 85.2, 86.9, 88.1, 88.9, 89.5, 90.2, 90.7],
    [0.0184, 0.0155, 0.026, 0.094, 0.161, 0.208, 0.242, 0.271, 0.301, 0.361, 0.541, 0.741, 1.16, 1.57, 1.98, 2.03, 2.38, 2.62, 3.13, 3.83, 4.22, 4.89, 5.39, 6.75, 9.12, 11.2, 13.1, 15, 15.2, 18.6, 22, 30.3, 38.2, 51.4, 62, 70.4, 76.9, 86.6, 93.2, 104, 111, 119, 124, 128, 131, 135, 138, 142, 145, 148, 150, 152, 153, 155, 155],
    [0.0189, 0.0416, 0.0655, 0.11, 0.14, 0.16, 0.177, 0.194, 0.214, 0.259, 0.395, 0.552, 0.888, 1.24, 1.58, 1.62, 1.93, 2.14, 2.59, 3.23, 3.58, 4.2, 4.68, 5.96, 8.21, 10.2, 12, 13.7, 13.9, 17, 20.1, 27.4, 34.4, 47.4, 59.2, 69.5, 78.3, 92.4, 103, 121, 133, 148, 158, 165, 170, 178, 183, 193, 198, 206, 212, 216, 219, 224, 228],
    [0.0182, 0.039, 0.0573, 0.0891, 0.114, 0.133, 0.15, 0.167, 0.185, 0.225, 0.348, 0.492, 0.802, 1.13, 1.45, 1.49, 1.78, 1.98, 2.41, 3.03, 3.37, 3.98, 4.45, 5.7, 7.9, 9.86, 11.7, 13.4, 13.6, 16.6, 19.7, 27.1, 34.4, 48.1, 60.9, 72.2, 82, 97.9, 110, 130, 143, 161, 172, 180, 186, 195, 201, 212, 220, 229, 235, 240, 244, 251, 255],
    [0.0337, 0.0664, 0.0986, 0.158, 0.199, 0.226, 0.248, 0.273, 0.297, 0.355, 0.528, 0.721, 1.12, 1.52, 1.92, 1.96, 2.3, 2.54, 3.04, 3.72, 4.1, 4.75, 5.24, 6.55, 8.84, 10.8, 12.7, 14.4, 14.6, 17.6, 20.6, 27.7, 34.4, 46.1, 56, 64.4, 71.2, 82, 89.7, 102, 111, 121, 128, 133, 136, 142, 145, 152, 156, 161, 165, 168, 170, 172, 175],
    [0.0288, 0.056, 0.0812, 0.127, 0.158, 0.18, 0.199, 0.218, 0.239, 0.287, 0.429, 0.589, 0.932, 1.28, 1.63, 1.67, 1.97, 2.17, 2.62, 3.25, 3.6, 4.2, 4.66, 5.9, 8.08, 10, 11.8, 13.5, 13.7, 16.6, 19.6, 26.8, 33.8, 46.1, 56.9, 66.2, 74.1, 87.2, 97.5, 116, 130, 147, 159, 168, 174, 185, 193, 208, 218, 232, 243, 251, 258, 268, 276],
    [0.061, 0.83, 1.05, 0.81, 0.64, 0.55, 0.51, 0.52, 0.53, 0.61, 0.89, 1.20, 1.80, 2.38, 2.93, 2.99, 3.44, 3.73, 4.38, 5.20, 5.60, 6.32, 6.90, 8.60, 11.10, 13.40, 15.50, 17.60, 17.86, 21.60, 25.60, 8.53, 8.29, 8.23, 8.26, 8.64, 8.71, 8.86, 9.00, 9.60, 10.20, 10.73, 11.27, 11.80, 11.78, 11.74, 11.70, 11.60, 11.50, 12.10, 12.70, 13.30, 13.08, 12.64, 12.20]
    ]

    E_electron = [0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    f_electron = [
    [0.0269, 0.0404, 0.0539, 0.081, 0.108, 0.135, 0.163, 0.218, 0.275, 0.418, 0.569, 0.889, 1.24, 1.63, 2.05, 4.04, 7.1, 15, 22.4, 36.1, 48.2, 59.3, 70.6, 97.9, 125, 188, 236, 302, 329, 337, 341, 346, 349, 355, 359, 365, 369, 372, 375, 379, 382, 387, 391, 397, 401, 405, 407, 411, 414],
    [0.0268, 0.0402, 0.0535, 0.0801, 0.107, 0.133, 0.16, 0.213, 0.267, 0.399, 0.53, 0.787, 1.04, 1.28, 1.5, 1.68, 1.68, 1.62, 1.62, 1.95, 2.62, 3.63, 5.04, 9.46, 18.3, 53.1, 104, 220, 297, 331, 344, 358, 366, 379, 388, 399, 408, 414, 419, 428, 434, 446, 455, 468, 477, 484, 490, 499, 507],
    [0.0188, 0.0283, 0.0377, 0.0567, 0.0758, 0.0948, 0.114, 0.152, 0.191, 0.291, 0.393, 0.606, 0.832, 1.08, 1.35, 1.97, 2.76, 4.96, 7.24, 11.9, 16.4, 21, 25.5, 35.5, 46.7, 76.9, 106, 164, 212, 249, 275, 309, 331, 363, 383, 410, 430, 445, 457, 478, 495, 525, 549, 583, 608, 628, 646, 675, 699]
    ]

    E_positron = [0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    f_positron = [
    [3.28, 3.29, 3.3, 3.33, 3.36, 3.39, 3.42, 3.47, 3.53, 3.67, 3.84, 4.16, 4.52, 4.9, 5.36, 7.41, 10.5, 18.3, 25.7, 39.1, 51, 61.7, 72.9, 99, 126, 184, 229, 294, 320, 327, 333, 339, 342, 349, 354, 362, 366, 369, 372, 376, 379, 385, 389, 395, 399, 402, 404, 408, 411],
    [1.62, 1.64, 1.65, 1.68, 1.71, 1.73, 1.76, 1.82, 1.87, 2.01, 2.14, 2.4, 2.65, 2.9, 3.12, 3.32, 3.37, 3.44, 3.59, 4.19, 5.11, 6.31, 8.03, 14, 23.6, 59, 111, 221, 291, 321, 334, 349, 357, 371, 381, 393, 402, 409, 415, 424, 430, 443, 451, 465, 473, 480, 486, 495, 503],
    [1.39, 1.4, 1.41, 1.43, 1.45, 1.47, 1.49, 1.53, 1.57, 1.67, 1.77, 1.98, 2.21, 2.45, 2.72, 3.38, 4.2, 6.42, 8.7, 13.3, 18, 22.4, 26.9, 36.7, 47.6, 75.5, 104, 162, 209, 243, 268, 302, 323, 356, 377, 405, 425, 440, 453, 474, 491, 522, 545, 580, 605, 627, 645, 674, 699]
    ]

    E_neutron = [1.00E-09, 1.00E-08, 2.50E-08, 1.00E-07, 2.00E-07, 5.00E-07, 1.00E-06, 2.00E-06, 5.00E-06, 1.00E-05, 2.00E-05, 5.00E-05, 1.00E-04, 2.00E-04, 5.00E-04, 0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 0.9, 1, 1.2, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 30, 50, 75, 100, 130, 150, 180, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 5000, 10000]
    f_neutron = [
    [3.09, 3.55, 4, 5.2, 5.87, 6.59, 7.03, 7.39, 7.71, 7.82, 7.84, 7.82, 7.79, 7.73, 7.54, 7.54, 7.61, 7.97, 9.11, 12.2, 15.7, 23, 30.6, 41.9, 60.6, 78.8, 114, 177, 232, 279, 301, 330, 365, 407, 458, 483, 494, 498, 499, 499, 500, 500, 499, 495, 493, 490, 484, 477, 474, 453, 433, 420, 402, 382, 373, 363, 359, 363, 389, 422, 457, 486, 508, 524, 537, 612, 716, 933],
    [1.85, 2.11, 2.44, 3.25, 3.72, 4.33, 4.73, 5.02, 5.3, 5.44, 5.51, 5.55, 5.57, 5.59, 5.6, 5.6, 5.62, 5.95, 6.81, 8.93, 11.2, 15.7, 20, 25.9, 34.9, 43.1, 58.1, 85.9, 112, 136, 148, 167, 195, 235, 292, 330, 354, 371, 383, 392, 398, 404, 412, 417, 419, 420, 422, 423, 423, 422, 428, 439, 444, 446, 446, 447, 448, 464, 496, 533, 569, 599, 623, 640, 654, 740, 924, 1.17E+03],
    [1.04, 1.15, 1.32, 1.7, 1.94, 2.21, 2.4, 2.52, 2.64, 2.65, 2.68, 2.66, 2.65, 2.66, 2.62, 2.61, 2.6, 2.74, 3.13, 4.21, 5.4, 7.91, 10.5, 14.4, 20.8, 27.2, 39.7, 63.7, 85.5, 105, 115, 130, 150, 179, 221, 249, 269, 284, 295, 303, 310, 316, 325, 333, 336, 338, 343, 347, 348, 360, 380, 399, 409, 416, 420, 425, 427, 441, 472, 510, 547, 579, 603, 621, 635, 730, 963, 1.23E+03],
    [0.893, 0.978, 1.12, 1.42, 1.63, 1.86, 2.02, 2.11, 2.21, 2.24, 2.26, 2.24, 2.23, 2.24, 2.21, 2.21, 2.2, 2.33, 2.67, 3.6, 4.62, 6.78, 8.95, 12.3, 17.9, 23.4, 34.2, 54.4, 72.6, 89.3, 97.4, 110, 128, 153, 192, 220, 240, 255, 267, 276, 284, 290, 301, 310, 313, 317, 323, 328, 330, 345, 370, 392, 404, 413, 418, 425, 429, 451, 483, 523, 563, 597, 620, 638, 651, 747, 979, 1.26E+03],
    [1.7, 2.03, 2.31, 2.98, 3.36, 3.86, 4.17, 4.4, 4.59, 4.68, 4.72, 4.73, 4.72, 4.67, 4.6, 4.58, 4.61, 4.86, 5.57, 7.41, 9.46, 13.7, 18, 24.3, 34.7, 44.7, 63.8, 99.1, 131, 160, 174, 193, 219, 254, 301, 331, 351, 365, 374, 381, 386, 390, 395, 398, 398, 399, 399, 398, 398, 395, 395, 402, 406, 411, 414, 418, 422, 443, 472, 503, 532, 558, 580, 598, 614, 718, 906, 1.14E+03],
    [1.29, 1.56, 1.76, 2.26, 2.54, 2.92, 3.15, 3.32, 3.47, 3.52, 3.54, 3.55, 3.54, 3.52, 3.47, 3.46, 3.48, 3.66, 4.19, 5.61, 7.18, 10.4, 13.7, 18.6, 26.6, 34.4, 49.4, 77.1, 102, 126, 137, 153, 174, 203, 244, 271, 290, 303, 313, 321, 327, 332, 339, 344, 346, 347, 350, 352, 353, 358, 371, 387, 397, 407, 412, 421, 426, 455, 488, 521, 553, 580, 604, 624, 642, 767, 1.01E+03, 1.32E+03]
    ]

    E_proton = [1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    f_proton = [
    [5.46, 8.2, 10.9, 16.4, 21.9, 27.3, 32.8, 43.7, 54.9, 189, 428, 750, 1.02E+03, 1.18E+03, 1.48E+03, 2.16E+03, 2.51E+03, 2.38E+03, 1.77E+03, 1.38E+03, 1.23E+03, 1.15E+03, 1.16E+03, 1.11E+03, 1.09E+03, 1.15E+03, 1.12E+03, 1.23E+03, 1.27E+03, 1.23E+03, 1.37E+03, 1.45E+03, 1.41E+03],
    [5.47, 8.21, 10.9, 16.4, 21.9, 27.3, 32.8, 43.7, 54.6, 56.1, 43.6, 36.1, 45.5, 71.5, 156, 560, 1.19E+03, 2.82E+03, 1.93E+03, 1.45E+03, 1.30E+03, 1.24E+03, 1.23E+03, 1.23E+03, 1.23E+03, 1.25E+03, 1.28E+03, 1.34E+03, 1.40E+03, 1.45E+03, 1.53E+03, 1.65E+03, 1.74E+03],
    [2.81, 4.21, 5.61, 8.43, 11.2, 14, 16.8, 22.4, 28.1, 50.7, 82.8, 180, 290, 379, 500, 799, 994, 1.64E+03, 2.15E+03, 1.44E+03, 1.27E+03, 1.21E+03, 1.20E+03, 1.19E+03, 1.18E+03, 1.21E+03, 1.25E+03, 1.32E+03, 1.31E+03, 1.39E+03, 1.44E+03, 1.56E+03, 1.63E+03],
    [2.81, 4.2, 5.62, 8.41, 11.2, 14, 16.8, 22.4, 28.1, 48.9, 78.8, 172, 278, 372, 447, 602, 818, 1.46E+03, 2.18E+03, 1.45E+03, 1.28E+03, 1.21E+03, 1.20E+03, 1.20E+03, 1.20E+03, 1.23E+03, 1.25E+03, 1.32E+03, 1.33E+03, 1.41E+03, 1.45E+03, 1.59E+03, 1.67E+03],
    [4.5, 6.75, 8.98, 13.4, 17.8, 22.1, 26.3, 34.5, 50.1, 93.7, 165, 296, 422, 532, 687, 1.09E+03, 1.44E+03, 2.16E+03, 1.96E+03, 1.44E+03, 1.28E+03, 1.22E+03, 1.22E+03, 1.20E+03, 1.19E+03, 1.23E+03, 1.23E+03, 1.30E+03, 1.29E+03, 1.35E+03, 1.41E+03, 1.49E+03, 1.56E+03],
    [3.52, 5.28, 7.02, 10.5, 13.9, 17.3, 20.5, 26.8, 45.8, 80.1, 136, 249, 358, 451, 551, 837, 1.13E+03, 1.79E+03, 1.84E+03, 1.42E+03, 1.25E+03, 1.18E+03, 1.17E+03, 1.17E+03, 1.15E+03, 1.21E+03, 1.22E+03, 1.31E+03, 1.40E+03, 1.43E+03, 1.57E+03, 1.71E+03, 1.78E+03]
    ]

    E_negmuon = [1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    f_negmuon = [
    [180, 180, 184, 188, 193, 205, 242, 293, 332, 414, 465, 657, 735, 755, 628, 431, 382, 340, 326, 319, 320, 321, 325, 327, 333, 331, 333, 336, 337, 337, 337, 337, 338],
    [75.2, 76.8, 78.3, 81.4, 84.8, 87.7, 86.7, 86.8, 88.6, 100, 122, 251, 457, 703, 775, 485, 402, 345, 329, 321, 321, 324, 326, 332, 337, 338, 341, 344, 345, 346, 346, 347, 347],
    [78.7, 79.5, 80.9, 83.7, 87.1, 91.5, 98.1, 113, 127, 161, 191, 275, 363, 446, 496, 498, 432, 354, 332, 321, 321, 323, 326, 331, 337, 338, 341, 344, 346, 347, 347, 348, 348]
    ]

    E_posmuon = [1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    f_posmuon = [
    [194, 196, 198, 202, 207, 216, 251, 300, 340, 425, 481, 674, 751, 768, 635, 431, 381, 339, 326, 318, 319, 320, 322, 325, 327, 331, 333, 336, 337, 337, 337, 337, 339],
    [82.6, 84.1, 85.7, 88.9, 92.1, 94.3, 92.5, 92.8, 94.8, 108, 133, 265, 473, 721, 787, 483, 399, 345, 328, 320, 321, 323, 325, 330, 333, 339, 341, 344, 345, 346, 346, 347, 347],
    [85.2, 86.2, 87.5, 90.3, 93.6, 97.7, 103, 117, 132, 167, 199, 284, 373, 456, 506, 502, 432, 354, 332, 320, 320, 322, 324, 329, 333, 338, 341, 344, 346, 347, 347, 348, 348]
    ]

    E_negpion = [1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 80000, 100000, 150000, 200000]
    f_negpion = [
    [406, 422, 433, 458, 491, 528, 673, 965, 1.09E+03, 1.25E+03, 1.28E+03, 1.77E+03, 1.92E+03, 1.93E+03, 1.68E+03, 1.14E+03, 995, 927, 902, 848, 844, 869, 901, 947, 977, 1.03E+03, 1.05E+03, 1.03E+03, 1.03E+03, 1.06E+03, 1.09E+03, 1.14E+03, 1.17E+03, 1.21E+03, 1.24E+03, 1.30E+03, 1.35E+03, 1.39E+03, 1.42E+03, 1.48E+03, 1.54E+03, 1.67E+03, 1.78E+03],
    [194, 201, 210, 225, 233, 237, 208, 181, 178, 197, 244, 547, 1.02E+03, 1.70E+03, 1.99E+03, 1.31E+03, 991, 889, 871, 843, 850, 880, 917, 976, 1.02E+03, 1.08E+03, 1.12E+03, 1.11E+03, 1.13E+03, 1.18E+03, 1.22E+03, 1.29E+03, 1.34E+03, 1.41E+03, 1.47E+03, 1.56E+03, 1.63E+03, 1.70E+03, 1.75E+03, 1.86E+03, 1.95E+03, 2.15E+03, 2.33E+03],
    [176, 189, 198, 215, 232, 251, 271, 317, 361, 439, 508, 676, 868, 1.02E+03, 1.15E+03, 1.15E+03, 1.03E+03, 857, 815, 794, 807, 838, 875, 935, 979, 1.05E+03, 1.09E+03, 1.11E+03, 1.15E+03, 1.20E+03, 1.26E+03, 1.36E+03, 1.43E+03, 1.55E+03, 1.64E+03, 1.79E+03, 1.91E+03, 2.02E+03, 2.11E+03, 2.29E+03, 2.46E+03, 2.80E+03, 3.04E+03]
    ]

    E_pospion = [1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 80000, 100000, 150000, 200000]
    f_pospion = [
    [314, 324, 340, 379, 429, 489, 540, 717, 819, 1000, 1.10E+03, 1.52E+03, 1.75E+03, 1.83E+03, 1.66E+03, 1.22E+03, 1.13E+03, 1.22E+03, 1.25E+03, 1.07E+03, 969, 943, 952, 999, 1.04E+03, 1.10E+03, 1.10E+03, 1.06E+03, 1.06E+03, 1.07E+03, 1.10E+03, 1.14E+03, 1.17E+03, 1.22E+03, 1.25E+03, 1.30E+03, 1.34E+03, 1.38E+03, 1.42E+03, 1.48E+03, 1.54E+03, 1.67E+03, 1.78E+03],
    [121, 125, 133, 151, 170, 183, 185, 177, 179, 201, 247, 494, 906, 1.48E+03, 1.82E+03, 1.38E+03, 1.12E+03, 1.15E+03, 1.23E+03, 1.10E+03, 998, 970, 980, 1.04E+03, 1.09E+03, 1.16E+03, 1.19E+03, 1.16E+03, 1.16E+03, 1.20E+03, 1.24E+03, 1.31E+03, 1.35E+03, 1.42E+03, 1.48E+03, 1.57E+03, 1.64E+03, 1.70E+03, 1.75E+03, 1.84E+03, 1.94E+03, 2.14E+03, 2.33E+03],
    [151, 160, 168, 183, 198, 216, 233, 265, 296, 367, 439, 602, 787, 953, 1.09E+03, 1.16E+03, 1.10E+03, 1.05E+03, 1.08E+03, 1.02E+03, 953, 930, 938, 993, 1.05E+03, 1.13E+03, 1.16E+03, 1.16E+03, 1.18E+03, 1.23E+03, 1.28E+03, 1.37E+03, 1.43E+03, 1.55E+03, 1.64E+03, 1.79E+03, 1.90E+03, 2.01E+03, 2.10E+03, 2.27E+03, 2.42E+03, 2.76E+03, 3.07E+03]
    ]

    E_He3ion = [1, 2, 3, 5, 10, 14, 20, 30, 50, 75, 100, 150, 200, 300, 500, 700, 1000, 2000, 3000, 5000, 10000, 20000, 50000, 100000]
    f_He3ion = [
    [219, 438, 656, 1.09E+03, 2.19E+03, 4.61E+03, 1.72E+04, 3.01E+04, 4.75E+04, 8.05E+04, 1.01E+05, 9.25E+04, 6.74E+04, 5.14E+04, 4.27E+04, 4.11E+04, 4.00E+04, 4.02E+04, 4.08E+04, 4.12E+04, 4.56E+04, 5.12E+04, 6.12E+04, 7.14E+04],
    [219, 438, 657, 1.09E+03, 2.19E+03, 2.56E+03, 1.74E+03, 1.44E+03, 2.88E+03, 1.75E+04, 4.84E+04, 1.10E+05, 7.29E+04, 5.33E+04, 4.49E+04, 4.60E+04, 4.47E+04, 4.80E+04, 5.01E+04, 5.17E+04, 6.26E+04, 6.10E+04, 8.14E+04, 1.01E+05],
    [141, 281, 419, 689, 1.82E+03, 2.81E+03, 5.46E+03, 9.86E+03, 1.78E+04, 3.00E+04, 4.55E+04, 6.95E+04, 7.01E+04, 5.25E+04, 4.27E+04, 4.19E+04, 4.09E+04, 4.31E+04, 4.50E+04, 4.76E+04, 5.73E+04, 7.10E+04, 9.67E+04, 1.24E+05]
    ]


    E_all = [E_photon, E_electron, E_positron, E_neutron, E_proton, E_negmuon, E_posmuon, E_negpion, E_pospion, E_He3ion]
    f_all = [f_photon, f_electron, f_positron, f_neutron, f_proton, f_negmuon, f_posmuon, f_negpion, f_pospion, f_He3ion]

    pi = find(particle, pars_list)
    if particle in ['photon','neutron','proton']:
        gi = find(geometry, geo_list_all)
    else:
        gi = find(geometry, geo_list_short)

    E_list = E_all[pi]
    f_list = f_all[pi][gi]

    # Interpolate f given E
    if E in E_list:
        f = f_list[find(E,E_list)]
    else:
        if not extrapolation_on and (E < E_list[0] or E > E_list[-1]):  # E is outside of bounds and extrapolation is off
            if E < E_list[0]:
                f = 0   # assume negligibly low energy particle
            if E > E_list[-1]:
                f = f_list[-1]  # just set equal to max energy particle's coefficient
        else:
            if E < E_list[0]:
                E_list = [0] + E_list
                f_list = [0] + f_list
                interp_scale = 'linear'

            if interp_scale=='log':
                cs = interp1d(np.log10(np.array(E_list)),np.log10(np.array(f_list)), kind=interp_type,fill_value='extrapolate')
                f = 10**cs(np.log10(E))
            else:
                cs = interp1d(np.array(E_list),np.array(f_list), kind=interp_type,fill_value='extrapolate')
                f = cs(E)

            # for sake of sanity, return zero for values quite below minimum coefficients
            if f < 1e-4:
                f = 0.0


        #if interp_type=='cubic':
        #    if interp_scale=='log':
        #        cs = interp1d(np.log10(np.array(E_list)),np.log10(np.array(f_list)), kind='cubic',fill_value='extrapolate')
        #        f = 10**cs(np.log10(E))
        #    else:
        #        cs = interp1d(np.array(E_list),np.array(f_list), kind='cubic',fill_value='extrapolate')
        #        f = cs(E)
        #else:
        #    if interp_scale=='log':
        #        f = 10**np.interp(np.log10(E),np.log10(np.array(E_list)),np.log10(np.array(f_list)))
        #    else:
        #        f = np.interp(E,np.array(E_list),np.array(f_list))

        #if interp_type=='cubic':
        #    if interp_scale=='log':
        #        cs = lagrange(np.log10(np.array(E_list)),np.log10(np.array(f_list)))
        #        f = 10**cs(np.log10(E))
        #    else:
        #        cs = lagrange(np.array(E_list),np.array(f_list))
        #        f = cs(E)
        #if interp_type=='cubic':
        #    if interp_scale=='log':
        #        cs = CubicSpline(np.log10(np.array(E_list)),np.log10(np.array(f_list)))
        #        f = 10**cs(np.log10(E))
        #    else:
        #        cs = CubicSpline(np.array(E_list),np.array(f_list))
        #        f = cs(E)

    return f

def split_into_header_and_content(output_file_path):
    '''
    Description:
        Initial parsing of a PHITS tally output file to isolate its header section (containing metadata) and main
        tally results "content" section for later processing.

    Inputs:
        - `output_file_path` = path to a PHITS tally output file

    Outputs:
        - `header` = list of lines belonging to the tally output's header section
        - `content` = list of lists of remaining lines after the tally output's header section; the top level list is
                broken into "blocks" ("newpage:"-separated) which are lists of lines belonging to each block/page.

    '''
    in_content = False
    header, content = [], [[]]
    with open(output_file_path, mode='rb') as f:
        for line in f:
            if b'\x00' in line:
                line = line.replace(b"\x00", b"")
            line = line.decode()
            #if "\x00" in line: line = line.replace("\x00", "")
            if '#newpage:' in line:
                in_content = True
                continue
            if in_content:
                if 'newpage:' in line:
                    content.append([])
                    continue
                content[-1].append(line.strip())
            else:
                header.append(line.strip())
    # add "footer" to peel off last bit of "content" section?
    return header, content




def extract_data_from_header_line(line):
    '''
    Description:
        Extract a "key" and its corresponding value from a PHITS tally output header line

    Dependencies:
        - `is_number` (function within the "PHITS tools" package)

    Inputs:
        - `line` = string to be processed

    Outputs:
        - `key` = a string "key" to become a key in the metadata dictionary
        - `value` = corresponding value they "key" is equal to; dtype is string, int, or float
    '''
    if '#' in line:
        info, trash = line.split('#',1)
    else:
        info = line
    key, value = info.split('=')
    key = key.strip()
    value = value.strip()
    if is_number(value):
        if '.' in value:
            value = float(value)
        else:
            value = int(value)
    return key, value

def data_row_to_num_list(line):
    '''
    Description:
        Extract numeric values from line of text from PHITS tally output content section

    Dependencies:
        - `is_number` (function within the "PHITS tools" package)

    Inputs:
        - `line` = string to be processed

    Outputs:
        - `values` = a list of ints and/or floats of numeric values in `line`
    '''
    value_strs = line.strip().split()
    values = []
    for value in value_strs:
        if is_number(value):
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        values.append(value)
    return values



def parse_group_string(text):
    '''
    Description:
        Separate "groups" in a string, wherein a group is a standalone value or a series of values inside parentheses.

    Inputs:
        - `text` = string to be processed

    Outputs:
        - `groups` = a list of strings extracted from `text`
    '''
    # returns list of items from PHITS-formatted string, e.g. w/ ()
    parts = text.strip().split()
    #print(parts)
    groups = []
    curly_vals = []
    in_brackets_group = False
    in_curly_brace_group = False
    num_group_members = 0
    for i in parts:
        if '(' in i and ')' in i:
            in_brackets_group = False
            groups.append(i)
        elif '(' in i:
            in_brackets_group = True
            groups.append(i)
        elif ')' in i:
            in_brackets_group = False
            num_group_members = 0
            groups[-1] += i
        elif '{' in i:
            in_curly_brace_group = True
            curly_vals = []
        elif '}' in i:
            in_curly_brace_group = False
            curly_int_strs = [str(j) for j in range(int(curly_vals[0]), int(curly_vals[-1])+1)]
            curly_vals = []
            groups += curly_int_strs
        else:
            if in_brackets_group or in_curly_brace_group:
                if in_brackets_group:
                    if num_group_members>0: groups[-1] += ' '
                    groups[-1] += i
                    num_group_members += 1
                if in_curly_brace_group:
                    if i != '-':
                        curly_vals.append(i)
            else:
                groups.append(i)
    #print(groups)
    return groups

def parse_tally_header(tally_header,tally_content):
    '''
    Description:
        Extracts metadata from PHITS tally output header (and some extra info from its contents section)

    Dependencies:
        - `extract_data_from_header_line` (function within the "PHITS tools" package)
        - `parse_group_string` (function within the "PHITS tools" package)

    Inputs:
        - `tally_header` = list of lines belonging to the tally output's header section
        - `tally_content` = list of lists of remaining lines after the tally output's header section; the top level list is
                broken into "blocks" ("newpage:"-separated) which are lists of lines belonging to each block/page.

    Outputs:
        - `meta` = Munch object / dictionary containing tally metadata

    '''
    nlines = len(tally_header)
    tally_type = tally_header[0].replace(' ','').replace('off','')
    if '[' not in tally_type and ']' not in tally_type: # file is not PHITS tally output
        if 'htitle' in tally_type:
            tally_type = '[T-Dchain]'
        else:
            tally_type = 'UNKNOWN'
    meta = Munch({})
    meta.tally_type = tally_type
    unsupported_tally_types = ['[T-WWG]', '[T-WWBG]', '[T-Volume]', '[T-Userdefined]', '[T-Gshow]', '[T-Rshow]',
                               '[T-3Dshow]', '[T-4Dtrack]', '[T-Dchain]', 'UNKNOWN']
    if tally_type in unsupported_tally_types:
        return meta
    # Initialize variables for possible array
    mesh_types = ['e','t','x','y','z','r','a','l']
    for m in mesh_types: meta['n'+m] = None
    meta['reg'] = None
    meta['part'] = None
    meta['npart'] = None
    meta['nc'] = None
    meta['samepage'] = 'part'
    found_mesh_kinds = []

    reading_axis_data = False
    reading_regions = False
    in_exceptional_mesh_kind = False
    for li, line in enumerate(tally_header):
        #if line[0]=='#': # commented line
        if 'data =' in line: # data section to parse
            reading_axis_data = True
            n_values_to_read = meta['n'+current_data_mesh_kind] + 1
            remaining_n_values_to_read = n_values_to_read
            data_values = []
            in_exceptional_mesh_kind = False
            #print('read ',n_values_to_read,current_data_mesh_kind,' values')
            continue
        elif '=' in line:
            if line[0] == '#':  # commented line
                key, value = extract_data_from_header_line(line[1:])
            else:
                key, value = extract_data_from_header_line(line)
            if in_exceptional_mesh_kind:
                if key[0]=='e':
                    key = current_data_mesh_kind + key[1:]
                elif key=='ne':
                    key = 'n' + current_data_mesh_kind
            meta[key] = value

            if 'type' in key:
                current_data_mesh_kind = key.replace('-type','')
                if current_data_mesh_kind == 'se': current_data_mesh_kind = 'e'
                current_data_mesh_type = value
                found_mesh_kinds.append(current_data_mesh_kind)
                if current_data_mesh_kind in ['e1','e2']:
                    in_exceptional_mesh_kind = True
                #print(current_data_mesh_kind,current_data_mesh_type)
            if key=='part':
                part_groups = parse_group_string(str(value))
                kf_groups = parse_group_string(tally_header[li + 1].split(':')[1])
                if meta['npart'] == None: # first instance of "part"
                    meta['part_groups'] = part_groups
                    meta['kf_groups'] = kf_groups
                    meta['npart'] = len(part_groups)
                    meta['part_serial_groups'] = ['p'+str(gi+1)+'-group' for gi in range(len(part_groups))]
                else: # an additional occurance of part?
                    if 'multiplier' not in tally_header[li - 1]: # the multiplier can also be followed by an erroneous "part" specification
                        for pi,pg in enumerate(part_groups):
                            if pg not in meta['part_groups']:
                                meta['part_groups'] += [pg]
                                meta['kf_groups'] += kf_groups[pi]
                                meta['npart'] += 1
                                meta['part_serial_groups'] += ['p' + str(pi + 1) + '-group']
            if key=='reg':
                if meta['tally_type']=='[T-Cross]':
                    num_regs = value
                    meta['num_reg_groups'] = num_regs
                    meta['reg_groups'] = []
                    # manually read in reg groups
                    li_start = li+2
                    li_stop = li_start + num_regs
                    for lii in range(li_start,li_stop):
                        non, rfrom, rto, area = tally_header[lii].split()
                        meta['reg_groups'].append(rfrom+' - '+rto)
                else:
                    reg_groups = parse_group_string(str(value))
                    eli = 0 # extra line index
                    if '=' not in tally_header[eli+li+1] and 'volume' not in tally_header[eli+li+1]: # reg specification continues to next line
                        while '=' not in tally_header[eli+li+1] and 'volume' not in tally_header[eli+li+1]:
                            reg_groups += parse_group_string(tally_header[eli+li+1].strip())
                            eli += 1
                    if 'all' in reg_groups and 'volume' in tally_header[li+1] and '=' not in tally_header[eli+li+1]:
                        # parse table of regions...
                        found_reg_grps = []
                        meta['reg_groups_inputted'] = reg_groups
                        reg_lines = tally_header[li+3:]
                        for reg_line in reg_lines:
                            if '=' in reg_line: break
                            line_parts = reg_line.split('#')
                            if len(line_parts) >= 2:
                                found_reg_grps.append(line_parts[1].strip())
                            else:
                                found_reg_grps.append(line_parts[0].split()[1])
                        meta['reg_groups'] = found_reg_grps
                        meta['num_reg_groups'] = len(found_reg_grps)
                    else:
                        meta['reg_groups'] = reg_groups
                        meta['num_reg_groups'] = len(reg_groups)
            if key == 'point':
                num_regs = value
                meta['point_detectors'] = {'non':[], 'x':[], 'y':[], 'z':[], 'r0':[]} # [T-Point] points
                li_start = li + 2
                li_stop = li_start + num_regs
                for lii in range(li_start, li_stop):
                    non, tppx, tppy, tppz, tppr0 = tally_header[lii].split()
                    meta['point_detectors']['non'].append(non)
                    meta['point_detectors']['x'].append(tppx)
                    meta['point_detectors']['y'].append(tppy)
                    meta['point_detectors']['z'].append(tppz)
                    meta['point_detectors']['r0'].append(tppr0)
            if key == 'ring':
                num_regs = value
                meta['point_detectors'] = {'non':[], 'axis':[], 'ar':[], 'rr':[], 'r0':[]} # [T-Point] points
                li_start = li + 2
                li_stop = li_start + num_regs
                for lii in range(li_start, li_stop):
                    non, tppx, tppy, tppz, tppr0 = tally_header[lii].split()
                    meta['point_detectors']['non'].append(non)
                    meta['point_detectors']['axis'].append(tppx)
                    meta['point_detectors']['ar'].append(tppy)
                    meta['point_detectors']['rr'].append(tppz)
                    meta['point_detectors']['r0'].append(tppr0)
        elif reading_axis_data:
            values = line.replace('#','').strip().split()
            for val in values:
                data_values.append(float(val))
                remaining_n_values_to_read += -1
            if remaining_n_values_to_read <= 0:
                reading_axis_data = False
                data_values = np.array(data_values)
                meta[current_data_mesh_kind+'-mesh_bin_edges'] = data_values
                meta[current_data_mesh_kind+'-mesh_bin_mids'] = 0.5*(data_values[1:]+data_values[:-1])
                #meta[current_data_mesh_kind+'-mesh_bin_mids_log'] = np.sqrt(data_values[1:]*data_values[:-1])
                # generate log-centered bin mids
                bin_mids_log = []
                for i in range(len(data_values)-1):
                    if data_values[i+1]<=0 or data_values[i]<=0: # if one or both edges <= 0
                        if data_values[i+1]<0 and data_values[i]<0: # both values are negative
                            bin_mids_log.append(-1*np.sqrt(data_values[i]*data_values[i+1]))
                        elif data_values[i+1]==0 or data_values[i]==0: # one value is zero
                            # use linear center instead...
                            bin_mids_log.append(0.5*(data_values[i]+data_values[i+1]))
                        elif data_values[i+1]<0 or data_values[i]<0: # bin straddles zero
                            # use linear center instead...
                            bin_mids_log.append(0.5*(data_values[i]+data_values[i+1]))
                        else:
                            print('unknown binning encountered, skipping generation of log-scale bin mids for '+current_data_mesh_kind+'-mesh')
                            break
                    else:
                        bin_mids_log.append(np.sqrt(data_values[i]*data_values[i+1]))
                meta[current_data_mesh_kind+'-mesh_bin_mids_log'] = np.array(bin_mids_log)
            continue
        else:
            continue

    meta['found_mesh_kinds'] = found_mesh_kinds

    if meta['tally_type']=='[T-Cross]':
        if meta['mesh']=='xyz':
            if 'enclos' in meta and meta['enclos']==1:
                pass # total items remains nx*ny*nz
            else:
                meta['nz_original'] = meta['nz']
                meta['nz'] += 1 # zmesh surfaces are scored, making array nx*ny*(nz+1)
        elif meta['mesh']=='r-z':
            if 'enclos' in meta and meta['enclos']==1:
                pass # total items remains nr*nz
            else:
                # Current solution addresses this by expanding the ierr axis
                meta['nr_original'] = meta['nr']
                meta['nz_original'] = meta['nz']
                meta['nr'] = meta['nr'] + 1
                meta['nz'] = meta['nz'] + 1
                # OLD SOLUTION IMPLEMENTED IS BELOW
                # max total num of pages = nrsurf*nz + nzsurf*nr = (nr+1)*nz + nr*(nz+1) = 2*nr*nz + nr + nz
                # if one radius is 0, this becomes = nr*nz + nr*(nz+1) = 2*nr*nz + nr
                # Solution used here:
                # use ir to iterate nr, use iy to iterate nrsurf, use iz to iterate nz, use ic to iterate nzsurf
                # since only rsurf*z [iy,iz] and r*zsurf [ir,ic] pairs exist, when one pair is being written
                # the other will be [-1,-1], hence the dimensions for the array are increased by an extra 1 to prevent overlap
                #meta['nr_original'] = meta['nr']
                #meta['nz_original'] = meta['nz']
                #meta['ny_original'] = meta['ny']
                ##meta['nc_original'] = meta['nc']
                #meta['ny'] = meta['nr'] + 1 + 1
                #meta['nc'] = meta['nz'] + 1 + 1
                #meta['nr'] = meta['nr'] + 1
                #meta['nz'] = meta['nz'] + 1

    if meta['tally_type'] == '[T-Point]':
        if 'mesh' not in meta:
            if 'point' in meta:
                meta['mesh'] = 'point'
                meta['nreg'] = meta['point']
            elif 'ring' in meta:
                meta['mesh'] = 'ring'
                meta['nreg'] = meta['ring']


    axes_1D = ['eng','reg','x','y','z','r','t','cos','the','mass','charge','let','tet','eng1','eng2','sed','rad','deg','act']
    axes_2D = ['xy','yz','zx','rz','chart','dchain','t-eng','eng-t','t-e1','e1-t','t-e2','e2-t','e12','e21','xz','yx','zy','zr']

    axes_ital_1D = [3,   0,  0,  1,  2,  0,  4,    5,    5,     8,       8,    6,    0,     3,     8,    3,    5,    5,   8]
    axes_ital_2D = [ [0,1],[1,2],[2,0],[0,2],[None,None],[None,None],[4,3],[3,4],[4,3],[3,4],[4,8],[8,4],[3,8],[8,3],[0,2],[1,0],[2,1],[2,0]]


    if meta['axis'] in axes_1D:
        meta['axis_dimensions'] = 1
        meta['axis_index_of_tally_array'] = axes_ital_1D[axes_1D.index(meta['axis'])]
    elif meta['axis'] in axes_2D:
        meta['axis_dimensions'] = 2
        meta['axis_index_of_tally_array'] = axes_ital_2D[axes_2D.index(meta['axis'])]
    else:
        print("WARNING: axis value of ",meta['axis']," is not in list of known/registered values")
        meta['axis_dimensions'] = None
        meta['axis_index_of_tally_array'] = None




    # Now extract portion of metadata only available from tally content

    if meta['mesh'] == 'reg' or meta['mesh'] == 'tet':
        num, reg, vol = [], [], []
        if meta['axis']=='reg' or meta['axis']=='tet':  # get number of regions and region data from first block of tally content
            outblock = tally_content[0]
            in_reg_list = False
            for line in outblock:
                if '#' in line and ' num ' in line:
                    cols = line[1:].split()
                    #print(cols)
                    in_reg_list = True
                    continue
                if len(line.split()) == 0 or '{' in line:
                    in_reg_list = False
                if in_reg_list:
                    vals = line.split()
                    if meta['tally_type'] == '[T-Cross]':
                        num.append(vals[0])
                        reg.append(vals[0])
                        vol.append(vals[1])
                    else:
                        num.append(vals[0])
                        reg.append(vals[1])
                        vol.append(vals[2])
        else: # scan output for region numbers:
            regcount = 0
            for outblock in tally_content:
                for line in outblock:
                    if 'reg =' in line or 'reg  =' in line:
                        eq_strs = split_str_of_equalities(line[1:])
                        reg_eq_str = ''
                        for eqsi in eq_strs:
                            if 'reg' in eqsi:
                                reg_eq_str = eqsi
                                break
                        regnum = reg_eq_str.split('=')[1].strip()
                        #regnum = line.strip().split('reg =')[1].strip().replace("'",'')
                        if regnum not in reg:
                            regcount += 1
                            num.append(regcount)
                            reg.append(regnum)
                            vol.append(None)
                        continue
        if meta['mesh'] == 'reg':
            meta.reg_serial_num = num
            meta.reg_num = reg
            if meta['tally_type'] == '[T-Cross]':
                meta.reg_area = vol
            else:
                meta.reg_volume = vol
            meta.nreg = len(reg)
        elif meta['mesh'] == 'tet':
            meta.tet_serial_num = num
            meta.tet_num = reg
            meta.reg_num = reg
            #meta.tet_volume = vol
            if meta['tally_type'] == '[T-Cross]':
                meta.tet_area = vol
            else:
                meta.tet_volume = vol
            meta.ntet = len(reg)

        #if meta['tally_type'] == '[T-Cross]':
        #    meta['reg_groups'] = reg



    elif meta['mesh'] == 'tet':
        num, reg, vol = [], [], []
        if meta['axis'] == 'tet':
            pass
        else:
            pass
        print('mesh=tet has not been tested!')
        meta.ntet = 0

    axis1_label = ''
    axis2_label = ''
    value_label = ''
    hc_passed = False # passed colorbar definition line
    outblock = tally_content[0]
    for line in outblock:
        if len(line) == 0: continue
        if line[:2] == 'x:':
            axis1_label = line[2:].strip()
        if line[:2] == 'y:':
            if meta.axis_dimensions == 1:
                value_label = line[2:].strip()
                #break
            elif meta.axis_dimensions == 2:
                if hc_passed: # second instance of y:
                    value_label = line[2:].strip()
                    #break
                else: # first instance of y:
                    axis2_label = line[2:].strip()
                    hc_passed = True
        #if line[:3] == 'hc:':
        #    hc_passed = True
        h_line_str = ''
        if line[0] == 'h' and (line[1] == ':' or line[2] == ':'):
            if meta['axis_dimensions'] == 1:
                ndatacol = line.count(' y')
                if ndatacol != 1:  # multiple columns are present "samepage"
                    # get first string with y
                    col_groups = parse_group_string(line)
                    i_first_y = next((i for i,v in enumerate(col_groups) if v[0]=='y'), None) # index of first column with "y"
                    first_data_col_header = col_groups[i_first_y][2:]
                    for m in mesh_types:
                        if first_data_col_header[0] == m:
                            if m == 'e':
                                meta['samepage'] = 'eng'
                            elif m == 'r':
                                if first_data_col_header[:3] == 'reg':
                                    meta['samepage'] = 'reg'
                                else:
                                    meta['samepage'] = m
                            elif m == 'l':
                                meta['samepage'] = 'let'
                            elif m == 'a':
                                if first_data_col_header[:3] not in ['all','alp']:
                                    meta['samepage'] = 'the' # or cos
                            else:
                                meta['samepage'] = m
                    if meta['samepage'] == 'part':  # still is default value
                        # double check to see if it could be region numbers vs particle names
                        if ndatacol != meta['npart']:
                            if 'num_reg_groups' in meta and ndatacol == meta['num_reg_groups']:
                                meta['samepage'] = 'reg'
                            else:
                                print('"samepage" was not correctly identified; needs to be implemented')
                    if meta['samepage'] == 'reg':
                        hcols = parse_group_string(line[3:])
                        num, reg, vol = [], [], []
                        reg_ser_num = 1
                        for hcol in hcols:
                            if hcol[0] == 'y':
                                num.append(reg_ser_num)
                                reg_ser_num += 1
                                reg.append(hcol.split(')')[0].replace('y(reg',''))
                                vol.append(None)
                        meta.reg_serial_num = num
                        meta.reg_num = reg
                        meta.reg_volume = vol
                        meta.nreg = len(reg)

            break
    meta.axis1_label = axis1_label
    meta.axis2_label = axis2_label
    meta.value_label = value_label

    # Now do any final overrides for specific tallies / circumstances

    if meta['tally_type'] == '[T-Deposit2]':
        meta['nreg'] = 1
        meta['reg_serial_num'] = [1]
        meta['reg_num'] = ['1']
        meta['reg_volume'] = [None]
        if meta['num_reg_groups'] > 1:
            meta['num_reg_groups'] = 1
            meta['reg_groups'] = [meta['reg_groups'][0] + ' ' + meta['reg_groups'][1]]

    if meta['tally_type'] == '[T-Heat]':
        if 'npart' not in meta or meta['npart'] == None: meta['npart'] = 1
        if 'part_groups' not in meta: meta['part_groups'] = ['all']

    return meta

def initialize_tally_array(tally_metadata,include_abs_err=True):
    '''
    Description:
        Initializes main tally data array in which tally results will be stored when read

    Dependencies:
        - `import numpy as np`

    Inputs:
        - `tally_metadata` = Munch object / dictionary containing tally metadata
        - `include_abs_err` = a Boolean (D=`True`) on whether absolute error will be calculated; the final dimension of `tdata` is
                `3/2` if this value is `True/False`

    Outputs:
        - `tdata` = 10-dimensional NumPy array of zeros of correct size for holding tally results

    '''
    ir_max, iy_max, iz_max, ie_max, it_max, ia_max, il_max, ip_max, ic_max = 1, 1, 1, 1, 1, 1, 1, 1, 1
    if include_abs_err:
        ierr_max = 3
    else:
        ierr_max = 2
    if tally_metadata['mesh'] == 'reg':
        ir_max = tally_metadata.nreg
    elif tally_metadata['mesh'] == 'xyz':
        ir_max = tally_metadata.nx
        iy_max = tally_metadata.ny
        iz_max = tally_metadata.nz
    elif tally_metadata['mesh'] == 'r-z':
        ir_max = tally_metadata.nr
        iz_max = tally_metadata.nz
        if 'ny' in tally_metadata and tally_metadata.ny != None: iy_max = tally_metadata.ny
        if 'nc' in tally_metadata and tally_metadata.nc != None: ic_max = tally_metadata.nc
    elif tally_metadata['mesh'] == 'tet':
        ir_max = tally_metadata.ntet
    elif tally_metadata['mesh'] == 'point' or tally_metadata['mesh'] == 'ring':
        ir_max = tally_metadata.nreg
    else:
        raise ValueError('ERROR! Unknown geometry mesh:'+ str(tally_metadata['mesh']))

    if tally_metadata.na != None: ia_max = tally_metadata.na
    if tally_metadata.nt != None: it_max = tally_metadata.nt
    if tally_metadata.nl != None: il_max = tally_metadata.nl
    if 'nc' in tally_metadata and tally_metadata.nc != None: ic_max = tally_metadata.nc
    #if 'npart' in tally_metadata and tally_metadata.npart != None: ip_max = tally_metadata.np

    if tally_metadata.ne == None:
        if tally_metadata['tally_type'] == '[T-Deposit2]':
            if 'ne1' in tally_metadata:
                ie_max = tally_metadata.ne1
            if 'ne2' in tally_metadata:
                ic_max = tally_metadata.ne2
        elif 'e1' in tally_metadata.axis or 'e2' in tally_metadata.axis:  # This should now be redundant?
            if tally_metadata.axis == 'e12':
                ie_max = tally_metadata.ne1
                ic_max = tally_metadata.ne2
            elif tally_metadata.axis == 'e21':
                ie_max = tally_metadata.ne1
                ic_max = tally_metadata.ne2
            elif 'e1' in tally_metadata.axis or 'eng1' in tally_metadata.axis:
                ie_max = tally_metadata.ne1
                if 'ne2' in tally_metadata:
                    ic_max = tally_metadata.ne2
            elif 'e2' in tally_metadata.axis or 'eng2' in tally_metadata.axis:
                ic_max = tally_metadata.ne2
                if 'ne1' in tally_metadata:
                    ie_max = tally_metadata.ne1
            else:
                if 'ne1' in tally_metadata:
                    ie_max = tally_metadata.ne1
                if 'ne2' in tally_metadata:
                    ic_max = tally_metadata.ne2

    else:
        ie_max = tally_metadata.ne

    ip_max = tally_metadata.npart

    if tally_metadata['tally_type'] == '[T-Cross]' and tally_metadata.mesh == 'r-z':
        if 'enclos' in tally_metadata and tally_metadata['enclos'] == 1:
            pass
        else: # enclos = 0 case
            ierr_max = 2*ierr_max

    if tally_metadata['tally_type'] == '[T-Yield]':
        if tally_metadata.axis == 'charge':
            ic_max = 130
        elif tally_metadata.axis == 'mass':
            ic_max = 320
        elif tally_metadata.axis == 'chart':
            if int(tally_metadata.mxnuclei) == 0:
                ic_max = 10000
            else:
                ic_max = int(tally_metadata.mxnuclei)

    if tally_metadata['tally_type'] == '[T-Interact]' and tally_metadata['axis'] == 'act':
        ic_max = 100
        if 'maxact' in tally_metadata:
            ic_max = tally_metadata.maxact

    if in_debug_mode:
        dims_str = 'tally dims: nr={:g}, ny={:g}, nz={:g}, ne={:g}, nt={:g}, na={:g}, nl={:g}, np={:g}, nc={:g}, nerr={:g}'
        print(dims_str.format(ir_max, iy_max, iz_max, ie_max, it_max, ia_max, il_max, ip_max, ic_max, ierr_max))
    tally_data = np.zeros((ir_max, iy_max, iz_max, ie_max, it_max, ia_max, il_max, ip_max, ic_max, ierr_max))
    return tally_data

def calculate_tally_absolute_errors(tdata):
    '''
    Description:
        Calculates the absolute uncertainty for every value in the PHITS tally data array

    Inputs:
        - `tdata` = 10-dimensional NumPy array containing read/extracted tally results

    Outputs:
        - `tdata` = updated `tdata` array now with absolute uncertainties in `ierr = 2` index

    '''

    ir_max, iy_max, iz_max, ie_max, it_max, ia_max, il_max, ip_max, ic_max, ierr_max = np.shape(tdata)
    for ir in range(ir_max):
        for iy in range(iy_max):
            for iz in range(iz_max):
                for ie in range(ie_max):
                    for it in range(it_max):
                        for ia in range(ia_max):
                            for il in range(il_max):
                                for ip in range(ip_max):
                                    for ic in range(ic_max):
                                        tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 2] = \
                                            tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 0] * \
                                            tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 1]
    if ierr_max==6:
        for ir in range(ir_max):
            for iy in range(iy_max):
                for iz in range(iz_max):
                    for ie in range(ie_max):
                        for it in range(it_max):
                            for ia in range(ia_max):
                                for il in range(il_max):
                                    for ip in range(ip_max):
                                        for ic in range(ic_max):
                                            tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 5] = \
                                                tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 3] * \
                                                tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 4]

    return tdata

def split_str_of_equalities(text):
    '''
    Description:
        Extract relevant regions, indices, etc. from somewhat inconsistently formatted lines in PHITS tally output content section.

    Dependencies:
        - `is_number` (function within the "PHITS tools" package)

    Inputs:
        - `text` = string to be processed

    Outputs:
        - `equalities_str_list` = list of strings of equalities each of the format "key = value"

    '''
    equalities_str_list = []
    original_text = text
    #if text[0] == "'": # more loosely formatted text
    #    problem_strs = ['tot DPA']
    text = text.replace("'",'').replace(',',' ').replace('#','').replace('=',' = ')
    text_pieces = text.split()
    #i_equal_sign = [i for i, x in enumerate(text_pieces) if x == "="]
    is_i_equal_sign = [x=='=' for x in text_pieces]
    #i_is_number = [i for i, x in enumerate(text_pieces) if is_number(x)]
    is_i_number = [is_number(x) for x in text_pieces]
    #num_equalities = len(i_equal_sign)
    #remaining_equalities = num_equalities
    equality_str = ''
    # the only condition enforced is that the last item in each value be numeric or )
    current_equality_contains_equalsign = False
    for i in reversed(range(len(text_pieces))): # easiest to build from right to left
        equality_str = text_pieces[i] + ' ' + equality_str
        if is_i_equal_sign[i]:
            current_equality_contains_equalsign = True
        elif current_equality_contains_equalsign: # looking to terminate if next item is numeric
            if i==0 or (is_i_number[i-1] or text_pieces[i-1][-1]==')'): # either final equality completed or next item belongs to next equality
                equalities_str_list.insert(0,equality_str.strip())
                equality_str = ''
                current_equality_contains_equalsign = False
    if '(' in text: # need to break up potential (ia,ib) pairs
        new_eq_str_list = []
        for x in equalities_str_list:
            if '(' in x:
                keys, values = x.split('=')
                keys = keys.strip().replace('(','').replace(')','').split()
                values = values.strip().replace('(','').replace(')','').split()
                for i in range(len(keys)):
                    new_eq_str = keys[i].strip() + ' = ' + values[i].strip()
                    new_eq_str_list.append(new_eq_str)
            else:
                new_eq_str_list.append(x)
        equalities_str_list = new_eq_str_list
    #print(equalities_str_list)
    return equalities_str_list


def parse_tally_content(tdata,meta,tally_blocks,is_err_in_separate_file,err_mode=False):
    '''
    Description:
        Parses the PHITS tally output content section and extract its results

    Dependencies:
        - `split_str_of_equalities` (function within the "PHITS tools" package)
        - `parse_group_string` (function within the "PHITS tools" package)
        - `data_row_to_num_list` (function within the "PHITS tools" package)

    Inputs:
        - `tdata` = 10-dimensional NumPy array of zeros of correct size to hold tally output/results
        - `meta` = Munch object / dictionary containing tally metadata
        - `tally_blocks` = blocks of tally output as outputted by the `split_into_header_and_content` function
        - `is_err_in_separate_file` = Boolean denoting whether the tally's relative errors are located in a separate file
        - `err_mode` = Boolean (D=`False`) used for manually forcing all read values to be regarded as relative uncertainties
                as is necessary when processing dedicated *_err files.

    Outputs:
        - `tdata` = updated `tdata` array containing read/extracted tally results

    '''
    global ir, iy, iz, ie, it, ia, il, ip, ic, ierr
    global ir_max, iy_max, iz_max, ie_max, it_max, ia_max, il_max, ip_max, ic_max, ierr_max
    ierr = 0
    if is_err_in_separate_file and err_mode:
        ierr = 1

    mesh_kind_chars = ['e', 't', 'x', 'y', 'z', 'r', 'a', 'l']
    mesh_kind_iax = [3, 4, 0, 1, 2, 0, 5, 6]
    tdata_ivar_strs = ['ir', 'iy', 'iz', 'ie', 'it', 'ia', 'il', 'ip', 'ic']
    ir, iy, iz, ie, it, ia, il, ip, ic = 0, 0, 0, 0, 0, 0, 0, 0, 0

    ignored_eq_strs = ['axis','axs','ar','rr','m jm','Z','cmax nmax']
    replace_eq_strs_dict = {'ang':'a'}

    ir_max, iy_max, iz_max, ie_max, it_max, ia_max, il_max, ip_max, ic_max, ierr_max = np.shape(tdata)

    axes_1D = ['eng', 'reg', 'x', 'y', 'z', 'r', 't', 'cos', 'the', 'mass', 'charge', 'let', 'tet', 'eng1', 'eng2',
               'sed', 'rad', 'deg', 'act']
    axes_2D = ['xy', 'yz', 'zx', 'rz', 'chart', 'dchain',
               't-eng', 'eng-t', 't-e1', 'e1-t', 't-e2', 'e2-t',
               'e12', 'e21', 'xz', 'yx', 'zy', 'zr']

    axes_ital_1D = [3, 0, 0, 1, 2, 0, 4, 5, 5, 8, 8, 6, 0, 3, 8,
                    3, 5, 5, 8]
    axes_ital_2D = [[0, 1], [1, 2], [2, 0], [0, 2], [None, None], [None, None],
                    [4, 3], [3, 4], [4, 3], [3, 4], [4, 8], [8, 4],
                    [3, 8], [8, 3], [0, 2], [1, 0], [2, 1], [2, 0]]

    ierr_mod = 0 # add to ierr for weird [T-Cross], mesh=r-z, enclos=0 case

    banked_uninterpreted_lines = [] # store lines with equalities that may be useful but are skipped owing to being a bit exceptional
    i_metastable = 0
    ZZZAAAM_list = []

    if meta.axis_dimensions==1:
        for bi, block in enumerate(tally_blocks):
            hli, fli = 0,0
            ierr_mod = 0
            hli_found = False
            for li, line in enumerate(block):
                if len(line) == 0: continue
                if line[:2].lower() == 'h:':  # start of data is here
                    hli = li
                    hli_found = True
                    continue
                if hli_found and (line[:12] == '#   sum over' or line[:7] == '#   sum' or line[:5] == '#----' or (len(block[li-1]) == 0 and hli != 0 and li>hli+2) or "'" in line or '{' in line):
                    fli = li
                    if (len(block[li-1]) == 0 and hli != 0 and li>hli+2): fli = li - 1 # triggered by blank line after data
                    #if "'" in line or '{' in line:
                    #    fli = li-1
                    break

            data_header = block[:hli]
            data_table = block[hli:fli]
            data_footer = block[fli:]

            if bi == len(tally_blocks) - 1:
                ffli = len(data_footer)
                for li, line in enumerate(data_footer):
                    if line[:37] == '# Information for Restart Calculation':
                        ffli = li
                        break
                data_footer = data_footer[:ffli]

            # print(data_header)
            #print(data_table)
            # print(data_footer)

            hash_line_already_evaluated = False

            # try to get relevant indices data from header and footer blocks
            for li, line in enumerate(data_header+data_footer):
                if len(line) == 0: continue

                if '=' in line and (line[0] == "'" or (line[0] == "#" and ('no.' in line or 'i' in line or 'reg' in line or 'part' in line))):
                    if line[0] == "#":
                        hash_line_already_evaluated = True
                    elif line[0] == "'" and hash_line_already_evaluated:
                        if meta['samepage'] == 'part':
                            continue  # '-starting lines tend to have more problematic formatting, best skipped if possible
                        elif meta['npart'] == 1:
                            continue  # can still skip if only one particle group tallied
                        else:
                            pass  # but this needs to be parsed if not using samepage = part and npart > 1
                    parts = split_str_of_equalities(line)
                    #print(line)
                    for part in parts:
                        mesh_char = part.split('=')[0].strip().replace('i','')
                        #print(mesh_char)
                        if mesh_char == 'no.':
                            if '***' in part:
                                break # this is a bugged line
                            continue
                        elif mesh_char == 'part.' or mesh_char == 'partcle' or mesh_char == 'part':
                            part_grp_name = part.split('=')[1].strip()
                            if part_grp_name in meta.part_groups:
                                ip = (meta.part_groups).index(part_grp_name)
                            elif part_grp_name in meta.part_serial_groups:
                                ip = (meta.part_serial_groups).index(part_grp_name)
                            else:
                                raise ValueError('ERROR! Particle "'+part_grp_name+'" could not be identified.')
                        elif mesh_char == 'reg':
                            regnum = part.split('=')[1].strip()
                            ir = (meta.reg_num).index(regnum)
                        elif mesh_char == 'pont' or mesh_char == 'rng': # [T-Point]
                            value_str = part.split('=')[1].strip()
                            ir = int(value_str) - 1
                        elif mesh_char == 'e1': # [T-Deposit2]
                            value_str = part.split('=')[1].strip()
                            ie = int(value_str) - 1
                        elif mesh_char == 'e2': # [T-Deposit2]
                            value_str = part.split('=')[1].strip()
                            ic = int(value_str) - 1
                        elif mesh_char in mesh_kind_chars or mesh_char in replace_eq_strs_dict:
                            if mesh_char in replace_eq_strs_dict:
                                mesh_char = replace_eq_strs_dict[mesh_char]
                            if 'i'+mesh_char not in part: continue # only looking for indices for meshes, not values
                            imesh = mesh_kind_chars.index(mesh_char)
                            itdata_axis = mesh_kind_iax[imesh]
                            tdata_ivar_str = tdata_ivar_strs[itdata_axis]
                            value_str = part.split('=')[1].strip()
                            if ' - ' in value_str:
                                vals = value_str.split('-')
                                if int(vals[0]) == int(vals[1]):
                                    value_str = vals[0]
                                else:  # samepage axis
                                    value_str = vals[0]  # this will be overwritten later
                            value = str(int(value_str)-1)
                            exec(tdata_ivar_str + ' = ' + value, globals())
                        elif mesh_char in ignored_eq_strs:
                            continue
                        elif meta['tally_type']=='[T-Cross]':
                            if meta['mesh'] == 'xyz' and mesh_char=='z surf':
                                #imesh = mesh_kind_chars.index('z')
                                itdata_axis = 2 #mesh_kind_iax[imesh]
                                tdata_ivar_str = tdata_ivar_strs[itdata_axis]
                                value_str = part.split('=')[1].strip()
                                value = str(int(value_str) - 1)
                                exec(tdata_ivar_str + ' = ' + value, globals())
                            elif meta['mesh'] == 'r-z':
                                if mesh_char=='r surf':
                                    itdata_axis = 0  # mesh_kind_iax[imesh]
                                    #itdata_axis = 1  # set to iy
                                    ierr_mod = int(ierr_max/2)
                                    #ir, ic = -1, -1
                                    # imesh = mesh_kind_chars.index('y')
                                elif mesh_char == 'z surf':
                                    itdata_axis = 2  # mesh_kind_iax[imesh]
                                    #itdata_axis = 8  # set to ic
                                    ierr_mod = 0
                                    #iy, iz = -1, -1
                                    # imesh = mesh_kind_chars.index('c')
                                else:
                                    raise ValueError('ERROR! Unregistered potential index ['+ part.split('=')[0].strip()+'] found')
                                tdata_ivar_str = tdata_ivar_strs[itdata_axis]
                                value_str = part.split('=')[1].strip()
                                if ' - ' in value_str:
                                    vals = value_str.split('-')
                                    if int(vals[0]) == int(vals[1]):
                                        value_str = vals[0]
                                    else: # samepage axis
                                        value_str = vals[0] # this will be overwritten later
                                value = str(int(value_str) - 1)
                                exec(tdata_ivar_str + ' = ' + value, globals())
                            else:
                                raise ValueError('ERROR! Unregistered potential index ['+ part.split('=')[0].strip()+ '] found')
                        elif meta['tally_type'] == '[T-Heat]':
                            banked_uninterpreted_lines.append(line)
                        else:
                            raise ValueError('ERROR! Unregistered potential index ['+part.split('=')[0].strip()+'] found')


            # extract data from table
            # determine meaning of table rows
            row_ivar = tdata_ivar_strs[meta.axis_index_of_tally_array]
            # determine meaning of table columns
            hcols = parse_group_string(data_table[0][3:])
            nhcols = len(hcols)
            col_names_line_str = data_table[1][1:]
            icol_mod = 0 # account for weirdness in column presence/absence
            if 'r surface position' in col_names_line_str:
                icol_mod = -1
                ierr_mod = int(ierr_max / 2)
            # Test for error in hcols
            num_data_vals_in_first_row = len(data_row_to_num_list(data_table[2])) # first row of data
            if num_data_vals_in_first_row != nhcols:
                if num_data_vals_in_first_row == (nhcols+1):
                    # most likely issue is hcol string is missing the "n" for the ?-lower column
                    nhcols = nhcols + 1
                    icol_mod = 1
            is_col_data = np.full(nhcols,False)
            data_col_indices = []
            is_col_err = np.full(nhcols,False)
            err_col_indices = []
            for iii in range(len(hcols)):
                if hcols[iii][0] == 'y':
                    is_col_data[iii+icol_mod] = True
                    is_col_err[iii+1+icol_mod] = True
                    data_col_indices.append(iii+icol_mod)
                    err_col_indices.append(iii+1+icol_mod)
            #print(is_col_data)
            #print(is_col_err)
            cols = data_table[1][1:].strip().split()
            ncols = len(cols)
            ndata_cols = np.sum(is_col_data) # number of data values per row
            # determine what variable this corresponds to, should be val of samepage
            # by default, this is usually particles (samepage = part by default)
            if meta.samepage == 'part':
                if meta.npart != ndata_cols:
                    raise ValueError('ERROR! samepage number of particle types ('+str(meta.npart)+') not equal to number of data columns y(part) = '+str(ndata_cols))
                data_ivar = 'ip'
                data_ivar_indices = [j for j in range(ndata_cols)]
            else: # figure out what axis samepage is on
                if meta.samepage not in axes_1D:
                    raise ValueError('ERROR! samepage parameter ('+str(meta.samepage)+') must be "part" or one of valid options for "axis" parameter')
                data_ivar = tdata_ivar_strs[axes_ital_1D[axes_1D.index(meta.samepage)]]
                if ndata_cols != eval(data_ivar+'_max'):
                    if meta['tally_type']=='[T-Cross]' and ndata_cols+1 == eval(data_ivar+'_max'):
                        # This is fine; for T-Cross, ndata cols can be one less than max length...
                        pass
                    elif meta['tally_type']=='[T-Cross]' and data_ivar == 'ir' and ndata_cols+2 == eval(data_ivar+'_max'):
                        # This is fine; for T-Cross, ndata cols for radius can be two less than max length if rmin=0...
                        pass
                    else:
                        raise ValueError('ERROR! number of data columns ('+str(ndata_cols)+') not equal to tally array dimension for '+str(data_ivar)+', '+str(eval(data_ivar+'_max')))
                data_ivar_indices = [j for j in range(ndata_cols)]
            #print(cols)
            #print(ndata_cols)
            for li, line in enumerate(data_table[2:]):
                if len(line)==0: continue
                #print(line)
                rowi = li
                exec(row_ivar + '=' + str(rowi),globals())
                #print(row_ivar + '=' + str(rowi))
                values = data_row_to_num_list(line)
                dcoli = 0
                ecoli = 0
                for vi, value in enumerate(values):
                    if is_col_data[vi]:
                        exec(data_ivar + '=' + str(dcoli),globals())
                        #print(data_ivar + '=' + str(dcoli))
                        tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 0+ierr_mod] = value
                        dcoli += 1
                    if is_col_err[vi]:
                        exec(data_ivar + '=' + str(ecoli),globals())
                        #print(data_ivar + '=' + str(ecoli))
                        tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 1+ierr_mod] = value
                        ecoli += 1





    elif meta.axis_dimensions==2:
        for bi, block in enumerate(tally_blocks):
            hli, bli = 0 , 0
            data_keyword_found = False
            for li, line in enumerate(block):
                if meta['2D-type'] in [1, 2, 3, 6, 7]:
                    if len(line) == 0: continue
                    if line[:3].lower() in ['hc:', 'h2:', 'hd:', 'hc2']:  # start of data is here
                        hli = li
                    if line[:12] == '#-----------':
                        fli = li
                        #if bi != len(tally_blocks) - 1:
                        break
                elif meta['2D-type'] == 4:
                    if line == '' and hli != 0:
                        fli = li
                        #if bi != len(tally_blocks) - 1:
                        break
                    elif line == '':  # start of data is here
                        hli = li
                elif meta['2D-type'] == 5:
                    if 'data' in line:
                        hli = li + 3
                    if line == '' and hli != 0 and li>hli+2:
                        fli = li
                        #if bi != len(tally_blocks) - 1:
                        break

            data_header = block[:hli]
            data_table = block[hli:fli]
            data_footer = block[fli:]

            #print(data_header)
            #print(data_table)
            #print(data_footer)

            hash_line_already_evaluated = False

            if bi == len(tally_blocks) - 1:
                for li, line in enumerate(data_footer):
                    if line[:37] == '# Information for Restart Calculation':
                        ffli = li
                        break
                data_footer = data_footer[:ffli]

            # try to get relevant indices data from header block
            for li, line in enumerate(data_header+data_footer): # +data_footer
                if len(line) == 0: continue
                #if 'reg =' in line:
                #    regnum = line.strip().split('reg =')[1].strip()
                #    ir = (meta.reg_num).index(regnum)
                #    # print(ir)
                if '=' in line and (line[0] == "'" or (line[0] == "#" and ('no.' in line or 'i' in line or 'reg' in line or 'part' in line))):
                    if line[0] == "#":
                        hash_line_already_evaluated = True
                    elif line[0] == "'" and hash_line_already_evaluated:
                        if meta['samepage'] == 'part':
                            continue # '-starting lines tend to have more problematic formatting, best skipped if possible
                        elif meta['npart'] == 1:
                            continue # can still skip if only one particle group tallied
                        else:
                            pass # but this needs to be parsed if not using samepage = part and npart > 1
                    parts = split_str_of_equalities(line)
                    for part in parts:
                        mesh_char = part.split('=')[0].strip().replace('i', '')
                        #print(mesh_char)
                        if mesh_char == 'no.':
                            continue
                        elif mesh_char == 'part.' or mesh_char == 'partcle':
                            part_grp_name = part.split('=')[1].strip()
                            try:
                                ip = (meta.part_groups).index(part_grp_name)
                            except:
                                ip = (meta.part_serial_groups).index(part_grp_name)
                        elif mesh_char == 'reg': # and meta['samepage'] != 'reg':
                            regnum = part.split('=')[1].strip()
                            ir = (meta.reg_num).index(regnum)
                        elif mesh_char == 'e1': # [T-Deposit2]
                            value_str = part.split('=')[1].strip()
                            ie = int(value_str) - 1
                        elif mesh_char == 'e2': # [T-Deposit2]
                            value_str = part.split('=')[1].strip()
                            ic = int(value_str) - 1
                        elif mesh_char in mesh_kind_chars or mesh_char in replace_eq_strs_dict:
                            if mesh_char in replace_eq_strs_dict:
                                mesh_char = replace_eq_strs_dict[mesh_char]
                            if 'i'+mesh_char not in part: continue # only looking for indices for meshes, not values
                            imesh = mesh_kind_chars.index(mesh_char)
                            itdata_axis = mesh_kind_iax[imesh]
                            tdata_ivar_str = tdata_ivar_strs[itdata_axis]
                            value = str(int(part.split('=')[1].strip()) - 1)
                            if mesh_char == 'l' and meta['tally_type'] == '[T-Yield]' and meta['axis'] == 'chart':
                                i_metastable = int(value) + 1
                                il = 0
                            else:
                                exec(tdata_ivar_str + ' = ' + value, globals())
                        elif mesh_char in ignored_eq_strs:
                            continue
                        elif meta['tally_type']=='[T-Cross]':
                            ierr_mod = 0
                            if meta['mesh'] == 'xyz' and mesh_char=='z surf':
                                #imesh = mesh_kind_chars.index('z')
                                itdata_axis = 2 #mesh_kind_iax[imesh]
                                tdata_ivar_str = tdata_ivar_strs[itdata_axis]
                                value = str(int(part.split('=')[1].strip()) - 1)
                                exec(tdata_ivar_str + ' = ' + value, globals())
                            elif meta['mesh'] == 'r-z':
                                if mesh_char=='r surf':
                                    # imesh = mesh_kind_chars.index('y')
                                    itdata_axis = 0 #1  # mesh_kind_iax[imesh]
                                    tdata_ivar_str = tdata_ivar_strs[itdata_axis]
                                    value = str(int(part.split('=')[1].strip()) - 1)
                                    exec(tdata_ivar_str + ' = ' + value, globals())
                                    #ir, ic = -1, -1
                                    ierr_mod = int(ierr_max / 2)
                                elif mesh_char=='z surf':
                                    # imesh = mesh_kind_chars.index('c')
                                    itdata_axis = 2 #8  # mesh_kind_iax[imesh]
                                    tdata_ivar_str = tdata_ivar_strs[itdata_axis]
                                    value = str(int(part.split('=')[1].strip()) - 1)
                                    exec(tdata_ivar_str + ' = ' + value, globals())
                                    iy, iz = -1, -1
                                    ierr_mod = 0
                                else:
                                    raise ValueError('ERROR! Unregistered potential index ['+ part.split('=')[0].strip()+'] found')
                            else:
                                raise ValueError('ERROR! Unregistered potential index ['+ part.split('=')[0].strip()+ '] found')
                        else:
                            raise ValueError('ERROR! Unregistered potential index ['+part.split('=')[0].strip()+'] found')


            # Now read data_table, with formatting dependent on 2D-type, and can be inferred from last line of header
            axis1_ivar = meta.axis_index_of_tally_array[0]
            axis2_ivar = meta.axis_index_of_tally_array[1]
            if meta['tally_type'] == '[T-Yield]' and meta['axis'] == 'chart': # this setting does not respect 2D-type and uses its own formatting
                data_write_format_str = data_table[0][3:]
                Z_y_segment = data_write_format_str.split(';')[0]
                N_x_segment = data_write_format_str.split(';')[1]
                Z_y_vals = Z_y_segment.replace('=','').replace('to','').replace('by','').replace('y','').strip().split()
                N_x_vals = N_x_segment.replace('=','').replace('to','').replace('by','').replace('x','').strip().split()
                Z_y_max, Z_y_min, Z_y_increment = int(Z_y_vals[0]), int(Z_y_vals[1]), int(Z_y_vals[2])
                N_x_max, N_x_min, N_x_increment = int(N_x_vals[1]), int(N_x_vals[0]), int(N_x_vals[2])
                #print(Z_y_max, Z_y_min, Z_y_increment, N_x_max, N_x_min, N_x_increment )
            elif meta['2D-type'] != 4:
                data_write_format_str = data_header[-2][1:]
                if 'data' not in data_write_format_str:
                    for line in data_header[::-1]:
                        if 'data' in line:
                            data_write_format_str = line[1:]
                            break
                #print(data_write_format_str)
                if 'data' not in data_write_format_str:
                    # failed to find a "data" line telling us how the values are ordered
                    # have to make guesses about output ordering...
                    # axis variable should give us a hint
                    axis = meta['axis']
                    if 'eng' in axis or 'e1' in axis or 'e2' in axis:
                        if axis == 'e12' or axis == 'e21':
                            ax1_ivar = 'ie'
                            ax2_ivar = 'ie'
                        else: # energy vs time
                            if axis[0] == 't':
                                ax1_ivar = 'it'
                                ax2_ivar = 'ie'
                            else:
                                ax1_ivar = 'ie'
                                ax2_ivar = 'it'
                    else:
                        if 'axis1_label' in meta and meta['axis1_label'][0] in axis:
                            # we know horizontal axis variable
                            ax1_ivar = 'i' + meta['axis1_label'][0]
                            ax2_ivar = 'i' + axis.replace(meta['axis1_label'][0],'')
                        else:
                            ax1_ivar = 'i' + meta['axis'][1]
                            ax2_ivar = 'i' + meta['axis'][0]
                else:
                    # We can, with confidence, determine output value ordering :)
                    for dsi in data_write_format_str.split():
                        if 'data' in dsi:
                            data_index_str = dsi
                            ax_vars = data_index_str.replace('data','').replace('(','').replace(')','')
                            #print(data_index_str)
                            #print(ax_vars)
                            ax1_ivar, ax2_ivar = ax_vars.split(',')[:2]
                            ax1_ivar = 'i' + ax1_ivar
                            ax2_ivar = 'i' + ax2_ivar
                    #print(data_write_format_str)
            else:  # 2D-type = 4
                cols = data_table[1][1:].split()
                ax1_ivar, ax2_ivar = cols[0], cols[1]
                ax1_ivar = 'i' + ax1_ivar
                ax2_ivar = 'i' + ax2_ivar

            # manually fix [T-Deposit2] axes
            if meta['tally_type'] == '[T-Deposit2]':
                if meta['axis'] == 'e12':
                    ax1_ivar, ax2_ivar = 'ie', 'ic'
                elif meta['axis'] == 'e21':
                    ax1_ivar, ax2_ivar = 'ic', 'ie'
                elif meta['axis'] == 't-e1':
                    ax1_ivar, ax2_ivar = 'it', 'ie'
                elif meta['axis'] == 't-e2':
                    ax1_ivar, ax2_ivar = 'it', 'ic'
                elif meta['axis'] == 'e1-t':
                    ax1_ivar, ax2_ivar = 'ie', 'it'
                elif meta['axis'] == 'e2-t':
                    ax1_ivar, ax2_ivar = 'ic', 'it'

            if meta['tally_type'] == '[T-Yield]' and meta['axis'] == 'chart':
                remaining_ndata_to_read = (Z_y_max - Z_y_min + 1) * (N_x_max - N_x_min + 1)
            else:
                # check if this is one of the backwards instances
                expected_ax1_ivar = tdata_ivar_strs[axis1_ivar]
                expected_ax2_ivar = tdata_ivar_strs[axis2_ivar]
                if meta.mesh=='xyz':
                    if expected_ax1_ivar == 'ir': expected_ax1_ivar = 'ix'
                    if expected_ax2_ivar == 'ir': expected_ax1_ivar = 'ix'
                if ax1_ivar==expected_ax1_ivar and ax2_ivar==expected_ax2_ivar:
                    pass # all is correct as is
                elif ax2_ivar == expected_ax1_ivar and ax1_ivar == expected_ax2_ivar:
                    axis1_ivar_temp = axis1_ivar
                    axis1_ivar = axis2_ivar
                    axis2_ivar = axis1_ivar_temp
                    #axis1_ivar = tdata_ivar_strs.index(ax1_ivar)
                    #axis2_ivar = tdata_ivar_strs.index(ax2_ivar)
                    #print('backwards!')
                else:
                    raise ValueError('ERROR! Unknown axes ('+ax1_ivar+' '+ax2_ivar +
                                     ') encountered that did not match expected axes (' +
                                     tdata_ivar_strs[meta.axis_index_of_tally_array[0]]+' ' +
                                     tdata_ivar_strs[meta.axis_index_of_tally_array[1]]+')')

                axis1_ivar_str = tdata_ivar_strs[axis1_ivar]
                axis2_ivar_str = tdata_ivar_strs[axis2_ivar]
                axis1_size = np.shape(tdata)[axis1_ivar]
                axis2_size = np.shape(tdata)[axis2_ivar]
                ndata_to_read = axis1_size*axis2_size
                #print(axis1_ivar_str,axis2_ivar_str)
                #print(axis1_size,axis2_size,ndata_to_read)
                remaining_ndata_to_read = ndata_to_read
                iax1 = 0
                iax2 = axis2_size - 1

            if meta['tally_type'] == '[T-Yield]' and meta['axis'] == 'chart':
                #Z_y_max, Z_y_min, Z_y_increment # big, 1, -1
                #N_x_max, N_x_min, N_x_increment # big, 1, 1
                current_Z = Z_y_max
                current_N = N_x_min - N_x_increment
                ic = 0
                for line in data_table[1:]:
                    values = data_row_to_num_list(line)
                    for value in values:
                        remaining_ndata_to_read += -1
                        current_N += N_x_increment
                        if current_N > N_x_max:
                            current_N = N_x_min
                            current_Z += Z_y_increment
                        #print('Z=',current_Z,', N=',current_N)

                        if value != 0:
                            ZZZAAAM = 10000*current_Z + 10*(current_Z+current_N) + i_metastable
                            if ZZZAAAM not in ZZZAAAM_list:
                                ic = len(ZZZAAAM_list)
                                ZZZAAAM_list.append(ZZZAAAM)
                            else:
                                ic = ZZZAAAM_list.index(ZZZAAAM)
                            #print(ic, i_metastable)
                            #print(ic,value)
                            tdata[ir, iy, iz, ie, it, ia, il, ip, ic, ierr + ierr_mod] = value

                        if remaining_ndata_to_read <= 0:
                            break







            elif meta['2D-type'] in [1,2,3,6,7]:
                for line in data_table[1:]:
                    values = data_row_to_num_list(line)
                    #print(line)
                    for value in values:
                        exec(axis1_ivar_str + ' = ' + str(iax1), globals())
                        exec(axis2_ivar_str + ' = ' + str(iax2), globals())
                        #print(ir, iy, iz, ie, it, ia, il, ip, ic, ierr, '\t', value)
                        tdata[ir, iy, iz, ie, it, ia, il, ip, ic, ierr + ierr_mod] = value
                        remaining_ndata_to_read += -1
                        #print(iax1, iax2)
                        iax1 += 1
                        if iax1 == axis1_size:
                            iax1 = 0
                            iax2 += -1
                    if remaining_ndata_to_read <= 0:
                        break

            elif meta['2D-type'] == 4:
                iax2 = 0
                for line in data_table[2:]:
                    values = data_row_to_num_list(line)
                    value = values[2]
                    value_err = values[3]
                    exec(axis1_ivar_str + ' = ' + str(iax1), globals())
                    exec(axis2_ivar_str + ' = ' + str(iax2), globals())
                    tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 0 + ierr_mod] = value
                    tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 1 + ierr_mod] = value_err
                    # print(ir, iy, iz, ie, it, ia, il, ip, ic, ierr,'\t',value)
                    remaining_ndata_to_read += -1
                    # print(iax1, iax2)
                    iax1 += 1
                    if iax1 == axis1_size:
                        iax1 = 0
                        iax2 += 1

                    if remaining_ndata_to_read <= 0:
                        break

            elif meta['2D-type'] == 5:
                for line in data_table[2:]:
                    values = data_row_to_num_list(line)
                    #print(line)
                    for vi, value in enumerate(values):
                        if vi==0: continue # header column
                        exec(axis1_ivar_str + ' = ' + str(iax1), globals())
                        exec(axis2_ivar_str + ' = ' + str(iax2), globals())
                        #print(ir, iy, iz, ie, it, ia, il, ip, ic, ierr, '\t', value)
                        tdata[ir, iy, iz, ie, it, ia, il, ip, ic, ierr + ierr_mod] = value
                        remaining_ndata_to_read += -1
                        # print(iax1, iax2)
                        iax1 += 1
                        if iax1 == axis1_size:
                            iax1 = 0
                            iax2 += -1
                    if remaining_ndata_to_read <= 0:
                        break

            else:
                raise ValueError('ERROR! unsupported 2D-type of '+str(meta['2D-type'])+' provided; legal values are [1,2,3,4,5,6,7]')

    else:
        raise ValueError(str(meta.axis_dimensions)+'axis dimensions is unknown, ERROR!')

    if len(banked_uninterpreted_lines) != 0:
        print('The following potentially useful output lines were found but not stored anywhere:')
        for line in banked_uninterpreted_lines:
            print('\t'+line)

    return_updated_metadata_too = False
    if meta['tally_type'] == '[T-Yield]':
        return_updated_metadata_too = True
        if meta['axis'] == 'chart':
            meta['nuclide_ZZZAAAM_list'] = ZZZAAAM_list
            meta['nuclide_isomer_list'] = [ZZZAAAM_to_nuclide_plain_str(i) for i in ZZZAAAM_list]
            nc_max = len(ZZZAAAM_list) #+ 1
            meta['nc'] = nc_max
            tdata = tdata[:,:,:,:,:,:,:,:,:nc_max,:]
        elif meta['axis'] == 'charge' or meta['axis'] == 'mass':
            ic_axis_tdata_sum = tdata.sum(axis=(0,1,2,3,4,5,6,7,9))
            nc_max = np.max(np.nonzero(ic_axis_tdata_sum)) + 1
            meta['nc'] = nc_max
            tdata = tdata[:, :, :, :, :, :, :, :, :nc_max, :]

    if return_updated_metadata_too:
        return tdata, meta
    else:
        return tdata

def build_tally_Pandas_dataframe(tdata,meta):
    '''
    Description:
        Calculates the absolute uncertainty for every value in the PHITS tally data array

    Dependencies:
        - `import pandas as pd`

    Inputs:
        - `tdata` = 10-dimensional NumPy array containing read/extracted tally results
        - `meta` = Munch object / dictionary containing tally metadata

    Outputs:
        - `tally_df` = Pandas dataframe containing the entire contents of the `tdata` array;
                note that tally_df.attrs returns values which are the same for all rows

    '''
    import pandas as pd
    ir_max, iy_max, iz_max, ie_max, it_max, ia_max, il_max, ip_max, ic_max, ierr_max = np.shape(tdata)
    num_df_rows = ir_max * iy_max * iz_max * ie_max * it_max * ia_max * il_max * ip_max * ic_max
    # determine what columns to include, based on what info was specified vs left at default values
    col_names_list = []

    in_irregular_TCross_rz_mesh = False
    in_irregular_TCross_xyz_mesh = False
    ierr_mod = 0
    if meta['tally_type'] == '[T-Cross]' and (meta.mesh == 'xyz' or meta.mesh == 'r-z'):
        if 'enclos' in meta and meta['enclos'] == 1:
            pass
        else:
            if meta.mesh == 'r-z':
                in_irregular_TCross_rz_mesh = True
                min_r_is_zero = False
                if meta['r-mesh_bin_edges'][0]==0:
                    min_r_is_zero = True
                ierr_mod = int(ierr_max / 2)
            else:
                in_irregular_TCross_xyz_mesh = True


    # region columns
    if meta.mesh == 'reg':
        reg_cols = ['ir','reg','reg#'] # use meta.reg_groups and meta.reg_num
    elif meta.mesh == 'xyz':
        if in_irregular_TCross_xyz_mesh:
            reg_cols = ['ix', 'iy', 'iz', 'x_mid', 'y_mid', 'z_surf']
        else:
            reg_cols = ['ix','iy','iz','x_mid','y_mid','z_mid']
    elif meta.mesh == 'r-z':
        if in_irregular_TCross_rz_mesh:
            #reg_cols = ['ir', 'ic', 'r_mid', 'z_surf', 'iy', 'iz', 'r_surf', 'z_mid']
            reg_cols = ['ir', 'iz', 'r_mid', 'z_surf', 'r_surf', 'z_mid']
        else:
            reg_cols = ['ir','iz','r_mid','z_mid']
    elif meta.mesh == 'tet':
        reg_cols = ['ir','tet'] #,'tet#']
    elif meta.mesh == 'point':
        reg_cols = ['ir','point#']
    elif meta.mesh == 'ring':
        reg_cols = ['ir','ring#']
    col_names_list += reg_cols



    # Determine what other columns will be present
    ecols, tcols, acols, lcols, pcols, ccols = False, False, False, False, False, False
    single_specified_bin_axes = [] # log axes which are provided by user but only contain 1 bin
    single_bin_ranges_or_values = []
    if meta.ne != None:
        if meta.ne==1:
            single_specified_bin_axes.append('e')
            single_bin_ranges_or_values.append(['Energy',meta['e-mesh_bin_edges']])
        else:
            ecols = True
            ecol_names_list = ['ie','e_mid']
            col_names_list += ecol_names_list
    else:
        single_bin_ranges_or_values.append(['Energy','default/all'])
    if meta.nt != None:
        if meta.nt==1:
            single_specified_bin_axes.append('t')
            single_bin_ranges_or_values.append(['Time',meta['t-mesh_bin_edges']])
        else:
            tcols = True
            tcol_names_list = ['it', 't_mid']
            col_names_list += tcol_names_list
    else:
        single_bin_ranges_or_values.append(['Time','default/all'])
    if meta.na != None:
        if meta.na==1:
            single_specified_bin_axes.append('a')
            single_bin_ranges_or_values.append(['Angle',meta['a-mesh_bin_edges']])
        else:
            acols = True
            acol_names_list = ['ia', 'a_mid']
            col_names_list += acol_names_list
    else:
        single_bin_ranges_or_values.append(['Angle','default/all'])
    if meta.nl != None:
        if meta.nl==1:
            single_specified_bin_axes.append('l')
            single_bin_ranges_or_values.append(['LET',meta['l-mesh_bin_edges']])
        else:
            lcols = True
            lcol_names_list = ['il', 'LET_mid']
            col_names_list += lcol_names_list
    else:
        single_bin_ranges_or_values.append(['LET','default/all'])

    if meta.nc != None:
        if meta.nc == 1:
            pass
        else:
            ccols = True
            if meta['tally_type'] == '[T-Yield]':
                if meta['axis'] == 'chart':
                    ccol_names_list = ['ic', 'nuclide', 'ZZZAAAM']
                    col_names_list += ccol_names_list
                elif meta['axis'] == 'charge':
                    ccol_names_list = ['ic/Z/charge']
                    col_names_list += ccol_names_list
                elif meta['axis'] == 'mass':
                    ccol_names_list = ['ic/A/mass']
                    col_names_list += ccol_names_list
            elif meta['tally_type'] == '[T-Deposit2]':
                pass

    if meta.npart != None: # and meta.part_groups[0]=='all':
        if meta.npart==1:
            single_specified_bin_axes.append('p')
            single_bin_ranges_or_values.append(['Particle',meta.part_groups[0]])
        else:
            pcols = True
            pcol_names_list = ['ip', 'particle', 'kf-code']
            col_names_list += pcol_names_list
    else:
        single_bin_ranges_or_values.append(['Particle','default/all'])

    # HANDLE SPECIAL COLUMNS HERE (ic / ccols)


    # value columns come last
    val_names_list = ['value', 'rel.err.']
    if ierr_max == 3 or ierr_max == 6: val_names_list += ['abs.err.']
    if ierr_max >= 4: val_names_list += ['value2', 'rel.err.2']
    if ierr_max == 6: val_names_list += ['abs.err.2']
    col_names_list += val_names_list

    # Initialize dictionary
    df_dict = {}
    for col in col_names_list:
        df_dict[col] = []


    # Populate dictionary
    for ir in range(ir_max):
        for iy in range(iy_max):
            for iz in range(iz_max):
                for ie in range(ie_max):
                    for it in range(it_max):
                        for ia in range(ia_max):
                            for il in range(il_max):
                                for ip in range(ip_max):
                                    for ic in range(ic_max):
                                        # Region columns
                                        if in_irregular_TCross_rz_mesh:
                                            if (ir == ir_max - 1 and iz == iz_max - 1): # only index that should be empty
                                                continue
                                            # ['ir', 'iz', 'r_mid', 'z_surf', 'r_surf', 'z_mid']
                                            df_dict[reg_cols[0]].append(ir)
                                            df_dict[reg_cols[1]].append(iz)
                                            if ir==ir_max-1:
                                                df_dict[reg_cols[2]].append(None)
                                            else:
                                                df_dict[reg_cols[2]].append(meta['r-mesh_bin_mids'][ir])
                                            df_dict[reg_cols[3]].append(meta['z-mesh_bin_edges'][iz])
                                            df_dict[reg_cols[4]].append(meta['r-mesh_bin_edges'][ir])
                                            if iz == iz_max - 1:
                                                df_dict[reg_cols[5]].append(None)
                                            else:
                                                df_dict[reg_cols[5]].append(meta['z-mesh_bin_mids'][iz])
                                            # OLD IMPLEMENTATION IS BELOW:
                                            '''
                                            # skip unwritten indices
                                            # reg_cols = ['ir', 'ic', 'r_mid', 'z_surf', 'iy', 'iz', 'r_surf', 'z_mid']
                                            if (ir==ir_max-1 and ic==ic_max-1):
                                                if (iy == iy_max - 1 or iz == iz_max - 1): continue
                                                if min_r_is_zero and iy==0: continue # surface vals not written for r=0.0
                                                df_dict[reg_cols[0]].append(None)
                                                df_dict[reg_cols[1]].append(None)
                                                df_dict[reg_cols[2]].append(None)
                                                df_dict[reg_cols[3]].append(None)
                                                df_dict[reg_cols[4]].append(iy)
                                                df_dict[reg_cols[5]].append(iz)
                                                df_dict[reg_cols[6]].append(meta['r-mesh_bin_edges'][iy])
                                                df_dict[reg_cols[7]].append(meta['z-mesh_bin_mids'][iz])
                                            elif (iy==iy_max-1 and iz==iz_max-1):
                                                if (ir == ir_max - 1 or ic == ic_max - 1): continue
                                                df_dict[reg_cols[0]].append(ir)
                                                df_dict[reg_cols[1]].append(ic)
                                                df_dict[reg_cols[2]].append(meta['r-mesh_bin_mids'][ir])
                                                df_dict[reg_cols[3]].append(meta['z-mesh_bin_edges'][ic])
                                                df_dict[reg_cols[4]].append(None)
                                                df_dict[reg_cols[5]].append(None)
                                                df_dict[reg_cols[6]].append(None)
                                                df_dict[reg_cols[7]].append(None)
                                            else: # all other indices should not have any content written into them
                                                continue
                                            '''
                                        else:
                                            if meta.mesh == 'reg': #reg_cols = ['ir','reg', 'reg#']  # use meta.reg_groups and meta.reg_num
                                                df_dict[reg_cols[0]].append(ir)
                                                df_dict[reg_cols[1]].append(meta.reg_groups[ir])
                                                df_dict[reg_cols[2]].append(meta.reg_num[ir])
                                            elif meta.mesh == 'xyz':
                                                #reg_cols = ['ix', 'iy', 'iz', 'xmid', 'ymid', 'zmid']
                                                df_dict[reg_cols[0]].append(ir)
                                                df_dict[reg_cols[1]].append(iy)
                                                df_dict[reg_cols[2]].append(iz)
                                                df_dict[reg_cols[3]].append(meta['x-mesh_bin_mids'][ir])
                                                df_dict[reg_cols[4]].append(meta['y-mesh_bin_mids'][iy])
                                                if in_irregular_TCross_xyz_mesh:
                                                    df_dict[reg_cols[5]].append(meta['z-mesh_bin_edges'][iz])
                                                else:
                                                    df_dict[reg_cols[5]].append(meta['z-mesh_bin_mids'][iz])
                                            elif meta.mesh == 'r-z':
                                                #reg_cols = ['ir', 'iz', 'rmid', 'zmid']
                                                df_dict[reg_cols[0]].append(ir)
                                                df_dict[reg_cols[1]].append(iz)
                                                df_dict[reg_cols[2]].append(meta['r-mesh_bin_mids'][ir])
                                                df_dict[reg_cols[3]].append(meta['z-mesh_bin_mids'][iz])
                                            elif meta.mesh == 'tet':
                                                #reg_cols = ['ir','tet']
                                                df_dict[reg_cols[0]].append(ir)
                                                df_dict[reg_cols[1]].append(meta.tet_num[ir])
                                            elif meta.mesh == 'point':
                                                #reg_cols = ['ir','point#']
                                                df_dict[reg_cols[0]].append(ir)
                                                df_dict[reg_cols[1]].append(str(ir+1))
                                            elif meta.mesh == 'ring':
                                                #reg_cols = ['ir','ring#']
                                                df_dict[reg_cols[0]].append(ir)
                                                df_dict[reg_cols[1]].append(str(ir+1))

                                        #ecols, tcols, acols, lcols, pcols, ccols
                                        if pcols: # pcol_names_list = ['ip', 'particle', 'kf-code']
                                            df_dict[pcol_names_list[0]].append(ip)
                                            df_dict[pcol_names_list[1]].append(meta.part_groups[ip])
                                            df_dict[pcol_names_list[2]].append(meta.kf_groups[ip])

                                        if ecols: # ecol_names_list = ['ie','e_mid']
                                            df_dict[ecol_names_list[0]].append(ie)
                                            df_dict[ecol_names_list[1]].append(meta['e-mesh_bin_mids'][ie])
                                        if tcols: # tcol_names_list = ['it','t_mid']
                                            df_dict[tcol_names_list[0]].append(it)
                                            df_dict[tcol_names_list[1]].append(meta['t-mesh_bin_mids'][it])
                                        if acols: # acol_names_list = ['ia','a_mid']
                                            df_dict[acol_names_list[0]].append(ia)
                                            df_dict[acol_names_list[1]].append(meta['a-mesh_bin_mids'][ia])
                                        if lcols: # lcol_names_list = ['il','LET_mid']
                                            df_dict[lcol_names_list[0]].append(il)
                                            df_dict[lcol_names_list[1]].append(meta['l-mesh_bin_mids'][il])

                                        if ccols:
                                            if meta['tally_type'] == '[T-Yield]':
                                                if meta['axis'] == 'chart':
                                                    #ccol_names_list = ['ic', 'nuclide', 'ZZZAAAM']
                                                    df_dict[ccol_names_list[0]].append(ic)
                                                    df_dict[ccol_names_list[1]].append(meta['nuclide_isomer_list'][ic])
                                                    df_dict[ccol_names_list[2]].append(meta['nuclide_ZZZAAAM_list'][ic])
                                                elif meta['axis'] == 'charge':
                                                    #ccol_names_list = ['ic/Z/charge']
                                                    df_dict[ccol_names_list[0]].append(ic)
                                                elif meta['axis'] == 'mass':
                                                    #ccol_names_list = ['ic/A/mass']
                                                    df_dict[ccol_names_list[0]].append(ic)

                                        # Value columns
                                        #val_names_list = ['value', 'rel.err.','abs.err.']
                                        df_dict[val_names_list[0]].append(tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 0])
                                        df_dict[val_names_list[1]].append(tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 1])
                                        if ierr_max == 3 or ierr_max == 6:
                                            df_dict[val_names_list[2]].append(tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 2])
                                        if in_irregular_TCross_rz_mesh:
                                            df_dict[val_names_list[0+ierr_mod]].append(tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 0+ierr_mod])
                                            df_dict[val_names_list[1+ierr_mod]].append(tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 1+ierr_mod])
                                            if ierr_max == 6:
                                                df_dict[val_names_list[2+ierr_mod]].append(tdata[ir, iy, iz, ie, it, ia, il, ip, ic, 2 + ierr_mod])


    # Convert dictionary to Pandas dataframe
    #for key in df_dict.keys():
    #    print(key,len(df_dict[key]))
    #sys.exit()
    tally_df = pd.DataFrame(df_dict)

    # store information on settings provided by user that are different from default but same for all rows
    if len(single_bin_ranges_or_values) > 0:
        for i in single_bin_ranges_or_values:
            col, val = i
            tally_df.attrs[col] = val

    #with pd.option_context('display.max_rows', None, 'display.max_columns', None): print(tally_df)
    if in_debug_mode:
        #print(tally_df.to_string())
        print(tally_df.attrs)
    return tally_df

def search_for_dump_parameters(output_file):
    '''
    Description:
        Try to determine the dump settings used for a dump file by searching for the same file without "_dmp" and parsing
        its header for the "dump = " line and subsequent line specifying the column ordering.

    Dependencies:
        - `from pathlib import Path`

    Inputs:
        - `output_file` = a file/filepath (string or Path object) to be judged

    Outputs:
        - `dump_data_number` = value following "dump = " in the PHITS tally (integer from -20 to 20, excluding 0) (D=`None`)
        - `dump_data_sequence` = list of integers specifying the order and meaning of the dump file columns (D=`None`)
    '''
    dump_data_number, dump_data_sequence = None, None
    output_file = Path(output_file)
    origin_tally_file = Path(output_file.parent, output_file.stem.replace('_dmp','') + output_file.suffix)
    PHITS_file_type = determine_PHITS_output_file_type(origin_tally_file)
    if PHITS_file_type['file_does_not_exist']:
        print("Could not find this dump file's companion original standard tally output file",origin_tally_file)
        return dump_data_number, dump_data_sequence
    elif not PHITS_file_type['is_standard_tally_output']:
        print("Found dump file's suspected companion original standard tally output file, but it does not seem to actually be formatted as a standard tally output file",origin_tally_file)
        return dump_data_number, dump_data_sequence
    tally_header, tally_content = split_into_header_and_content(origin_tally_file)
    for li, line in enumerate(tally_header):
        if "dump =" in line:
            if line[0] == '#':  # commented line
                key, value = extract_data_from_header_line(line[1:])
            else:
                key, value = extract_data_from_header_line(line)
            dump_data_number = int(value)
            dump_data_sequence_str_list = tally_header[li+1].strip().split()
            dump_data_sequence = [int(i) for i in dump_data_sequence_str_list]
            break
    if dump_data_number == None and dump_data_sequence == None:
        print('Was unable to locate dump specification information in tally output file',origin_tally_file)
    return dump_data_number, dump_data_sequence

def determine_PHITS_output_file_type(output_file):
    '''
    Description:
        Determine what kind of PHITS file is being hanlded (tally standard output, binary tally dump, ASCII tally dump, etc.)

    Dependencies:
        - `from pathlib import Path`

    Inputs:
        - `output_file` = a file/filepath (string or Path object) to be judged

    Outputs:
        - `PHITS_file_type` = a dictionary of Booleans detailing what kind of file `output_file` is (and isn't) with
            the following keys (each with a value set to `True` or `False`):
            `'is_standard_tally_output'`, `'is_binary_tally_dump'`, `'is_ASCII_tally_dump'`,
            `'is_unknown_file_type'`, and `'file_does_not_exist'`.  By default, all are set to `False` except for
            `'is_unknown_file_type'` which is `True` by default.
    '''
    PHITS_file_type = {'is_standard_tally_output': False,
                       'is_binary_tally_dump': False,
                       'is_ASCII_tally_dump': False,
                       'is_unknown_file_type': True,
                       'file_does_not_exist': False
                       }
    output_file = Path(output_file)
    if not output_file.is_file():
        print('Provided output file',output_file,'was determined to not be a file!')
        PHITS_file_type['is_unknown_file_type'] = False
        PHITS_file_type['file_does_not_exist'] = True
        return PHITS_file_type
    with open(output_file) as f:
        try:
            first_line = f.readline().strip()
        except:  # triggered if encountering binary / non ASCII or UTF-8 file
            if '_dmp' in output_file.stem:
                PHITS_file_type['is_binary_tally_dump'] = True
                PHITS_file_type['is_unknown_file_type'] = False
                return PHITS_file_type
        if first_line[0] == '[':
            PHITS_file_type['is_standard_tally_output'] = True
            PHITS_file_type['is_unknown_file_type'] = False
        elif '_dmp' in output_file.stem:
            PHITS_file_type['is_ASCII_tally_dump'] = True
            PHITS_file_type['is_unknown_file_type'] = False
    return PHITS_file_type













if run_with_CLI_inputs:
    def validate_file(arg):
        if (file := Path(arg)).is_file():
            return file
        else:
            raise FileNotFoundError(arg)
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=validate_file, help="path to PHITS output file to parse or directory containing files to parse (relative or absolute path)")
    # Flags for standard output files
    parser.add_argument("-g", "--GUI", help="Launch the PHITS Tools GUI and ignore all other command line inputs", action="store_true")
    parser.add_argument("-np", "--disable_PandasDF", help="[standard output] disable automatic creation of Pandas DataFrame of PHITS output", action="store_true")
    parser.add_argument("-na", "--disable_abs_err_calc", help="[standard output] disable automatic calculation of absolute errors", action="store_true")
    # Not going to add below option. Why would you ever run this in CLI if not trying to generate the pickle file?
    # parser.add_argument("-ns", "--disable_saving_pickle", help="disable saving of pickle of of PHITS output", action="store_true")
    # Flags for dump files
    parser.add_argument("-d", "--is_dump_file", action="store_true", help="add this flag if the file is a dump file, omit if standard PHITS tally output; if inputting a directory path to 'file', this flag specifies that dump files will be read too (by default, they will be skipped), and if so the below flags will be applied to the settings used when parsing them")
    parser.add_argument('-dvals', '--dump_data_sequence', nargs='+', type=int, help='[dump output] provide a series of integers separated by spaces that match the line after "dump = " in the tally whose dump file is being parsed, detailing how the columns of the dump file are to be interpreted. (REQUIRED for dump files, but an attempt to assign automatically will be made first if left unspecified)')
    parser.add_argument("-dbin", "--dump_file_is_binary", action="store_true", help="[dump output] specify that the provided dump file is binary; otherwise it is assumed to be ASCII (REQUIRED for dump files, but an attempt to assign automatically will be made first if left unspecified)")
    parser.add_argument("-dnmax", "--dump_max_entries_read", type=int, help="[dump output] specify maximum integer number of entries to read (read all by default)")
    parser.add_argument("-ddir", "--dump_return_directional_info", action="store_true", help="[dump output] return extra directional information: radial distance r from the origin in cm, radial distance rho from the z-axis in cm, polar angle theta between the direction vector and z-axis in radians [0,pi] (or degrees), and azimuthal angle phi of the direction vector in radians [-pi,pi] (or degrees). Note: This option requires all position and direction values [x,y,z,u,v,w] to be included in the dump file.")
    parser.add_argument("-ddeg", "--dump_use_degrees", action="store_true", help="[dump output] anular quantities will be in degrees instead of radians")
    parser.add_argument("-dnsl", "--dump_no_save_namedtuple_list", action="store_true", help="[dump output] do NOT save parsed dump file info to list of namedtuples to dill file (-dnsl and -dnsp cannot both be enabled if parsing a dump file)")
    parser.add_argument("-dnsp", "--dump_no_save_Pandas_dataframe", action="store_true", help="[dump output] do NOT save parsed dump file info to Pandas DataFrame to pickle file (-dnsl and -dnsp cannot both be enabled if parsing a dump file)")
    # Flags for processing files in a directory
    parser.add_argument("-r", "--recursive_search", action="store_true", help="[directory parsing] If the provided 'file' is a directory, also recursively search subdirectories for files to process.")
    parser.add_argument("-fpre", "--file_prefix", default='', help="[directory parsing] A string specifying what characters processed filenames (including the file extension) must begin with to be included. This condition is not enforced if set to an empty string (default).")
    parser.add_argument("-fsuf", "--file_suffix", default='.out', help="[directory parsing] A string specifying what characters processed filenames (including the file extension) must end in to be included. This condition is not enforced if set to an empty string. This is '.out' by deault.")
    parser.add_argument("-fstr", "--file_required_string", default='', help="[directory parsing] A string which must be present anywhere within processed filenames (including the file extension) to be included. This condition is not enforced if set to an empty string (default).")

    args = parser.parse_args()

    output_file_path = Path(args.file)
    is_dump_file = args.is_dump_file

    is_path_a_dir = output_file_path.is_dir()
    is_path_a_file = output_file_path.is_file()

    if not is_path_a_file and not is_path_a_dir:
        raise ValueError("ERROR! The inputted filepath is neither a recognized file nor directory.")

    # directory options
    recursive_search = args.recursive_search
    file_suffix = args.file_suffix
    file_prefix = args.file_prefix
    file_reqstr = args.file_required_string

    # Standard output options
    make_PandasDF = not args.disable_PandasDF
    calculate_absolute_errors = not args.disable_abs_err_calc

    # Dump output options
    dump_data_sequence = args.dump_data_sequence
    if dump_data_sequence != None:
        dump_data_number = len(dump_data_sequence)
        if not args.dump_file_is_binary:
            dump_data_number = -1 * dump_data_number
    else:
        dump_data_number = None
    return_namedtuple_list = False
    return_Pandas_dataframe = False
    max_entries_read = args.dump_max_entries_read
    return_directional_info = args.dump_return_directional_info
    use_degrees = args.dump_use_degrees
    no_save_namedtuple_list = args.dump_no_save_namedtuple_list
    no_save_Pandas_dataframe = args.dump_no_save_Pandas_dataframe
    save_namedtuple_list = not no_save_namedtuple_list
    save_Pandas_dataframe = not no_save_Pandas_dataframe

    if is_path_a_dir:
        parse_all_tally_output_in_dir(output_file_path, output_file_suffix=file_suffix, output_file_prefix=file_prefix,
                                      output_file_required_string=file_reqstr, include_subdirectories=recursive_search,
                                      return_tally_output=False,
                                      make_PandasDF=make_PandasDF, calculate_absolute_errors=calculate_absolute_errors,
                                      save_output_pickle=True, prefer_reading_existing_pickle=False,
                                      include_dump_files=is_dump_file,
                                      dump_data_number=dump_data_number, dump_data_sequence=dump_data_sequence,
                                      dump_return_directional_info=return_directional_info, dump_use_degrees=use_degrees,
                                      dump_max_entries_read=max_entries_read,
                                      dump_save_namedtuple_list=save_namedtuple_list,
                                      dump_save_Pandas_dataframe=save_Pandas_dataframe
                                      )
    else: # if is_path_a_file
        if is_dump_file:
            if dump_data_number == None:
                dump_data_number, dump_data_sequence = search_for_dump_parameters(output_file_path)
                if dump_data_number == None or dump_data_sequence == None:
                    raise ValueError('You MUST provide a space-delimited list of integers to the -dvals / --dump_data_sequence input specifying ' +
                          'how the data columns in the dump file are to be interpreted, the same as the line following "dump = " in your PHITS tally input. ' +
                          'An attempt was made to automatically find these values, but it failed (thus, manual specification is required).')
            if no_save_namedtuple_list and no_save_Pandas_dataframe:
                raise ValueError('You MUST select how the dump file data is to be saved by disabling either or both of the following flags:' +
                      ' -dsl / --dump_save_namedtuple_list AND/OR -dsp / --dump_save_Pandas_dataframe')
            parse_tally_dump_file(output_file_path, dump_data_number, dump_data_sequence,
                                  return_directional_info=return_directional_info, use_degrees=use_degrees,
                                  max_entries_read=max_entries_read,
                                  return_namedtuple_list=return_namedtuple_list,
                                  return_Pandas_dataframe=return_Pandas_dataframe,
                                  save_namedtuple_list=save_namedtuple_list,
                                  save_Pandas_dataframe=save_Pandas_dataframe)
        else:
            parse_tally_output_file(output_file_path, make_PandasDF=make_PandasDF,
                                    calculate_absolute_errors=calculate_absolute_errors,
                                    save_output_pickle=True, prefer_reading_existing_pickle=False)

elif launch_GUI:
    # tkinter GUI below written with the assistance of ChatGPT

    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import ttk
    import warnings
    import sys


    # Function to issue a warning on unexpected closure and then exit the program
    def on_closing(window):
        window.destroy()
        warnings.warn("Window closed unexpectedly", UserWarning)
        sys.exit()


    # Initialize the settings dictionary
    settings = {}

    standard_mode_short_text = "[STANDARD mode]"
    dump_mode_short_text = "[DUMP mode]"
    directory_mode_short_text = "[DIRECTORY mode]"

    standard_mode_full_text = standard_mode_short_text + " for processing a single standard PHITS tally output file"
    dump_mode_full_text = dump_mode_short_text + " for processing a single PHITS tally dump output file (*_dmp.out)"
    directory_mode_full_text = directory_mode_short_text + " for processing all PHITS output files in a directory"


    def on_option_selected():
        option = selected_option.get()
        file_chosen = None

        try:
            if option in [1, 2]:
                if option == 1:
                    window_name_str = 'Select standard PHITS tally output file'
                else:
                    window_name_str = 'Select PHITS tally dump output file'
                file_chosen = filedialog.askopenfilename(title=window_name_str)
                if not file_chosen:
                    raise ValueError("File selection is required")
                settings['file'] = file_chosen
            elif option == 3:
                directory_chosen = filedialog.askdirectory(title="Select Directory of PHITS outputs to parse")
                if not directory_chosen:
                    raise ValueError("Directory selection is required")
                settings['directory'] = directory_chosen
        except:
            raise ValueError("User closed the file/directory dialog")
        else:
            root.withdraw()
            create_secondary_gui(option)


    def create_secondary_gui(option):
        secondary_gui = tk.Toplevel(root)

        def on_closing_secondary_gui():
            on_closing(secondary_gui)

        secondary_gui.protocol("WM_DELETE_WINDOW", on_closing_secondary_gui)



        inputs = {
            1: ['Checkbox 1', 'Checkbox 2'],
            2: ['Checkbox A', 'Checkbox B', 'Radio 1', 'Radio 2', 'Radio 3', 'Input 1 (str)', 'Input 2 (int)',
                'Input 3 (int)'],
            3: ['Checkbox 1', 'Checkbox 2', 'Checkbox A', 'Checkbox B', 'Radio 1', 'Radio 2', 'Radio 3',
                'Input 1 (str)', 'Input 2 (int)', 'Input 3 (int)', 'Input 4 (str)', 'Input 5 (str)', 'Input 6 (str)',
                'Extra Checkbox 1', 'Extra Checkbox 2']
        }

        def save_settings():
            settings.update({
                'main_mode': selected_option.get()
            })
            if option == 1:
                settings.update({
                    'option_1_cb1': cb1_var.get(),
                    'option_1_cb2': cb2_var.get()
                })
            elif option == 2:
                settings.update({
                    'option_2_cb1': cb1_var.get(),
                    'option_2_cb2': cb2_var.get(),
                    'radio': radio_var.get(),
                    'input_str': entry_str.get() or None,
                    'input_int1': entry_int1.get() or None,
                    'input_int2': entry_int2.get() or None,
                })
            elif option == 3:
                settings.update({
                    'option_3_cb1': cb1_var.get(), 'option_3_cb2': cb2_var.get(),
                    'option_3_cb3': cb3_var.get(), 'option_3_cb4': cb4_var.get(),
                    'radio': radio_var.get(),
                    'input_str_1': secondary_entry_str1.get() or None,
                    'input_int_1': secondary_entry_int1.get() or None,
                    'input_int_2': secondary_entry_int2.get() or None,
                    'input_str_2': secondary_entry_str2.get() or None,
                    'input_str_3': secondary_entry_str3.get() or None,
                    'input_str_6': extra_entry_str1.get() or None,  # Renamed 'Extra Input 1' to 'Input 6'
                    'extra_cb1': extra_cb1_var.get(),
                    'extra_cb2': extra_cb2_var.get(),
                })
            secondary_gui.destroy()
            root.destroy()  # Ensure root window is destroyed after closing secondary GUI

        common_widgets = []

        if option == 1:
            sample_text_label = tk.Label(secondary_gui, text=standard_mode_full_text,
                                         anchor=tk.W, font='16')
            sample_text_label.pack(anchor=tk.W, padx=10, pady=2)
            cb1_var = tk.BooleanVar()
            cb2_var = tk.BooleanVar()
            common_widgets.append(tk.Checkbutton(secondary_gui, text="Also make and save Pandas DataFrame object of results (in addition to default NumPy array)", variable=cb1_var, anchor=tk.W))
            common_widgets[-1].select()  # This makes the checkbox be ticked by default
            common_widgets.append(tk.Checkbutton(secondary_gui, text="Also calculate absolute uncertainties", variable=cb2_var, anchor=tk.W))
            common_widgets[-1].select()  # This makes the checkbox be ticked by default

        elif option == 2:
            sample_text_label = tk.Label(secondary_gui, text=dump_mode_full_text,
                                         anchor=tk.W, font='16')
            sample_text_label.pack(anchor=tk.W, padx=10, pady=2)
            cb1_var = tk.BooleanVar()
            cb2_var = tk.BooleanVar()
            radio_var = tk.IntVar(value=3)
            entry_str = tk.Entry(secondary_gui, width=50)
            entry_int1 = tk.Entry(secondary_gui)
            entry_int2 = tk.Entry(secondary_gui)

            dir_info_str = "Return extra directional information (relative to the origin and z-axis); \nthis requires all position and direction values [x,y,z,u,v,w] to be included in the dump file."
            common_widgets.append(tk.Checkbutton(secondary_gui, text=dir_info_str, variable=cb1_var, anchor=tk.W, justify='left'))
            common_widgets.append(tk.Checkbutton(secondary_gui, text="Use degrees (instead of radians) for extra directional information", variable=cb2_var, anchor=tk.W))

            options_frame = tk.LabelFrame(secondary_gui, text="Data output format options")
            options_frame.pack(padx=10, pady=10, anchor=tk.W)

            tk.Radiobutton(options_frame, text="Save only a dill file of a list of named tuples with dump event information", variable=radio_var, value=1, anchor=tk.W).pack(anchor=tk.W)
            tk.Radiobutton(options_frame, text="Save only a pickle file of a Pandas DataFrame of dump event information", variable=radio_var, value=2, anchor=tk.W).pack(anchor=tk.W)
            tk.Radiobutton(options_frame, text="Save both the named tuples list dill file and the Pandas DataFrame pickle file", variable=radio_var, value=3, anchor=tk.W).pack(anchor=tk.W)

            dump_instrcutions = 'If in the same directory as your dump file exists the corresponding standard tally output file,\n' + \
                                'and the only difference in their file names is the "_dmp" at the end of the dump file, the \n' + \
                                'below two fields can be left blank as PHITS Tools should automatically find this information.\n' + \
                                'Otherwise, in the below two boxes, place what you entered following "dump = " in your PHITS tally.\n' + \
                                'In the first box, enter a nonzero integer between -20 and 20 specifying the number of dump\n' + \
                                'columns and whether the data will be in ASCII (<0) or binary (>0) format.\n' + \
                                'In the second box, enter a sequence of that many numbers, separated by spaces, describing \n' + \
                                'the column order of the dump file.'
            common_widgets.append(tk.Label(secondary_gui, text=dump_instrcutions, anchor=tk.W, justify="left"))
            common_widgets.append(entry_int1)
            #common_widgets.append(tk.Label(secondary_gui, text="Input 1 (string)", anchor=tk.W))
            common_widgets.append(entry_str)



            common_widgets.append(tk.Label(secondary_gui, text="\nMaximum number of dump entries to read. Leave blank to read all.", anchor=tk.W))
            common_widgets.append(entry_int2)

        elif option == 3:
            cb1_var = tk.BooleanVar()
            cb2_var = tk.BooleanVar()
            cb3_var = tk.BooleanVar()
            cb4_var = tk.BooleanVar()
            radio_var = tk.IntVar(value=3)

            secondary_entry_str1 = tk.Entry(secondary_gui, width=50)  # Extra width added here
            secondary_entry_int1 = tk.Entry(secondary_gui)
            secondary_entry_int2 = tk.Entry(secondary_gui)
            secondary_entry_str2 = tk.Entry(secondary_gui)
            secondary_entry_str2.insert(0, ".out") # this is how default values have to be specified for tkinter...
            secondary_entry_str3 = tk.Entry(secondary_gui)

            extra_entry_str1 = tk.Entry(secondary_gui)
            extra_cb1_var = tk.BooleanVar()
            extra_cb2_var = tk.BooleanVar()

            # Add extra sample text label at the top of the secondary GUI
            top_sample_label = tk.Label(secondary_gui, text=directory_mode_full_text,
                                        anchor=tk.W, font='16')
            top_sample_label.pack(anchor=tk.W, padx=10, pady=10)

            common_widgets.append(tk.Checkbutton(secondary_gui, text="Also include contents of all subdirectories", variable=cb1_var, anchor=tk.W))
            common_widgets.append(tk.Checkbutton(secondary_gui, text="Include dump files (otherwise, they will be skipped)", variable=cb2_var, anchor=tk.W))

        # Pack common widgets with left alignment.
        for widget in common_widgets:
            widget.pack(anchor=tk.W, padx=10, pady=2)

        if option == 3:
            name_instructions_str = 'In the below 3 fields, specify what characters processed filenames (including the file extension)\n' + \
                                    'must either end with, start with, or contain in order to be processed. Leave blank to ignore.'
            tk.Label(secondary_gui, text=name_instructions_str, anchor=tk.W, justify='left').pack(anchor=tk.W, padx=10, pady=2)

            tk.Label(secondary_gui, text="End of filename character string (suffix)", anchor=tk.W).pack(anchor=tk.W, padx=10, pady=2)
            secondary_entry_str2.pack(anchor=tk.W, padx=10, pady=2)

            tk.Label(secondary_gui, text="Start of filename character string (prefix)", anchor=tk.W).pack(anchor=tk.W, padx=10, pady=2)
            secondary_entry_str3.pack(anchor=tk.W, padx=10, pady=2)

            tk.Label(secondary_gui, text="String which must appear in filename (anywhere)", anchor=tk.W).pack(anchor=tk.W, padx=10, pady=2)
            extra_entry_str1.pack(anchor=tk.W, padx=10, pady=2)


            # Add horizontal separator immediately beneath "Checkbox 2"
            separator = ttk.Separator(secondary_gui, orient='horizontal')
            separator.pack(fill=tk.X, padx=10, pady=10)

            sample_text_label2 = tk.Label(secondary_gui, text="Options for processing standard PHITS tally output files",
                                         anchor=tk.W, font='14')
            sample_text_label2.pack(anchor=tk.W, padx=10, pady=2)

            cb3obj = tk.Checkbutton(secondary_gui, text="Also make and save Pandas DataFrame object of results (in addition to default NumPy array)", variable=cb3_var, anchor=tk.W)
            cb3obj.select() # This makes the checkbox be ticked by default
            cb3obj.pack(anchor=tk.W, padx=10, pady=2)
            cb4obj = tk.Checkbutton(secondary_gui, text="Also calculate absolute uncertainties", variable=cb4_var, anchor=tk.W)
            cb4obj.select() # This makes the checkbox be ticked by default
            cb4obj.pack(anchor=tk.W, padx=10, pady=2)

            options_frame = tk.LabelFrame(secondary_gui, text="Data output format options for dump files")
            tk.Radiobutton(options_frame, text="Save only a dill file of a list of named tuples with dump event information", variable=radio_var, value=1, anchor=tk.W).pack(anchor=tk.W)
            tk.Radiobutton(options_frame, text="Save only a pickle file of a Pandas DataFrame of dump event information", variable=radio_var, value=2, anchor=tk.W).pack(anchor=tk.W)
            tk.Radiobutton(options_frame, text="Save both the named tuples list dill file and the Pandas DataFrame pickle file", variable=radio_var, value=3, anchor=tk.W).pack(anchor=tk.W)



            # Add horizontal separator immediately beneath "Input 3 (integer)"
            separator_1 = ttk.Separator(secondary_gui, orient='horizontal')
            separator_1.pack(fill=tk.X, padx=10, pady=10)

            sample_text_label = tk.Label(secondary_gui, text="Options for processing PHITS tally dump output files",
                                         anchor=tk.W, font='14')
            sample_text_label.pack(anchor=tk.W, padx=10, pady=2)

            options_frame.pack(padx=10, pady=10, anchor=tk.W) # radio buttons

            dir_info_str = "Return extra directional information (relative to the origin and z-axis); \nthis requires all position and direction values [x,y,z,u,v,w] to be included in the dump file."
            tk.Checkbutton(secondary_gui, text=dir_info_str, variable=extra_cb1_var, anchor=tk.W, justify='left').pack(
                anchor=tk.W, padx=10, pady=2)
            tk.Checkbutton(secondary_gui, text="Use degrees (instead of radians) for extra directional information", variable=extra_cb2_var, anchor=tk.W).pack(
                anchor=tk.W, padx=10, pady=2)

            dump_instrcutions = 'If in the same directory as the found dump file exists the corresponding standard tally output file,\n' + \
                                'and the only difference in their file names is the "_dmp" at the end of the dump file, the \n' + \
                                'below two fields can be left blank as PHITS Tools should automatically find this information.\n' + \
                                'Otherwise, in the below two boxes, place what you entered following "dump = " in your PHITS tally.\n' + \
                                'In the first box, enter a nonzero integer between -20 and 20 specifying the number of dump\n' + \
                                'columns and whether the data will be in ASCII (<0) or binary (>0) format.\n' + \
                                'In the second box, enter a sequence of that many numbers, separated by spaces, describing \n' + \
                                'the column order of the dump file.'

            tk.Label(secondary_gui, text=dump_instrcutions, anchor=tk.W, justify='left').pack(anchor=tk.W, padx=10, pady=2)
            secondary_entry_int1.pack(anchor=tk.W, padx=10, pady=2)
            #tk.Label(secondary_gui, text="Input 1 (string)", anchor=tk.W).pack(anchor=tk.W, padx=10, pady=2)
            secondary_entry_str1.pack(anchor=tk.W, padx=10, pady=2)



            tk.Label(secondary_gui, text="\nMaximum number of dump entries to read. Leave blank to read all.", anchor=tk.W).pack(anchor=tk.W, padx=10, pady=2)
            secondary_entry_int2.pack(anchor=tk.W, padx=10, pady=2)



        save_btn = tk.Button(secondary_gui, text="Run PHITS Tools with selected settings", command=save_settings)
        save_btn.pack(pady=10)


    root = tk.Tk()
    root.title('PHITS Tools')

    # protocol for main menu window to issue warning and exit if closed
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    selected_option = tk.IntVar(value=1)

    sample_text_label2 = tk.Label(text="Select what mode PHITS Tools should be ran in:",anchor=tk.W,font='16')
    sample_text_label2.pack(anchor=tk.W, padx=10, pady=2)

    tk.Radiobutton(root, text=standard_mode_full_text, variable=selected_option, value=1).pack(anchor=tk.W)
    tk.Radiobutton(root, text=dump_mode_full_text, variable=selected_option, value=2).pack(anchor=tk.W)
    tk.Radiobutton(root, text=directory_mode_full_text, variable=selected_option, value=3).pack(anchor=tk.W)

    confirm_btn = tk.Button(root, text="Select", command=on_option_selected)
    confirm_btn.pack(pady=4)

    root.mainloop()

    # Print final settings dictionary
    if in_debug_mode:
        print("Settings:", settings)

    if settings['main_mode'] == 1: # standard tally mode
        make_PandasDF = settings['option_1_cb1']
        calculate_absolute_errors = settings['option_1_cb2']
        parse_tally_output_file(Path(settings['file']), make_PandasDF=make_PandasDF,
                                calculate_absolute_errors=calculate_absolute_errors,
                                save_output_pickle=True, prefer_reading_existing_pickle=False)

    elif settings['main_mode'] == 2:  # dump tally mode
        output_file_path = Path(settings['file'])
        return_directional_info = settings['option_2_cb1']
        use_degrees = settings['option_2_cb2']
        save_namedtuple_list = False
        save_Pandas_dataframe = False
        if settings['radio'] == 1:
            save_namedtuple_list = True
        elif settings['radio'] == 2:
            save_Pandas_dataframe = True
        elif settings['radio'] == 3:
            save_namedtuple_list = True
            save_Pandas_dataframe = True
        dump_data_number = settings['input_int1']
        if dump_data_number != None: dump_data_number = int(dump_data_number)
        dump_data_sequence = settings['input_str']
        max_entries_read = settings['input_int2']
        if max_entries_read != None: max_entries_read = int(max_entries_read)

        if dump_data_number == None:
            dump_data_number, dump_data_sequence = search_for_dump_parameters(output_file_path)
            if dump_data_number == None or dump_data_sequence == None:
                raise ValueError(
                    'You MUST provide a space-delimited list of integers to the -dvals / --dump_data_sequence input specifying ' +
                    'how the data columns in the dump file are to be interpreted, the same as the line following "dump = " in your PHITS tally input. ' +
                    'An attempt was made to automatically find these values, but it failed (thus, manual specification is required).')
        parse_tally_dump_file(output_file_path, dump_data_number, dump_data_sequence,
                              return_directional_info=return_directional_info, use_degrees=use_degrees,
                              max_entries_read=max_entries_read,
                              return_namedtuple_list=False,
                              return_Pandas_dataframe=False,
                              save_namedtuple_list=save_namedtuple_list,
                              save_Pandas_dataframe=save_Pandas_dataframe)

    elif settings['main_mode'] == 3:  # directory mode
        recursive_search = settings['option_3_cb1']
        include_dump_files = settings['option_3_cb2']
        make_PandasDF = settings['option_3_cb3']
        calculate_absolute_errors = settings['option_3_cb4']
        file_suffix = settings['input_str_2']
        if file_suffix == None: file_suffix = ''
        file_prefix = settings['input_str_3']
        if file_prefix == None: file_prefix = ''
        file_reqstr = settings['input_str_6']
        if file_reqstr == None: file_reqstr = ''

        save_namedtuple_list = False
        save_Pandas_dataframe = False
        if settings['radio'] == 1:
            save_namedtuple_list = True
        elif settings['radio'] == 2:
            save_Pandas_dataframe = True
        elif settings['radio'] == 3:
            save_namedtuple_list = True
            save_Pandas_dataframe = True
        dump_data_sequence = settings['input_str_1']
        dump_data_number = settings['input_int_1']
        if dump_data_number != None: dump_data_number = int(dump_data_number)
        max_entries_read = dump_data_number = settings['input_int_2']
        if max_entries_read != None: max_entries_read = int(max_entries_read)
        return_directional_info = settings['extra_cb1']
        use_degrees = settings['extra_cb2']

        parse_all_tally_output_in_dir(Path(settings['directory']),
                                      output_file_suffix=file_suffix, output_file_prefix=file_prefix,
                                      output_file_required_string=file_reqstr, include_subdirectories=recursive_search,
                                      return_tally_output=False,
                                      make_PandasDF=make_PandasDF, calculate_absolute_errors=calculate_absolute_errors,
                                      save_output_pickle=True, prefer_reading_existing_pickle=False,
                                      include_dump_files=include_dump_files,
                                      dump_data_number=dump_data_number, dump_data_sequence=dump_data_sequence,
                                      dump_return_directional_info=return_directional_info,
                                      dump_use_degrees=use_degrees,
                                      dump_max_entries_read=max_entries_read,
                                      dump_save_namedtuple_list=save_namedtuple_list,
                                      dump_save_Pandas_dataframe=save_Pandas_dataframe
                                      )

    else:
        raise ValueError('ERROR: Main mode for PHITS Tools not selected correctly in first GUI')








elif test_explicit_files_dirs:
    #base_path = r'G:\Cloud\OneDrive\work\PHITS\test_tallies\tally\\'
    #output_file_path = Path(base_path + 't-deposit\deposit_reg.out')
    #output_file_path = Path(base_path + 't-deposit\deposit_eng_sp-reg.out')
    #output_file_path = Path(base_path + 't-track\\track_reg.out')
    #output_file_path = Path(base_path + 't-track\\track_r-z.out')
    #output_file_path = Path(base_path + 't-track\\track_xyz-xy.out')
    #output_file_path = Path(base_path + r't-track\track_r-z_axis-rad.out')
    #output_file_path = Path(base_path + r't-track\track_r-z_axis-deg.out')
    #output_file_path = Path(base_path + 't-deposit\deposit_r-z.out')
    #output_file_path = Path(base_path + 't-deposit\deposit_r-z_2dtype4.out')
    #output_file_path = Path(base_path + 't-deposit\deposit_r-z_2dtype5.out')
    #output_file_path = Path(base_path + 't-deposit\deposit_xyz_2dtype5.out')
    #output_file_path = Path(base_path + 'tet_test\deposit-tet_axis-tet.out')
    #output_file_path = Path(base_path + 'tet_test\deposit-tet_axis-eng.out')
    #output_file_path = Path(base_path + 't-cross\cross_reg_axis-eng.out')
    #output_file_path = Path(base_path + 't-cross\cross_reg_axis-reg.out')
    #output_file_path = Path(base_path + 't-cross\cross_xyz_axis-eng.out')
    #output_file_path = Path(base_path + 't-cross\cross_xyz_axis-eng_enclosed.out')
    #output_file_path = Path(base_path + 't-cross\cross_xyz_axis-reg.out')
    #output_file_path = Path(base_path + 't-cross\cross_xyz_axis-xy.out')
    #output_file_path = Path(base_path + 't-cross\cross-r-z_axis-eng.out')
    #output_file_path = Path(base_path + 't-cross\cross-r-z_axis-eng_0r.out')
    #output_file_path = Path(base_path + 't-cross\cross-r-z_axis-eng_enclosed.out')
    #output_file_path = Path(base_path + 't-cross\complex\proton_in_hist_rz.out')
    #output_file_path = Path(base_path + 't-cross\complex\\neutron_yield_rz-e-a-mesh.out')
    #output_file_path = Path(base_path + 't-cross\complex\\neutron_yield.out')
    #output_file_path = Path(base_path + 't-cross\complex\\xtra_neutron_yield_EvsTheta_whole-target.out')
    #output_file_path = Path(base_path + 't-dpa\dpa_reg.out')
    #output_file_path = Path(base_path + 't-dpa\dpa_xyz.out')
    #output_file_path = Path(base_path + 't-dpa\dpa_r-z.out')
    #output_file_path = Path(base_path + 'samepage\\proton_in_hist_rz_axis-eng_samepage-z.out')
    #output_file_path = Path(base_path + 'samepage\\proton_in_hist_rz_reduced.out') # has NULL characters in it
    #output_file_path = Path(base_path + 'samepage\\proton_in_hist_rz_sp-eng.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg_axis-e21.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg_axis-t-e1.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg_axis-t-e2.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg_axis-e1-t.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg_axis-e2-t.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg_axis-eng1.out')
    #output_file_path = Path(base_path + 't-deposit2\deposit2_reg_axis-eng2.out')
    #output_file_path = Path(base_path + 't-heat\heat_reg.out')
    #output_file_path = Path(base_path + 't-heat\heat_xyz.out')
    #output_file_path = Path(base_path + 't-interact\interact_reg.out')
    #output_file_path = Path(base_path + 't-interact\interact_xyz.out')
    #output_file_path = Path(base_path + 't-let\let-distribution_reg.out')
    #output_file_path = Path(base_path + 't-let\let-distribution_r-z.out')
    #output_file_path = Path(base_path + r't-point\point.out')
    #output_file_path = Path(base_path + r't-point\ring.out')
    #output_file_path = Path(base_path + 't-product\product_reg.out')
    #output_file_path = Path(base_path + 't-sed\y-distribution_reg.out')
    #output_file_path = Path(base_path + 't-sed\y-distribution_xyz.out')
    #output_file_path = Path(base_path + r't-time\time_reg.out')
    #output_file_path = Path(base_path + r't-time\time_xyz.out')
    #output_file_path = Path(base_path + r't-yield\yield_reg_axis-charge.out')
    #output_file_path = Path(base_path + r't-yield\yield_reg_axis-mass.out')
    #output_file_path = Path(base_path + r't-yield\yield_reg_axis-chart.out')
    #output_file_path = Path(base_path + r't-yield\yield_xyz_axis-chart.out')

    base_path = r'G:\Cloud\OneDrive\work\PHITS\test_tallies\\'
    #output_file_path = Path(base_path + r'tally\t-deposit\deposit_reg_spec-all.out')
    #output_file_path = Path(base_path + r'sample\icrp\mrcp\External\result\Dose_MRCP-AF_reg.out')
    #output_file_path = Path(base_path + r'sample\misc\batch_source\track_yz_001.out')
    #output_file_path = Path(base_path + r'sample\source\Cosmicray\GCR-ground\cross.out')
    #output_file_path = Path(base_path + r'recommendation\Fusion\track.out')
    #output_file_path = Path(base_path + r'sample\benchmark\Iwamoto-JNST2022\case5-isis800\output\rr_air_model.out')
    #output_file_path = Path(base_path + r'recommendation\muon\product.out')
    #output_file_path = Path(base_path + r'recommendation\BNCT\dose.out')
    #output_file_path = Path(base_path + r'recommendation\SemiConductor\deposit.out')
    #output_file_path = Path(base_path + r'recommendation\Shielding\track-rz.out')
    output_file_path = Path(base_path + r'recommendation\TrackStructure\interact.out')


    test_parsing_of_dir = False #True
    if test_parsing_of_dir:
        dir_path = output_file_path = Path(base_path + 't-cross\complex\proton_in_hist_rz.out')
        dir_output_list = parse_all_tally_output_in_dir(dir_path)
        print(dir_output_list)
        sys.exit()


    test_dump_file = False
    if test_dump_file:
        dump_file_path = Path(base_path + 't-cross\complex\\neutron_yield_dmp.out')
        dump_control_str = '2   3   4   5   6   7   8  10'
        #nt_list, df = parse_tally_dump_file(dump_file_path,8,dump_control_str, save_namedtuple_list=True, save_Pandas_dataframe=True)
        # test automatic finding of dump parameters
        nt_list, df = parse_tally_dump_file(dump_file_path, save_namedtuple_list=True, save_Pandas_dataframe=True)

        # test dill of namedtuple list
        import dill
        path_to_pickle_file = Path(base_path + 't-cross\complex\\neutron_yield_dmp_namedtuple_list.dill')
        with open(path_to_pickle_file, 'rb') as handle:
            nt_list_dill = dill.load(handle)

        if nt_list==nt_list_dill: print('It works!')

        sys.exit()



    tally_output_filepath = output_file_path
    tally_output = parse_tally_output_file(tally_output_filepath, make_PandasDF=True, calculate_absolute_errors=True,
                                           save_output_pickle=True)
    tally_data = tally_output['tally_data']
    tally_metadata = tally_output['tally_metadata']

    #pprint.pp(dict(tally_metadata))
    #                ir, iy, iz, ie, it, ia, il, ip, ic, ierr
    print(tally_data[ :,  0,  0,  :,  0,  0,  0,  0,  0, 0])
    print(tally_data[ :,  0,  0,  :,  0,  0,  0,  0,  0, 1])
    print(tally_data[0, :, :, 0, 0, 0, 0, 0, 0, 0])
    print(np.shape(tally_data))

    #print(tally_data[ 1,  0,  0,  0,  0,  0,  0,  0,  :, 0])
    #print(tally_metadata['nuclide_ZZZAAAM_list'])
    #print(tally_metadata['nuclide_isomer_list'])

    #ic = tally_metadata['nuclide_ZZZAAAM_list'].index(10020)
    #print(tally_data[1, 0, 0, 0, 0, 0, 0, 0, ic, 0])








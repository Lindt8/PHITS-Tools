'''

This module serves to function as a library of functions related to DCHAIN which can be easily
imported into and used by scripts for processing DCHIAN output.  They are summarized below.

###  Main function for DCHAIN output parsing
- `process_dchain_simulation_output`           : **This is main master function for parsing DCHAIN output and is generally the function one should use for this purpose.**  It processes all DCHAIN output for a given DCHAIN run.


###  DCHAIN output file parsing
- `parse_DCHAIN_act_file`                      : parser for the *.act file from DCHAIN
- `generate_nuclide_time_profiles`             : processes nuclide output from parse_DCHAIN_act_file into a more usable form
- `parse_DCS_file_from_DCHAIN`                 : parser for the *.dcs file from DCHAIN
- `parse_dtrk_file`                            : parser for the *.dtrk file from PHITS meant for DCHAIN
- `parse_dyld_files`                           : parser for the *.dyld files from PHITS meant for DCHAIN


###  DCHAIN output data plotting
- `plot_top10_nuclides`                        : generates a nice visualization on the ranking of nuclides


### Relating to DCHAIN data libraries

- `rxn_to_dchain_str`                          : converts a reaction to the format used by the neutron reaction cross section libraries
- `ZZZAAAM_to_dchain_xs_lib_str`               : converts a ZZZAAAM number to the 7-character nuclide string used by the n rxn xs libs
- `ECCO1968_Ebins`                             : returns the n highest energy bins of the ECCO 1968-group structure
- `retrieve_rxn_xs_from_lib`                   : returns cross section for a reaction from a provided n rxn xs library file
- `calc_one_group_nrxn_xs_dchain`              : provided a neutron flux, reaction, and library file, determine 1-grp nrxn xs


### For handling nuclide names and identities with DCHAIN

- `Dname_to_ZAM`                               : converts a DCHAIN-formatted nuclide name to a ZZZAAAM number
- `ZAM_to_Dname`                               : converts a ZZZAAAM number to a DCHAIN-formatted nuclide name
- `Dname_to_Latex`                             : converts a DCHAIN-formatted nuclide name to pretty LaTeX formatting
- `nuclide_plain_str_to_Dname`                 : converts a plaintext string for a nuclide to a DCHAIN-formatted nuclide name string


###  Other
- `parse_DCHAIN_act_file_legacy`               : legacy version of parse_DCHAIN_act_file from before error implementation
- `generate_nuclide_time_profiles_legacy`      : legacy version of generate_nuclide_time_profiles from before error implementation
- `find`                                       : return index of the first instance of a value in a list
- `Element_Z_to_Sym`                           : returns elemental symbol provided the atomic number Z
- `Element_Sym_to_Z`                           : returns an atomic number Z provided the elemental symbol
- `Element_ZorSym_to_name`                     : returns a string of the name of an element provided its atomic number Z or symbol
- `Element_ZorSym_to_mass`                     : returns the average atomic mass of an element provided its atomic number Z or symbol
- `nuclide_to_Latex_form`                      : form a LaTeX-formatted string of a nuclide provided its information
- `nuclide_plain_str_to_latex_str`             : convert a plaintext string for a nuclide to a LaTeX formatted raw string
- `nuclide_plain_str_ZZZAAAM`                  : convert a plaintext string for a nuclide to an integer ZZZAAAM value
- `time_str_to_sec_multiplier`                 : determine multiplier to convert a time unit to seconds
- `seconds_to_dhms`                            : convert a time in seconds to a string of human-relatable time units
- `seconds_to_ydhms`                           : convert a time in seconds to a string of human-relatable time units (also with years)

'''


import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import time
import re
import bisect
import unicodedata as ud
try:
    from munch import *
except:
    pass
try:
    from Hunters_tools import fancy_plot
    Hunters_tools_is_available = True
except:
    Hunters_tools_is_available = False

if __name__ == "__main__":
    in_dchain_tools_debug_mode = True
else:
    in_dchain_tools_debug_mode = False

def process_dchain_simulation_output(simulation_folder_path,simulation_basename,dtrk_filepath=None,dyld_filepath=None,process_DCS_file=False):
    '''
    Description:
        This is intended to be a single master function for processing DCHAIN output.

    Dependencies:
        from munch import *

    Inputs:
        - `simulation_folder_path` = text string of path to folder containing simulation output (should end with forward slash `/` or backslash `\`)
        - `simulation_basename` = common string of the DCHAIN simulations; output files are named THIS_NAME.*
        - `dtrk_filepath` = file path to \*.dtrk file, only necessary if it has a different basename and there are multiple \*.dtrk files in the folder
        - `dyld_filepath` = file path to \*.dyld files, only necessary if it has a different basename and there are multiple \*.dyld files in the folder
        - `process_DCS_file` (optional) = Boolean variable specifying whether the DCS file should be processed too. (D=False)

    Outputs:
        - `dchain_output` = a dictionary object containing all information from DCHAIN's output files.  See the keys breakdown below.

            Technically, it tries to return a "munchify" object which can be used both exactly like a dictionary but also
            provides attribute-style access like a namedtuple or Class object such as `dchain_output.time.of_EOB_sec` rather
            than the dictionary style `dchain_output['time']['of_EOB_sec']`


    dchain_output dictionary structure:
    --------
        # Notation for output array dimensions
        #   R  regions
        #   T  time steps
        #   N  max number of nuclides found in a single region
        #   E  number of gamma energy bins
        # le10 for top 10 lists, a number <= 10

        {
        dchain_output = {
        'time':{                            #  ~  Time information
            'from_start_sec'                # [T] list of times from start time [sec]
            'from_EOB_sec'                  # [T] times from end of final bombardment [sec]
            'of_EOB_sec'                    #     scalar time of end of final bombardment [sec]
            }

        'region':{                          #  ~  Information which only varies with region
            'numbers'                       # [R] region numbers
            'number'                        # [R] region numbers
            'irradiation_time_sec'          # [R] irradiation time per region
            'volume'                        # [R] volume in [cc] per region
            'neutron_flux'                  # [R] neutron flux in [n/cm^2/s] per region
            'beam_power_MW'                 # [R] beam power in [MW] per region
            'beam_energy_GeV'               # [R] beam energy in [GeV] per region
            'beam_current_mA'               # [R] beam current in [mA] per region
            }

        'nuclides':{                        #  ~  Main nuclide results from *.act file
            'names'                         # [R][N] names of nuclides produced in each region
            'TeX_names'                     # [R][N] LaTeX-formatted names of nuclides produced
            'ZZZAAAM'                       # [R][N] ZZZAAAM values (=10000Z+10A+M) of nuclides
                                            #        (ground state m=0, metastable m=1,2,etc.)
            'half_life'                     # [R][N] half lives of nuclides produced [sec]
            'inventory':{'value'            # [R][T,N] atoms [#/cc]
                         'error'}           # [R][T,N] atoms [#/cc]
            'activity':{'value'             # [R][T,N] activity [Bq/cc]
                        'error'}            # [R][T,N] activity [Bq/cc]
            'dose_rate':{'value'            # [R][T,N] dose-rate [uSv/h*m^2]
                         'error'}           # [R][T,N] dose-rate [uSv/h*m^2]
            'decay_heat':{
                'total':{'value'            # [R][T,N] total decay heat [W/cc]
                         'error'}           # [R][T,N] total decay heat [W/cc]
                'beta':{'value'             # [R][T,N] beta decay heat [W/cc]
                        'error'}            # [R][T,N] beta decay heat [W/cc]
                'gamma':{'value'            # [R][T,N] gamma decay heat [W/cc]
                         'error'}           # [R][T,N] gamma decay heat [W/cc]
                'alpha':{'value'            # [R][T,N] alpha decay heat [W/cc]
                         'error'}           # [R][T,N] alpha decay heat [W/cc]
                }
            'column_headers'                # Length 7 list of the *.act columns' descriptions
            'total':{                       #  ~  Total values summed over all nuclides
                'activity':{'value'         # [R][T] total activity [Bq/cc]
                            'error'}        # [R][T] total activity [Bq/cc]
                'decay_heat':{'value'       # [R][T] total decay heat [W/cc]
                              'error'}      # [R][T] total decay heat [W/cc]
                'beta_heat':{'value'        # [R][T] total beta decay heat [W/cc]
                             'error'}       # [R][T] total beta decay heat [W/cc]
                'gamma_heat':{'value'       # [R][T] total gamma decay heat [W/cc]
                              'error'}      # [R][T] total gamma decay heat [W/cc]
                'alpha_heat':{'value'       # [R][T] total alpha decay heat [W/cc]
                              'error'}      # [R][T] total alpha decay heat [W/cc]
                'activated_atoms':{'value'  # [R][T] total activated atoms [#/cc]
                                   'error'} # [R][T] total activated atoms [#/cc]
                'gamma_dose_rate':{'value'  # [R][T] total gamma dose rate [uSV/h*m^2]
                                   'error'} # [R][T] total gamma dose rate [uSV/h*m^2]
                }
            }

        'gamma':{                           #  ~  Gamma spectra and totals
            'spectra':{
                'group_number'              # [R][T,E] group number
                'E_lower'                   # [R][T,E] bin energy lower-bound [MeV]
                'E_upper'                   # [R][T,E] bin energy upper-bound [MeV]
                'flux':{'value'             # [R][T,E] flux [#/s/cc]
                        'error'}            # [R][T,E] flux [#/s/cc]
                'energy_flux':{'value'      # [R][T,E] energy flux [MeV/s/cc]
                               'error'}     # [R][T,E] energy flux [MeV/s/cc]
                }
            'total_flux':{'value'           # [R][T] total gamma flux [#/s/cc]
                          'error'}          # [R][T] total gamma flux [#/s/cc]
            'total_energy_flux':{'value'    # [R][T] total gamma energy flux [MeV/s/cc]
                                 'error'}   # [R][T] total gamma energy flux [MeV/s/cc]
            'annihilation_flux':{'value'    # [R][T] annihilation gamma flux [#/s/cc]
                                 'error'}   # [R][T] annihilation gamma flux [#/s/cc]
            'current_underflow':{'value'    # [R][T] gamma current underflow [#/s]
                                 'error'}   # no error reported
            'current_overflow':{'value'     # [R][T] gamma current overflow [#/s]
                                'error'}    # no error reported
            }

        'top10':{                           #  ~  Top 10 lists from *.act file
            'activity':{
                'rank'                      # [R][T,le10] rank
                'nuclide'                   # [R][T,le10] nuclide name
                'value'                     # [R][T,le10] activity [Bq/cc]
                'error'                     # [R][T,le10] activity [Bq/cc]
                'percent'                   # [R][T,le10] percent of total activity
                }
            'decay_heat':{
                'rank'                      # [R][T,le10] rank
                'nuclide'                   # [R][T,le10] nuclide name
                'value'                     # [R][T,le10] decay heat [W/cc]
                'error'                     # [R][T,le10] decay heat [W/cc]
                'percent'                   # [R][T,le10] percent of total decay heat
                }
            'gamma_dose':{
                'rank':                     # [R][T,le10] rank
                'nuclide'                   # [R][T,le10] nuclide name
                'value'                     # [R][T,le10] dose-rate [uSv/h*m^2]
                'error'                     # [R][T,le10] dose-rate [uSv/h*m^2]
                'percent'                   # [R][T,le10] percent of total gamma dose rate
                }
            }

        'number_of':{                       #  ~  Maximum values of R, T, N, and E
            'regions'                       #  R  = total number of regions
            'time_steps'                    #  T  = total number of time steps
            'max_nuclides_in_any_region'    #  N  = maximum unique nuclides found in any region
            'gamma_energy_bins'             #  E  = number of gamma energy bins (default=42)
            }

        }

        if process_dtrk_file:
        dchain_output.update({
        'neutron':{                         #  ~  Neutron spectra and totals
            'spectra':{                     #  -  Actual values used in DCHAIN
                'E_lower'                   # [R][E] bin energy lower-bound [MeV]
                'E_upper'                   # [R][E] bin energy upper-bound [MeV]
                'flux':{'value'             # [R][E] neutron flux [#/s/cm^2]
                        'error'}            # [R][E] neutron flux [#/s/cm^2]
                }
            'total_flux':{'value'           # [R] total neutron flux [#/s/cm^2]
                          'error'}          # [R] total neutron flux [#/s/cm^2]
            'unit_spectra':{                #  -  Flux per unit source particle
                'E_lower'                   # [R][E] bin energy lower-bound [MeV]
                'E_upper'                   # [R][E] bin energy upper-bound [MeV]
                'flux':{'value'             # [R][E] neutron flux [#/s/cm^2/s.p.]
                        'error'}            # [R][E] neutron flux [#/s/cm^2/s.p.]
                }
            }
        })

        if process_dyld_files:
        dchain_output.update({
        'yields':{                          #  ~  Yield spectra
            'all_names'                     # [N] names of all nuclides produced
            'names'                         # [R][N] names of nuclides produced in each region
            'TeX_names'                     # [R][N] LaTeX-formatted names of nuclides produced
            'ZZZAAAM'                       # [R][N] ZZZAAAM values (=10000Z+10A+M) of nuclides
                                            #        (ground state m=0, metastable m=1,2,etc.)
            'rate':{                        #  -  Actual values used in DCHAIN (100% beam power)
                   'value'                  # [R][E] nuclide yield rate [#/s/cm^3]
                   'error'                  # [R][E] nuclide yield rate [#/s/cm^3]
                }
            'unit_spectra':{                #  -  Yields per unit source particle
                   'value'                  # [R][E] nuclide yield rate [#/s.p.]
                   'error'                  # [R][E] nuclide yield rate [#/s.p.]
                }
            }
        })

        if process_DCS_file: # add extra information
            # Notation for output array dimensions
            #   R  (n_reg)    regions
            #   Td (ntsteps)  time steps in DCS file (usually differs from that of *.act file!)
            #   Nd (nnuc_max) max number of nuclides (this index differs from the *.act N index)
            #   C  (chni_max) maximum index of relevant chains
            #   L  (chln_max) maximum number of links per chain

        dchain_output.update({

        'DCS':{
            'time':{
                'from_start_sec'            # [Td] list of times from start time [sec]
                'from_EOB_sec'              # [Td] times from end of final bombardment [sec]
                'of_EOB_sec'                #      scalar time of end of final bombardment [sec]
                }

            'number_of':{                   #  ~  Maximum values of R, Td, Nd, C, and L
                'regions'                   #  R  = total number of regions
                'time_steps'                #  Td = total number of time steps
                'max_nuclides'              #  Nd = max number of end nuclides in any time step
                'max_number_of_chains'      #  C  = highest index of a relevant chain found
                'max_chain_length'          #  L  = max number of links (nuclides) in any chain
                }

            'end_nuclide':{                 #  ~  Informtaion on nuclides ending each chain
                'names'                     # [R][Td,Nd] nuclide names
                'inventory':{
                    'N_previous'            # [R][Td,Nd,C] N in previous time step [atoms/cc]
                    'N_now'                 # [R][Td,Nd,C] N in current time step [atoms/cc]
                    'dN'                    # [R][Td,Nd,C] change in N of end nuclide from
                                            #              prev. to current time step [atoms/cc]
                    }
                'activity':{
                    'A_previous'            # [R][Td,Nd,C] A in previous time step [Bq/cc]
                    'A_now'                 # [R][Td,Nd,C] A in the current time step [Bq/cc]
                    'dA'                    # [R][Td,Nd,C] change in A of end nuclide from
                                            #              prev. to current time step [Bq/cc]
                    }
                }

            'chains':{                      #  ~  Chains, links, and their contributions
                'indices_of_printed_chains' # [R][Td,Nd]     list of chain indices printed to
                                            #                *.dcs, valid values of C index
                'length'                    # [R][Td,Nd,C]   length of listed chain, L max index
                'link_nuclides'             # [R][Td,Nd,C,L] strings of nuclides in each chain
                'link_decay_modes'          # [R][Td,Nd,C,L] strings of decay modes each link
                                            #                undergoes to produce the next link
                'link_dN':{                 # (only filled if values in file, 'None' otherwise)
                    'beam'                  # [R][Td,Nd,C,L] beam contribution to dN per link
                    'decay_nrxn'            # [R][Td,Nd,C,L] decay/neutron rxn dN contribution
                    'total'                 # [R][Td,Nd,C,L] total contribution to dN per link
                    }
                }

            'relevant_nuclides':{           #  ~  A vs t of nuclides over relevancy threshold
                'names'                     # [R]        list of relevant nuclides per region
                'times'                     # [R][Td,Nd] time [s]
                'inventory'                 # [R][Td,Nd] inventory [atm/cc]
                'activity'                  # [R][Td,Nd] activity [Bq/cc]
                }
            }
        })

    '''
    global start

    try:
        start_time = start
    except:
        start_time = time.time()
    start = start_time 

    if simulation_basename[-3:] == '.in': simulation_basename = simulation_basename[:-3]
    simulation_file_basic_path = simulation_folder_path + simulation_basename # only need to add output file extension

    act_file = simulation_file_basic_path + '.act'
    dcs_file = simulation_file_basic_path + '.dcs'

    process_dtrk_file = True
    if dtrk_filepath: # DTRK file manually provided
        dtrk_file = dtrk_filepath
        if not os.path.exists(dtrk_file):
            print('    Provided .dtrk file could not be found: {}'.format(dtrk_filepath))
            process_dtrk_file = False
    else: # automatically find DTRK file
        dtrk_file = simulation_file_basic_path + '.dtrk'
        if not os.path.exists(dtrk_file):
            # look for any files with the .dtrk extension in the simulation folder path
            valid_files = []
            valid_filepaths = []
            for file in os.listdir(simulation_folder_path):
                if file.endswith(".dtrk"):
                    valid_files.append(file)
                    valid_filepaths.append(os.path.join(simulation_folder_path, file))
            if len(valid_files)>0:
                print('    Could not find default .dtrk file {}, using {} in same directory instead.'.format(simulation_basename + '.dtrk',valid_files[0]))
                dtrk_file = valid_filepaths[0]
            else:
                print('    No .dtrk files could not be found in provided simulation folder: {}'.format(simulation_folder_path))
                process_dtrk_file = False

    if process_dtrk_file:
        neutron_flux, dtrk_metadata = parse_dtrk_file(dtrk_file,return_metadata=True)

    process_dyld_file = True
    if dyld_filepath: # dyld file manually provided
        dyld_file = dyld_filepath
        if not os.path.exists(dyld_file):
            print('    Provided .dyld file could not be found: {}'.format(dyld_filepath))
            process_dyld_file = False
    else: # automatically find dyld file
        dyld_file = simulation_file_basic_path + '.dyld'
        if not os.path.exists(dyld_file):
            # look for any files with the .dyld extension in the simulation folder path
            valid_files = []
            valid_filepaths = []
            for file in os.listdir(simulation_folder_path):
                if file.endswith(".dyld"):
                    valid_files.append(file)
                    valid_filepaths.append(os.path.join(simulation_folder_path, file))
            if len(valid_files)>0:
                print('    Could not find default .dyld file {}, using {} in same directory instead.'.format(simulation_basename + '.dyld',valid_files[0]))
                dyld_file = valid_filepaths[0]
            else:
                print('    No .dyld files could not be found in provided simulation folder: {}'.format(simulation_folder_path))
                process_dyld_file = False

    print('{:<50}     ({:0.2f} seconds elapsed)'.format('\tParsing DCHAIN activation file...',time.time()-start))

    parse_DCHAIN_act_file_OUTPUT = parse_DCHAIN_act_file(act_file)
    reg_nos           = parse_DCHAIN_act_file_OUTPUT[0]  # length R list of region numbers
    time_list_sec     = parse_DCHAIN_act_file_OUTPUT[1]  # length T list of measurement times (in sec) from start of irradiation
    time_list_sec_after_EOB = parse_DCHAIN_act_file_OUTPUT[2] # length T list of measurement times (in sec) from end of last irradiation
    irradiation_end_t = parse_DCHAIN_act_file_OUTPUT[3]  # time of end of irradiation (in sec)
    nuclides_produced = parse_DCHAIN_act_file_OUTPUT[4]  # NumPy array of dimension RxTxNx11x2 of nuclide table data (N=max recorded table lenth) (last index 0=value, 1=abs error) [0='nuclide',1='atoms [#/cc]',2='activity [Bq/cc]',3='activity [Bq]',4='rate [%]',5='beta decay heat [W/cc]',6='gamma decay heat [W/cc]',7='alpha decay heat [W/cc]',8='total decay heat [W/cc]',9='half life [s]',10='dose-rate [uSv/h*m^2]']
    gamma_spectra     = parse_DCHAIN_act_file_OUTPUT[5]  # NumPy array of dimension RxTxEx5x2 of gamma spectrum table data (last index 0=value, 1=abs error) [0='group number',1='bin energy lower-bound [MeV]',2='bin energy upper-bound [MeV]',3='flux [#/s/cc]',4='energy flux [MeV/s/cc]']
    top10_lists       = parse_DCHAIN_act_file_OUTPUT[6]  # NumPy array of dimension RxTxNx12x2 of top-10 list table data (last index 0=value, 1=abs error) [0='rank',1='nuclide -  Activity ranking',2='activity [Bq/cc]',3='activity [Bq]',4='rate [%]',5='nuclide - Decay heat ranking',6='decay heat [W/cc]',7='decay heat [W]',8='rate [%]',9='nuclide - Dose rate ranking',10='dose-rate [uSv/h*m^2]',11='rate [%]']
    column_headers    = parse_DCHAIN_act_file_OUTPUT[7]  # List containing 3 lists of column headers for the preceding three NumPy arrays
    summary_info      = parse_DCHAIN_act_file_OUTPUT[8]  # list of the below lists/arrays of summary information
    r_summary_info              = summary_info[0]  # NumPy array of dimension Rx7 of region-specific summary info [0='region number',1='irradiation time [s]',2='region volume [cc]',3='neutron flux [n/cm^2/s]',4='beam power [MW]',5='beam energy [GeV]',6='beam current [mA]']
    r_summary_info_description  = summary_info[1]  # list of length 7 containing descriptions of the above items [0='region number',1='irradiation time [s]',2='region volume [cc]',3='neutron flux [n/cm^2/s]',4='beam power [MW]',5='beam energy [GeV]',6='beam current [mA]']
    rt_summary_info             = summary_info[2]  # NumPy array of dimension RxTx12x2 of region and time-specific summary info (last index 0=value, 1=abs error) [0='total gamma flux [#/s/cc]',1='total gamma energy flux [MeV/s/cc]',2='annihilation gamma flux [#/s/cc]',3='gamma current underflow [#/s]',4='gamma current overflow [#/s]',5='total activity [Bq/cc]',6='total decay heat [W/cc]',7='beta decay heat [W/cc]',8='gamma decay heat [W/cc]',9='alpha decay heat [W/cc]',10='activated atoms [#/cc]',11='total gamma dose rate [uSV/h*m^2]']
    rt_summary_info_description = summary_info[3]  # list of length 12 containing descriptions of the above items [0='total gamma flux [#/s/cc]',1='total gamma energy flux [MeV/s/cc]',2='annihilation gamma flux [#/s/cc]',3='gamma current underflow [#/s]',4='gamma current overflow [#/s]',5='total activity [Bq/cc]',6='total decay heat [W/cc]',7='beta decay heat [W/cc]',8='gamma decay heat [W/cc]',9='alpha decay heat [W/cc]',10='activated atoms [#/cc]',11='total gamma dose rate [uSV/h*m^2]']


    if in_dchain_tools_debug_mode: print('{:<50}     ({:0.2f} seconds elapsed)'.format('    Restructuring nuclide data table array...',time.time()-start))

    generate_nuclide_time_profiles_OUTPUT = generate_nuclide_time_profiles(nuclides_produced)
    nuclide_names        = generate_nuclide_time_profiles_OUTPUT[0]  # List of length R of lists containing names of nuclides produced in each region
    LaTeX_nuclide_names  = generate_nuclide_time_profiles_OUTPUT[1]  # List of length R of lists containing LaTeX-formatted names of nuclides produced in each region
    nuclide_ZAM_vals     = generate_nuclide_time_profiles_OUTPUT[2]  # List of length R of lists containing ZZZAAAM values (=10000*Z+10*A+M) of nuclides produced in each region (ground state m=0, metastable m=1,2,etc.)
    nuclide_half_lives   = generate_nuclide_time_profiles_OUTPUT[3]  # List of length R of lists containing half lives of nuclides produced in each region (in seconds)
    nuclide_info         = generate_nuclide_time_profiles_OUTPUT[4]  # List of length R of NumPy arrays of dimension TxNx7x2 of nuclide info (last index 0=value, 1=abs error) [0='atoms [#/cc]',1='activity [Bq/cc]','2=beta decay heat [W/cc]','3=gamma decay heat [W/cc]','4=alpha decay heat [W/cc]','5=total decay heat [W/cc]','6=dose-rate [uSv/h*m^2]']
    nuclide_info_headers = generate_nuclide_time_profiles_OUTPUT[5]  # List of length 7 containing text descriptions of the 7 columns of the info arrays [0='atoms [#/cc]',1='activity [Bq/cc]','2=beta decay heat [W/cc]','3=gamma decay heat [W/cc]','4=alpha decay heat [W/cc]','5=total decay heat [W/cc]','6=dose-rate [uSv/h*m^2]']


    if process_dyld_file:
        if process_dtrk_file:
            if dtrk_metadata[0]=='dchain':
                iredufmt=1
            else: # dtrk_metadata[0]=='eng'
                iredufmt=0
        else:
            iredufmt=0
        yields, nuclide_names_yld = parse_dyld_files(dyld_file,iredufmt=iredufmt)

        # Now reformat for more user-friendly output values
        # regionwise values
        beam_fluxs = (6.2415064e15)*r_summary_info[:,6] # particles/sec (converted from mA)
        reg_vols = r_summary_info[:,2]
        nregs,nnuc = np.shape(yields)[0],np.shape(yields)[1]
        reg_yld_names = []
        reg_yld_texnames = []
        reg_yld_zam = []
        yield_values_by_reg = [[],[],[],[]] # yield, yield abs err, unit yield, unit yield abs err
        for ri in range(nregs):
            for ni in range(nnuc):
                if ni==0:
                    reg_yld_names.append([])
                    reg_yld_texnames.append([])
                    reg_yld_zam.append([])
                    for j in range(4):
                        yield_values_by_reg[j].append([])
                if yields[ri,ni,0] != 0.0:
                    reg_yld_names[-1].append(nuclide_names_yld[ni])
                    reg_yld_texnames[-1].append(Dname_to_Latex(nuclide_names_yld[ni]))
                    reg_yld_zam[-1].append(Dname_to_ZAM(nuclide_names_yld[ni]))
                    yield_values_by_reg[0][-1].append(beam_fluxs[ri]*yields[ri,ni,0]/reg_vols[ri])
                    yield_values_by_reg[1][-1].append(beam_fluxs[ri]*yields[ri,ni,1]/reg_vols[ri])
                    yield_values_by_reg[2][-1].append(yields[ri,ni,0])
                    yield_values_by_reg[3][-1].append(yields[ri,ni,1])



    if process_DCS_file:
        # Control parameters
        relevancy_threshold=0.01 # fraction of total activity an isotope must be at any time step in DCS file to be placed in the "relevant" array

        fcn_out = parse_DCS_file_from_DCHAIN(dcs_file,relevancy_threshold=relevancy_threshold)

        # Notation for output array dimensions
        #   R (n_reg)    regions
        #   T (ntsteps)  time steps
        #   N (nnuc_max) max number of nuclides
        #   C (chni_max) maximum index of relevant chains
        #   L (chln_max) maximum number of links per chain

        inventory  = fcn_out[0] # universal columns of DCS file [R,T,N,C,vi], vi: 0=N_i-1/V, 1=dN/V, 2=N_i/V, 3=A_i/V, 4=A_i
        l_chains   = fcn_out[1] # [R,T,N,C], length of listed chain
        prod_nuc   = fcn_out[2] # [R,T,N], strings of the nuclide being produced
        chn_indx   = fcn_out[3] # [R,T,N], lists of the chain indices printed
        link_nuc   = fcn_out[4] # [R,T,N,C,L], strings of the nuclides in each chain
        decay_mode = fcn_out[5] # [R,T,N,C,L], strings of the decay modes each link undergoes to produce the next link
        link_dN_info=fcn_out[6] # [R,T,N,C,L,di], extra dN info di: 0=dN_Beam, 1=dN_Decay/nrxn, 2=dN_Total (only generated if these values are found in file, 'None' otherwise)
        end_of_irradiation_time = fcn_out[7] # time of end of final irradiation step [seconds]
        notable_nuclides_names_by_region = fcn_out[8] # list of lists (one per region) containing the relevant nuclides per region
        notable_nuclides_AvT_by_region   = fcn_out[9] # list of arrays (one per region, [T,N_rlv-nuc,3]) containing the time[s]/inventory[atm/cc]/activity[Bq/cc] data of relevant nuclides

        n_reg,ntsteps,nnuc_max,chni_max,chln_max = np.shape(decay_mode)

        relevant_nuclides = notable_nuclides_names_by_region[0]
        n_relevant_nuclides = len(relevant_nuclides)
        relv_nuc_inv = notable_nuclides_AvT_by_region[0]

        t_from_start = relv_nuc_inv[:,0,0]
        t_after_irrad_sec = ((relv_nuc_inv[:,0,0]-end_of_irradiation_time))

    nreg = len(reg_nos)
    rilist = range(nreg)
    #regionwise_gamma_spectra = [gamma_spectra[ri,:,:,:,:] for ri in range(nreg)]
    #rw_totgflux_val = [rt_summary_info[ri,:,0,0] for ri in range(nreg)]
    #rw_totgflux_ae = [rt_summary_info[ri,:,0,1] for ri in range(nreg)]
    #rw_totegflux = [rt_summary_info[ri,:,1,:] for ri in range(nreg)]


    # Notation for output array dimensions
    #   R  regions
    #   T  time steps
    #   N  max number of nuclides found in a single region
    #   E  number of gamma energy bins
    # le10 for top 10 lists, a number <= 10

    dchain_output = {
        'time':{                                              #  ~  Time information
            'from_start_sec':time_list_sec,                   # [T] list of times from start time [sec]
            'from_EOB_sec':time_list_sec_after_EOB,           # [T] list of times from end of final bombardment [sec]
            'of_EOB_sec':irradiation_end_t,                   #     scalar time marking end of final bombardment [sec]
            },

        'region':{                                            #  ~  Information which only varies with region
            'numbers':reg_nos,                                # [R] list of all region numbers
            'number': r_summary_info[:,0],                    # [R] list of all region numbers
            'irradiation_time_sec': r_summary_info[:,1],      # [R] list of irradiation time per region
            'volume': r_summary_info[:,2],                    # [R] list of volume in cc per region
            'neutron_flux': r_summary_info[:,3],              # [R] list of neutron flux in n/cm^2/s per region
            'beam_power_MW': r_summary_info[:,4],             # [R] list of beam power in MW per region
            'beam_energy_GeV': r_summary_info[:,5],           # [R] list of beam energy in GeV per region
            'beam_current_mA': r_summary_info[:,6]            # [R] list of beam current in mA per region
            },

        'nuclides':{                                          #  ~  Main nuclide results from *.act file
            'names':nuclide_names,                            # [R][N] list of lists containing names of nuclides produced in each region
            'TeX_names':LaTeX_nuclide_names,                  # [R][N] list of lists containing LaTeX-formatted names of nuclides produced in each region
            'ZZZAAAM':nuclide_ZAM_vals,                       # [R][N] list of lists containing ZZZAAAM values (=10000*Z+10*A+M) of nuclides produced in each region (ground state m=0, metastable m=1,2,etc.)
            'half_life':nuclide_half_lives,                   # [R][N] list of lists containing half lives of nuclides produced in each region (in seconds)
            'inventory':{'value':[nuclide_info[ri][:,:,0,0] for ri in rilist],       # [R][T,N] atoms [#/cc]
                         'error':[nuclide_info[ri][:,:,0,1] for ri in rilist]},      # [R][T,N] atoms [#/cc]
            'activity':{'value':[nuclide_info[ri][:,:,1,0] for ri in rilist],        # [R][T,N] activity [Bq/cc]
                        'error':[nuclide_info[ri][:,:,1,1] for ri in rilist]},       # [R][T,N] activity [Bq/cc]
            'dose_rate':{'value':[nuclide_info[ri][:,:,6,0] for ri in rilist],       # [R][T,N] dose-rate [uSv/h*m^2]
                         'error':[nuclide_info[ri][:,:,6,1] for ri in rilist]},      # [R][T,N] dose-rate [uSv/h*m^2]
            'decay_heat':{
                'total':{'value':[nuclide_info[ri][:,:,5,0] for ri in rilist],       # [R][T,N] total decay heat [W/cc]
                         'error':[nuclide_info[ri][:,:,5,1] for ri in rilist]},      # [R][T,N] total decay heat [W/cc]
                'beta':{'value':[nuclide_info[ri][:,:,2,0] for ri in rilist],        # [R][T,N] beta decay heat [W/cc]
                        'error':[nuclide_info[ri][:,:,2,1] for ri in rilist]},       # [R][T,N] beta decay heat [W/cc]
                'gamma':{'value':[nuclide_info[ri][:,:,3,0] for ri in rilist],       # [R][T,N] gamma decay heat [W/cc]
                         'error':[nuclide_info[ri][:,:,3,1] for ri in rilist]},      # [R][T,N] gamma decay heat [W/cc]
                'alpha':{'value':[nuclide_info[ri][:,:,4,0] for ri in rilist],       # [R][T,N] alpha decay heat [W/cc]
                         'error':[nuclide_info[ri][:,:,4,1] for ri in rilist]},      # [R][T,N] alpha decay heat [W/cc]
                },
            'column_headers':nuclide_info_headers, # List of length 7 containing text descriptions of the 7 columns of the info arrays [0='atoms [#/cc]',1='activity [Bq/cc]','2=beta decay heat [W/cc]','3=gamma decay heat [W/cc]','4=alpha decay heat [W/cc]','5=total decay heat [W/cc]','6=dose-rate [uSv/h*m^2]']
            'total':{                                                                       #  ~  Total values summed over all nuclides
                'activity':{'value':[rt_summary_info[ri,:,5,0] for ri in rilist] ,          # [R][T] total activity [Bq/cc]
                            'error':[rt_summary_info[ri,:,5,1] for ri in rilist]},          # [R][T] total activity [Bq/cc]
                'decay_heat':{'value':[rt_summary_info[ri,:,6,0] for ri in rilist] ,        # [R][T] total decay heat [W/cc]
                              'error':[rt_summary_info[ri,:,6,1] for ri in rilist]},        # [R][T] total decay heat [W/cc]
                'beta_heat':{'value':[rt_summary_info[ri,:,7,0] for ri in rilist] ,         # [R][T] total beta decay heat [W/cc]
                             'error':[rt_summary_info[ri,:,7,1] for ri in rilist]},         # [R][T] total beta decay heat [W/cc]
                'gamma_heat':{'value':[rt_summary_info[ri,:,8,0] for ri in rilist] ,        # [R][T] total gamma decay heat [W/cc]
                              'error':[rt_summary_info[ri,:,8,1] for ri in rilist]},        # [R][T] total gamma decay heat [W/cc]
                'alpha_heat':{'value':[rt_summary_info[ri,:,9,0] for ri in rilist] ,        # [R][T] total alpha decay heat [W/cc]
                              'error':[rt_summary_info[ri,:,9,1] for ri in rilist]},        # [R][T] total alpha decay heat [W/cc]
                'activated_atoms':{'value':[rt_summary_info[ri,:,10,0] for ri in rilist],   # [R][T] total activated atoms [#/cc]
                                   'error':[rt_summary_info[ri,:,10,1] for ri in rilist]},  # [R][T] total activated atoms [#/cc]
                'gamma_dose_rate':{'value':[rt_summary_info[ri,:,11,0] for ri in rilist],   # [R][T] total gamma dose rate [uSV/h*m^2]
                                   'error':[rt_summary_info[ri,:,11,1] for ri in rilist]}   # [R][T] total gamma dose rate [uSV/h*m^2]
                }
            },


        'gamma':{                                                                                              #  ~  Gamma spectra and totals
            'spectra':{
                'group_number':[gamma_spectra[ri,:,:,0,0] for ri in rilist],                                   # [R][T,E] group number
                'E_lower':[gamma_spectra[ri,:,:,1,0] for ri in rilist],                                        # [R][T,E] bin energy lower-bound [MeV]
                'E_upper':[gamma_spectra[ri,:,:,2,0] for ri in rilist],                                        # [R][T,E] bin energy upper-bound [MeV]
                'flux':{'value':[gamma_spectra[ri,:,:,3,0] for ri in rilist],                                  # [R][T,E] flux [#/s/cc]
                        'error':[gamma_spectra[ri,:,:,3,0]*gamma_spectra[ri,:,:,3,1] for ri in rilist]},       # [R][T,E] flux [#/s/cc]
                'energy_flux':{'value':[gamma_spectra[ri,:,:,4,0] for ri in rilist],                           # [R][T,E] energy flux [MeV/s/cc]
                               'error':[gamma_spectra[ri,:,:,4,0]*gamma_spectra[ri,:,:,4,1] for ri in rilist]} # [R][T,E] energy flux [MeV/s/cc]
                },
            'total_flux':{'value':[rt_summary_info[ri,:,0,0] for ri in rilist],                                # [R][T] total gamma flux [#/s/cc]
                          'error':[rt_summary_info[ri,:,0,1] for ri in rilist]},                               # [R][T] total gamma flux [#/s/cc]
            'total_energy_flux':{'value':[rt_summary_info[ri,:,1,0] for ri in rilist] ,                        # [R][T] total gamma energy flux [MeV/s/cc]
                                 'error':[rt_summary_info[ri,:,1,1] for ri in rilist]},                        # [R][T] total gamma energy flux [MeV/s/cc]
            'annihilation_flux':{'value':[rt_summary_info[ri,:,2,0] for ri in rilist] ,                        # [R][T] annihilation gamma flux [#/s/cc]
                                 'error':[rt_summary_info[ri,:,2,1] for ri in rilist]},                        # [R][T] annihilation gamma flux [#/s/cc]
            'current_underflow':{'value':[rt_summary_info[ri,:,3,0] for ri in rilist] ,                        # [R][T] gamma current underflow [#/s]
                                 'error':[rt_summary_info[ri,:,3,1] for ri in rilist]}, # no error reported
            'current_overflow':{'value':[rt_summary_info[ri,:,4,0] for ri in rilist],                          # [R][T] gamma current overflow [#/s]
                                'error':[rt_summary_info[ri,:,4,1] for ri in rilist]}   # no error reported
            },

        'top10':{                                                          #  ~  Top 10 lists from *.act file
            'activity':{
                'rank':[top10_lists[ri,:,:,0,0] for ri in rilist],         # [R][T,le10] rank
                'nuclide':[top10_lists[ri,:,:,1,0] for ri in rilist],      # [R][T,le10] nuclide name
                'value':[top10_lists[ri,:,:,2,0] for ri in rilist],        # [R][T,le10] activity [Bq/cc]
                'error':[top10_lists[ri,:,:,2,1] for ri in rilist],        # [R][T,le10] activity [Bq/cc]
                'percent':[top10_lists[ri,:,:,4,0] for ri in rilist],      # [R][T,le10] percent of total activity
                },
            'decay_heat':{
                'rank':[top10_lists[ri,:,:,0,0] for ri in rilist],         # [R][T,le10] rank
                'nuclide':[top10_lists[ri,:,:,5,0] for ri in rilist],      # [R][T,le10] nuclide name
                'value':[top10_lists[ri,:,:,6,0] for ri in rilist],        # [R][T,le10] decay heat [W/cc]
                'error':[top10_lists[ri,:,:,6,1] for ri in rilist],        # [R][T,le10] decay heat [W/cc]
                'percent':[top10_lists[ri,:,:,8,0] for ri in rilist],      # [R][T,le10] percent of total decay heat
                },
            'gamma_dose':{
                'rank':[top10_lists[ri,:,:,0,0] for ri in rilist],         # [R][T,le10] rank
                'nuclide':[top10_lists[ri,:,:,9,0] for ri in rilist],      # [R][T,le10] nuclide name
                'value':[top10_lists[ri,:,:,10,0] for ri in rilist],       # [R][T,le10] dose-rate [uSv/h*m^2]
                'error':[top10_lists[ri,:,:,10,1] for ri in rilist],       # [R][T,le10] dose-rate [uSv/h*m^2]
                'percent':[top10_lists[ri,:,:,11,0] for ri in rilist],     # [R][T,le10] percent of total gamma dose rate
                }
            },

        'number_of':{                                                      #  ~  Maximum values of R, T, N, and E
            'regions':nreg,                                                #  R  = total number of regions
            'time_steps':len(time_list_sec),                               #  T  = total number of time steps
            'max_nuclides_in_any_region':np.shape(nuclides_produced)[2],   #  N  = maximum unique nuclides found in any region
            'gamma_energy_bins':np.shape(gamma_spectra)[2]                 #  E  = number of gamma energy bins (default=42)
            }

        }

    if process_dtrk_file:
        dflux_norm = []
        for ri in rilist:
            if np.sum(neutron_flux[ri,:,2]) != 0:
                dflux_norm.append(r_summary_info[ri,3]/np.sum(neutron_flux[ri,:,2]))
            else:
                dflux_norm.append(0.0)
        #dflux_norm = [r_summary_info[ri,3]/np.sum(neutron_flux[ri,:,2]) for ri in rilist] # normalize unit flux to total flux
        dchain_output.update({
            'neutron':{
                'spectra':{                                                                                         # Actual values used by DCHAIN for rate calcs
                    'E_lower':[neutron_flux[ri,:,0] for ri in rilist],                                              # [R][E] bin energy lower-bound [MeV]
                    'E_upper':[neutron_flux[ri,:,1] for ri in rilist],                                              # [R][E] bin energy upper-bound [MeV]
                    'flux':{'value':[neutron_flux[ri,:,2]*dflux_norm[ri] for ri in rilist],                         # [R][E] neutron flux [#/s/cm^2]
                            'error':[neutron_flux[ri,:,3]*dflux_norm[ri] for ri in rilist]},                        # [R][E] neutron flux [#/s/cm^2]
                    },
                'total_flux':{'value':[np.sum(neutron_flux[ri,:,2])*dflux_norm[ri] for ri in rilist],               # [R] total neutron flux [#/s/cm^2]
                              'error':[np.sqrt(np.sum(neutron_flux[ri,:,3]**2))*dflux_norm[ri] for ri in rilist]},  # [R] total neutron flux [#/s/cm^2]
                'unit_spectra':{                                                         # Raw T-Track output from PHITS
                    'E_lower':[neutron_flux[ri,:,0] for ri in rilist],                   # [R][E] bin energy lower-bound [MeV]
                    'E_upper':[neutron_flux[ri,:,1] for ri in rilist],                   # [R][E] bin energy upper-bound [MeV]
                    'flux':{'value':[neutron_flux[ri,:,2] for ri in rilist],             # [R][E] neutron flux [#/s/cm^2]
                            'error':[neutron_flux[ri,:,3] for ri in rilist]},            # [R][E] neutron flux [#/s/cm^2]
                    },
                }
            })

    if process_dyld_file:
        dchain_output.update({
            'yields':{                                              #  ~  Yield spectra
                'all_names':nuclide_names_yld,                      # [N] names of nuclides produced in all regions
                'names':reg_yld_names,                              # [R][N] names of nuclides produced in each region
                'TeX_names':reg_yld_texnames,                       # [R][N] LaTeX-formatted names of nuclides produced
                'ZZZAAAM':reg_yld_zam,                              # [R][N] ZZZAAAM values (=10000Z+10A+M) of nuclides
                'rate':{'value':yield_values_by_reg[0],             # [R][E] nuclide yield rate [#/s/cm^3]
                        'error':yield_values_by_reg[1]},            # [R][E] nuclide yield rate [#/s/cm^3]
                'unit_rate':{'value':yield_values_by_reg[2],        # [R][E] unit nuclide yield rate [#/s.p.]
                             'error':yield_values_by_reg[3]}        # [R][E] unit nuclide yield rate [#/s.p.]
                }
            })

    if process_DCS_file: # add extra information
        # Notation for output array dimensions
        #   R  (n_reg)    regions
        #   Td (ntsteps)  time steps in DCS file (usually different from that of ACT file!)
        #   Nd (nnuc_max) max number of nuclides (this index differs from the ACT N index)
        #   C  (chni_max) maximum index of relevant chains
        #   L  (chln_max) maximum number of links per chain
        np.seterr(divide='ignore', invalid='ignore')
        dchain_output.update({'DCS':{
            'time':{
                'from_start_sec':t_from_start,         # [Td] list
                'from_EOB_sec':t_after_irrad_sec,      # [Td] list
                'of_EOB_sec':irradiation_end_t         #      scalar
                },

            'number_of':{                              #  ~  Maximum values of R, Td, Nd, C, and L
                'regions':n_reg,                       #  R  = total number of regions
                'time_steps':ntsteps,                  #  Td = total number of time steps
                'max_nuclides':nnuc_max,               #  Nd = maximum number of nuclides listed in a time step
                'max_number_of_chains':chni_max,       #  C  = highest index of a relevant chain found
                'max_chain_length':chln_max            #  L  = maximum number of links (nuclides) found in any chain
                },

            'end_nuclide':{
                'names':[prod_nuc[ri,:,:] for ri in rilist],                  # [R][Td,Nd] nuclide names

                'inventory':{
                    'N_previous':[inventory[ri,:,:,:,0] for ri in rilist],    # [R][Td,Nd,C] inventory of end nuclide in previous time step [atoms/cc]
                    'N_now':[inventory[ri,:,:,:,2] for ri in rilist],         # [R][Td,Nd,C] inventory of end nuclide in the current time step [atoms/cc]
                    'dN':[inventory[ri,:,:,:,1] for ri in rilist]             # [R][Td,Nd,C] change in inventory of end nuclide from the previous to the current time step [atoms/cc]
                    },

                'activity':{
                    'A_previous':[inventory[ri,:,:,:,0]*(inventory[ri,:,:,:,3]/inventory[ri,:,:,:,2]) for ri in rilist], # [R][Td,Nd,C] activity of end nuclide in previous time step [Bq/cc]
                    'A_now':[inventory[ri,:,:,:,3] for ri in rilist],                                                    # [R][Td,Nd,C] activity of end nuclide in the current time step [Bq/cc]
                    'dA':[inventory[ri,:,:,:,1]*(inventory[ri,:,:,:,3]/inventory[ri,:,:,:,2]) for ri in rilist]          # [R][Td,Nd,C] change in activity of end nuclide from the previous to the current time step [Bq/cc]
                    }
                },


            'chains':{
                'indices_of_printed_chains':[chn_indx[ri,:,:] for ri in rilist],           # [R][Td,Nd]     lists of the chain indices printed
                'length':[l_chains[ri,:,:,:] for ri in rilist],                            # [R][Td,Nd,C]   length of listed chain
                'link_nuclides':[link_nuc[ri,:,:,:,:] for ri in rilist],                   # [R][Td,Nd,C,L] strings of the nuclides in each chain
                'link_decay_modes':[decay_mode[ri,:,:,:,:] for ri in rilist],              # [R][Td,Nd,C,L] strings of the decay modes each link undergoes to produce the next link
                'link_dN':{
                    'beam':[None if link_dN_info is None else link_dN_info[ri,:,:,:,:,0] for ri in rilist],                  # [R][Td,Nd,C,L] beam contribution to dN from each link (only generated if these values are found in file, 'None' otherwise)
                    'decay_nrxn':[None if link_dN_info is None else link_dN_info[ri,:,:,:,:,1] for ri in rilist],            # [R][Td,Nd,C,L] decay + neutron rxn contribution to dN from each link (only generated if these values are found in file, 'None' otherwise)
                    'total':[None if link_dN_info is None else link_dN_info[ri,:,:,:,:,2] for ri in rilist]                  # [R][Td,Nd,C,L] total contribution to dN from each link (only generated if these values are found in file, 'None' otherwise)
                    }
                },

            'relevant_nuclides':{
                'names':notable_nuclides_names_by_region,                                  # [R]        list of relevant nuclides per region
                'times':[notable_nuclides_AvT_by_region[ri][:,:,0] for ri in rilist],      # [R][Td,Nd] time [s]
                'inventory':[notable_nuclides_AvT_by_region[ri][:,:,1] for ri in rilist],  # [R][Td,Nd] inventory [atm/cc]
                'activity':[notable_nuclides_AvT_by_region[ri][:,:,2] for ri in rilist]    # [R][Td,Nd] activity [Bq/cc]
                }

            }})
        np.seterr(divide='warn', invalid='warn')


    # https://github.com/Infinidat/munch
    try:
        dchain_output = munchify(dchain_output)
    except:
        print("munchify failed.  Returned object is a conventional dictionary rather than a munchify object.")

    return dchain_output


def parse_DCHAIN_act_file(act_file_path):
    '''
    Description:
         This code parses the .act file generated by DCHAIN

    Inputs:
        - path to a DCHAIN-generated .act file

    Outputs:
        - length R list of region numbers
        - length T list of measurement times (in sec) from start of irradiation
        - time of end of irradiation (in sec)
        - NumPy array of dimension RxTxNx11x2 of nuclide table data (N=max recorded table length)
        - NumPy array of dimension RxTxEx5x2 of gamma spectrum table data (E=number of energy groups of gamma spectra)
        - NumPy array of dimension RxTxNx12x2 of top-10 list table data
        - List containing 3 lists of column headers for the preceding three NumPy arrays
        - list of the below lists/arrays of summary information
            + NumPy array of dimension Rx7 of region-specific summary info:
                Beam current, beam energy, beam power, total neutron flux, region volume, irradiation time, region number
            + list of length 7 containing descriptions of the above items
            + NumPy array of dimension RxTx12x2 of region and time-specific summary info
                Rank, [nuclide, A/cc, A, %], [nuclide, P/cc, P, %], [nuclide, H, %] with values and absolute uncertainties
            + list of length 12 containing descriptions of the above items
    '''
    # Extract file info
    f = open(act_file_path)
    lines = f.readlines()
    f.close()

    # Parse file to determine number of regions
    nreg = 0
    reg_nos = []
    for line in lines:
        if 'region number' in line:
            nreg += 1
            reg_nos.append(int(line[21:31]))

    # Parse file again to determine number of time steps
    current_reg_no = -1
    #irradiation_time = -1.0 # seconds
    end_of_irradiation_time = -1.0 # seconds
    ntimes = 0
    time_strs = []
    time_list_sec = [] # time steps in seconds
    time_list_sec_after_EOB = [] # time steps in seconds after EOB
    for line in lines:
        #if 'irradiation time' in line: irradiation_time = float(line[21:31])*time_str_to_sec_multiplier(line[33])
        if 'region number' in line: current_reg_no = int(line[21:31])
        if current_reg_no != reg_nos[0]: continue # only read times from first region
        if '--- output time ---' in line:
            ntimes += 1
            time_strs.append(line)
            time_list_sec.append(float(line[40:53]))
            time_list_sec_after_EOB.append(0.0)
        if ('--- output time ---' in line) and ('after the last shutdown' in line):
            time_list_sec_after_EOB[ntimes-1] = float(line[87:97])*time_str_to_sec_multiplier(line[99])
            if end_of_irradiation_time == -1:
                end_of_irradiation_time = float(line[21:31])*time_str_to_sec_multiplier(line[33]) - float(line[87:97])*time_str_to_sec_multiplier(line[99])

    for ti in range(len(time_list_sec_after_EOB)):
        if time_list_sec_after_EOB[ti]==0.0:
            time_list_sec_after_EOB[ti] = time_list_sec[ti] - end_of_irradiation_time

    # Extract "summary info" from file
    ri = -1 # region index
    ti = -1 # time index
    r_summary_info = np.empty((nreg,7), dtype='object') # (regionwise) initialize Rx7 array
    r_summary_info_description = ['region number','irradiation time [s]','region volume [cc]','neutron flux [n/cm^2/s]','beam power [MW]','beam energy [GeV]','beam current [mA]'] # (regionwise) initialize Rx7 array
    '''
    r_summary_info[i,j,k]
       i = region number
       j = category (see table below)
    index  meaning
       0   region number
       1   irradiation time [sec]
       2   region volume [cc]
       3   neutron flux [n/cm^2/s]
       4   beam power [MW]
       5   beam energy [GeV]
       6   beam current [mA] 
    '''
    rt_summary_info = np.empty((nreg,ntimes,12,2), dtype='object') # (region-and-timewise) initialize RxTx12x2 array
    rt_summary_info_description = ['total gamma flux [#/s/cc]','total gamma energy flux [MeV/s/cc]','annihilation gamma flux [#/s/cc]','gamma current underflow [#/s]','gamma current overflow [#/s]','total activity [Bq/cc]','total decay heat [W/cc]','beta decay heat [W/cc]','gamma decay heat [W/cc]','alpha decay heat [W/cc]','activated atoms [#/cc]','total gamma dose rate [uSV/h*m^2]'] # (region-and-timewise) initialize RxTx12 array
    '''
    rt_summary_info[i,j,k,m]
       i = region number
       j = output time step
       k = category (see table below)
       m = value (k=0) or absolute uncertainty (k=1)
    index  meaning
       0   total gamma flux [#/s/cc]
       1   total gamma energy flux [MeV/s/cc]
       2   annihilation gamma flux [#/s/cc]
       3   gamma current underflow [#/s] (gammas below lowest energy bin)
       4   gamma current overflow [#/s] (gammas above highest energy bin)
       5   total activity [Bq/cc]
       6   total decay heat [W/cc]
       7     beta decay heat [W/cc]
       8     gamma decay heat [W/cc]
       9     alpha decay heat [W/cc]
       10  activated atoms [#/cc]
       11  total gamma dose rate [uSV/h*m^2]
    '''
    for li in range(len(lines)):
        line = lines[li]
        if 'region number' in line:
            ri = find(int(line[21:31]),reg_nos)

            # region-specific summary info
            r_summary_info[ri,0] = int(line[21:31])
            r_summary_info[ri,1] = float(lines[li-1][21:31])*time_str_to_sec_multiplier(lines[li-1][33])
            r_summary_info[ri,2] = float(lines[li-2][21:31])
            r_summary_info[ri,3] = float(lines[li-3][21:31])
            r_summary_info[ri,4] = float(lines[li-4][21:31])
            r_summary_info[ri,5] = float(lines[li-5][21:31])
            r_summary_info[ri,6] = float(lines[li-6][21:31])

        if '--- output time ---' in line:
            ti = find(line,time_strs)

        # gamma info specific to region and time
        if 'total gamma-ray flux' in line:
            rt_summary_info[ri,ti,0,0] = float(line[38:49])
            rt_summary_info[ri,ti,1,0] = float(lines[li+1][38:49])
            rt_summary_info[ri,ti,2,0] = float(lines[li+2][38:49])
            rt_summary_info[ri,ti,0,1] = float(line[53:64])
            rt_summary_info[ri,ti,1,1] = float(lines[li+1][53:64])
            rt_summary_info[ri,ti,2,1] = float(lines[li+2][53:64])
            if 'group limitation' in lines[li+3]:
                rt_summary_info[ri,ti,3,0] = float(lines[li+3][91:101])
                rt_summary_info[ri,ti,4,0] = float(lines[li+3][64:74])
            else:
                rt_summary_info[ri,ti,3,0] = 0.0
                rt_summary_info[ri,ti,4,0] = 0.0

        if 'no gamma-ray' in line:
            rt_summary_info[ri,ti,0,0] = 0.0
            rt_summary_info[ri,ti,1,0] = 0.0
            rt_summary_info[ri,ti,2,0] = 0.0
            rt_summary_info[ri,ti,0,1] = 0.0
            rt_summary_info[ri,ti,1,1] = 0.0
            rt_summary_info[ri,ti,2,1] = 0.0
            rt_summary_info[ri,ti,3,0] = 0.0
            rt_summary_info[ri,ti,4,0] = 0.0

        # activation info specific to region and time
        if 'total activity' in line:
            rt_summary_info[ri,ti,5,0] = float(line[24:36])
            rt_summary_info[ri,ti,6,0] = float(lines[li+1][24:36])
            rt_summary_info[ri,ti,7,0] = float(lines[li+2][24:36])
            rt_summary_info[ri,ti,8,0] = float(lines[li+3][24:36])
            rt_summary_info[ri,ti,9,0] = float(lines[li+4][24:36])
            rt_summary_info[ri,ti,10,0]= float(lines[li+5][24:36])
            rt_summary_info[ri,ti,11,0]= float(lines[li+6][24:36])
            rt_summary_info[ri,ti,5,1] = float(line[40:52])
            rt_summary_info[ri,ti,6,1] = float(lines[li+1][40:52])
            rt_summary_info[ri,ti,7,1] = float(lines[li+2][40:52])
            rt_summary_info[ri,ti,8,1] = float(lines[li+3][40:52])
            rt_summary_info[ri,ti,9,1] = float(lines[li+4][40:52])
            rt_summary_info[ri,ti,10,1]= float(lines[li+5][40:52])
            rt_summary_info[ri,ti,11,1]= float(lines[li+6][40:52])

    summary_info = [r_summary_info, r_summary_info_description, rt_summary_info, rt_summary_info_description]

    # Extract major "blocks" (nuclides, gamma spec, top10 list) for each time step in each region
    act_block_text = np.empty((nreg,ntimes,3), dtype='object') # initialize RxTx3 array to hold character strings where final index 0=nuclides, 1=gamma-spec, and 2=top10-list
    ri = -1 # region index
    ti = -1 # time index
    qi = -1 # quantity index - 0=nuclides, 1=gamma-spec, and 2=top10-list
    max_array_len = [0,0,0] # maximum number of entries for a given quantity
    current_array_len = [0,0,0] # current number of entries for a given quantity
    for line in lines:
        if 'region number' in line:
            ri = find(int(line[21:31]),reg_nos)
        if '--- output time ---' in line:
            ti = find(line,time_strs)
            qi = 0 # reset quantity index
        if 'gamma-ray spectrum weighted by energy' in line:
            qi = 1
        if 'dominant nuclides (top 10)' in line:
            qi = 2
        if 'total' in line[:20] or line=='\n': # no longer reading info block
            if current_array_len[qi] > max_array_len[qi]:
                max_array_len[qi] = current_array_len[qi]
            current_array_len[qi] = 0
            qi = -1

        if qi < 0: continue # not in region of interest

        try:
            act_block_text[ri,ti,qi] += line
        except:
            act_block_text[ri,ti,qi] = line

        current_array_len[qi] += 1

    header_len = [3,4,3] # number of lines present in table header

    nuclides_produced = np.empty((nreg,ntimes,max_array_len[0]-header_len[0],11,2), dtype='object') # initialize RxTxNx11x2 array to hold nuclide information
    gamma_spectra     = np.empty((nreg,ntimes,max_array_len[1]-header_len[1], 5,2), dtype='object') # initialize RxTxNx5x2 array to hold gamma spec information
    top10_lists       = np.empty((nreg,ntimes,max_array_len[2]-header_len[2],12,2), dtype='object') # initialize RxTxNx12x2 array to hold top 10 list information

    column_headers = [ [],[],[] ]

    # Now, populate each array

    # Nuclides produced
    column_headers[0] = ['nuclide','atoms [#/cc]','activity [Bq/cc]','activity [Bq]','rate [%]','beta decay heat [W/cc]','gamma decay heat [W/cc]','alpha decay heat [W/cc]','total decay heat [W/cc]','half life [s]','dose-rate [uSv/h*m^2]']
    for ri in range(nreg):
        for ti in range(ntimes):
            table_text = act_block_text[ri,ti,0].split('\n')
            for ei in range(len(table_text)):
                if ei < header_len[0]: continue # in header lines
                ii = ei - header_len[0] # actual number index
                line = table_text[ei]
                if line=='' or line==None: continue # skip blank/nonexistent lines
                rel_err = float(line[51:61])
                nuclides_produced[ri,ti,ii,0,0] = line[3:9]            # nuclide
                nuclides_produced[ri,ti,ii,1,0] = float(line[12:23].replace('      ','0.0'))    # atoms [#/cc]
                nuclides_produced[ri,ti,ii,2,0] = float(line[25:36].replace('      ','0.0'))    # activity [Bq/cc]
                nuclides_produced[ri,ti,ii,3,0] = float(line[38:49].replace('      ','0.0'))    # activity [Bq]
                nuclides_produced[ri,ti,ii,4,0] = float(line[61:68].replace('     ','0.0'))    # rate [%]
                nuclides_produced[ri,ti,ii,5,0] = float(line[70:80].replace('      ','0.0'))    # beta decay heat [W/cc]
                nuclides_produced[ri,ti,ii,6,0] = float(line[81:91].replace('      ','0.0'))    # gamma decay heat [W/cc]
                nuclides_produced[ri,ti,ii,7,0] = float(line[92:102].replace('      ','0.0'))   # alpha decay heat [W/cc]
                nuclides_produced[ri,ti,ii,8,0] = float(line[103:113].replace('      ','0.0'))  # total decay heat [W/cc]
                nuclides_produced[ri,ti,ii,9,0] = float(line[116:126].replace('stable','0.0')) # half life [s]
                if nuclides_produced[ri,ti,ii,9,0] == 0:
                    nuclides_produced[ri,ti,ii,10,0]= 0.0  # dose-rate [uSv/h*m^2]
                else:
                    nuclides_produced[ri,ti,ii,10,0]= float(line[128:138].replace('      ','0.0'))  # dose-rate [uSv/h*m^2]

                # absolute errors for corresponding values
                nuclides_produced[ri,ti,ii,1,1] = nuclides_produced[ri,ti,ii,1,0]*rel_err
                nuclides_produced[ri,ti,ii,2,1] = nuclides_produced[ri,ti,ii,2,0]*rel_err
                nuclides_produced[ri,ti,ii,3,1] = nuclides_produced[ri,ti,ii,3,0]*rel_err
                nuclides_produced[ri,ti,ii,4,1] = nuclides_produced[ri,ti,ii,4,0]*rel_err
                nuclides_produced[ri,ti,ii,5,1] = nuclides_produced[ri,ti,ii,5,0]*rel_err
                nuclides_produced[ri,ti,ii,6,1] = nuclides_produced[ri,ti,ii,6,0]*rel_err
                nuclides_produced[ri,ti,ii,7,1] = nuclides_produced[ri,ti,ii,7,0]*rel_err
                nuclides_produced[ri,ti,ii,8,1] = nuclides_produced[ri,ti,ii,8,0]*rel_err
                nuclides_produced[ri,ti,ii,9,1] = nuclides_produced[ri,ti,ii,9,0]*rel_err
                nuclides_produced[ri,ti,ii,10,1]= nuclides_produced[ri,ti,ii,10,0]*rel_err

    # Gamma-ray spectra
    column_headers[1] = ['group number','bin energy lower-bound [MeV]','bin energy upper-bound [MeV]','flux [#/s/cc]','energy flux [MeV/s/cc]']
    for ri in range(nreg):
        for ti in range(ntimes):
            if not act_block_text[ri,ti,1]:
                gamma_spectra[ri,ti,:,0,0] = None  # group number
                gamma_spectra[ri,ti,:,1,0] = None  # bin energy lower-bound [MeV]
                gamma_spectra[ri,ti,:,2,0] = None  # bin energy upper-bound [MeV]
                gamma_spectra[ri,ti,:,3,0] = 0.0   # flux [#/s/cc]
                gamma_spectra[ri,ti,:,4,0] = 0.0   # energy flux [MeV/s/cc]
                gamma_spectra[ri,ti,:,3,1] = 0.0   # flux absolute error [#/s/cc]
                gamma_spectra[ri,ti,:,4,1] = 0.0   # energy flux absolute error [MeV/s/cc]
                continue
            table_text = act_block_text[ri,ti,1].split('\n')
            for ei in range(len(table_text)):
                if ei < header_len[1]: continue # in header lines
                ii = ei - header_len[1] # actual number index
                line = table_text[ei]
                if line=='' or line==None: continue # skip blank/nonexistent lines
                gamma_spectra[ri,ti,ii,0,0] = int(line[1:4])       # group number
                gamma_spectra[ri,ti,ii,1,0] = float(line[17:25])   # bin energy lower-bound [MeV]
                gamma_spectra[ri,ti,ii,2,0] = float(line[7:15])    # bin energy upper-bound [MeV]
                gamma_spectra[ri,ti,ii,3,0] = float(line[27:38])   # flux [#/s/cc]
                gamma_spectra[ri,ti,ii,4,0] = float(line[40:51])   # energy flux [MeV/s/cc]
                gamma_spectra[ri,ti,ii,3,1] = gamma_spectra[ri,ti,ii,3,0]*float(line[53:64])   # flux absolute error [#/s/cc]
                gamma_spectra[ri,ti,ii,4,1] = gamma_spectra[ri,ti,ii,4,0]*float(line[53:64])   # energy flux absolute error [MeV/s/cc]

    # Top 10 lists
    column_headers[2] = ['rank','nuclide -  Activity ranking','activity [Bq/cc]','activity [Bq]','rate [%]','nuclide - Decay heat ranking','decay heat [W/cc]','decay heat [W]','rate [%]','nuclide - Dose rate ranking','dose-rate [uSv/h*m^2]','rate [%]']
    for ri in range(nreg):
        for ti in range(ntimes):
            if not act_block_text[ri,ti,2]: continue
            table_text = act_block_text[ri,ti,2].split('\n')
            for ei in range(len(table_text)):
                if ei < header_len[2]: continue # in header lines
                ii = ei - header_len[2] # actual number index
                line = table_text[ei]
                if line=='' or line==None: continue # skip blank/nonexistent lines
                top10_lists[ri,ti,ii,0,0] = int(line[1:5])       # number/rank
                top10_lists[ri,ti,ii,1,0] = line[8:14]           # nuclide -  Activity ranking
                top10_lists[ri,ti,ii,2,0] = float(line[15:26])   # activity [Bq/cc]
                top10_lists[ri,ti,ii,3,0] = float(line[26:37])   # activity [Bq]
                top10_lists[ri,ti,ii,4,0] = float(line[48:55])   # rate [%]
                rel_err = float(line[37:48])
                top10_lists[ri,ti,ii,2,1] = top10_lists[ri,ti,ii,2,0]*rel_err   # activity absolute error [Bq/cc]
                top10_lists[ri,ti,ii,3,1] = top10_lists[ri,ti,ii,3,0]*rel_err   # activity absolute error [Bq]
                top10_lists[ri,ti,ii,4,1] = top10_lists[ri,ti,ii,4,0]*rel_err   # rate absolute error [%]

                top10_lists[ri,ti,ii,5,0] = line[60:66]          # nuclide - Decay heat ranking
                top10_lists[ri,ti,ii,6,0] = float(line[67:78])   # decay heat [W/cc]
                top10_lists[ri,ti,ii,7,0] = float(line[78:89])   # decay heat [W]
                top10_lists[ri,ti,ii,8,0] = float(line[100:107]) # rate [%]
                rel_err = float(line[89:100])
                top10_lists[ri,ti,ii,6,1] = top10_lists[ri,ti,ii,6,0]*rel_err   # decay heat absolute error [W/cc]
                top10_lists[ri,ti,ii,7,1] = top10_lists[ri,ti,ii,7,0]*rel_err   # decay heat absolute error [W]
                top10_lists[ri,ti,ii,8,1] = top10_lists[ri,ti,ii,8,0]*rel_err   # rate absolute error [%]

                top10_lists[ri,ti,ii,9,0] = line[112:118]        # nuclide - Dose rate ranking
                top10_lists[ri,ti,ii,10,0]= float(line[119:130]) # dose-rate [uSv/h*m^2]
                top10_lists[ri,ti,ii,11,0]= float(line[142:149]) # rate [%]
                rel_err = float(line[131:142])
                top10_lists[ri,ti,ii,10,1]= top10_lists[ri,ti,ii,10,0]*rel_err # dose-rate absolute error [uSv/h*m^2]
                top10_lists[ri,ti,ii,11,1]= top10_lists[ri,ti,ii,11,0]*rel_err # rate absolute error [%]

    return reg_nos, time_list_sec, time_list_sec_after_EOB, end_of_irradiation_time, nuclides_produced, gamma_spectra, top10_lists, column_headers, summary_info


def generate_nuclide_time_profiles(nuclides_info_array):
    '''
    Description:
        Reformats DCHAIN's tabular nuclide data into time profiles of each nuclide in each region

    Inputs:
       - the `nuclides_produced` array from function "parse_DCHAIN_act_file"

    Outputs:
       - List of length R of lists containing names of nuclides produced in each region
       - List of length R of lists containing LaTeX-formatted names of nuclides produced in each region
       - List of length R of lists containing ZZZAAAM values (10000Z+10A+M) of nuclides produced in each region
       - List of length R of lists containing half lives of nuclides produced in each region (in seconds)
       - List of length R of NumPy arrays of dimension NxTx7x2 of nuclide info
       - List of length 7 containing text descriptions of the 7 columns of the info arrays
    '''
    nuclide_names = []
    nuclide_ZAM_vals = []
    nuclide_Latex_names = []
    nuclide_half_lives = []
    nuclide_info = []
    nuclide_info_headers = ['Atoms [#/cc]','Activity [Bq/cc]','Beta decay heat [W/cc]','Gamma decay heat [W/cc]','Alpha decay heat [W/cc]','Total decay heat [W/cc]','Dose-rate [uSv/h*m^2]']


    nreg = np.shape(nuclides_info_array)[0]
    ntime= np.shape(nuclides_info_array)[1]
    nnuc = np.shape(nuclides_info_array)[2]

    # Get nuclide name info first, ordering them by increasing Z and A
    for ri in range(nreg):
        reg_nuclides = []
        reg_t_halves = []
        reg_ZAM_vals = []
        reg_tex_nuclides = []
        for ti in range(ntime):
            for ni in range(nnuc):
                Dname = nuclides_info_array[ri,ti,ni,0,0]
                if Dname == None: continue
                ZAM = Dname_to_ZAM(Dname)
                if ZAM not in reg_ZAM_vals:
                    bisect.insort_left(reg_ZAM_vals, ZAM)
                    zami = reg_ZAM_vals.index(ZAM)
                    #zami = find(ZAM,reg_ZAM_vals)
                    reg_nuclides.insert(zami,Dname)
                    reg_t_halves.insert(zami,nuclides_info_array[ri,ti,ni,9,0])
                    reg_tex_nuclides.insert(zami,Dname_to_Latex(Dname))

        nuclide_names.append(reg_nuclides)
        nuclide_ZAM_vals.append(reg_ZAM_vals)
        nuclide_half_lives.append(reg_t_halves)
        nuclide_Latex_names.append(reg_tex_nuclides)

    # Now get arrays of nuclide info
    for ri in range(nreg):
        reg_nnuc = len(nuclide_names[ri])
        reg_nuclide_info = np.zeros((ntime,reg_nnuc,7,2))
        for ti in range(ntime):
            for ni in range(reg_nnuc):
                if nuclide_names[ri][ni] not in nuclides_info_array[ri,ti,:,0,0]: continue
                sni = find(nuclide_names[ri][ni],nuclides_info_array[ri,ti,:,0,0])
                reg_nuclide_info[ti,ni,0,0] = nuclides_info_array[ri,ti,sni,1,0]   # atoms [#/cc]
                reg_nuclide_info[ti,ni,1,0] = nuclides_info_array[ri,ti,sni,2,0]   # activity [Bq/cc]
                reg_nuclide_info[ti,ni,2,0] = nuclides_info_array[ri,ti,sni,5,0]   # beta decay heat [W/cc]
                reg_nuclide_info[ti,ni,3,0] = nuclides_info_array[ri,ti,sni,6,0]   # gamma decay heat [W/cc]
                reg_nuclide_info[ti,ni,4,0] = nuclides_info_array[ri,ti,sni,7,0]   # alpha decay heat [W/cc]
                reg_nuclide_info[ti,ni,5,0] = nuclides_info_array[ri,ti,sni,8,0]   # total decay heat [W/cc]
                reg_nuclide_info[ti,ni,6,0] = nuclides_info_array[ri,ti,sni,10,0]  # dose-rate [uSv/h*m^2]

                reg_nuclide_info[ti,ni,0,1] = nuclides_info_array[ri,ti,sni,1,1]   # atoms absolute error [#/cc]
                reg_nuclide_info[ti,ni,1,1] = nuclides_info_array[ri,ti,sni,2,1]   # activity absolute error [Bq/cc]
                reg_nuclide_info[ti,ni,2,1] = nuclides_info_array[ri,ti,sni,5,1]   # beta decay heat absolute error [W/cc]
                reg_nuclide_info[ti,ni,3,1] = nuclides_info_array[ri,ti,sni,6,1]   # gamma decay heat absolute error [W/cc]
                reg_nuclide_info[ti,ni,4,1] = nuclides_info_array[ri,ti,sni,7,1]   # alpha decay heat absolute error [W/cc]
                reg_nuclide_info[ti,ni,5,1] = nuclides_info_array[ri,ti,sni,8,1]   # total decay heat absolute error [W/cc]
                reg_nuclide_info[ti,ni,6,1] = nuclides_info_array[ri,ti,sni,10,1]  # dose-rate absolute error [uSv/h*m^2]

        nuclide_info.append(reg_nuclide_info)

    return nuclide_names, nuclide_Latex_names, nuclide_ZAM_vals, nuclide_half_lives, nuclide_info, nuclide_info_headers


def parse_DCS_file_from_DCHAIN(filepath,relevancy_threshold=0.01,print_progress=False,nch_max=100):
    '''
    Description:
        Parse a decay chain information file produced by DCHAIN-SP

    Dependencies:
        `import numpy as np`

        `import time`

    Inputs:
       (required)

       - `filepath` = string, path to DCS file

    Inputs:
       (optional, keyword)

       - `print_progress` = logical variable denoting whether time and significant nuclide info will be printed while scanning file (D=`False`)
       - `nch_max` = maximum number of chains per isotope (D=`100`)
       - `relevancy_threshold` = what fraction of total activity must a nuclide contribute to be deemed relevant

    Outputs:

       | dimension      |  meaning for output array dimensions |
       | :------------- | :-------------------------------- |
       |   R (n_reg)    | regions                           |
       |   T (ntsteps)  | time steps                        |
       |   N (nnuc_max) | max number of nuclides            |
       |   C (chni_max) | maximum index of relevant chains  |
       |   L (chln_max) | maximum number of links per chain |


        - 0) `inventory`    = universal columns of DCS file `[R,T,N,C,vi]`, vi: 0=N_i-1/V, 1=dN/V, 2=N_i/V, 3=A_i/V, 4=A_i
        - 1) `l_chains`     = `[R,T,N,C]`, length of listed chain
        - 2) `prod_nuc`     = `[R,T,N]`, strings of the nuclide being produced
        - 3) `chn_indx`     = `[R,T,N]`, lists of the chain indices printed
        - 4) `link_nuc`     = `[R,T,N,C,L]`, strings of the nuclides in each chain
        - 5) `decay_mode`   = `[R,T,N,C,L]`, strings of the decay modes each link undergoes to produce the next link
        - 6) `link_dN_info` = `[R,T,N,C,L,di]`, extra dN info di: 0=dN_Beam, 1=dN_Decay/nrxn, 2=dN_Total (only generated if these values are found in file, 'None' otherwise)
        - 7) `end_of_irradiation_time` = time of end of final irradiation step [seconds]
        - 8) `notable_nuclides_names_by_region` = list of lists (one per region) containing the relevant nuclides per region
        - 9) `notable_nuclides_AvT_by_region`   = list of arrays (one per region, `[T,N_rlv-nuc,3]`) containing the time[s]/inventory[atm/cc]/activity[Bq/cc] data of relevant nuclides
    '''
    global start

    try:
        start_time = start
    except:
        start_time = time.time()
    start = start_time


    print('\tProcessing the *.DCS decay chain file...     ({:0.2f} seconds elapsed)'.format(time.time()-start))

    # Extract text from file
    f = open(filepath)
    lines = f.readlines()
    f.close()

    # Determine if extra data is written per isotope by querying whether an isotope's name or blank spaces are present in the line immediately below the first nuclide
    if len(lines[9][3:9].strip())==0:
        extra_chain_data_present = True
    else:
        extra_chain_data_present = False

    # First, scan for regions
    n_reg = 0
    reg_nos = []
    reg_labels = []
    for line in lines:
        if 'c<>-<>   no.' in line:
            n_reg += 1
            reg_nos.append(int(line[12:19]))
        if 'c<>-<>   region label :' in line:
            reg_labels.append(line[23:52].strip())
    if in_dchain_tools_debug_mode: print('{} regions found...     ({:0.2f} seconds elapsed)'.format(n_reg,time.time()-start))


    # Then, scan for time steps.  Need all individual times from beginning and time of end of irradiation.
    ntsteps = 0
    wtimes = [] # written times since start of calculations in seconds (so, the times at the end of each time step)
    beam_state = [] # in each time step, 1 if beam on, 0 if beam off
    end_of_irradiation_time = 0.0 # time (in seconds since start of irradiation) at which beam was switched off for the final time
    end_irr_time_located = False
    for line in lines:
        if ' --- during' in line:
            if 'irradiation' in line:
                beam_state.append(1)
            elif 'cooling' in line:
                beam_state.append(0)
            else:
                beam_state.append(None)
                print('found weird beam condition')
        elif ' --- output time' in line:
            ntsteps += 1
            t = float(line[39:53])
            wtimes.append(t)
            if 'after the last shutdown:' in line and not end_irr_time_located:
                taeoi_val = float(line[88:97])
                taeoi_unit = line[99]
                taeoi = taeoi_val*(time_str_to_sec_multiplier(taeoi_unit))
                end_of_irradiation_time = t - taeoi
                end_irr_time_located = True
        elif 'end of irradiation and decay calculation for this region' in line:
            break
    wtimes = np.array(wtimes)

    pstr = '{} time steps found\nend of irradiation at t = {:g} sec ({})\nend of calculation at t = {:g} sec ({})...                ({:0.2f} seconds elapsed)'.format(
            ntsteps,end_of_irradiation_time,seconds_to_ydhms(end_of_irradiation_time),wtimes[-1],seconds_to_ydhms(wtimes[-1]),time.time()-start)
    if in_dchain_tools_debug_mode: print(pstr)



    # Next, scan for other maximum limiting dimensions
    nnuc_max = 0 # maximum number of nuclides listed in a time step
    chni_max = 0 # highest index of a relevant chain found
    chln_max = 0 # maximum number of links (nuclides) found in any chain

    current_tstep_nnuc = 0 # number of nuclides in current time step
    chni = 0 # chain number index
    chln = 0 # chain length

    for line in lines:
        if len(line) < 5: continue

        if ' --- output time' in line or 'end of irradiation' in line:
            if current_tstep_nnuc > nnuc_max: nnuc_max = current_tstep_nnuc
            current_tstep_nnuc = 0 # reset count of nuclides in time step

        if len(line[3:9].strip())!=0 and line[11]=='(': # first chain entry of a nuclide
            current_tstep_nnuc += 1

        if line[11]=='(': # all chains have this in common
            chni = int(line[12:16])
            if chni > chni_max: chni_max = chni
            chln = 1 + line.count(')->')
            if chln > chln_max: chln_max = chln

    pstr =  '{} = maximum number of nuclides listed in a single time step\n'.format(nnuc_max)
    pstr += '{} = highest index found of all relevant chains\n'.format(chni_max)
    pstr += '{} = length of longest chain listed...                          ({:0.2f} seconds elapsed)'.format(chln_max,time.time()-start)
    if in_dchain_tools_debug_mode: print(pstr)


    # Construct arrays to hold decay chain information
    #   R (n_reg)    regions
    #   T (ntsteps)  time steps
    #   N (nnuc_max) max number of nuclides
    #   C (chni_max) maximum index of relevant chains
    #   L (chln_max) maximum number of links per chain

    inventory = np.zeros((n_reg,ntsteps,nnuc_max,chni_max,5)) # universal columns of DCS file [R,T,N,C,vi], vi: 0=N_i-1/V, 1=dN/V, 2=N_i/V, 3=A_i/V, 4=A_i
    l_chains  = np.zeros((n_reg,ntsteps,nnuc_max,chni_max)) # [R,T,N,C], length of listed chain
    prod_nuc  = np.empty((n_reg,ntsteps,nnuc_max), dtype='object') # [R,T,N], strings of the nuclide being produced
    chn_indx  = np.empty((n_reg,ntsteps,nnuc_max), dtype='object') # [R,T,N], lists of the chain indices printed
    link_nuc  = np.empty((n_reg,ntsteps,nnuc_max,chni_max,chln_max), dtype='object') # [R,T,N,C,L], strings of the nuclides in each chain
    decay_mode= np.empty((n_reg,ntsteps,nnuc_max,chni_max,chln_max), dtype='object') # [R,T,N,C,L], strings of the decay modes each link undergoes to produce the next link
    nuc_relvnt= np.empty((n_reg,ntsteps,nnuc_max), dtype='object') # [R,T,N], True/False denoting whether a nuclide meets the relevancy threshold in each time step
    if extra_chain_data_present:
        link_dN_info = np.zeros((n_reg,ntsteps,nnuc_max,chni_max,chln_max,3)) # [R,T,N,C,L,di], extra dN info di: 0=dN_Beam, 1=dN_Decay/nrxn, 2=dN_Total
        col_strs = ['dN_Beam','dN_Decay/nx','dN_Total']
        nexcol = len(col_strs)
    else:
        link_dN_info = None

    # Populate these arrays
    ri = None # region index
    ti = None # time step index
    ni = None # nuclide index
    ci = None # chain index (1 lower than Fortran value)

    # character column and spacing numbers for decay chains
    ch_sci = 95 # chain start column index
    dc_sci = 105 # column index of first decay mode listing
    vl_sci = 94 # column index of first extra decay chain value
    link_gap_sts = 17 # number of characters between start of one link and the next

    for line in lines:
        if len(line) < 5: continue

        if 'c<>-<>   no.' in line: # entering new region
            ri = find(int(line[12:19]),reg_nos)
            continue
        elif ' --- output time' in line: # entering new time step
            t = float(line[39:53])
            ti = find(t,wtimes)
            ni = -1 # reset nuclide index
            continue
        elif len(line[3:9].strip())!=0 and line[11]=='(': # entering new output nuclide
            ni += 1
            prod_nuc[ri,ti,ni] = line[3:9]

        if line[11]=='(': # if line contains a chain
            ci = int(line[12:16]) - 1 # chain index
            if not chn_indx[ri,ti,ni]:
                chn_indx[ri,ti,ni] = [ci]
            else:
                chn_indx[ri,ti,ni].append(ci)
            col_vals = line[25:92].strip().split()
            for vi in range(len(col_vals)):
                inventory[ri,ti,ni,ci,vi] = float(col_vals[vi])
            chln = 1 + line.count(')->')
            l_chains[ri,ti,ni,ci] = chln
            for li in range(chln):
                nci1 = ch_sci + li*link_gap_sts
                nci2 = nci1 + 6
                link_nuc[ri,ti,ni,ci,li] = line[nci1:nci2]
                if li != chln:
                    dci1 = dc_sci + li*link_gap_sts
                    dci2 = dci1 + 2
                    decay_mode[ri,ti,ni,ci,li] = line[dci1:dci2]
            continue

        if len(line[3:9].strip())==0 and extra_chain_data_present:
            vi = None
            for i in range(nexcol):
                if col_strs[i] in line:
                    vi = i
            for li in range(chln):
                vci1 = vl_sci + li*link_gap_sts
                vci2 = vci1 + 14
                if len(line[vci1:vci2].strip())==0:
                    val = 0
                else:
                    val = float(line[vci1:vci2])
                link_dN_info[ri,ti,ni,ci,li,vi] = val



    # Now extract results from the data arrays
    if in_dchain_tools_debug_mode: print()
    print('\tNow processing decay chain results...        ({:0.2f} seconds elapsed)'.format(time.time()-start))

    notable_nuclides_AvT_by_region = [] # list of arrays (one per region) containing the time/inventory/activity data of relevant nuclides
    notable_nuclides_names_by_region = [] # list of lists (one per region) containing the relevant nuclides per region

    for ri in range(n_reg):
        if in_dchain_tools_debug_mode: print('Region no. {} ({})'.format(reg_nos[ri],reg_labels[ri]))
        relevant_nuclides = []
        for ti in range(ntsteps):
            t = wtimes[ti]
            if print_progress:
                if t > end_of_irradiation_time:
                    tai = t - end_of_irradiation_time
                    print('\tAt time {:g} sec ({}), which is {:g} sec ({}) after end of final irradiation'.format(t,seconds_to_ydhms(t),tai,seconds_to_ydhms(tai)))
                else:
                    print('\tAt time {:g} sec ({})'.format(t,seconds_to_ydhms(t)))

            # First, get total information for the time step
            N0 = [] # inventory at start of time step
            N1 = [] # inventory at end of time step
            A0 = [] # activity at start of time step
            A1 = [] # activity at end of time step

            for ni in range(nnuc_max):
                if not prod_nuc[ri,ti,ni]: continue # skip empty nuclide indices
                chain_indices = chn_indx[ri,ti,ni]
                ci0 = chain_indices[0] # First chain
                ci1 = chain_indices[-1] # Last (nonzero) chain
                N0.append(inventory[ri,ti,ni,ci0,0])
                N1.append(inventory[ri,ti,ni,ci1,2])
                lam = inventory[ri,ti,ni,ci0,3]/inventory[ri,ti,ni,ci0,2]
                A0.append(lam*inventory[ri,ti,ni,ci0,0])
                A1.append(inventory[ri,ti,ni,ci1,3])

            N0_tot_tstep = np.sum(N0) # total inventory at start of time step
            N1_tot_tstep = np.sum(N1) # total inventory at end of time step
            A0_tot_tstep = np.sum(A0) # total activity at start of time step
            A1_tot_tstep = np.sum(A1) # total activity at end of time step

            # Determine which nuclides meet the relevancy threshold
            pstr = ('\t\tRelevant radionuclides include:\n')

            nii = -1
            for ni in range(nnuc_max):
                if not prod_nuc[ri,ti,ni]: continue # skip empty nuclide indices
                nii += 1
                A1_fract_threshold = relevancy_threshold # Nuclide must be responsible for at least 0.1% total activity at end of time step
                A1_nuc_frac = A1[nii]/A1_tot_tstep
                if A1_nuc_frac > A1_fract_threshold:
                    nuc_relvnt[ri,ti,ni] = True
                    if prod_nuc[ri,ti,ni] not in relevant_nuclides: relevant_nuclides.append(prod_nuc[ri,ti,ni])
                    pstr += ('\t\t  - {} with {:0.2f}% total activity\n'.format(prod_nuc[ri,ti,ni],100*A1_nuc_frac))
                else:
                    nuc_relvnt[ri,ti,ni] = False

            if print_progress:
                print(pstr)

        n_relevant_nuclides = len(relevant_nuclides)

        # now collect activity of each nuclide at each time step
        relv_nuc_inv  = np.zeros((ntsteps,n_relevant_nuclides,3)) # [T,rlvN,3], time[s]/inventory[atm/cc]/activity[Bq/cc] for relevant nuclides

        for ti in range(ntsteps):
            t = wtimes[ti]
            relv_nuc_inv[ti,:,0] = t
            for ni in range(nnuc_max):
                if not prod_nuc[ri,ti,ni]: continue # skip empty nuclide indices
                if prod_nuc[ri,ti,ni] not in relevant_nuclides: continue # only want nuclides which are at some point relevant
                chain_indices = chn_indx[ri,ti,ni]
                ci1 = chain_indices[-1]

                #if nuclide is relevant, find its index among the relevant ones
                rni = find(prod_nuc[ri,ti,ni],relevant_nuclides)
                relv_nuc_inv[ti,rni,1] = inventory[ri,ti,ni,ci1,2]
                relv_nuc_inv[ti,rni,2] = inventory[ri,ti,ni,ci1,3]

        notable_nuclides_names_by_region.append(relevant_nuclides)
        notable_nuclides_AvT_by_region.append(relv_nuc_inv)


    return inventory, l_chains, prod_nuc, chn_indx, link_nuc, decay_mode, link_dN_info, end_of_irradiation_time, notable_nuclides_names_by_region, notable_nuclides_AvT_by_region


def parse_dtrk_file(path_to_dtrk_file,return_metadata=False):
    '''
    Description:
        Parses the output file of a T-Track tally generated by PHITS.  Note that this specific function assumes that the T-Track
        tally was one automatically generated by and corresponding to a T-Dchain tally but in principle works with any T-Track tally.
        This works for region, xyz, and tetrahedral mesh geometries in either the original or reduced format.

    Inputs:
        - `path_to_dtrk_file` = path to the T-Track tally output file to be parsed
        - `return_metadata` = Boolean indicating whether additional information is outputted with the flux (D=`False`)

    Outputs:
        - `flux` = a RxEx4 array containing regionwise fluxes [Elower/Eupper/flux/abs_error]
        - `dtrk_metadata` (only returned if `return_metadata=True`) = list of length two
               - `dtrk_metadata[0]` = string denoting axis type 'eng' (old full format) or 'dchain' (new reduced format)
               - `dtrk_metadata[1]` = string denoting mesh type as either 'reg', 'xyz', or 'tet'
    '''

    # Extract text from file
    f = open(path_to_dtrk_file)
    file_text = f.read()
    lines = file_text.split('\n')
    f.close()

    # Determine geometry type (mesh = reg, xyz, or tet)
    for line in lines:
        if 'mesh =' in line:
            meshtype = line.replace('mesh =','').strip().split()[0]
            break

    # Determine if original or reduced format (axis = eng or axis = dchain)
    for line in lines:
        if 'axis =' in line:
            axistype = line.replace('axis =','').strip().split()[0]
            break
    # Double check
    for li, line in enumerate(lines):
        if li>500: break
        if '#  e-lower      e-upper      neutron     r.err ' in line:
            axistype='eng'
            break

    dtrk_metadata = [axistype,meshtype]

    # Determine number of regions
    if axistype=='eng':
        nreg = file_text.count('#   no. =')
    elif axistype=='dchain':
        for li, line in reversed(list(enumerate(lines))):
            #print(line)
            if '0    0   0.0000E+00  0.0000' in line:
                nreg = int(lines[li-1].split()[0])
                break

    if axistype=='dchain':
        nEbins = 1968
    else:
        for line in lines:
            if 'ne =' in line:
                nEbins = int(line.replace('ne =','').strip().split()[0])
                break

    flux = np.zeros((nreg,nEbins,4))

    if axistype=='eng':
        in_flux_lines = False
        ei = 0
        ri = -1

        for line in lines:
            if '#   no. =' in line:
                ri += 1
            if '#  e-lower      e-upper      neutron     r.err ' in line:
                in_flux_lines = True
                continue
            if in_flux_lines:
                flux[ri,ei,:] = [float(x) for x in line.split()]
                flux[ri,ei,3] = flux[ri,ei,3]*flux[ri,ei,2] # convert relative error to absolute error
                ei += 1
                if ei == nEbins:
                    in_flux_lines = False
                    ei = 0
    elif axistype=='dchain':
        ebins = [20.0] + ECCO1968_Ebins(1968)
        ebins = ebins[::-1]
        in_flux_lines = False
        for line in lines:
            if '# num ie flux r.err' in line:
                in_flux_lines = True
                continue
            if '0    0   0.0000E+00  0.0000' in line:
                in_flux_lines = False
                break
            if in_flux_lines:
                vals = line.split()
                ri = int(vals[0])-1
                ei = int(vals[1])-1
                fval = float(vals[2])
                ferr = float(vals[3])

                flux[ri,ei,0] = ebins[ei]
                flux[ri,ei,1] = ebins[ei+1]
                flux[ri,ei,2] = fval
                flux[ri,ei,3] = fval*ferr

    if return_metadata:
        return flux, dtrk_metadata
    else:
        return flux


def parse_dyld_files(path_to_dyld_file,iredufmt=None):
    '''
    Description:
        Parses the output files of a T-Yield tally generated by PHITS with axis=dchain.  This function assumes
        that the T-Yield tally was one automatically generated by and corresponding to a T-Dchain tally (axis=dchain).
        This works for region, xyz, and tetrahedral mesh geometries in either the original or reduced format.

    Inputs:
        - `path_to_dyld_file` = path to the T-Yield tally output file to be parsed
                           (the *_err.dyld file of the same name is automatically searched for and read, if present)
        - `iredufmt` = (DEPRICATED; this is now determined automatically)
                   integer 1 or 0 specifying how the xyz meshes are ordered relative to the internal region numbers.
                   In the new format (1), region indices are incremented as x->y->z (x=innermost loop); this is reversed in the old format (0).
                   Ultimately, this corresponds to the same iredufmt parameter in PHITS/DCHAIN, 1='new' and 0='old'.
                   This variable is only used for xyz meshes where this ordering matters.

    Outputs:
        - `yields` = a RxNx2 array containing regionwise yields (and their absolute uncertainties) for all nuclides produced in T-Yield
        - `nuclide_names_yld` = a length N list of all nuclide names in order
    '''

    # Extract text from file
    f = open(path_to_dyld_file)
    file_text = f.read()
    lines = file_text.split('\n')
    f.close()

    # determine if in reduced format
    iredufmt=0
    for li, line in enumerate(lines):
        if "# num nucleusID yield r.err" in line:
            iredufmt=1
            break
        if "isotope production #" in line:
            iredufmt=0
            break


    # Get error data if available
    if iredufmt==0:
        try:
            f_err = open(path_to_dyld_file.replace('.dyld','_err.dyld'))
            file_text_err = f_err.read()
            lines_err = file_text_err.split('\n')
            f_err.close()
            err_dyld_found = True
        except:
            file_text_err = None
            lines_err = None
            err_dyld_found = False

    # Determine geometry type (mesh = reg, xyz, or tet)
    for line in lines:
        if 'mesh =' in line:
            meshtype = line.replace('mesh =','').strip().split()[0]
            break

    # If xyz mesh, need to find mesh dimensions:
    if meshtype=='xyz':
        for line in lines:
            if 'nx =' in line:
                nx = int(line.replace('nx =','').strip().split()[0])
            elif 'ny =' in line:
                ny = int(line.replace('ny =','').strip().split()[0])
            elif 'nz =' in line:
                nz = int(line.replace('nz =','').strip().split()[0])
                break

    # Find starting line
    for li, line in enumerate(lines):
        if 'nuclear yield (or production)' in line:
            li_start = li
            break

    if iredufmt==1:
        # Count number of nuclides present in whole file
        nreg = 0
        nuc_id_list = []
        for li, line in enumerate(lines):
            if li <= li_start+3: continue # in header
            vals = line.strip().split()
            if int(vals[0])==0: break # reached end
            if int(vals[0])>nreg: nreg = int(vals[0])
            zzzaaam = int(vals[1])
            if zzzaaam not in nuc_id_list: nuc_id_list.append(zzzaaam)

        nnuc = len(nuc_id_list)
        yields = np.zeros((nreg,nnuc,2))
        nuclide_names_yld = []

        # Get names
        nuc_id_list = sorted(nuc_id_list)
        for id in nuc_id_list:
            nuclide_names_yld.append(ZAM_to_Dname(id))

        # Get values
        for li, line in enumerate(lines):
            if li <= li_start+3: continue # in header
            vals = line.strip().split()
            if int(vals[0])==0: break # reached end
            ri = int(vals[0]) - 1
            zzzaaam = int(vals[1])
            ni = nuc_id_list.index(zzzaaam)
            yields[ri,ni,0] = float(vals[2])
            yields[ri,ni,1] = float(vals[3])*float(vals[2])

    else: # old ''traditional'' format
        # Count number of nuclides present in whole file
        nnuc = 0
        for li, line in enumerate(lines):
            if li <= li_start+2: continue # skip header lines
            if 'isotope production' in line:
                N_bounds = line.strip().split('=')[-1].split()
                N_bounds = [int(i) for i in N_bounds]
                nnuc += N_bounds[1] - N_bounds[0] + 1

        # Determine number of regions
        nreg = 0
        for li, line in enumerate(lines):
            if li <= li_start+4: continue # skip header lines
            if len(line) < 2: break # reached end of first element block
            nreg += 1

        yields = np.zeros((nreg,nnuc,2))
        nuclide_names_yld = []

        # Extract yield data
        ni = 0 # nuclide index
        ni_newstart = 0
        ri = 0 # region index
        for li, line in enumerate(lines):
            if li <= li_start+2: continue # skip header lines
            if len(line) < 2: continue # skip line breaks

            if 'isotope production' in line:
                # extract Z and A info
                Z = int(line.strip().split('-')[0])
                N_bounds = line.strip().split('=')[-1].split()
                N_bounds = [int(i) for i in N_bounds]
                N_list = []
                for i in range(N_bounds[1]-N_bounds[0]+1):
                    N_list.append(N_bounds[0]+i)
                nisotopes = len(N_list)
                A_list = [N+Z for N in N_list]
                ni_newstart = len(nuclide_names_yld)
                for A in A_list:
                    ZAM = 10*A + 10000*Z
                    nuclide_names_yld.append(ZAM_to_Dname(ZAM))
                on_buffer_line = True
                continue

            if on_buffer_line:
                ri = 0
                on_buffer_line = False
                continue

            if '# Information for Restart Calculation' in line: break # reached end of useful info

            # Only lines making it to this point will be ones with region and yield data
            vals = line.strip().split()
            if meshtype=='xyz':
                yvals = vals[3:]
                if err_dyld_found: yvals_rerr = lines_err[li].strip().split()[3:]
                jx,jy,jz = int(vals[0]),int(vals[1]),int(vals[2])
                rii = jz + (jy-1)*nz + (jx-1)*(nz*ny)
                #if iredufmt==1:
                #    rii = jx + (jy-1)*nx + (jz-1)*(nx*ny)
                #else:
                #    rii = jz + (jy-1)*nz + (jx-1)*(nz*ny)
            else:
                yvals = vals[1:]
                if err_dyld_found: yvals_rerr = lines_err[li].split()[1:]
                rii = ri

            for i in range(nisotopes):
                yields[rii,ni_newstart+i,0] = float(yvals[i])
                if err_dyld_found: yields[rii,ni_newstart+i,1] = float(yvals_rerr[i])*yields[rii,ni_newstart+i,0]

            ri += 1

    return yields, nuclide_names_yld





def Dname_to_ZAM(Dname):
    '''
    Description:
        Converts a DCHAIN-formatted nuclide name to a ZZZAAAM number

    Inputs:
        - `Dname` = nuclide identification string in DCHAIN format

    Outputs:
        - `ZZZAAAM` = nuclide identification ineger, calculated as 10000\*Z + 10\*A + m

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
    AAA = Dname[2:5]
    A = int(AAA)
    symbol = Dname[0:2]
    if 'XX' in symbol: symbol='n '
    Z = find(symbol,elms)
    if Dname[-1] == ' ':
        m = 0
    elif Dname[-1] == 'm':
        m = 1
    elif Dname[-1] == 'n':
        m = 2
    ZAM = int(10000*Z + 10*A + m)
    return ZAM

def ZAM_to_Dname(ZAM):
    '''
    Description:
        Converts a ZZZAAAM number to a DCHAIN-formatted nuclide name

    Inputs:
        - `ZZZAAAM` = nuclide identification ineger, calculated as 10000\*Z + 10\*A + m

    Outputs:
        - `Dname` = nuclide identification string in DCHAIN format
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
    m = int(str(ZAM)[-1])
    A = int(str(ZAM)[-4:-1])
    Z = int(str(ZAM)[:-4])
    sym = elms[Z]
    A_str = '{:>3}'.format(A)
    m_str_list = [' ','m','n']
    m_str = m_str_list[m]
    Dname = sym + A_str + m_str
    return Dname

def Dname_to_Latex(Dname):
    '''
    Description:
        Converts a DCHAIN-formatted nuclide name to a LaTeX-formatted string

    Inputs:
        - `Dname` = nuclide identification string in DCHAIN format

    Outputs:
        - nuclide name as a LaTeX-formatted raw string
    '''
    AAA = Dname[2:5].strip()
    symbol = Dname[0:2].strip()
    m = Dname[-1].strip()
    latex_str = r"$^{{{}{}}}$".format(AAA,m) + "{}".format(symbol)
    return latex_str


def nuclide_plain_str_to_Dname(nuc_str):
    '''
    Description:
        Converts a plaintext string of a nuclide to a DCHAIN-formatted nuclide string

    Dependencies:
        - `nuclide_plain_str_ZZZAAAM`
        - `ZAM_to_Dname`

    Inputs:

       - `nuc_str` = string to be converted; a huge variety of formats are supported, but they all must follow the following rules:
            + Isomeric/metastable state characters must always immediately follow the atomic mass characters.
                Isomeric state labels MUST either:
                  - (1) be a single lower-case character
                  - (2) begin with any non-numeric character and end with a number
            + Atomic mass numbers must be nonnegative integers OR the string `"nat"` (in which case no metastable states can be written)
            + Elemental symbols MUST begin with an upper-case character

    Outputs:
        - DCHAIN-formatted string of nuclide name
    '''
    return ZAM_to_Dname(nuclide_plain_str_ZZZAAAM(nuc_str))

def rxn_to_dchain_str(target,reaction=None,product=None):
    '''
    Desription:
        Provided a target nuclide and reaction, and optionally a target, generate a reaction string in the format used in DCHAIN's nrxn libs

    Dependencies:
        `nuclide_plain_str_ZZZAAAM`

        `ZZZAAAM_to_dchain_xs_lib_str`

    Inputs:
        - `target` = string in general format of target nuclide
        - Note: at least one of the below options must be provided.
             - `reaction` = (optional) either an int MT number (ENDF6 format) or a string of the ejectiles from the neutron reaction (case-insensitive), the "X" in (N,X)
             - `product` = (optional) string in general format of product nuclide (if omitted, product in ground state is assumed)

    Outputs:
        - `rxn_dchain_str` = string formatted identically as that found in DCHAIN's neutron reaction cross section libraries
    '''

    if not reaction and not product:
        print('Warning: no reaction or product provided with target {}.'.format(target))
        ZZZAAAM = nuclide_plain_str_ZZZAAAM(target)
        target_dstr = ZZZAAAM_to_dchain_xs_lib_str(ZZZAAAM)
        dstr = target_dstr + '(N,'
        return dstr


    ZZZAAAM = nuclide_plain_str_ZZZAAAM(target)
    target_dstr = ZZZAAAM_to_dchain_xs_lib_str(ZZZAAAM)
    if product: # if not None (product is provided)
        ZZZAAAM_prod = nuclide_plain_str_ZZZAAAM(product)
        product_dstr = ZZZAAAM_to_dchain_xs_lib_str(ZZZAAAM_prod)

    react = ['   ', '   ', '   ', '   ', 'N  ', '   ', '   ', '   ', '   ', '   ', '   ', '2ND', '   ', '   ', '   ', '   ', '2N ', '3N ', 'FIS', '   ',
             '   ', '   ', 'NA ', 'N3A', '2NA', '3NA', '   ', '   ', 'NP ', 'N2A', '2N2', '   ', 'ND ', 'NT ', 'NE ', 'ND2', 'NT2', '4N ', '   ', '   ',
             '   ', '2NP', '3NP', '   ', 'N2P', 'NPA', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ',
             '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ',
             '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ', '   ',
             '   ', '   ', 'G  ', 'P  ', 'D  ', 'T  ', 'HE3', 'A  ', '2A ', '3A ', '   ', '2P ', 'PA ', 'T2A', 'D2A', 'PD ', 'PT ', 'DA ', '   ', '   ']
    dZ = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -6, -2, -2, 0, 0, -1, -4, -4, 0, -1, -1, -2, -5, -5, 0, 0, 0, 0, -1, -1,
          0, -2, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -2, -2, -4, -6, 0, -2, -3, -5, -5, -2, -2, -3, 0, 0]
    dA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, 0, 0, 0, 0, -1, -2, 0, 0, 0, 0, -4, -12, -5, -6, 0, 0, -1, -8, -9, 0, -2, -3, -3, -10, -11, -3, 0, 0, 0, -2,
          -3, 0, -2, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, -2, -2, -3, -7, -11, 0, -1, -4, -10, -9, -2, -3, -5, 0, 0]

    if reaction: # reaction is provided
        # Get reaction from MT / check if valid reaction
        if isinstance(reaction, float): reaction = int(reaction)
        if isinstance(reaction, int):
            MT = reaction
            rxn = react[MT]
        else:
            rxn = "{:3}".format(reaction.upper())
            if rxn not in react:
                print('Reaction "{}" not in reaction list for DCHAIN, check formatting or enter ENDF MT number (0-119)'.format(rxn))
                return None
            else:
                MT = react.index(rxn)

    if not product: # need to figure out product from parent and rxn, assume ground state (but omit final isomeric characters from string in case xslib has other states too)
        ZAM_str = str(ZZZAAAM)
        M = 0
        A = int(ZAM_str[-4:-1]) + dA[MT]
        Z = int(ZAM_str[:-4]) + dZ[MT]
        ZZZAAAM_prod = 10000*Z + 10*A + M
        product_dstr = ZZZAAAM_to_dchain_xs_lib_str(ZZZAAAM_prod)[:-2]
        if MT == 18: product_dstr = '' # fission

    if not reaction: # need to find missing reaction from target and product, isomeric states are ignored
        ZAM_str = str(ZZZAAAM)
        A_tar = int(ZAM_str[-4:-1])
        Z_tar = int(ZAM_str[:-4])
        ZAM_str_prod = str(ZZZAAAM_prod)
        A_prod = int(ZAM_str_prod[-4:-1])
        Z_prod = int(ZAM_str_prod[:-4])
        rxn_dA = A_prod - A_tar
        rxn_dZ = Z_prod - Z_tar
        matching_dA = [index for index,value in enumerate(dA) if value == rxn_dA]
        matching_dZ = [index for index,value in enumerate(dZ) if value == rxn_dZ]
        MT = set(matching_dA).intersection(matching_dZ).pop() # gets the value which is common between the two lists, in this case the index of the reaction
        rxn = react[MT]

    if reaction and product: # check to make sure they are compatible
        # if mismatch occurs, assume product is more likely correct than rxn
        ZAM_str = str(ZZZAAAM)
        A_tar = int(ZAM_str[-4:-1])
        Z_tar = int(ZAM_str[:-4])
        ZAM_str_prod = str(ZZZAAAM_prod)
        A_prod = int(ZAM_str_prod[-4:-1])
        Z_prod = int(ZAM_str_prod[:-4])
        rxn_dA = A_prod - A_tar
        rxn_dZ = Z_prod - Z_tar
        matching_dA = [index for index,value in enumerate(dA) if value == rxn_dA]
        matching_dZ = [index for index,value in enumerate(dZ) if value == rxn_dZ]
        if A_tar==A_prod and Z_tar==Z_prod:
            MT_calc = 4
        else:
            MT_calc = set(matching_dA).intersection(matching_dZ).pop() # gets the value which is common between the two lists, in this case the index of the reaction
        rxn_calc = react[MT_calc]
        if rxn_calc != rxn:
            print('Warning, mismatch between reaction (N,{}) and product ({}) with target {}; assuming product ({}) is correct and reaction should be (N,{}) instead.'.format(rxn.strip(),product,target,product_dstr,rxn_calc.strip()))
            rxn = rxn_calc

    dstr = target_dstr + '(N,{})'.format(rxn) + product_dstr

    return dstr

def ZZZAAAM_to_dchain_xs_lib_str(ZZZAAAM):
    '''
    Description:
       Converts a ZZZAAAM number to the 7-character nuclide string used by the DCHAIN neutron reaction cross section libraries.

    Inputs:
        - `ZZZAAAM` = nuclide identification ineger, calculated as 10000\*Z + 10\*A + m

    Outputs:
        - `D_xs_name` = nuclide identification string in DCHAIN's cross section library format
    '''
    ZAM_str = str(ZZZAAAM)
    M = int(ZAM_str[-1])
    A = str(int(ZAM_str[-4:-1]))
    Z = ZAM_str[:-4]
    sym = Element_Z_to_Sym(int(Z)).upper()
    if M==0:
        M_str = '  '
    else:
        M_str = 'M' + str(M)
    dstr = "{:2}{:>3}{:2}".format(sym,A,M_str)
    return dstr

def ECCO1968_Ebins(n):
    '''
    Description:
        Returns the n highest energy bin values of the ECCO 1968-group energy binning structure.

    Inputs:
        - `n` = number of energy bins (from 20 MeV down) to be returned

    Outputs:
        - list of `n` energy bins of the ECCO 1968-group structure
    '''
    ECCO_bins = [
        1.964033E+01,1.947734E+01,1.931570E+01,1.915541E+01,1.899644E+01,1.883880E+01,1.868246E+01,1.852742E+01,1.837367E+01,1.822119E+01,1.806998E+01,1.792002E+01,1.777131E+01,1.762383E+01,1.747757E+01,1.733253E+01,1.718869E+01,1.704605E+01,1.690459E+01,1.676430E+01,1.662518E+01,
        1.648721E+01,1.635039E+01,1.621470E+01,1.608014E+01,1.594670E+01,1.581436E+01,1.568312E+01,1.555297E+01,1.542390E+01,1.529590E+01,1.516897E+01,1.504309E+01,1.491825E+01,1.479444E+01,1.467167E+01,1.454991E+01,1.442917E+01,1.430943E+01,1.419068E+01,1.407291E+01,
        1.395612E+01,1.384031E+01,1.372545E+01,1.361155E+01,1.349859E+01,1.338657E+01,1.327548E+01,1.316531E+01,1.305605E+01,1.294770E+01,1.284025E+01,1.273370E+01,1.262802E+01,1.252323E+01,1.241930E+01,1.231624E+01,1.221403E+01,1.211267E+01,1.201215E+01,1.191246E+01,
        1.181360E+01,1.171557E+01,1.161834E+01,1.152193E+01,1.142631E+01,1.133148E+01,1.123745E+01,1.114419E+01,1.105171E+01,1.095999E+01,1.086904E+01,1.077884E+01,1.068939E+01,1.060068E+01,1.051271E+01,1.042547E+01,1.033895E+01,1.025315E+01,1.016806E+01,1.008368E+01,
        1.000000E+01,9.917013E+00,9.834715E+00,9.753099E+00,9.672161E+00,9.591895E+00,9.512294E+00,9.433354E+00,9.355070E+00,9.277435E+00,9.200444E+00,9.124092E+00,9.048374E+00,8.973284E+00,8.898818E+00,8.824969E+00,8.751733E+00,8.679105E+00,8.607080E+00,8.535652E+00,
        8.464817E+00,8.394570E+00,8.324906E+00,8.255820E+00,8.187308E+00,8.119363E+00,8.051983E+00,7.985162E+00,7.918896E+00,7.853179E+00,7.788008E+00,7.723377E+00,7.659283E+00,7.595721E+00,7.532687E+00,7.470175E+00,7.408182E+00,7.346704E+00,7.285736E+00,7.225274E+00,
        7.165313E+00,7.105850E+00,7.046881E+00,6.988401E+00,6.930406E+00,6.872893E+00,6.815857E+00,6.759294E+00,6.703200E+00,6.647573E+00,6.592406E+00,6.537698E+00,6.483443E+00,6.429639E+00,6.376282E+00,6.323367E+00,6.270891E+00,6.218851E+00,6.167242E+00,6.116062E+00,
        6.065307E+00,6.014972E+00,5.965056E+00,5.915554E+00,5.866462E+00,5.817778E+00,5.769498E+00,5.721619E+00,5.674137E+00,5.627049E+00,5.580351E+00,5.534042E+00,5.488116E+00,5.442572E+00,5.397406E+00,5.352614E+00,5.308195E+00,5.264143E+00,5.220458E+00,5.177135E+00,
        5.134171E+00,5.091564E+00,5.049311E+00,5.007408E+00,4.965853E+00,4.924643E+00,4.883775E+00,4.843246E+00,4.803053E+00,4.763194E+00,4.723666E+00,4.684465E+00,4.645590E+00,4.607038E+00,4.568805E+00,4.530890E+00,4.493290E+00,4.456001E+00,4.419022E+00,4.382350E+00,
        4.345982E+00,4.309916E+00,4.274149E+00,4.238679E+00,4.203504E+00,4.168620E+00,4.134026E+00,4.099719E+00,4.065697E+00,4.031957E+00,3.998497E+00,3.965314E+00,3.932407E+00,3.899773E+00,3.867410E+00,3.835316E+00,3.803488E+00,3.771924E+00,3.740621E+00,3.709579E+00,
        3.678794E+00,3.648265E+00,3.617989E+00,3.587965E+00,3.558189E+00,3.528661E+00,3.499377E+00,3.470337E+00,3.441538E+00,3.412978E+00,3.384654E+00,3.356566E+00,3.328711E+00,3.301087E+00,3.273692E+00,3.246525E+00,3.219583E+00,3.192864E+00,3.166368E+00,3.140091E+00,
        3.114032E+00,3.088190E+00,3.062562E+00,3.037147E+00,3.011942E+00,2.986947E+00,2.962159E+00,2.937577E+00,2.913199E+00,2.889023E+00,2.865048E+00,2.841272E+00,2.817693E+00,2.794310E+00,2.771121E+00,2.748124E+00,2.725318E+00,2.702701E+00,2.680272E+00,2.658030E+00,
        2.635971E+00,2.614096E+00,2.592403E+00,2.570889E+00,2.549554E+00,2.528396E+00,2.507414E+00,2.486605E+00,2.465970E+00,2.445505E+00,2.425211E+00,2.405085E+00,2.385126E+00,2.365332E+00,2.345703E+00,2.326237E+00,2.306932E+00,2.287787E+00,2.268802E+00,2.249973E+00,
        2.231302E+00,2.212785E+00,2.194421E+00,2.176211E+00,2.158151E+00,2.140241E+00,2.122480E+00,2.104866E+00,2.087398E+00,2.070076E+00,2.052897E+00,2.035860E+00,2.018965E+00,2.002210E+00,1.985595E+00,1.969117E+00,1.952776E+00,1.936570E+00,1.920499E+00,1.904561E+00,
        1.888756E+00,1.873082E+00,1.857538E+00,1.842122E+00,1.826835E+00,1.811675E+00,1.796640E+00,1.781731E+00,1.766944E+00,1.752281E+00,1.737739E+00,1.723318E+00,1.709017E+00,1.694834E+00,1.680770E+00,1.666821E+00,1.652989E+00,1.639271E+00,1.625667E+00,1.612176E+00,
        1.598797E+00,1.585530E+00,1.572372E+00,1.559323E+00,1.546383E+00,1.533550E+00,1.520823E+00,1.508202E+00,1.495686E+00,1.483274E+00,1.470965E+00,1.458758E+00,1.446652E+00,1.434646E+00,1.422741E+00,1.410934E+00,1.399225E+00,1.387613E+00,1.376098E+00,1.364678E+00,
        1.353353E+00,1.342122E+00,1.330984E+00,1.319938E+00,1.308985E+00,1.298122E+00,1.287349E+00,1.276666E+00,1.266071E+00,1.255564E+00,1.245145E+00,1.234812E+00,1.224564E+00,1.214402E+00,1.204324E+00,1.194330E+00,1.184418E+00,1.174589E+00,1.164842E+00,1.155175E+00,
        1.145588E+00,1.136082E+00,1.126654E+00,1.117304E+00,1.108032E+00,1.098836E+00,1.089717E+00,1.080674E+00,1.071706E+00,1.062812E+00,1.053992E+00,1.045245E+00,1.036571E+00,1.027969E+00,1.019438E+00,1.010978E+00,1.002588E+00,9.942682E-01,9.860171E-01,9.778344E-01,
        9.697197E-01,9.616723E-01,9.536916E-01,9.457772E-01,9.379285E-01,9.301449E-01,9.224259E-01,9.147709E-01,9.071795E-01,8.996511E-01,8.921852E-01,8.847812E-01,8.774387E-01,8.701570E-01,8.629359E-01,8.557746E-01,8.486728E-01,8.416299E-01,8.346455E-01,8.277190E-01,
        8.208500E-01,8.140380E-01,8.072825E-01,8.005831E-01,7.939393E-01,7.873507E-01,7.808167E-01,7.743369E-01,7.679109E-01,7.615382E-01,7.552184E-01,7.489511E-01,7.427358E-01,7.365720E-01,7.304594E-01,7.243976E-01,7.183860E-01,7.124243E-01,7.065121E-01,7.006490E-01,
        6.948345E-01,6.890683E-01,6.833499E-01,6.776790E-01,6.720551E-01,6.664779E-01,6.609470E-01,6.554620E-01,6.500225E-01,6.446282E-01,6.392786E-01,6.339734E-01,6.287123E-01,6.234948E-01,6.183206E-01,6.131893E-01,6.081006E-01,6.030542E-01,5.980496E-01,5.930866E-01,
        5.881647E-01,5.832837E-01,5.784432E-01,5.736429E-01,5.688824E-01,5.641614E-01,5.594796E-01,5.548366E-01,5.502322E-01,5.456660E-01,5.411377E-01,5.366469E-01,5.321934E-01,5.277769E-01,5.233971E-01,5.190535E-01,5.147461E-01,5.104743E-01,5.062381E-01,5.020369E-01,
        4.978707E-01,4.937390E-01,4.896416E-01,4.855782E-01,4.815485E-01,4.775523E-01,4.735892E-01,4.696591E-01,4.657615E-01,4.618963E-01,4.580631E-01,4.542618E-01,4.504920E-01,4.467535E-01,4.430460E-01,4.393693E-01,4.357231E-01,4.321072E-01,4.285213E-01,4.249651E-01,
        4.214384E-01,4.179410E-01,4.144727E-01,4.110331E-01,4.076220E-01,4.042393E-01,4.008846E-01,3.975578E-01,3.942586E-01,3.909868E-01,3.877421E-01,3.845243E-01,3.813333E-01,3.781687E-01,3.750304E-01,3.719181E-01,3.688317E-01,3.657708E-01,3.627354E-01,3.597252E-01,
        3.567399E-01,3.537795E-01,3.508435E-01,3.479320E-01,3.450446E-01,3.421812E-01,3.393415E-01,3.365254E-01,3.337327E-01,3.309631E-01,3.282166E-01,3.254928E-01,3.227916E-01,3.201129E-01,3.174564E-01,3.148219E-01,3.122093E-01,3.096183E-01,3.070489E-01,3.045008E-01,
        3.019738E-01,2.994678E-01,2.985000E-01,2.972000E-01,2.969826E-01,2.945181E-01,2.920740E-01,2.896501E-01,2.872464E-01,2.848626E-01,2.824986E-01,2.801543E-01,2.778293E-01,2.755237E-01,2.732372E-01,2.709697E-01,2.687210E-01,2.664910E-01,2.642794E-01,2.620863E-01,
        2.599113E-01,2.577544E-01,2.556153E-01,2.534941E-01,2.513904E-01,2.493042E-01,2.472353E-01,2.451835E-01,2.431488E-01,2.411310E-01,2.391299E-01,2.371455E-01,2.351775E-01,2.332258E-01,2.312903E-01,2.293709E-01,2.274674E-01,2.255797E-01,2.237077E-01,2.218512E-01,
        2.200102E-01,2.181844E-01,2.163737E-01,2.145781E-01,2.127974E-01,2.110314E-01,2.092801E-01,2.075434E-01,2.058210E-01,2.041130E-01,2.024191E-01,2.007393E-01,1.990734E-01,1.974214E-01,1.957830E-01,1.941583E-01,1.925470E-01,1.909491E-01,1.893645E-01,1.877930E-01,
        1.862346E-01,1.846891E-01,1.831564E-01,1.816364E-01,1.801291E-01,1.786342E-01,1.771518E-01,1.756817E-01,1.742237E-01,1.727779E-01,1.713441E-01,1.699221E-01,1.685120E-01,1.671136E-01,1.657268E-01,1.643514E-01,1.629875E-01,1.616349E-01,1.602936E-01,1.589634E-01,
        1.576442E-01,1.563359E-01,1.550385E-01,1.537519E-01,1.524760E-01,1.512106E-01,1.499558E-01,1.487113E-01,1.474772E-01,1.462533E-01,1.450396E-01,1.438360E-01,1.426423E-01,1.414586E-01,1.402847E-01,1.391205E-01,1.379660E-01,1.368210E-01,1.356856E-01,1.345596E-01,
        1.334429E-01,1.323355E-01,1.312373E-01,1.301482E-01,1.290681E-01,1.279970E-01,1.269348E-01,1.258814E-01,1.248368E-01,1.238008E-01,1.227734E-01,1.217545E-01,1.207441E-01,1.197421E-01,1.187484E-01,1.177629E-01,1.167857E-01,1.158165E-01,1.148554E-01,1.139022E-01,
        1.129570E-01,1.120196E-01,1.110900E-01,1.101681E-01,1.092538E-01,1.083471E-01,1.074480E-01,1.065563E-01,1.056720E-01,1.047951E-01,1.039254E-01,1.030630E-01,1.022077E-01,1.013595E-01,1.005184E-01,9.968419E-02,9.885694E-02,9.803655E-02,9.722297E-02,9.641615E-02,
        9.561602E-02,9.482253E-02,9.403563E-02,9.325525E-02,9.248135E-02,9.171388E-02,9.095277E-02,9.019798E-02,8.944945E-02,8.870714E-02,8.797098E-02,8.724094E-02,8.651695E-02,8.579897E-02,8.508695E-02,8.438084E-02,8.368059E-02,8.298615E-02,8.250000E-02,8.229747E-02,
        8.161451E-02,8.093721E-02,8.026554E-02,7.959944E-02,7.950000E-02,7.893887E-02,7.828378E-02,7.763412E-02,7.698986E-02,7.635094E-02,7.571733E-02,7.508897E-02,7.446583E-02,7.384786E-02,7.323502E-02,7.262726E-02,7.202455E-02,7.142684E-02,7.083409E-02,7.024626E-02,
        6.966330E-02,6.908519E-02,6.851187E-02,6.794331E-02,6.737947E-02,6.682031E-02,6.626579E-02,6.571586E-02,6.517051E-02,6.462968E-02,6.409333E-02,6.356144E-02,6.303396E-02,6.251086E-02,6.199211E-02,6.147765E-02,6.096747E-02,6.046151E-02,5.995976E-02,5.946217E-02,
        5.896871E-02,5.847935E-02,5.799405E-02,5.751277E-02,5.703549E-02,5.656217E-02,5.609278E-02,5.562728E-02,5.516564E-02,5.470784E-02,5.425384E-02,5.380360E-02,5.335710E-02,5.291430E-02,5.247518E-02,5.203971E-02,5.160785E-02,5.117957E-02,5.075484E-02,5.033364E-02,
        4.991594E-02,4.950170E-02,4.909090E-02,4.868351E-02,4.827950E-02,4.787884E-02,4.748151E-02,4.708747E-02,4.669671E-02,4.630919E-02,4.592488E-02,4.554376E-02,4.516581E-02,4.479099E-02,4.441928E-02,4.405066E-02,4.368510E-02,4.332257E-02,4.296305E-02,4.260651E-02,
        4.225293E-02,4.190229E-02,4.155455E-02,4.120970E-02,4.086771E-02,4.052857E-02,4.019223E-02,3.985869E-02,3.952791E-02,3.919988E-02,3.887457E-02,3.855196E-02,3.823203E-02,3.791476E-02,3.760011E-02,3.728808E-02,3.697864E-02,3.667176E-02,3.636743E-02,3.606563E-02,
        3.576633E-02,3.546952E-02,3.517517E-02,3.488326E-02,3.459377E-02,3.430669E-02,3.402199E-02,3.373965E-02,3.345965E-02,3.318198E-02,3.290662E-02,3.263353E-02,3.236272E-02,3.209415E-02,3.182781E-02,3.156368E-02,3.130174E-02,3.104198E-02,3.078437E-02,3.052890E-02,
        3.027555E-02,3.002430E-02,2.977514E-02,2.952804E-02,2.928300E-02,2.903999E-02,2.879899E-02,2.856000E-02,2.850000E-02,2.832299E-02,2.808794E-02,2.785485E-02,2.762369E-02,2.739445E-02,2.716711E-02,2.700000E-02,2.694166E-02,2.671808E-02,2.649635E-02,2.627647E-02,
        2.605841E-02,2.584215E-02,2.562770E-02,2.541502E-02,2.520411E-02,2.499495E-02,2.478752E-02,2.458182E-02,2.437782E-02,2.417552E-02,2.397489E-02,2.377593E-02,2.357862E-02,2.338295E-02,2.318890E-02,2.299646E-02,2.280562E-02,2.261636E-02,2.242868E-02,2.224255E-02,
        2.205796E-02,2.187491E-02,2.169338E-02,2.151335E-02,2.133482E-02,2.115777E-02,2.098218E-02,2.080806E-02,2.063538E-02,2.046413E-02,2.029431E-02,2.012589E-02,1.995887E-02,1.979324E-02,1.962898E-02,1.946608E-02,1.930454E-02,1.914434E-02,1.898547E-02,1.882791E-02,
        1.867166E-02,1.851671E-02,1.836305E-02,1.821066E-02,1.805953E-02,1.790966E-02,1.776104E-02,1.761364E-02,1.746747E-02,1.732251E-02,1.717876E-02,1.703620E-02,1.689482E-02,1.675461E-02,1.661557E-02,1.647768E-02,1.634094E-02,1.620533E-02,1.607085E-02,1.593748E-02,
        1.580522E-02,1.567406E-02,1.554398E-02,1.541499E-02,1.528706E-02,1.516020E-02,1.503439E-02,1.490963E-02,1.478590E-02,1.466319E-02,1.454151E-02,1.442083E-02,1.430116E-02,1.418247E-02,1.406478E-02,1.394806E-02,1.383231E-02,1.371752E-02,1.360368E-02,1.349079E-02,
        1.337883E-02,1.326780E-02,1.315770E-02,1.304851E-02,1.294022E-02,1.283283E-02,1.272634E-02,1.262073E-02,1.251599E-02,1.241212E-02,1.230912E-02,1.220697E-02,1.210567E-02,1.200521E-02,1.190558E-02,1.180678E-02,1.170880E-02,1.161163E-02,1.151527E-02,1.141970E-02,
        1.132494E-02,1.123095E-02,1.113775E-02,1.104532E-02,1.095366E-02,1.086276E-02,1.077261E-02,1.068321E-02,1.059456E-02,1.050664E-02,1.041944E-02,1.033298E-02,1.024723E-02,1.016219E-02,1.007785E-02,9.994221E-03,9.911282E-03,9.829031E-03,9.747463E-03,9.666572E-03,
        9.586352E-03,9.506797E-03,9.427903E-03,9.349664E-03,9.272074E-03,9.195127E-03,9.118820E-03,9.043145E-03,8.968099E-03,8.893675E-03,8.819869E-03,8.746676E-03,8.674090E-03,8.602106E-03,8.530719E-03,8.459926E-03,8.389719E-03,8.320095E-03,8.251049E-03,8.182576E-03,
        8.114671E-03,8.047330E-03,7.980548E-03,7.914319E-03,7.848641E-03,7.783507E-03,7.718914E-03,7.654857E-03,7.591332E-03,7.528334E-03,7.465858E-03,7.403901E-03,7.342458E-03,7.281525E-03,7.221098E-03,7.161172E-03,7.101744E-03,7.042809E-03,6.984362E-03,6.926401E-03,
        6.868921E-03,6.811918E-03,6.755388E-03,6.699327E-03,6.643731E-03,6.588597E-03,6.533920E-03,6.479697E-03,6.425924E-03,6.372597E-03,6.319712E-03,6.267267E-03,6.215257E-03,6.163678E-03,6.112528E-03,6.061802E-03,6.011496E-03,5.961609E-03,5.912135E-03,5.863072E-03,
        5.814416E-03,5.766164E-03,5.718312E-03,5.670858E-03,5.623797E-03,5.577127E-03,5.530844E-03,5.484945E-03,5.439427E-03,5.394287E-03,5.349521E-03,5.305127E-03,5.261101E-03,5.217441E-03,5.174143E-03,5.131204E-03,5.088622E-03,5.046393E-03,5.004514E-03,4.962983E-03,
        4.921797E-03,4.880952E-03,4.840447E-03,4.800277E-03,4.760441E-03,4.720936E-03,4.681758E-03,4.642906E-03,4.604375E-03,4.566165E-03,4.528272E-03,4.490693E-03,4.453426E-03,4.416468E-03,4.379817E-03,4.343471E-03,4.307425E-03,4.271679E-03,4.236230E-03,4.201075E-03,
        4.166211E-03,4.131637E-03,4.097350E-03,4.063347E-03,4.029627E-03,3.996186E-03,3.963023E-03,3.930135E-03,3.897520E-03,3.865175E-03,3.833099E-03,3.801290E-03,3.769744E-03,3.738460E-03,3.707435E-03,3.676668E-03,3.646157E-03,3.615898E-03,3.585891E-03,3.556133E-03,
        3.526622E-03,3.497355E-03,3.468332E-03,3.439549E-03,3.411005E-03,3.382698E-03,3.354626E-03,3.326787E-03,3.299179E-03,3.271800E-03,3.244649E-03,3.217722E-03,3.191019E-03,3.164538E-03,3.138276E-03,3.112233E-03,3.086405E-03,3.060792E-03,3.035391E-03,3.010202E-03,
        2.985221E-03,2.960447E-03,2.935879E-03,2.911515E-03,2.887354E-03,2.863392E-03,2.839630E-03,2.816065E-03,2.792695E-03,2.769519E-03,2.746536E-03,2.723743E-03,2.701139E-03,2.678723E-03,2.656494E-03,2.634448E-03,2.612586E-03,2.590904E-03,2.569403E-03,2.548081E-03,
        2.526935E-03,2.505965E-03,2.485168E-03,2.464545E-03,2.444092E-03,2.423809E-03,2.403695E-03,2.383747E-03,2.363965E-03,2.344347E-03,2.324892E-03,2.305599E-03,2.286465E-03,2.267490E-03,2.248673E-03,2.230012E-03,2.211506E-03,2.193153E-03,2.174953E-03,2.156904E-03,
        2.139004E-03,2.121253E-03,2.103650E-03,2.086192E-03,2.068879E-03,2.051710E-03,2.034684E-03,2.017798E-03,2.001053E-03,1.984447E-03,1.967979E-03,1.951647E-03,1.935451E-03,1.919389E-03,1.903461E-03,1.887665E-03,1.871999E-03,1.856464E-03,1.841058E-03,1.825780E-03,
        1.810628E-03,1.795602E-03,1.780701E-03,1.765923E-03,1.751268E-03,1.736735E-03,1.722323E-03,1.708030E-03,1.693855E-03,1.679798E-03,1.665858E-03,1.652034E-03,1.638324E-03,1.624728E-03,1.611245E-03,1.597874E-03,1.584613E-03,1.571463E-03,1.558422E-03,1.545489E-03,
        1.532663E-03,1.519944E-03,1.507331E-03,1.494822E-03,1.482417E-03,1.470115E-03,1.457915E-03,1.445816E-03,1.433817E-03,1.421919E-03,1.410118E-03,1.398416E-03,1.386811E-03,1.375303E-03,1.363889E-03,1.352571E-03,1.341346E-03,1.330215E-03,1.319176E-03,1.308228E-03,
        1.297372E-03,1.286605E-03,1.275928E-03,1.265339E-03,1.254839E-03,1.244425E-03,1.234098E-03,1.223857E-03,1.213700E-03,1.203628E-03,1.193639E-03,1.183734E-03,1.173910E-03,1.164168E-03,1.154507E-03,1.144926E-03,1.135425E-03,1.126002E-03,1.116658E-03,1.107391E-03,
        1.098201E-03,1.089088E-03,1.080050E-03,1.071087E-03,1.062198E-03,1.053383E-03,1.044641E-03,1.035972E-03,1.027375E-03,1.018849E-03,1.010394E-03,1.002009E-03,9.936937E-04,9.854473E-04,9.772694E-04,9.691593E-04,9.611165E-04,9.531405E-04,9.452307E-04,9.373865E-04,
        9.296074E-04,9.218928E-04,9.142423E-04,9.066553E-04,8.991312E-04,8.916696E-04,8.842699E-04,8.769316E-04,8.696542E-04,8.624372E-04,8.552801E-04,8.481824E-04,8.411435E-04,8.341631E-04,8.272407E-04,8.203756E-04,8.135676E-04,8.068160E-04,8.001205E-04,7.934805E-04,
        7.868957E-04,7.803654E-04,7.738894E-04,7.674671E-04,7.610981E-04,7.547820E-04,7.485183E-04,7.423066E-04,7.361464E-04,7.300373E-04,7.239790E-04,7.179709E-04,7.120126E-04,7.061038E-04,7.002441E-04,6.944330E-04,6.886701E-04,6.829550E-04,6.772874E-04,6.716668E-04,
        6.660928E-04,6.605651E-04,6.550832E-04,6.496469E-04,6.442557E-04,6.389092E-04,6.336071E-04,6.283489E-04,6.231345E-04,6.179633E-04,6.128350E-04,6.077492E-04,6.027057E-04,5.977040E-04,5.927438E-04,5.878248E-04,5.829466E-04,5.781089E-04,5.733114E-04,5.685536E-04,
        5.638354E-04,5.591563E-04,5.545160E-04,5.499142E-04,5.453506E-04,5.408249E-04,5.363368E-04,5.318859E-04,5.274719E-04,5.230946E-04,5.187536E-04,5.144486E-04,5.101793E-04,5.059455E-04,5.017468E-04,4.975830E-04,4.934537E-04,4.893587E-04,4.852976E-04,4.812703E-04,
        4.772763E-04,4.733156E-04,4.693877E-04,4.654923E-04,4.616294E-04,4.577984E-04,4.539993E-04,4.502317E-04,4.464953E-04,4.427900E-04,4.391154E-04,4.354713E-04,4.318575E-04,4.282736E-04,4.247195E-04,4.211949E-04,4.176995E-04,4.142332E-04,4.107955E-04,4.073865E-04,
        4.040057E-04,4.006530E-04,3.973281E-04,3.940308E-04,3.907608E-04,3.875180E-04,3.843021E-04,3.811129E-04,3.779502E-04,3.748137E-04,3.717032E-04,3.686185E-04,3.655595E-04,3.625258E-04,3.595173E-04,3.565338E-04,3.535750E-04,3.506408E-04,3.477309E-04,3.448452E-04,
        3.419834E-04,3.391454E-04,3.363309E-04,3.335398E-04,3.307719E-04,3.280269E-04,3.253047E-04,3.226051E-04,3.199279E-04,3.172729E-04,3.146399E-04,3.120288E-04,3.094394E-04,3.068715E-04,3.043248E-04,3.017993E-04,2.992948E-04,2.968110E-04,2.943479E-04,2.919052E-04,
        2.894827E-04,2.870804E-04,2.846980E-04,2.823354E-04,2.799924E-04,2.776688E-04,2.753645E-04,2.730793E-04,2.708131E-04,2.685657E-04,2.663370E-04,2.641267E-04,2.619348E-04,2.597611E-04,2.576054E-04,2.554676E-04,2.533476E-04,2.512451E-04,2.491601E-04,2.470924E-04,
        2.450418E-04,2.430083E-04,2.409917E-04,2.389917E-04,2.370084E-04,2.350416E-04,2.330910E-04,2.311567E-04,2.292384E-04,2.273360E-04,2.254494E-04,2.235784E-04,2.217230E-04,2.198830E-04,2.180583E-04,2.162487E-04,2.144541E-04,2.126744E-04,2.109095E-04,2.091592E-04,
        2.074234E-04,2.057021E-04,2.039950E-04,2.023021E-04,2.006233E-04,1.989584E-04,1.973073E-04,1.956699E-04,1.940461E-04,1.924358E-04,1.908388E-04,1.892551E-04,1.876845E-04,1.861269E-04,1.845823E-04,1.830505E-04,1.815315E-04,1.800250E-04,1.785310E-04,1.770494E-04,
        1.755802E-04,1.741231E-04,1.726781E-04,1.712451E-04,1.698239E-04,1.684146E-04,1.670170E-04,1.656310E-04,1.642565E-04,1.628933E-04,1.615415E-04,1.602010E-04,1.588715E-04,1.575531E-04,1.562456E-04,1.549489E-04,1.536631E-04,1.523879E-04,1.511232E-04,1.498691E-04,
        1.486254E-04,1.473920E-04,1.461688E-04,1.449558E-04,1.437529E-04,1.425599E-04,1.413768E-04,1.402036E-04,1.390401E-04,1.378862E-04,1.367420E-04,1.356072E-04,1.344818E-04,1.333658E-04,1.322590E-04,1.311615E-04,1.300730E-04,1.289935E-04,1.279231E-04,1.268615E-04,
        1.258087E-04,1.247646E-04,1.237292E-04,1.227024E-04,1.216842E-04,1.206744E-04,1.196729E-04,1.186798E-04,1.176949E-04,1.167182E-04,1.157496E-04,1.147890E-04,1.138364E-04,1.128917E-04,1.119548E-04,1.110258E-04,1.101044E-04,1.091907E-04,1.082845E-04,1.073859E-04,
        1.064947E-04,1.056110E-04,1.047345E-04,1.038654E-04,1.030034E-04,1.021486E-04,1.013009E-04,1.004603E-04,9.962658E-05,9.879981E-05,9.797990E-05,9.716679E-05,9.636043E-05,9.556076E-05,9.476773E-05,9.398128E-05,9.320136E-05,9.242791E-05,9.166088E-05,9.090021E-05,
        9.014586E-05,8.939776E-05,8.865588E-05,8.792015E-05,8.719052E-05,8.646695E-05,8.574939E-05,8.503778E-05,8.433208E-05,8.363223E-05,8.293819E-05,8.224991E-05,8.156734E-05,8.089044E-05,8.021915E-05,7.955344E-05,7.889325E-05,7.823854E-05,7.758926E-05,7.694537E-05,
        7.630682E-05,7.567357E-05,7.504558E-05,7.442280E-05,7.380518E-05,7.319270E-05,7.258529E-05,7.198293E-05,7.138556E-05,7.079316E-05,7.020566E-05,6.962305E-05,6.904527E-05,6.847228E-05,6.790405E-05,6.734053E-05,6.678169E-05,6.622749E-05,6.567789E-05,6.513285E-05,
        6.459233E-05,6.405630E-05,6.352471E-05,6.299754E-05,6.247474E-05,6.195628E-05,6.144212E-05,6.093223E-05,6.042657E-05,5.992511E-05,5.942781E-05,5.893464E-05,5.844556E-05,5.796053E-05,5.747954E-05,5.700253E-05,5.652948E-05,5.606036E-05,5.559513E-05,5.513376E-05,
        5.467623E-05,5.422248E-05,5.377251E-05,5.332626E-05,5.288373E-05,5.244486E-05,5.200963E-05,5.157802E-05,5.114999E-05,5.072551E-05,5.030456E-05,4.988709E-05,4.947309E-05,4.906253E-05,4.865538E-05,4.825160E-05,4.785117E-05,4.745407E-05,4.706026E-05,4.666972E-05,
        4.628243E-05,4.589834E-05,4.551744E-05,4.513971E-05,4.476511E-05,4.439361E-05,4.402521E-05,4.365985E-05,4.329753E-05,4.293822E-05,4.258189E-05,4.222851E-05,4.187807E-05,4.153054E-05,4.118589E-05,4.084410E-05,4.050514E-05,4.016900E-05,3.983565E-05,3.950507E-05,
        3.917723E-05,3.885211E-05,3.852969E-05,3.820994E-05,3.789285E-05,3.757838E-05,3.726653E-05,3.695727E-05,3.665057E-05,3.634642E-05,3.604479E-05,3.574566E-05,3.544902E-05,3.515484E-05,3.486310E-05,3.457378E-05,3.428686E-05,3.400233E-05,3.372015E-05,3.344032E-05,
        3.316281E-05,3.288760E-05,3.261467E-05,3.234401E-05,3.207560E-05,3.180942E-05,3.154544E-05,3.128365E-05,3.102404E-05,3.076658E-05,3.051126E-05,3.025805E-05,3.000695E-05,2.975793E-05,2.951098E-05,2.926607E-05,2.902320E-05,2.878235E-05,2.854349E-05,2.830662E-05,
        2.807171E-05,2.783875E-05,2.760773E-05,2.737862E-05,2.715141E-05,2.692609E-05,2.670264E-05,2.648104E-05,2.626128E-05,2.604335E-05,2.582722E-05,2.561289E-05,2.540033E-05,2.518954E-05,2.498050E-05,2.477320E-05,2.456761E-05,2.436373E-05,2.416154E-05,2.396104E-05,
        2.376219E-05,2.356499E-05,2.336944E-05,2.317550E-05,2.298317E-05,2.279244E-05,2.260329E-05,2.241572E-05,2.222969E-05,2.204522E-05,2.186227E-05,2.168084E-05,2.150092E-05,2.132249E-05,2.114554E-05,2.097006E-05,2.079603E-05,2.062345E-05,2.045231E-05,2.028258E-05,
        2.011426E-05,1.994734E-05,1.978180E-05,1.961764E-05,1.945484E-05,1.929339E-05,1.913328E-05,1.897449E-05,1.881703E-05,1.866087E-05,1.850601E-05,1.835244E-05,1.820013E-05,1.804910E-05,1.789931E-05,1.775077E-05,1.760346E-05,1.745738E-05,1.731250E-05,1.716883E-05,
        1.702635E-05,1.688506E-05,1.674493E-05,1.660597E-05,1.646816E-05,1.633150E-05,1.619597E-05,1.606156E-05,1.592827E-05,1.579609E-05,1.566500E-05,1.553500E-05,1.540608E-05,1.527823E-05,1.515144E-05,1.502570E-05,1.490101E-05,1.477735E-05,1.465472E-05,1.453310E-05,
        1.441250E-05,1.429289E-05,1.417428E-05,1.405665E-05,1.394000E-05,1.382431E-05,1.370959E-05,1.359582E-05,1.348299E-05,1.337110E-05,1.326014E-05,1.315010E-05,1.304097E-05,1.293274E-05,1.282542E-05,1.271898E-05,1.261343E-05,1.250876E-05,1.240495E-05,1.230201E-05,
        1.219991E-05,1.209867E-05,1.199827E-05,1.189870E-05,1.179995E-05,1.170203E-05,1.160492E-05,1.150861E-05,1.141311E-05,1.131839E-05,1.122446E-05,1.113132E-05,1.103894E-05,1.094733E-05,1.085648E-05,1.076639E-05,1.067704E-05,1.058843E-05,1.050056E-05,1.041342E-05,
        1.032701E-05,1.024130E-05,1.015631E-05,1.007203E-05,9.988446E-06,9.905554E-06,9.823351E-06,9.741830E-06,9.660985E-06,9.580812E-06,9.501303E-06,9.422455E-06,9.344261E-06,9.266715E-06,9.189814E-06,9.113550E-06,9.037919E-06,8.962916E-06,8.888536E-06,8.814772E-06,
        8.741621E-06,8.669077E-06,8.597135E-06,8.525790E-06,8.455037E-06,8.384871E-06,8.315287E-06,8.246281E-06,8.177848E-06,8.109982E-06,8.042680E-06,7.975936E-06,7.909746E-06,7.844105E-06,7.779009E-06,7.714454E-06,7.650434E-06,7.586945E-06,7.523983E-06,7.461544E-06,
        7.399622E-06,7.338215E-06,7.277317E-06,7.216925E-06,7.157034E-06,7.097640E-06,7.038739E-06,6.980326E-06,6.922399E-06,6.864952E-06,6.807981E-06,6.751484E-06,6.695455E-06,6.639892E-06,6.584789E-06,6.530144E-06,6.475952E-06,6.422210E-06,6.368914E-06,6.316060E-06,
        6.263645E-06,6.211665E-06,6.160116E-06,6.108995E-06,6.058298E-06,6.008022E-06,5.958164E-06,5.908719E-06,5.859684E-06,5.811056E-06,5.762832E-06,5.715008E-06,5.667581E-06,5.620547E-06,5.573904E-06,5.527647E-06,5.481775E-06,5.436284E-06,5.391169E-06,5.346430E-06,
        5.302061E-06,5.258061E-06,5.214426E-06,5.171153E-06,5.128239E-06,5.085681E-06,5.043477E-06,4.918953E-06,4.797503E-06,4.679053E-06,4.563526E-06,4.450853E-06,4.340961E-06,4.233782E-06,4.129250E-06,4.000000E-06,3.927860E-06,3.830880E-06,3.736300E-06,3.644050E-06,
        3.554080E-06,3.466330E-06,3.380750E-06,3.300000E-06,3.217630E-06,3.137330E-06,3.059020E-06,2.983490E-06,2.909830E-06,2.837990E-06,2.767920E-06,2.720000E-06,2.659320E-06,2.600000E-06,2.550000E-06,2.485030E-06,2.421710E-06,2.382370E-06,2.360000E-06,2.300270E-06,
        2.242050E-06,2.185310E-06,2.130000E-06,2.100000E-06,2.059610E-06,2.020000E-06,1.974490E-06,1.930000E-06,1.884460E-06,1.855390E-06,1.840000E-06,1.797000E-06,1.755000E-06,1.711970E-06,1.670000E-06,1.629510E-06,1.590000E-06,1.544340E-06,1.500000E-06,1.475000E-06,
        1.440000E-06,1.404560E-06,1.370000E-06,1.337500E-06,1.300000E-06,1.267080E-06,1.235000E-06,1.202060E-06,1.170000E-06,1.150000E-06,1.123000E-06,1.110000E-06,1.097000E-06,1.080000E-06,1.071000E-06,1.045000E-06,1.035000E-06,1.020000E-06,9.960000E-07,9.860000E-07,
        9.720000E-07,9.500000E-07,9.300000E-07,9.100000E-07,8.764250E-07,8.600000E-07,8.500000E-07,8.194500E-07,7.900000E-07,7.800000E-07,7.415500E-07,7.050000E-07,6.825600E-07,6.531500E-07,6.250000E-07,5.952800E-07,5.669600E-07,5.400000E-07,5.315800E-07,5.196200E-07,
        5.000000E-07,4.850000E-07,4.670100E-07,4.496800E-07,4.330000E-07,4.139900E-07,4.000000E-07,3.910000E-07,3.699300E-07,3.500000E-07,3.346600E-07,3.200000E-07,3.145000E-07,3.000000E-07,2.800000E-07,2.635100E-07,2.480000E-07,2.335800E-07,2.200000E-07,2.091400E-07,
        1.988100E-07,1.890000E-07,1.800000E-07,1.697100E-07,1.600000E-07,1.530300E-07,1.463700E-07,1.400000E-07,1.340000E-07,1.150000E-07,1.000000E-07,9.500000E-08,8.000000E-08,7.700000E-08,6.700000E-08,5.800000E-08,5.000000E-08,4.200000E-08,3.500000E-08,3.000000E-08,
        2.500000E-08,2.000000E-08,1.500000E-08,1.000000E-08,6.900000E-09,5.000000E-09,3.000000E-09,1.000010E-11
        ]

    #pstr = ''
    #for i in range(len(ECCO_bins)):
    #    pstr += ECCO_bins[i] + ','
    #    if i!=0 and i%20==0:
    #        pstr += '\n'
    #print(pstr)

    return ECCO_bins[:n]

def retrieve_rxn_xs_from_lib(libfile,target,reaction=None,product=None):
    '''
    Description:
        Provided a DCHAIN neutron rxn cross section library file and sufficient information
        about a reaction, return that reaction's cross section.

    Dependencies:
        `rxn_to_dchain_str`

        `ECCO1968_Ebins`

    Inputs:
        - `libfile` = string of file path to data library file to be searched
        - `target` = string in general format of target nuclide
        - `reaction` = (optional) either an int MT number (ENDF6 format) or a string of the ejectiles from the neutron reaction (case-insensitive), the "X" in (N,X)
                   if `reaction = 'tot'` or `'total'`, the summed total transmutation xs (reactions which change the target's nuclide species) is provided and input for product is ignored;
                   this behavior is also assumed when missing both reaction and product information
        - `product` = (optional) string in general format of product nuclide (if omitted, sum of all isomeric states is assumed; if provided product but not isomeric state, ground state is assumed)

    Outputs:
        - `xs` = a 2x1968 numpy array containing energy [eV] (i=0) and cross sections [b] (i=1) for all 1968 ECCO bins
        - `rxn_tex_str` = a LaTeX-formatted string of the reaction
    '''

    datafolder, lib = os.path.split(libfile.replace('_n_act_xs_lib',''))

    n_occurances = 0
    rxn_locations= []
    rxn_listings = []
    xs_data_raw  = []

    # determine if rxn or product is provided
    if (not reaction and not product) or (reaction=='tot' or reaction=='total'): # only target provided
        #print('Total transmutation cross section of {}'.format(target))
        calc_total_xs = True
    else:
        calc_total_xs = False

    if calc_total_xs: # only concerned with target, not target or reaction
        # First, assemble reaction string
        rt = rxn_to_dchain_str(target,None,target)[:10] # only concerned with target + '(N,'
        rt_alt = None # alternate string to cover ground state when 'g' is present in product too
        catalog_rxn_text = rt[0] + rt[1:].lower()
        catalog_rxn_text_alt = None
        # make pretty Latex str of reaction too
        target_str = rt[0]  + rt[1:7].lower()
        not_symbol = r'$\neg$' # '!'
        rxn_str    = '(n,*)'
        tex_target = nuclide_plain_str_to_latex_str(target_str)
        if target_str[-2:] == '  ':
            tex_product = nuclide_plain_str_to_latex_str(target_str[:-2]+'g ')
        else:
            tex_product = tex_target
        rxn_tex_str = tex_target + rxn_str + not_symbol + tex_product
    else:
        # First, assemble reaction string
        rt = rxn_to_dchain_str(target,reaction,product)
        rt_alt = None # alternate string to cover ground state when 'g' is present in product too
        if product:
            if rt[-2] == ' ': rt_alt = rt[:-2] + 'G '
        # Format string found in the catalog file
        catalog_rxn_text = rt[0] + rt[1:14].lower()
        if reaction.lower() != 'fis': catalog_rxn_text+= rt[14] + rt[15:].lower()
        catalog_rxn_text_alt = None
        if rt_alt: catalog_rxn_text_alt = rt_alt[0] + rt_alt[1:14].lower() + rt_alt[14] + rt_alt[15:].lower()
        # make pretty Latex str of reaction too
        target_str = rt[0]  + rt[1:7].lower()
        if reaction.lower() == 'fis':
            product_str = ''
        else:
            product_str= rt[14] + rt[15:22].lower()
        rxn_str    = rt[7:14].lower().replace(' ','')
        if 'a' in rxn_str: rxn_str = rxn_str.replace('a',r'$\alpha$')
        if 'g' in rxn_str: rxn_str = rxn_str.replace('g',r'$\gamma$')
        if 'he3' in rxn_str: rxn_str = rxn_str.replace('he3',r'$^3$He')
        tex_target = nuclide_plain_str_to_latex_str(target_str)
        if product_str:
            tex_product= nuclide_plain_str_to_latex_str(product_str)
        else:
            tex_product = ''
        rxn_tex_str = tex_target + rxn_str + tex_product

    if lib[0]=='h': # in hybrid_lib_dchain_names:
        hlib = True
    else:
        hlib = False
    catalog_file = libfile.replace('_n_act_xs_lib','_n_reaction_list.txt')
    library_file = libfile
    if os.path.isfile(catalog_file): # catalog file exists
        search_file = catalog_file
        search_text = catalog_rxn_text
        search_text_alt = catalog_rxn_text_alt
        using_catalog_file = True
    elif os.path.isfile(library_file): # library file exists
        search_file = library_file
        search_text = rt
        search_text_alt = rt_alt
        using_catalog_file = False
    else:
        print('\t{} library files not found.'.format(lib))
        return None
    with open(search_file) as f:
        asterisk_counter = -1
        for num, line in enumerate(f, 1):
            if '*' in line: asterisk_counter += 1
            if search_text in line or (rt_alt and search_text_alt in line):
                n_occurances += 1
                if using_catalog_file:
                    rxn_locations.append(num-2) # index of reaction in reaction lib
                    rxn_listings.append(line.replace('\n',''))
                else: # searching through actual library file
                    rxn_locations.append(asterisk_counter) # index of reaction in reaction lib
                    rxn_listings.append(line[20:41])

    if n_occurances == 0:
        print('Reaction "{}" not found in library "{}".'.format(catalog_rxn_text,lib))
        return None, 'null'
    if n_occurances > 1:
        if calc_total_xs:
            print('   Multiple reactions found.  The sum of all will be used.')
        else:
            print('   Multiple product isomers for reaction found.  The sum of all isomeric states will be used.')
        for j in range(n_occurances):
            print('\t{}   (lib entry index {} of {})'.format(rxn_listings[j],rxn_locations[j],lib))

    if hlib:
        print('Hybrid library {} uses data from {} for reaction {}.'.format(lib,rxn_listings[0][26:],catalog_rxn_text))

    # State library availability
    #if hlib and n_occurances>0: # this is a hybrid library
    #    src_lib  = rxn_listings[libi][0][26:]
    #    print('\t{}   {} (from {})'.format(lib,n_occurances,src_lib))
    #    lib_colors[libi] = lib_colors[lib_names.index(src_lib)]
    #else: # normal library
    #    print('\t{}   {}'.format(lib,n_occurances[libi]))

    #if n_occurances[libi]>0 and libi in libis_to_compare: n_plotable_lines += 1

    if not os.path.isfile(library_file):
        print('\t{} library file not found.'.format(lib))
        return None, 'null'
    if n_occurances == 0:
        print('\t\tCross section not present in this library, skipping')
        return None, 'null'
    entry_index = -1
    with open(library_file) as f:
        lines = f.readlines()
        for line in lines:
            if '*' in line: entry_index += 1
            if entry_index in rxn_locations: # reached bookmarked entry index of interest for this lib
                found_entry = True
                enti = rxn_locations.index(entry_index)

                if '*' in line:
                    if rxn_listings[enti][:22].upper() not in line: # double check that entry is correct
                        print('Library index mismatch!')
                        found_entry = False
                    xs_vals = []
                    entry_li = -1
                if found_entry:
                    entry_li += 1
                    if entry_li == 0: # first line
                        nEbins = int(line[12:18])
                    elif entry_li == 1 or entry_li == 2: # skip descriptive lines
                        continue
                    else:
                        xs_vals += [float(xsi) for xsi in line.replace('\n','').split()]

                    if len(xs_vals) == nEbins:
                        if len(xs_data_raw)==0: # need to initialize entry
                            xs_data_raw = np.zeros(1968)
                        xs_data_raw[:nEbins] += np.array(xs_vals)

    # Now pretty up the results to be provided to the user
    xs = np.zeros((2,1968))
    xs[0,:] = (1e6)*np.array(ECCO1968_Ebins(1968)[::-1]) # all energy bins in increasing order in eV
    # now flip order of lists to have them in energy increasing order
    for i in range(len(xs_data_raw)):
        xs[1,1967-i] = xs_data_raw[i]

    return xs, rxn_tex_str



def calc_one_group_nrxn_xs_dchain(neutron_flux,neutron_flux_errors,libfile,target,reaction=None,product=None):
    '''
    Description:
        Combines a neutron flux and cross section into a flux-weighted single-group cross section.

    Inputs:
        - `neutron_flux` = 1D array of flux values
        - `neutron_flux_errors` = 1D array of flux absolute uncertainties
        - `libfile` = string of file path to data library file to be searched
        - `target` = string in general format of target nuclide
        - `reaction` = (optional) either an int MT number (ENDF6 format) or a string of the ejectiles from the neutron reaction (case-insensitive), the "X" in (N,X)

              if `reaction = 'tot'` or `'total'`, the summed total transmutation xs (reactions which change the target's nuclide species) is provided and input for product is ignored;
              this behavior is also assumed when missing both reaction and product information
        - `product` = (optional) string in general format of product nuclide (if omitted, sum of all isomeric states is assumed; if provided product but not isomeric state, ground state is assumed)

    Outputs:
        - `xs` = a length-2 list of the single group cross section and its absolute uncertainty
    '''

    xs_out, rxn_str_out = retrieve_rxn_xs_from_lib(libfile,target,reaction,product)
    xs_vals = xs_out[1,:]

    flux_val = neutron_flux
    flux_err = neutron_flux_errors

    if len(xs_vals) != len(flux_val):
        print('Warning: mismatch in flux and cross section energy binning!')

    xs = np.sum(flux_val*xs_vals)/np.sum(flux_val)
    xs_fer_num = np.sqrt(np.sum((flux_err*xs_vals)**2))/np.sum(flux_val*xs_vals)
    xs_fer_denom = np.sqrt(np.sum(flux_err**2))/np.sum(flux_val)
    xs_fer = np.sqrt(xs_fer_num**2 + xs_fer_denom**2)
    xs_aer = xs*xs_fer

    return [xs, xs_aer]




def parse_DCHAIN_act_file_legacy(act_file_path):
    '''
    Description:
       This code parses the .act file generated by DCHAIN (without uncertainty values)

    Inputs:
        - path to a DCHAIN-generated .act file

    Outputs:
        - length R list of region numbers
        - length T list of measurement times (in sec) from start of irradiation
        - time of end of irradiation (in sec)
        - NumPy array of dimension RxTxNx11 of nuclide table data (N=max recorded table lenth)
        - NumPy array of dimension RxTxNx5 of gamma spectrum table data
        - NumPy array of dimension RxTxNx12 of top-10 list table data
        - List containing 3 lists of column headers for the preceding three NumPy arrays
        - list of the below lists/arrays of summary information
            - NumPy array of dimension Rx7 of region-specific summary info
            - list of length 7 containing descriptions of the above items
            - NumPy array of dimension RxTx12 of region and time-specific summary info
            - list of length 12 containing descriptions of the above items
    '''
    # Extract file info
    f = open(act_file_path)
    lines = f.readlines()
    f.close()

    # Parse file to determine number of regions
    nreg = 0
    reg_nos = []
    for line in lines:
        if 'region number' in line:
            nreg += 1
            reg_nos.append(int(line[21:31]))

    # Parse file again to determine number of time steps
    current_reg_no = -1
    #irradiation_time = -1.0 # seconds
    end_of_irradiation_time = -1.0 # seconds
    ntimes = 0
    time_strs = []
    time_list_sec = [] # time steps in seconds
    for line in lines:
        #if 'irradiation time' in line: irradiation_time = float(line[21:31])*time_str_to_sec_multiplier(line[33])
        if 'region number' in line: current_reg_no = int(line[21:31])
        if current_reg_no != reg_nos[0]: continue # only read times from first region
        if '--- output time ---' in line:
            ntimes += 1
            time_strs.append(line)
            time_list_sec.append(float(line[40:53]))
        if ('--- output time ---' in line) and ('after the last shutdown' in line) and end_of_irradiation_time == -1:
            end_of_irradiation_time = float(line[21:31])*time_str_to_sec_multiplier(line[33]) - float(line[88:97])*time_str_to_sec_multiplier(line[99])

    # Extract "summary info" from file
    ri = -1 # region index
    ti = -1 # time index
    r_summary_info = np.empty((nreg,7), dtype='object') # (regionwise) initialize Rx7 array
    r_summary_info_description = ['region number','irradiation time [s]','region volume [cc]','neutron flux [n/cm^2/s]','beam power [MW]','beam energy [GeV]','beam current [mA]'] # (regionwise) initialize Rx7 array
    '''
    index  meaning
       0   region number
       1   irradiation time [sec]
       2   region volume [cc]
       3   neutron flux [n/cm^2/s]
       4   beam power [MW]
       5   beam energy [GeV]
       6   beam current [mA] 
    '''
    rt_summary_info = np.empty((nreg,ntimes,12), dtype='object') # (region-and-timewise) initialize RxTx12 array
    rt_summary_info_description = ['total gamma flux [#/s/cc]','total gamma energy flux [MeV/s/cc]','annihilation gamma flux [#/s/cc]','gamma current underflow [#/s]','gamma current overflow [#/s]','total activity [Bq/cc]','total decay heat [W/cc]','beta decay heat [W/cc]','gamma decay heat [W/cc]','alpha decay heat [W/cc]','activated atoms [#/cc]','total gamma dose rate [uSV/h*m^2]'] # (region-and-timewise) initialize RxTx12 array
    '''
    index  meaning
       0   total gamma flux [#/s/cc]
       1   total gamma energy flux [MeV/s/cc]
       2   annihilation gamma flux [#/s/cc]
       3   gamma current underflow [#/s] (gammas below lowest energy bin)
       4   gamma current overflow [#/s] (gammas above highest energy bin)
       5   total activity [Bq/cc]
       6   total decay heat [W/cc]
       7     beta decay heat [W/cc]
       8     gamma decay heat [W/cc]
       9     alpha decay heat [W/cc]
       10  activated atoms [#/cc]
       11  total gamma dose rate [uSV/h*m^2]
    '''
    for li in range(len(lines)):
        line = lines[li]
        if 'region number' in line:
            ri = find(int(line[21:31]),reg_nos)

            # region-specific summary info
            r_summary_info[ri,0] = int(line[21:31])
            r_summary_info[ri,1] = float(lines[li-1][21:31])*time_str_to_sec_multiplier(lines[li-1][33])
            r_summary_info[ri,2] = float(lines[li-2][21:31])
            r_summary_info[ri,3] = float(lines[li-3][21:31])
            r_summary_info[ri,4] = float(lines[li-4][21:31])
            r_summary_info[ri,5] = float(lines[li-5][21:31])
            r_summary_info[ri,6] = float(lines[li-6][21:31])

        if '--- output time ---' in line:
            ti = find(line,time_strs)

        # gamma info specific to region and time
        if 'total gamma-ray flux' in line:
            rt_summary_info[ri,ti,0] = float(line[39:49])
            rt_summary_info[ri,ti,1] = float(lines[li+1][39:49])
            rt_summary_info[ri,ti,2] = float(lines[li+2][39:49])
            if 'group limitation' in lines[li+3]:
                rt_summary_info[ri,ti,3] = float(lines[li+3][91:101])
                rt_summary_info[ri,ti,4] = float(lines[li+3][64:74])
            else:
                rt_summary_info[ri,ti,3] = 0.0
                rt_summary_info[ri,ti,4] = 0.0

        # activation info specific to region and time
        if 'total activity' in line:
            rt_summary_info[ri,ti,5] = float(line[25:36])
            rt_summary_info[ri,ti,6] = float(lines[li+1][25:36])
            rt_summary_info[ri,ti,7] = float(lines[li+2][25:36])
            rt_summary_info[ri,ti,8] = float(lines[li+3][25:36])
            rt_summary_info[ri,ti,9] = float(lines[li+4][25:36])
            rt_summary_info[ri,ti,10]= float(lines[li+5][25:36])
            rt_summary_info[ri,ti,11]= float(lines[li+6][25:36])

    summary_info = [r_summary_info, r_summary_info_description, rt_summary_info, rt_summary_info_description]

    # Extract major "blocks" (nuclides, gamma spec, top10 list) for each time step in each region
    act_block_text = np.empty((nreg,ntimes,3), dtype='object') # initialize RxTx3 array to hold character strings where final index 0=nuclides, 1=gamma-spec, and 2=top10-list
    ri = -1 # region index
    ti = -1 # time index
    qi = -1 # quantity index - 0=nuclides, 1=gamma-spec, and 2=top10-list
    max_array_len = [0,0,0] # maximum number of entries for a given quantity
    current_array_len = [0,0,0] # current number of entries for a given quantity
    for line in lines:
        if 'region number' in line:
            ri = find(int(line[21:31]),reg_nos)
        if '--- output time ---' in line:
            ti = find(line,time_strs)
            qi = 0 # reset quantity index
        if 'gamma-ray spectrum weighted by energy' in line:
            qi = 1
        if 'dominant nuclides (top 10)' in line:
            qi = 2
        if 'total' in line[:20] or line=='\n': # no longer reading info block
            if current_array_len[qi] > max_array_len[qi]:
                max_array_len[qi] = current_array_len[qi]
            current_array_len[qi] = 0
            qi = -1

        if qi < 0: continue # not in region of interest

        try:
            act_block_text[ri,ti,qi] += line
        except:
            act_block_text[ri,ti,qi] = line

        current_array_len[qi] += 1

    header_len = [3,4,3] # number of lines present in table header

    nuclides_produced = np.empty((nreg,ntimes,max_array_len[0]-header_len[0],11), dtype='object') # initialize RxTxNx11 array to hold nuclide information
    gamma_spectra     = np.empty((nreg,ntimes,max_array_len[1]-header_len[1], 5), dtype='object') # initialize RxTxNx5 array to hold gamma spec information
    top10_lists       = np.empty((nreg,ntimes,max_array_len[2]-header_len[2],12), dtype='object') # initialize RxTxNx12 array to hold top 10 list information

    column_headers = [ [],[],[] ]

    # Now, populate each array

    # Nuclides produced
    column_headers[0] = ['nuclide','atoms [#/cc]','activity [Bq/cc]','activity [Bq]','rate [%]','beta decay heat [W/cc]','gamma decay heat [W/cc]','alpha decay heat [W/cc]','total decay heat [W/cc]','half life [s]','dose-rate [uSv/h*m^2]']
    for ri in range(nreg):
        for ti in range(ntimes):
            table_text = act_block_text[ri,ti,0].split('\n')
            for ei in range(len(table_text)):
                if ei < header_len[0]: continue # in header lines
                ii = ei - header_len[0] # actual number index
                line = table_text[ei]
                if line=='' or line==None: continue # skip blank/nonexistent lines
                nuclides_produced[ri,ti,ii,0] = line[3:9]            # nuclide
                nuclides_produced[ri,ti,ii,1] = float(line[13:23])   # atoms [#/cc]
                nuclides_produced[ri,ti,ii,2] = float(line[26:36])   # activity [Bq/cc]
                nuclides_produced[ri,ti,ii,3] = float(line[38:48])   # activity [Bq]
                nuclides_produced[ri,ti,ii,4] = float(line[49:56].replace('     ','0.0'))   # rate [%]
                nuclides_produced[ri,ti,ii,5] = float(line[58:67])   # beta decay heat [W/cc]
                nuclides_produced[ri,ti,ii,6] = float(line[69:78])   # gamma decay heat [W/cc]
                nuclides_produced[ri,ti,ii,7] = float(line[80:89])   # alpha decay heat [W/cc]
                nuclides_produced[ri,ti,ii,8] = float(line[91:100])  # total decay heat [W/cc]
                nuclides_produced[ri,ti,ii,9] = float(line[104:113]) # half life [s]
                nuclides_produced[ri,ti,ii,10]= float(line[116:125]) # dose-rate [uSv/h*m^2]

    # Gamma-ray spectra
    column_headers[1] = ['group number','bin energy lower-bound [MeV]','bin energy upper-bound [MeV]','flux [#/s/cc]','energy flux [MeV/s/cc]']
    for ri in range(nreg):
        for ti in range(ntimes):
            table_text = act_block_text[ri,ti,1].split('\n')
            for ei in range(len(table_text)):
                if ei < header_len[1]: continue # in header lines
                ii = ei - header_len[1] # actual number index
                line = table_text[ei]
                if line=='' or line==None: continue # skip blank/nonexistent lines
                gamma_spectra[ri,ti,ii,0] = int(line[1:4])       # group number
                gamma_spectra[ri,ti,ii,1] = float(line[17:25])   # bin energy lower-bound [MeV]
                gamma_spectra[ri,ti,ii,2] = float(line[7:15])    # bin energy upper-bound [MeV]
                gamma_spectra[ri,ti,ii,3] = float(line[28:38])   # flux [#/s/cc]
                gamma_spectra[ri,ti,ii,4] = float(line[41:51])   # energy flux [MeV/s/cc]

    # Top 10 lists
    column_headers[2] = ['rank','nuclide -  Activity ranking','activity [Bq/cc]','activity [Bq]','rate [%]','nuclide - Decay heat ranking','decay heat [W/cc]','decay heat [W]','rate [%]','nuclide - Dose rate ranking','dose-rate [uSv/h*m^2]','rate [%]']
    for ri in range(nreg):
        for ti in range(ntimes):
            table_text = act_block_text[ri,ti,2].split('\n')
            for ei in range(len(table_text)):
                if ei < header_len[2]: continue # in header lines
                ii = ei - header_len[2] # actual number index
                line = table_text[ei]
                if line=='' or line==None: continue # skip blank/nonexistent lines
                top10_lists[ri,ti,ii,0] = int(line[1:5])       # number/rank
                top10_lists[ri,ti,ii,1] = line[8:14]           # nuclide -  Activity ranking
                top10_lists[ri,ti,ii,2] = float(line[16:26])   # activity [Bq/cc]
                top10_lists[ri,ti,ii,3] = float(line[27:37])   # activity [Bq]
                top10_lists[ri,ti,ii,4] = float(line[38:43])   # rate [%]
                top10_lists[ri,ti,ii,5] = line[48:54]          # nuclide - Decay heat ranking
                top10_lists[ri,ti,ii,6] = float(line[56:66])   # decay heat [W/cc]
                top10_lists[ri,ti,ii,7] = float(line[67:77])   # decay heat [W]
                top10_lists[ri,ti,ii,8] = float(line[78:83])   # rate [%]
                top10_lists[ri,ti,ii,9] = line[88:94]          # nuclide - Dose rate ranking
                top10_lists[ri,ti,ii,10]= float(line[96:106])  # dose-rate [uSv/h*m^2]
                top10_lists[ri,ti,ii,11]= float(line[107:113]) # rate [%]

    return reg_nos, time_list_sec, end_of_irradiation_time, nuclides_produced, gamma_spectra, top10_lists, column_headers, summary_info

def generate_nuclide_time_profiles_legacy(nuclides_info_array):
    '''
    Description:
        Reformats DCHAIN's tabular nuclide data into time profiles of each nuclide in each region (without uncertainty values)

    Inputs:
       - the `nuclides_produced' array from function "parse_DCHAIN_act_file"

    Outputs:
       - List of length R of lists containing names of nuclides produced in each region
       - List of length R of lists containing LaTeX-formatted names of nuclides produced in each region
       - List of length R of lists containing ZZZAAAM values (10000Z+10A+M) of nuclides produced in each region
       - List of length R of lists containing half lives of nuclides produced in each region (in seconds)
       - List of length R of NumPy arrays of dimension NxTx7 of nuclide info
       - List of length 7 containing text descriptions of the 7 columns of the info arrays
    '''
    nuclide_names = []
    nuclide_ZAM_vals = []
    nuclide_Latex_names = []
    nuclide_half_lives = []
    nuclide_info = []
    nuclide_info_headers = ['Atoms [#/cc]','Activity [Bq/cc]','Beta decay heat [W/cc]','Gamma decay heat [W/cc]','Alpha decay heat [W/cc]','Total decay heat [W/cc]','Dose-rate [uSv/h*m^2]']


    nreg = np.shape(nuclides_info_array)[0]
    ntime= np.shape(nuclides_info_array)[1]
    nnuc = np.shape(nuclides_info_array)[2]

    # Get nuclide name info first, ordering them by increasing Z and A
    for ri in range(nreg):
        reg_nuclides = []
        reg_t_halves = []
        reg_ZAM_vals = []
        reg_tex_nuclides = []
        for ti in range(ntime):
            for ni in range(nnuc):
                Dname = nuclides_info_array[ri,ti,ni,0]
                if Dname == None: continue
                ZAM = Dname_to_ZAM(Dname)
                if ZAM not in reg_ZAM_vals:
                    bisect.insort_left(reg_ZAM_vals, ZAM)
                    zami = reg_ZAM_vals.index(ZAM)
                    #zami = find(ZAM,reg_ZAM_vals)
                    reg_nuclides.insert(zami,Dname)
                    reg_t_halves.insert(zami,nuclides_info_array[ri,ti,ni,9])
                    reg_tex_nuclides.insert(zami,Dname_to_Latex(Dname))

        nuclide_names.append(reg_nuclides)
        nuclide_ZAM_vals.append(reg_ZAM_vals)
        nuclide_half_lives.append(reg_t_halves)
        nuclide_Latex_names.append(reg_tex_nuclides)

    # Now get arrays of nuclide info
    for ri in range(nreg):
        reg_nnuc = len(nuclide_names[ri])
        reg_nuclide_info = np.zeros((ntime,reg_nnuc,7))
        for ti in range(ntime):
            for ni in range(reg_nnuc):
                if nuclide_names[ri][ni] not in nuclides_info_array[ri,ti,:,0]: continue
                sni = find(nuclide_names[ri][ni],nuclides_info_array[ri,ti,:,0])
                reg_nuclide_info[ti,ni,0] = nuclides_info_array[ri,ti,sni,1]   # atoms [#/cc]
                reg_nuclide_info[ti,ni,1] = nuclides_info_array[ri,ti,sni,2]   # activity [Bq/cc]
                reg_nuclide_info[ti,ni,2] = nuclides_info_array[ri,ti,sni,5]   # beta decay heat [W/cc]
                reg_nuclide_info[ti,ni,3] = nuclides_info_array[ri,ti,sni,6]   # gamma decay heat [W/cc]
                reg_nuclide_info[ti,ni,4] = nuclides_info_array[ri,ti,sni,7]   # alpha decay heat [W/cc]
                reg_nuclide_info[ti,ni,5] = nuclides_info_array[ri,ti,sni,8]   # total decay heat [W/cc]
                reg_nuclide_info[ti,ni,6] = nuclides_info_array[ri,ti,sni,10]  # dose-rate [uSv/h*m^2]

        nuclide_info.append(reg_nuclide_info)

    return nuclide_names, nuclide_Latex_names, nuclide_ZAM_vals, nuclide_half_lives, nuclide_info, nuclide_info_headers






def plot_top10_nuclides(dchain_output,rank_val='activity',xaxis_val='time',xaxis_type='indices',regions=None,region_indices=None,times=None,time_indices=None,rank_cutoff=10,xscale='linear'):
    '''
    Description:
        Generate a nice plot illustrating dominant nuclides as a function of time or region

    Dependencies:
        - `import numpy as np`
        - `import matplotlib.pyplot as plt`
        - `process_dchain_simulation_output`

    Inputs:
        (required)

        - `dchain_output` = dictionary output from the process_dchain_simulation_output for a simulation

    Inputs:
        (optional, keyword)

        - `rank_val` = which top 10 list is selected. (D=`'activity'`, options include `'activity'`, `'decay_heat'`, and `'gamma_dose'`)
        - `xaxis_val` = value to be plotted on x-axis; can be either `"time"` (default) or `"region"`
        - `xaxis_type` = space xaxis entries either equally by `"indices"` (default) or realistically by `"values"`
        - `regions` = list of region numbers (or individual value) to generate plots for (D=`None`, plotting all regions)
        - `region_indices` = same as above but uses indices rather than region numbers; this has higher priority if specified (D=`None`, plot all regions)
        - `times` = list of times (from start in seconds) (or individual value) to generate plots for (D=`None`, plotting all times)
        - `time_indices` = same as above but uses indices rather than time values; this has higher priority if specified (D=`None`, plot all times)
        - `rank_cutoff` = highest rank (or number of ranks) to be displayed (D=`10`, cannot be any greater than 10)
        - `xscale` = string specifying scale of x-axis, either `'linear'` (default) or `'log'`

    Outputs:
        - `fig_list` = list of figures which can be plotted.
    '''

    max_nregs = len(dchain_output['region']['numbers'])
    all_regs = dchain_output['region']['numbers']
    max_ntimes = len(dchain_output['time']['from_start_sec'])
    all_times = dchain_output['time']['from_start_sec']

    if not regions and not region_indices:
        regions = dchain_output['region']['numbers']
        region_indices  = range(len(regions))
    elif region_indices:
        if isinstance(region_indices, list):
            regions = []
            for i in region_indices:
                if i >= max_nregs:
                    print('region index {} greater than number of regions {}, skipping...'.format(i,max_nregs))
                    region_indices.remove(i)
                    continue
                regions.append(dchain_output['region']['numbers'][i])
        else:
            if region_indices < max_nregs:
                regions = [dchain_output['region']['numbers'][region_indices]]
                region_indices = [region_indices]
            else:
                print('Single provided region index {} is out of bounds of total number of regions {}, aborting...'.format(region_indices,max_nregs))
                return None
    elif regions:
        if isinstance(regions, list):
            region_indices = []
            for i in regions:
                if i not in all_regs:
                    print('region {} is not contained in list of region numbers, skipping...'.format(i))
                    regions.remove(i)
                    continue
                region_indices.append(dchain_output['region']['numbers'].index(i))
        else:
            if regions in all_regs:
                region_indices = [dchain_output['region']['numbers'].index(regions)]
                regions = [regions]
            else:
                print('Single provided region {} is not in the simulated region numbers, aborting...'.format(region_indices))
                return None

    if not times and not time_indices:
        times = dchain_output['time']['from_start_sec']
        time_indices  = range(len(times))
    elif time_indices:
        if isinstance(time_indices, list):
            times = []
            for i in time_indices:
                if i >= max_ntimes:
                    print('time index {} greater than number of times {}, skipping...'.format(i,max_ntimes))
                    time_indices.remove(i)
                    continue
                times.append(dchain_output['time']['from_start_sec'][i])
        else:
            if time_indices < max_ntimes:
                times = [dchain_output['time']['from_start_sec'][time_indices]]
                time_indices = [time_indices]
            else:
                print('Single provided time index {} is out of bounds of total number of times {}, aborting...'.format(time_indices,max_ntimes))
                return None
    elif times:
        if isinstance(times, list):
            time_indices = []
            for i in times:
                if i not in all_times:
                    print('time {} is not contained in list of times, skipping...'.format(i))
                    times.remove(i)
                    continue
                time_indices.append(dchain_output['time']['from_start_sec'].index(i))
        else:
            if times in all_times:
                time_indices = [dchain_output['time']['from_start_sec'].index(times)]
                times = [times]
            else:
                print('Single provided time {} is not in the outputted times, aborting...'.format(time_indices))
                return None

    if rank_val=='photon_dose':
        rank_val = 'gamma_dose'
    if rank_val not in ['activity','decay_heat','gamma_dose']:
        print("rank_val must be either 'activity', 'decay_heat', or 'gamma_dose', aborting...")
        return None

    if xaxis_val not in ['time','region']:
        print("xaxis_val must be either 'time' or 'region', aborting...")
        return None

    if xaxis_type=='index': xaxis_type = 'indices'
    if xaxis_type=='value': xaxis_type = 'values'
    if xaxis_type not in ['indices','values']:
        print("xaxis_val must be either 'indices' or 'values', aborting...")
        return None

    fig_list = []
    ax_list = []
    figi = 0

    if xaxis_val=='time':
        major_indices = region_indices
        minor_indices = time_indices
        major_values = regions
        minor_values = times
        xstr = 'Time'
    else:
        major_indices = time_indices
        minor_indices = region_indices
        major_values = times
        minor_values = regions
        xstr = 'Region'

    if xaxis_type=='indices':
        xdata = minor_indices
        xstr += ' (index)'
    else:
        xdata = minor_values

    for majori in major_indices:
        figi += 1
        # Assemble list of all ranked nuclides
        nuclides = []
        for minori in minor_indices:

            if xaxis_val=='time':
                ri = majori
                ti = minori
            else:
                ri = minori
                ti = majori

            for tti in range(len(dchain_output['top10'][rank_val]['nuclide'][ri][ti,:])):
                if (dchain_output['top10'][rank_val]['nuclide'][ri][ti,tti]!=None) and (dchain_output['top10'][rank_val]['nuclide'][ri][ti,tti] not in nuclides) and (dchain_output['top10'][rank_val]['rank'][ri][ti,tti]<=rank_cutoff):
                    nuclides.append(dchain_output['top10'][rank_val]['nuclide'][ri][ti,tti])
        # Now assemble plot for each nuclide
        plot_dicts = []
        for nuclide in nuclides:
            ni = nuclides.index(nuclide)
            ydata = []
            for minori in minor_indices:
                if xaxis_val=='time':
                    ri = majori
                    ti = minori
                else:
                    ri = minori
                    ti = majori
                if nuclide in dchain_output['top10'][rank_val]['nuclide'][ri][ti,:]:
                    tti = dchain_output['top10'][rank_val]['nuclide'][ri][ti,:].tolist().index(nuclide)
                    #tti = np.where(dchain_output['top10'][rank_val]['nuclide'][ri][ti,:]==nuclide)
                    if dchain_output['top10'][rank_val]['rank'][ri][ti,tti]<=rank_cutoff:
                        ydata.append( 1 + rank_cutoff - dchain_output['top10'][rank_val]['rank'][ri][ti,tti] )
                    else:
                        ydata.append(np.nan)
                else:
                    ydata.append(np.nan)
            tex_name = nuclide_plain_str_to_latex_str(nuclide)
            # dict = {'xdata':xdata,'ydata':ydata,'marker':tex_name,'markersize':30,'color':colors_list_12(ni%12)}
            dict = {'xdata':xdata,'ydata':ydata,'marker':tex_name,'markersize':30}
            plot_dicts.append(dict)
        # Now generate plot

        if xaxis_val=='time':
            title_str = 'Top {} nuclides by {} in region {}'.format(rank_cutoff,rank_val.replace('_',' '),major_values[major_indices.index(majori)])
        else:
            title_str = 'Top {} nuclides by {} at t = {} seconds'.format(rank_cutoff,rank_val.replace('_',' '),major_values[major_indices.index(majori)])
        ystr = 'Rank'


        if Hunters_tools_is_available:
            fig1, ax1 = fancy_plot(
                                   xdata_lists=None,
                                   ydata_lists=None,
                                   dictionaries=plot_dicts,
                                   figi=figi,
                                   title_str=title_str,
                                   x_label_str=xstr,
                                   y_label_str=ystr,
                                   x_scale=xscale,
                                   y_scale='linear',
                                   fig_height_inch=6.5*(rank_cutoff/10)+0.1*(10-rank_cutoff)
                                   )
        else:
            # For public version, just make this a basic plot rather than using my complicated personal plotting function
            fig1 = plt.figure()
            ax1 = plt.subplot(111)

            for entry in plot_dicts:
                ax1.plot(entry['xdata'],entry['ydata'],marker=entry['marker'],markersize=entry['markersize'],ls='')

            plt.xlabel(xstr,fontsize=14)
            plt.ylabel(ystr,fontsize=14)
            plt.xscale(xscale)
            fig1.tight_layout()
            fig1.set_size_inches(0.2+6.3*(len(plot_dicts[0]['xdata'])/12),6.5*(rank_cutoff/10)+0.1*(10-rank_cutoff))


        ax1.set_yticks(range(1,rank_cutoff+1))
        ax1.set_yticklabels([str(i) for i in range(rank_cutoff,0,-1)])

        if xaxis_type=='indices':
            ax1.set_xticks(minor_indices)
            ax1.set_xticklabels([str(i) for i in minor_indices])

        plt.grid(visible=True, which='major', linestyle='-', alpha=0)#0.25)
        plt.grid(visible=True, which='minor', linestyle='-', alpha=0)#0.10)

        fig_list.append(fig1)
        ax_list.append(ax1)


    return fig_list #, ax_list




















'''
**************************************************************************************************
------------------------------------ Other misc. functions ---------------------------------------
**************************************************************************************************
'''

def find(target, myList):
    '''
    Description:
        Search for and return the index of the first occurance of a value in a list.

    Inputs:
        - `target` = value to be searched for
        - `myList` = list of values

    Outputs:
        - index of first instance of `target` in `myList`
    '''
    for i in range(len(myList)):
        if myList[i] == target:
            return i


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
        `find`

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

def Element_ZorSym_to_name(Z):
    '''
    Description:
        Returns an element's name provided its atomic number Z or elemental symbol

    Inputs:
        - `Z` = string of elemental symbol or atomic number Z

    Outputs:
        - `name` = element name
    '''
    element_names = ['neutron','Hydrogen','Helium','Lithium','Beryllium','Boron','Carbon','Nitrogen','Oxygen','Fluorine',
                     'Neon','Sodium','Magnesium','Aluminium','Silicon','Phosphorus','Sulfur','Chlorine','Argon',
                     'Potassium','Calcium','Scandium','Titanium','Vanadium','Chromium','Manganese','Iron','Cobalt',
                     'Nickel','Copper','Zinc','Gallium','Germanium','Arsenic','Selenium','Bromine','Krypton',
                     'Rubidium','Strontium','Yttrium','Zirconium','Niobium','Molybdenum','Technetium','Ruthenium',
                     'Rhodium','Palladium','Silver','Cadmium','Indium','Tin','Antimony','Tellurium','Iodine','Xenon',
                     'Caesium','Barium','Lanthanum','Cerium','Praseodymium','Neodymium','Promethium','Samarium',
                     'Europium','Gadolinium','Terbium','Dysprosium','Holmium','Erbium','Thulium','Ytterbium',
                     'Lutetium','Hafnium','Tantalum','Tungsten','Rhenium','Osmium','Iridium','Platinum','Gold',
                     'Mercury','Thallium','Lead','Bismuth','Polonium','Astatine','Radon','Francium','Radium',
                     'Actinium','Thorium','Protactinium','Uranium','Neptunium','Plutonium','Americium','Curium',
                     'Berkelium','Californium','Einsteinium','Fermium','Mendelevium','Nobelium','Lawrencium',
                     'Rutherfordium','Dubnium','Seaborgium','Bohrium','Hassium','Meitnerium','Darmstadtium',
                     'Roentgenium','Copernicium','Nihonium','Flerovium','Moscovium','Livermorium','Tennessine','Oganesson']

    try:
        zi = int(Z)
    except:
        zi = Element_Sym_to_Z(Z)

    return element_names[zi]

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

def nuclide_to_Latex_form(Z,A,m=''):
    '''
    Description:
        Form a LaTeX-formatted string of a nuclide provided its information

    Dependencies:
        `Element_Z_to_Sym`
        (only required if inputed Z is not already an elemental symbol)

    Inputs:
        - `Z` = atomic number of nuclide (int, float, or string) or elemental symbol (string)
        - `A` = atomic mass of nuclide (int, float, or string) or string to go in place of A (ex. 'nat')
        - `m` = metastable state (D='', ground state); this will be appended to the end of A
              if not a string already, it will be converted into one and appended to 'm' (ex. 1 -> 'm1')

    Outputs:
        - LaTeX-formatted raw string of a nuclide, excellent for plot titles, labels, and auto-generated LaTeX documents
    '''
    if isinstance(A,(int,float)): A = str(int(A))
    if not isinstance(Z,str): symbol = Element_Z_to_Sym(int(Z))
    if isinstance(m,float): m = int(m)
    if isinstance(m,int): m = 'm' + str(m)
    latex_str = r"$^{{{}{}}}$".format(A,m) + "{}".format(symbol)
    return latex_str

def nuclide_plain_str_to_latex_str(nuc_str,include_Z=False):
    '''
    Description:
        Converts a plaintext string of a nuclide to a LaTeX-formatted raw string
        Note: if you already have the Z, A, and isomeric state information determined, the "nuclide_to_Latex_form" function can be used instead

    Dependencies:
        - `Element_Z_to_Sym` (only required if `include_Z = True`)

    Inputs:
        (required)

       - `nuc_str` = string to be converted; a huge variety of formats are supported, but they all must follow the following rules:
           + Isomeric/metastable state characters must always immediately follow the atomic mass characters.
               Isomeric state labels MUST either:
               - (1) be a single lower-case character OR
               - (2) begin with any non-numeric character and end with a number
           + Atomic mass numbers must be nonnegative integers OR the string `"nat"` (in which case no metastable states can be written)
           + Elemental symbols MUST begin with an upper-case character

    Inputs:
       (optional)

       - `include_Z` = `True`/`False` determining whether the nuclide's atomic number Z will be printed as a subscript beneath the atomic mass

    Outputs:
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

def nuclide_plain_str_ZZZAAAM(nuc_str):
    '''
    Description:
        Converts a plaintext string of a nuclide to an integer ZZZAAAM = 10000\*Z + 10\*A + M

    Dependencies:
        `Element_Z_to_Sym`

    Inputs:
       - `nuc_str` = string to be converted; a huge variety of formats are supported, but they all must follow the following rules:
           + Isomeric/metastable state characters must always immediately follow the atomic mass characters.
               Isomeric state labels MUST either:
               - (1) be a single lower-case character OR
               - (2) begin with any non-numeric character and end with a number
           + Atomic mass numbers must be nonnegative integers OR the string "nat" (in which case no metastable states can be written)
           + Elemental symbols MUST begin with an upper-case character


    Outputs:
        - ZZZAAAM integer
    '''

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

    if 'nat' in nuc_str:
        print('Must specify a specific nuclide, not natural abundances')
        return None

    # string MUST begin with either mass number or elemental symbol
    if isdigit_list[0]: # mass first
        mass_first = True
    else:
        mass_first = False

    if mass_first:
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
        ci = 0
        # Extract all characters before first number as the elemental symbol
        while nuc_str[ci].isalpha():
            symbol += nuc_str[ci]
            ci += 1

        # now, extract mass
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


    if symbol == 'n':
        Z = 0
    elif symbol == 'p' or symbol == 'd' or symbol == 't':
        Z = 1
    else:
        Z = Element_Sym_to_Z(symbol)

    A = int(mass)

    if isost.strip()=='' or isost=='g':
        M = 0
    elif isost=='m' or isost=='m1':
        M = 1
    elif isost=='n' or isost=='m2':
        M = 2
    elif isost=='o' or isost=='m3':
        M = 3
    elif isost=='p' or isost=='m4':
        M = 4
    elif isost=='q' or isost=='m5':
        M = 5
    else:
        print("Unknown isomeric state {}, assumed ground state".format(isost))
        M = 0

    ZZZAAAM = 10000*Z + 10*A + M

    return ZZZAAAM


def time_str_to_sec_multiplier(time_str):
    '''
    Description:
        Provide a time unit and this function provides what those time units need to be multiplied by to obtain seconds.

    Inputs:
        - `time_str` = string containing time units character(s) [s,m,h,d,y,ms,us,ns,ps,fs]

    Outputs:
        - `m` = multiplier to convert a time of the supplied units to seconds

    '''
    try:
        if time_str == 's':
            m = 1
        elif time_str == 'm':
            m = 60
        elif time_str == 'h':
            m = 60*60
        elif time_str == 'd':
            m = 60*60*24
        elif time_str == 'y':
            m = 60*60*24*365.25
        elif time_str == 'ms':
            m = 1e-3
        elif time_str == 'us':
            m = 1e-6
        elif time_str == 'ns':
            m = 1e-9
        elif time_str == 'ps':
            m = 1e-12
        elif time_str == 'fs':
            m = 1e-15
        return m
    except:
        print('"{}" is not a valid time unit; please use one of the following: [s,m,h,d,y,ms,us,ns,ps,fs]'.format(time_str))
        return None

def seconds_to_dhms(t_sec):
    '''
    Description:
        Provide a time in seconds and obtain a string with the time in days, hours, minutes, and seconds

    Inputs:
        - `t_sec` = a time in seconds (float or int)

    Outputs:
        - `time_str` = string containing the time prettily formatted in d/h/m/s format

    '''
    m, s = divmod(t_sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d != 0:
        time_str = "{:0.0f}d {:0.0f}h {:0.0f}m {:0.2f}s".format(d,h,m,s)
    elif h != 0:
        time_str = "{:0.0f}h {:0.0f}m {:0.2f}s".format(h,m,s)
    elif m != 0:
        time_str = "{:0.0f}m {:0.2f}s".format(m,s)
    elif s != 0:
        time_str = "{:0.2f}s".format(s)
    else:
        time_str = ""

    return time_str

def seconds_to_ydhms(t_sec):
    '''
    Description:
        Provide a time in seconds and obtain a string with the time in years, days, hours, minutes, and seconds

    Inputs:
        - `t_sec` = a time in seconds (float or int)

    Outputs:
        - `time_str` = string containing the time prettily formatted in y/d/h/m/s format

    '''
    m, s = divmod(t_sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    y, d = divmod(d, 365)

    if y>=4 : # if leap year occurred
        n_leap_years = int(y/4)
        d = d-n_leap_years

    if y != 0:
        time_str = "{:0.0f}y {:0.0f}d {:0.0f}h {:0.0f}m {:0.2f}s".format(y,d,h,m,s)
    elif d != 0:
        time_str = "{:0.0f}d {:0.0f}h {:0.0f}m {:0.2f}s".format(d,h,m,s)
    elif h != 0:
        time_str = "{:0.0f}h {:0.0f}m {:0.2f}s".format(h,m,s)
    elif m != 0:
        time_str = "{:0.0f}m {:0.2f}s".format(m,s)
    elif s != 0:
        time_str = "{:0.2f}s".format(s)
    else:
        time_str = ""

    return time_str































show_output_from_example = False
if show_output_from_example:
    test_folder = r'example\\'
    test_basename = 'example_Na22'

    output = process_dchain_simulation_output(test_folder,test_basename)

    print('\n')

    print('Output times relative to start (in seconds):',output['time']['from_start_sec'])
    print('Output times relative to EOB (in seconds):  ',output.time.from_EOB_sec)

    print('\n')

    print('Total neutron flux in first region (in n/cm^2/sec):',output['region']['neutron_flux'][0])
    print('Fractional uncertainty in total neutron flux in first region:',output['neutron']['total_flux']['error'][0]/output['neutron']['total_flux']['value'][0])

    print('\n')

    print('All produced nuclides (in DCHAIN-formatted strings):',output['nuclides']['names'])
    #print(np.shape(np.array(output['gamma']['spectra']['flux']['value'])))
    #print(output['gamma']['spectra']['flux']['value'][0][0,:])

    #pprint.pprint(output['top10']['activity']['rank'][0][0,:])

    print('\n')

    print('[T-Yield] high energy reaction-produced nuclides:',output['yields']['names'][0])
    print('[T-Yield] nuclide yields per source particle:',output['yields']['unit_rate']['value'][0])

    print('\n')

    library_file = r'C:\phits\dchain-sp\data\JEFF-3-3--_n_act_xs_lib'
    #xs_out, rxn_str_out = retrieve_rxn_xs_from_lib(library_file,'F-19','p')
    xs_1g = calc_one_group_nrxn_xs_dchain(output['neutron']['unit_spectra']['flux']['value'][0],output['neutron']['unit_spectra']['flux']['error'][0],library_file,'F-19','p')
    print('Single group cross section (and its absolute uncertainty) for 19F(n,p)19O reaction in provided neutron flux (in barns): ',xs_1g)


    figs = plot_top10_nuclides(output,region_indices=1,rank_cutoff=5,xaxis_val='time',xaxis_type='indices',xscale='linear')
    plt.show()


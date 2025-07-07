'''
This module is used for managing the MC materials database.

'''


import re
import os
import csv
import sys
import json
from pathlib import Path
from PHITS_tools import Element_Z_to_Sym, fetch_MC_material, nuclide_plain_str_to_ZZZAAAM

def pnnl_lib_csv_to_dict_list(path_to_materials_compendium_csv=Path(Path.cwd(), 'materials_compendium.csv')):
    '''
    Description:
        This function converts a CSV file of the PNNL
        Compendium of Material Composition Data for Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, 
        to a Python dictionary object.
        The PNNL library's CSV file was obtained from PYNE:
        https://github.com/pyne/pyne/blob/develop/pyne/dbgen/materials_compendium.csv

    Dependencies:


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

def materials_dict_list_to_json(mat_list,json_filepath=Path(Path.cwd(), 'materials_compendium.json')):
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

def materials_json_to_dict_list(json_filepath=Path(Path.cwd(), 'materials_compendium.json')):
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
        entry_text += '  MCNP formatted ({}) \n'.format(par)
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
        - 'comment_char' = (D=`'$'`) string denoting the comment character to use (Note: `'$'` works for both PHITS and MCNP.)

    Outputs:
        - `entry_text` = a string of MCNP/PHITS-formatted text with material composition information
    '''
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
        - `write_index_file` = (D=`True`) Boolean specifying if an index file, just listing the materials contained 
             in the outputted file along with their ID number and data source (tab delimited), should also be written. 
             If `True`, this file will have the same filepath as `lib_filepath` but with `'_index'` appended to its basename. 
    
    Outputs:
        - - `None`; the materials text data will be saved to `lib_filepath`.
    '''
    lib_text = ''
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

def write_MC_formated_files(mat_list,lib_filepath=Path(Path.cwd(),'MC_materials.txt'),comment_char='$',header_text=''):
    '''
    Description:
        Generates four text files of MCNP/PHITS-formatted materials section text blocks for a list of material dictionary objects.
        The four files cover every combination of concentration formats `['atom fraction', 'weight fraction']` and 
        particle formats `['neutrons', 'photons']`.

    Inputs:
        - `mat_list` = a list of dictionary objects of the extracted materials information
        - `lib_filepath` = string or Path object denoting the basic path to the materials library text files to be saved
        - 'comment_char' = (D=`'$'`) string denoting the comment character to use (Note: `'$'` works for both PHITS and MCNP.)
        - `header_text` = a string of text appearing at the very top of the output text files. 
            If left blank (`''`), a default header string as defined at the start of this function will be used.
        
    Outputs:
        - - `None`; the materials text data will be saved to `lib_filepath`.
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


def write_general_MC_file(mat_list,lib_filepath=Path(Path.cwd(),'MC_materials_general.txt'),comment_char='$',header_text=''):
    '''
    Description:
        Generates a text file of MCNP/PHITS-formatted materials section text blocks for a list of material dictionary objects.
        This single file is a mix of concentration and particle formats as automatically selected for most general situations.
        If a material entry contains a chemical formula, its concentration will be specified by atom fraction; otherwise, 
        weight fraction will be used.  If any of the "neutron keywords" (`['depleted','enriched',' heu',' leu','uranium','plutonium','uranyl']`)
        appear in a material's name (case insensitive), the "neutrons" particle-formatted data is use (isotopic compositions specified); 
        otherwise, the "photons" particle format (natural abundances for elements) is used.
        
    Inputs:
        - `mat_list` = a list of dictionary objects of the extracted materials information
        - `lib_filepath` = string or Path object denoting the basic path to the materials library text file to be saved
        - 'comment_char' = (D=`'$'`) string denoting the comment character to use (Note: `'$'` works for both PHITS and MCNP.)
        - `header_text` = a string of text appearing at the very top of the output text files. 
            If left blank (`''`), a default header string as defined at the start of this function will be used.
        
    Outputs:
        - `None`; the materials text data will be saved to `lib_filepath`.
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
    lib_text = header_text
    for i in range(len(mat_list)):
        lib_text += fetch_MC_material(i + 1, matdict=mat_list[i])
    # save file
    f = open(lib_filepath, 'w+')
    f.write(lib_text)
    f.close()
    print('Materials library file written:', lib_filepath)
    return None


def update_materials_database_files(json_filepath,name,mat_str,matid=None,density=None,source=None,
                                    source_short=None,formula=None,molecular_weight=None,total_atom_density=None,
                                    new_database_base_name=None,update_descriptive_file=True,
                                    update_MC_formated_files=True,update_general_MC_file=True):
    '''
    Description:
    
        Add or modify a material in a MC materials database JSON file (optionally updating text files too).

    Inputs:
        (required)
        
        - `json_filepath` = string or Path object denoting the path to the JSON materials file
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
                as generated by `write_MC_formated_files()`, should be updated/(re)written.
        - `update_general_MC_file` = (D=`True`) Boolean denoting whether the updated descriptive file for the database, 
                as generated by `write_general_MC_file()`, should be updated/(re)written.

    Outputs:
    
        - `None`; the materials data from `json_filepath` will be updated with the provided new material (or written to 
                a new JSON database named with `new_database_base_name`), and derived text files are optionally updated 
                too as designated by `update_descriptive_file`, `update_MC_formated_files`, and `update_general_MC_file`.
    
    Notes:
        
        Entries in the database are uniquely identified by their `matid` or the combination of `name` and `source`.
        If provided with a `matid` or `name` and `source` combination already present within the database, a prompt
        will appear asking whether the existing entry should be overwritten.
        
    '''
    add_new_material = False
    rewrite_existing_material = False
    rewrite_matid = None  # material ID (=index + 1) to overwrite
    #if matid is not None:
        
    
    
    return None











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
#write_MC_formated_files(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium.txt'),header_text=header_text)
write_general_MC_file(mat_list,lib_filepath=Path(Path.cwd(),'PNNL_materials_compendium_general.txt'),header_text=header_text)

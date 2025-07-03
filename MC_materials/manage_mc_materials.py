'''
This module is used for managing the MC materials database.

'''


import re
import os
import csv
import sys
import pickle
from pathlib import Path


def pnnl_lib_csv_to_dict(path_to_materials_compendium_csv=Path(Path.cwd(), 'materials_compendium.csv')):
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
        - `mat` = a dictionary object of the extracted materials information
    
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
    mat_list = []
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
                mat_list.append(mat)
            else:
                mat['photons']['weight fraction']['ZA'].append(line[1])
                mat['photons']['weight fraction']['value'].append(line[2])
                mat['photons']['atom fraction']['ZA'].append(line[3])
                mat['photons']['atom fraction']['value'].append(line[4])
                mat['photons']['atom density']['ZA'].append(line[5])
                mat['photons']['atom density']['value'].append(line[6])
    
    return mat

#def material_lib_dict_to_text(path_to_materials_compendium_csv):

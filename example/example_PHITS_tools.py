import PHITS_tools
from pathlib import Path
import pprint
import numpy as np
import matplotlib.pyplot as plt
import pickle
import lzma

path_to_example_dir = Path.cwd() #Path('example/')
standard_output_file = Path(path_to_example_dir, 'product.out')
dump_output_file = Path(path_to_example_dir, 'product_dmp.out')

# parse standard tally output file
print('STANDARD TALLY OUTPUT')
# run the output file through the main parsing function in PHITS Tools
results_dict = PHITS_tools.parse_tally_output_file(standard_output_file, autoplot_tally_output=True)
# setting autoplot_tally_output=True will cause a plot to be made automatically and saved to product.pdf

# If you already have a pickle file from running PHITS Tools previously, you can skip re-parsing it and
# just load in the pickle file with the `prefer_reading_existing_pickle=True` setting.  If set to True
# but the pickle file doesn't exist, `parse_tally_output_file` will run just like normal, parse the output file
# and return the same dictionary object.  (You can also just load in the pickle file as one normally would.)
#results_dict = PHITS_tools.parse_tally_output_file(standard_output_file, prefer_reading_existing_pickle=True)

print("keys of output dictionary:", results_dict.keys(), '\n')
tally_metadata = results_dict['tally_metadata']
tally_data = results_dict['tally_data']
tally_df = results_dict['tally_dataframe']

print('Collected tally metadata dictionary:')
pprint.pp(dict(tally_metadata))
print()

print('Pandas DataFrame column headers and attributes:')
print(tally_df.columns.values.tolist())
print(tally_df.attrs)
print('Number of rows = ', tally_df.shape[0])
# print(tally_df.to_string())   # uncomment to print the whole dataframe (200 lines)
print()

np_array_dims = np.shape(tally_data)
print('NumPy array dimensions:', np_array_dims, '\n')

# Now let's recreate the .eps plot automatically produced by PHITS
energy_bin_midpoints = tally_metadata['e-mesh_bin_mids_log']  # in units of MeV
# the "e-type = 3" setting means energy bins are log-spaced, so using the log-centered bin midpoints makes the most sense here
particle_group_labels = tally_metadata['part_groups']
particle_group_labels[-1] = 'other'  # rename the "not neutrons and not protons" group to just "other"
for ip in range(np_array_dims[7]):
    plt.errorbar(energy_bin_midpoints, tally_data[0,0,0,:,0,0,0,ip,0,0], yerr=tally_data[0,0,0,:,0,0,0,ip,0,2])
plt.legend(particle_group_labels)
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Energy [MeV]')
plt.ylabel('Number [1/source]')
plt.title('Particle production in region 100')
plt.grid(which='both', linewidth=1, color='#EEEEEE')
fig_path = Path(path_to_example_dir,'production_energy_spectrum_by_particle.png')
plt.savefig(fig_path)

# The PHITS Tools function for generating plots automatically can also return the seaborn FacetGrid objects, 
# allowing for further customization if desired.
customized_autoplot_pdf = Path(path_to_example_dir, 'product_customized.pdf')
fg_list = PHITS_tools.autoplot_tally_results(results_dict, output_filename=customized_autoplot_pdf, return_fg_list=True)
text_color, background_color = '#260F80', '#FCF6E3'
fg_list[0].fig.set_facecolor(background_color)  # change background color of figure exterior
fg_list[0].ax.set_facecolor(background_color)  # change background color of plot area
fg_list[0].ax.tick_params(labelcolor=text_color)  # change font color of axis tick labels (the numbers)
for spine in fg_list[0].ax.spines.values(): spine.set_edgecolor(text_color)  # change color of axes and ticks
fg_list[0].fig._suptitle.set_color(text_color)  # change font color of title
fg_list[0]._legend.get_title().set(color=text_color)  # change font color of legend title
for text in fg_list[0]._legend.get_texts(): text.set(color=text_color)  # change font color of text entries in legend
fg_list[0].ax.set_xlabel('Energy of produced particle [MeV]', color=text_color)  # change x-axis label text and color
fg_list[0].ax.set_ylabel(fg_list[0].ax.get_ylabel(), color=text_color)  # change y-axis label color only
fg_list[0].savefig(customized_autoplot_pdf)  # save the new customized plot

# parse DUMP tally output file
print('\n\nDUMP TALLY OUTPUT')
# Given parsing dump files can take a bit longer owing to their size, I think it's generally preferable to only
# parse the dump file once and then just load in the saved pickle file(s) afterward.
named_tuple_dill_file = Path(dump_output_file.parent, dump_output_file.stem + '_namedtuple_list.pickle.xz')
dump_dataframe_file = Path(dump_output_file.parent, dump_output_file.stem + '_Pandas_df.pickle.xz')
if named_tuple_dill_file.is_file() and dump_dataframe_file.is_file():
    with lzma.open(named_tuple_dill_file, 'rb') as file: events_list = pickle.load(file)
    with lzma.open(dump_dataframe_file, 'rb') as file: events_df = pickle.load(file)
else:
    events_list, events_df = PHITS_tools.parse_tally_dump_file(dump_output_file, save_namedtuple_list=True, save_Pandas_dataframe=True)
# This file has 11 columns of data for every single history that contributed to the tally.

print('Pandas DataFrame column headers for dump file:')
print(events_df.columns.values.tolist())
print('Number of rows (one per tallied event) = ', events_df.shape[0])
# print(events_df.to_string())   # uncomment to print the whole dataframe
print()

# Let's compile a list of all the unique product nuclides produced, telling us what's in that "other" category
found_kf_codes = []
for i in events_list:
    if i.kf not in found_kf_codes:
        found_kf_codes.append(int(i.kf))
found_kf_codes.sort()
# print(found_kf_codes)
# Let's make a human-readable list
# the kf-code table can be found in Table 4.4 of the PHITS manual
found_products = []
for i in found_kf_codes:
    found_products.append(PHITS_tools.kfcode_to_common_name(i))
print('The following particles and nuclides were produced:')
print(found_products)

plt.show()
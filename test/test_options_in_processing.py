import pytest, PHITS_tools, os, pickle
import numpy as np
from pathlib import Path
from traceback import format_exc

path_to_phits_base_folder = Path(r'C:\phits')

phits_sample_dir = Path(path_to_phits_base_folder,'sample')
phits_recommendation_dir = Path(path_to_phits_base_folder,'recommendation')

def test_extract_tally_outputs_from_phits_input_options():
    phits_input = phits_recommendation_dir / 'NeutronSource' / 'NeutronSource.inp'
    x = PHITS_tools.extract_tally_outputs_from_phits_input(phits_input, only_seek_phitsout=True)
    assert x['phitsout'] != []

@pytest.mark.slow
@pytest.mark.integration
def test_parse_tally_output_file_options():
    tally_output_filepath = phits_recommendation_dir / 'muon' / 'product.out'
    tod = PHITS_tools.parse_tally_output_file(tally_output_filepath, make_PandasDF=True, 
                                              calculate_absolute_errors=True,
                                              save_output_pickle=False, include_phitsout_in_metadata=False, 
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=False, 
                                              autoplot_tally_output=False
                                              )
    assert tod['tally_metadata'] != []
    tod = PHITS_tools.parse_tally_output_file(tally_output_filepath, make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=True, include_phitsout_in_metadata=False,
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=False,
                                              autoplot_tally_output=False
                                              )
    output_pickle = Path(tally_output_filepath.parent, tally_output_filepath.stem + '.pickle')
    assert output_pickle.exists()
    tod2 = PHITS_tools.parse_tally_output_file(tally_output_filepath, make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=False, include_phitsout_in_metadata=False,
                                              prefer_reading_existing_pickle=True, compress_pickle_with_lzma=False,
                                              autoplot_tally_output=False
                                              )
    assert (tod['tally_data'] == tod2['tally_data']).all()
    os.remove(output_pickle)
    tod = PHITS_tools.parse_tally_output_file(tally_output_filepath, make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=True, include_phitsout_in_metadata=True,
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                              autoplot_tally_output=False
                                              )
    output_pickle = Path(tally_output_filepath.parent, tally_output_filepath.stem + '.pickle.xz')
    assert output_pickle.exists()
    tod = PHITS_tools.parse_tally_output_file(tally_output_filepath, make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=True, include_phitsout_in_metadata=True,
                                              prefer_reading_existing_pickle=True, compress_pickle_with_lzma=True,
                                              autoplot_tally_output=True
                                              )
    os.remove(output_pickle)
    assert Path(tally_output_filepath.parent, tally_output_filepath.stem + '.pdf').exists()
    assert Path(tally_output_filepath.parent, tally_output_filepath.stem + '.png').exists()
    assert np.shape(tod['tally_data'])[-1] == 3
    tod = PHITS_tools.parse_tally_output_file(tally_output_filepath, make_PandasDF=False,
                                              calculate_absolute_errors=False,
                                              save_output_pickle=False, include_phitsout_in_metadata=False,
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=False,
                                              autoplot_tally_output=True
                                              )
    assert np.shape(tod['tally_data'])[-1] == 2
    assert tod['tally_dataframe'] is None

@pytest.mark.slow
@pytest.mark.integration
def test_dchain_sample_3_step_dose():
    '''
    WARNING
    For this test to work at all, you need to run through the example calculation located at:
    C:\phits\dchain-sp\sample\3-step_dose_xyz
    Minimally, you need to run `phits_3-step.inp` through PHITS and 
    the `W_reg_target.out` and `W_xyz_target.out` outputs through DCHAIN
    '''
    tally_output_directory = path_to_phits_base_folder / 'dchain-sp' / 'sample' / '3-step_dose_xyz' 
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_directory,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=False, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False
                                                  )
    assert len(x) > 3
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_directory,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=True, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=True, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False
                                                  )
    assert (tally_output_directory / 'ALL_TALLY_OUTPUTS.pickle.xz').exists()
    #assert (tally_output_directory / 'phits_3-step_ALL_TALLY_OUTPUTS_PLOTTED.pdf').exists()
import pytest, PHITS_tools, os, pickle, glob
import numpy as np
import pandas as pd
from pathlib import Path

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
def test_dir_mode_options():
    tally_output_actual_dir = phits_recommendation_dir / 'muon'
    tally_output_directory = tally_output_actual_dir
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_directory,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=True, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False
                                                  )
    assert len(x) == 2
    assert (tally_output_actual_dir / 'ALL_TALLY_OUTPUTS.pickle.xz').exists()
    tally_output_directory = tally_output_actual_dir / 'product.out'
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_directory,
                                                  include_subdirectories=True,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=False, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False
                                                  )
    assert len(x) == 2
    tally_output_directory = tally_output_actual_dir / 'phits.out'
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_directory,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=False, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False
                                                  )
    assert len(x) == 2
    tally_output_directory = tally_output_actual_dir / 'muon.inp'
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_directory,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=True, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False
                                                  )
    assert len(x) == 2
    assert (tally_output_actual_dir / 'muon_ALL_TALLY_OUTPUTS.pickle.xz').exists()
    
    

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


@pytest.mark.slow
@pytest.mark.integration
def test_dump_file_options():
    '''
    WARNING
    For this test to work at all, you need to modify and rerun in PHITS the example calculation located at:
    C:\phits\sample\source\Cosmicray\GCR-blackhole\phits-blackhole-1st.inp
    
    Then, follow these steps:
       1. Open `phits-blackhole-1st.inp` and scroll down to the "[ T - C r o s s ]" tally at the very bottom of the file.
       2. Copy and paste the [T-Cross] tally.
       3. In the new duplicate tally, change `file = cross.out` to `file = cross_bin.out`
       4. In the new duplicate tally, change `dump =   -11` to `dump =    11`
       5. Rerun `phits-blackhole-1st.inp` in PHITS
       
    Then, the tests here should work just fine.
    '''
    tally_output_dir = phits_sample_dir / 'source' / 'Cosmicray' / 'GCR-blackhole'
    tally_output_file = tally_output_dir / 'cross_dmp.out'
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=True, use_degrees=True, max_entries_read=None,
                                          return_namedtuple_list=False, return_Pandas_dataframe=False,
                                          save_namedtuple_list=True, save_Pandas_dataframe=True,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=False,
                                          split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0
                                          )
    assert x is None
    assert (tally_output_dir / 'cross_dmp_namedtuple_list.pickle.xz').exists()
    assert (tally_output_dir / 'cross_dmp_Pandas_df.pickle.xz').exists()
    
    tally_output_file = tally_output_dir / 'cross_bin_dmp.out'
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None, 
                                          return_directional_info=False, use_degrees=False, max_entries_read=None, 
                                          return_namedtuple_list=False, return_Pandas_dataframe=False, 
                                          save_namedtuple_list=True, save_Pandas_dataframe=True, 
                                          compress_pickles_with_lzma=True, 
                                          prefer_reading_existing_pickle=False, 
                                          split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0
                                          )
    assert x is None
    assert (tally_output_dir / 'cross_bin_dmp_namedtuple_list.pickle.xz').exists()
    assert (tally_output_dir / 'cross_bin_dmp_Pandas_df.pickle.xz').exists()
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=True, use_degrees=True, max_entries_read=None,
                                          return_namedtuple_list=False, return_Pandas_dataframe=False,
                                          save_namedtuple_list=True, save_Pandas_dataframe=True,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=False,
                                          split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0
                                          )
    assert x is None
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=False, use_degrees=False, max_entries_read=None,
                                          return_namedtuple_list=True, return_Pandas_dataframe=False,
                                          save_namedtuple_list=True, save_Pandas_dataframe=True,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=True,
                                          split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0
                                          )
    assert isinstance(x, np.recarray)
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=False, use_degrees=False, max_entries_read=None,
                                          return_namedtuple_list=False, return_Pandas_dataframe=True,
                                          save_namedtuple_list=True, save_Pandas_dataframe=True,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=False,
                                          split_binary_dumps_over_X_GB=0.0003, merge_split_dump_handling=2
                                          )
    assert isinstance(x, pd.DataFrame)
    assert (tally_output_dir / 'cross_bin_dmp_namedtuple_list.pickle.xz').exists()
    assert (tally_output_dir / 'cross_bin_dmp_Pandas_df.pickle.xz').exists()
    assert glob.glob(str(tally_output_dir / 'cross_bin_dmp_part-1of*_namedtuple_list.pickle.xz'))
    assert glob.glob(str(tally_output_dir / 'cross_bin_dmp_part-1of*_Pandas_df.pickle.xz'))
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=False, use_degrees=False, max_entries_read=None,
                                          return_namedtuple_list=False, return_Pandas_dataframe=True,
                                          save_namedtuple_list=True, save_Pandas_dataframe=True,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=False,
                                          split_binary_dumps_over_X_GB=0.0003, merge_split_dump_handling=0
                                          )
    assert (tally_output_dir / 'cross_bin_dmp_namedtuple_list.pickle.xz').exists()
    assert (tally_output_dir / 'cross_bin_dmp_Pandas_df.pickle.xz').exists()
    assert not glob.glob(str(tally_output_dir / 'cross_bin_dmp_part-1of*_namedtuple_list.pickle.xz'))
    assert not glob.glob(str(tally_output_dir / 'cross_bin_dmp_part-1of*_Pandas_df.pickle.xz'))
    
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_dir/'phits-blackhole-1st.inp',
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=True, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False,
                                                  include_dump_files=True,
                                                  split_binary_dumps_over_X_GB=0.0003, merge_split_dump_handling=0,
                                                  )
    assert len(x) == 4
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_dir,
                                                  include_subdirectories=False,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=True, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False,
                                                  include_dump_files=True,
                                                  split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0,
                                                  )
    assert len(x) == 6
    x = PHITS_tools.parse_all_tally_output_in_dir(tally_output_dir,
                                                  include_subdirectories=True,
                                                  return_tally_output=False, make_PandasDF=True,
                                                  calculate_absolute_errors=True, save_output_pickle=True,
                                                  include_phitsout_in_metadata=False,
                                                  prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                                  merge_tally_outputs=True, save_pickle_of_merged_tally_outputs=None,
                                                  autoplot_tally_output=False, autoplot_all_tally_output_in_dir=False,
                                                  include_dump_files=True,
                                                  split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0,
                                                  )
    assert len(x) == 8
    
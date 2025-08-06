import pytest, PHITS_tools, os, pickle, glob
import numpy as np
import pandas as pd
from pathlib import Path
from conftest import path_to_base_phits_test_dir

phits_sample_dir = Path(path_to_base_phits_test_dir,'sample')
phits_recommendation_dir = Path(path_to_base_phits_test_dir,'recommendation')

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
    os.remove(Path(tally_output_filepath.parent, tally_output_filepath.stem + '.pdf'))
    os.remove(Path(tally_output_filepath.parent, tally_output_filepath.stem + '.png'))
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
    tally_output_directory = path_to_base_phits_test_dir / 'dchain-sp' / 'sample' / '3-step_dose_xyz' 
    if not (tally_output_directory / 'W_reg_target.act').exists() or not (tally_output_directory / 'W_xyz_target.act').exists():
        print('Please follow the instructions in the `test_dchain_sample_3_step_dose()` docstring to run this test.')
        pytest.skip("Missing required files. Please follow the instructions in the `test_dchain_sample_3_step_dose()` docstring to run this test.")
        # pytest.fail('message', pytrace=False) is an option too.
    tod = PHITS_tools.parse_tally_output_file(tally_output_directory / 'W_reg_target.dyld', make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=True, include_phitsout_in_metadata=True,
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                              autoplot_tally_output=False
                                              )
    assert tod['tally_metadata'] != []
    tod = PHITS_tools.parse_tally_output_file(tally_output_directory / 'W_reg_target.dtrk', make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=True, include_phitsout_in_metadata=True,
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                              autoplot_tally_output=False
                                              )
    assert tod['tally_metadata'] != []
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
    if not (tally_output_file).exists():
        print('Please follow the instructions in the `test_dump_file_options()` docstring to run this test.')
        pytest.skip("Missing required files. Please follow the instructions in the `test_dump_file_options()` docstring to run this test.")
        # pytest.fail('message', pytrace=False) is an option too.
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
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=-11, 
                                          dump_data_sequence='1   2   3   4   5   6   7   8   9  18  19',
                                          return_directional_info=True, use_degrees=True, max_entries_read=1000000,
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
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=11, 
                                          dump_data_sequence='1   2   3   4   5   6   7   8   9  18  19',
                                          return_directional_info=True, use_degrees=True, max_entries_read=1000000,
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
    os.remove(tally_output_dir / 'cross_bin_dmp_namedtuple_list.pickle.xz')
    os.remove(tally_output_dir / 'cross_bin_dmp_Pandas_df.pickle.xz')
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=True, use_degrees=True, max_entries_read=None,
                                          return_namedtuple_list=True, return_Pandas_dataframe=False,
                                          save_namedtuple_list=True, save_Pandas_dataframe=True,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=True,
                                          split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0
                                          )
    assert isinstance(x, list)
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=True, use_degrees=True, max_entries_read=None,
                                          return_namedtuple_list=True, return_Pandas_dataframe=True,
                                          save_namedtuple_list=True, save_Pandas_dataframe=True,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=True,
                                          split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0
                                          )
    assert isinstance(x[0], np.recarray)
    assert isinstance(x[1], pd.DataFrame)
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=True, use_degrees=True, max_entries_read=None,
                                          return_namedtuple_list=True, return_Pandas_dataframe=True,
                                          save_namedtuple_list=False, save_Pandas_dataframe=False,
                                          compress_pickles_with_lzma=True,
                                          prefer_reading_existing_pickle=True,
                                          split_binary_dumps_over_X_GB=20, merge_split_dump_handling=0
                                          )
    assert isinstance(x[0], np.recarray)
    assert isinstance(x[1], pd.DataFrame)
    x = PHITS_tools.parse_tally_dump_file(tally_output_file, dump_data_number=None, dump_data_sequence=None,
                                          return_directional_info=True, use_degrees=False, max_entries_read=None,
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
    os.remove(tally_output_dir / 'cross_dmp_namedtuple_list.pickle.xz')
    os.remove(tally_output_dir / 'cross_dmp_Pandas_df.pickle.xz')
    os.remove(tally_output_dir / 'cross_bin_dmp_namedtuple_list.pickle.xz')
    os.remove(tally_output_dir / 'cross_bin_dmp_Pandas_df.pickle.xz')
    x = PHITS_tools.merge_dump_file_pickles([tally_output_dir / 'cross_dmp.out', tally_output_dir / 'cross_bin_dmp.out'],
                                            merged_dump_base_filepath=tally_output_dir/'merged_dump',
                                            delete_pre_merge_pickles=False, compress_pickles_with_lzma=True)
    assert x  # function returns True if the merge succeeds 
    


@pytest.mark.slow
@pytest.mark.integration
def test_tyield_chart_options():
    '''
    WARNING
    For this test to work at all, you need to modify and rerun in PHITS the example calculations located at:
    C:\phits\sample\tally\t-yield\

    Then, follow these steps:
       1. Open `t-yield_reg.inp`
       2. In the "[Parameters]" section, change `maxcas = 10` to `maxcas = 1000` (or higher)
       3. Scroll down to the "[ T - Y i e l d ]" tally at the very bottom of the file.
       4. Copy and paste the [T-Yield] tally.
       5. In the new duplicate tally, change:
          a. `file = yield_reg.out` to `file = yield_reg_charge.out`
          b. `axis = chart` to `axis = charge`
       6. Rerun `t-yield_reg.inp` in PHITS

    Then, the tests here should work just fine.
    The run needs better statistics to produce a greater variety of nuclides to trigger some of the special
    chart plotting options.
    '''
    tally_output_dir = phits_sample_dir / 'tally' / 't-yield'
    tally_output_file = tally_output_dir / 'yield_reg_charge.out'
    if not (tally_output_file).exists():
        print('Please follow the instructions in the `test_tyield_chart_options()` docstring to run this test.')
        pytest.skip("Missing required files. Please follow the instructions in the `test_tyield_chart_options()` docstring to run this test.")
        # pytest.fail('message', pytrace=False) is an option too.
    tod = PHITS_tools.parse_tally_output_file(tally_output_file, make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=True, include_phitsout_in_metadata=False,
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                              autoplot_tally_output=True
                                              )
    tally_output_file = tally_output_dir / 'yield_reg.out'
    tod = PHITS_tools.parse_tally_output_file(tally_output_file, make_PandasDF=True,
                                              calculate_absolute_errors=True,
                                              save_output_pickle=True, include_phitsout_in_metadata=False,
                                              prefer_reading_existing_pickle=False, compress_pickle_with_lzma=True,
                                              autoplot_tally_output=True
                                              )

@pytest.mark.slow
@pytest.mark.integration
def test_2dtype_and_tcross_options():
    '''
    For 2d table outputs, the 2d-type = 4 and 5 options have formatting a bit different from the others
    and aren't present for testing in the default sample/recommendation data.
    
    WARNING
    For this test to work at all, you need to modify and rerun in PHITS the example calculations located at:
    C:\phits\sample\tally\t-cross\

    Then, follow these steps for `t-cross_r-z.inp`:
       1. Open `t-cross_r-z.inp` and scroll down to the "[ T - C r o s s ]" tally at the very bottom of the file.
       2. Copy and paste the [T-Cross] tally.
       3. In the new duplicate tally, change:
          a. `file = cross-r-z.out` to `file = cross-r-z_2dtype4.out`
          b. `nr =   1` to `nr =   5`
          c. (in the following line) `0.0 10.0` to `0.0 2 4 6 8 10.0`
          d. `nz =   1` to `ny =   10`
          e. `ne =   50` to `ne =   2`
          f. `axis =  eng` to `axis =  rz`
       4. In the new duplicate tally, add a line with `   enclos = 1`
       5. In the new duplicate tally, add a line with `  2d-type = 4`
       7. Rerun `t-cross_r-z.inp` in PHITS
    
    And then follow these steps for `t-cross_xyz.inp`:
       1. Open `t-cross_xyz.inp` and scroll down to the "[ T - C r o s s ]" tally at the very bottom of the file.
       2. Copy and paste the [T-Cross] tally.
       3. In the new duplicate tally, change:
          a. `file = cross-xyz.out` to `file = cross-xyz_2dtype5.out`
          b. `nx =   1` to `nx =   10`
          c. `ny =   1` to `ny =   10`
          d. `ne =   50` to `ne =   2`
          e. `axis =  eng` to `axis =  xy`
       4. In the new duplicate tally, add a line with `  2d-type = 5`
       5. Rerun `t-cross_xyz.inp` in PHITS

    Then, the tests here should work just fine.
    '''
    tally_output_dir = phits_sample_dir / 'tally' / 't-cross' 
    if not (tally_output_dir/'cross_xyz_2dtype5.out').exists() or not (tally_output_dir/'cross-r-z_2dtype4.out').exists():
        print('Please follow the instructions in the `test_2dtype_and_tcross_options()` docstring to run this test.')
        pytest.skip("Missing required files. Please follow the instructions in the `test_2dtype_and_tcross_options()` docstring to run this test.")
        # pytest.fail('message', pytrace=False) is an option too.
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
    assert x is not None
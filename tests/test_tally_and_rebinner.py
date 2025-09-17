import pytest 
from PHITS_tools import tally_data_indices, tally, rebinner
import numpy as np

@pytest.mark.unit
def test_tally_data_indices():
    tally_metadata = {'reg_groups': ['1', '2', '16', '50', '51', '99'], 
                      'part_groups': ['all', 'neutron', 'proton', '-(neutron proton)']
                      }
    assert tally_data_indices(default_to_all=False, ir=2, ie=":", ip="all", ierr=None) == (2,0,0,slice(None),0,0,0,slice(None),0,slice(None))
    assert tally_data_indices(default_to_all=False, tally_metadata=tally_metadata, reg=16, ie=":", ip=":", ierr=":") == (2,0,0,slice(None),0,0,0,slice(None),0,slice(None))
    assert tally_data_indices(ireg=2, ie=":", ip=":", ierr=":") == (2,slice(None),slice(None),slice(None),slice(None),slice(None),slice(None),slice(None),slice(None),slice(None))
    assert tally_data_indices(default_to_all=False, tally_metadata=tally_metadata, reg=[1,2,16], ie=":", part="proton", ierr=":") == ([0,1,2],0,0,slice(None),0,0,0,2,0,slice(None))

    # Test different formats for specifying slices
    # np.s_ slice form
    idx = tally_data_indices(ie=np.s_[:10:2])
    assert isinstance(idx[3], slice) and (idx[3].start, idx[3].stop, idx[3].step) == (None, 10, 2)
    # np.s_ integer-sequence form
    idx = tally_data_indices(ip=np.s_[[0, 2, 5]])
    assert idx[7] == [0, 2, 5]
    # boolean mask passthrough
    mask = [True, False, True, False]
    idx = tally_data_indices(ip=mask)
    assert idx[7] is mask
    # negative index and reverse slice
    idx = tally_data_indices(ir=-1, ie=slice(None, None, -1))
    assert idx[0] == -1 and isinstance(idx[3], slice) and idx[3].step == -1

    # Test with synthetic tally_data array to ensure equivalence with old approach
    shape = (6, 1, 1, 5, 1, 1, 1, 4, 1, 3)
    idx = np.indices(shape) # Unique per-index value for easy equality checks
    flat = np.ravel_multi_index(tuple(idx), shape).astype(np.int64)
    tally_data = flat  # deterministic, unique per coordinate
    # full spectrum in region index 2 for all particles, with errors
    new_idx = tally_data_indices(default_to_all=False, ir=2, ie=":", ip=":", ierr=":")
    assert np.array_equal(
        tally_data[2, 0, 0, :, 0, 0, 0, :, 0, :],
        tally_data[new_idx]
    )
    # region/particle by VALUE using metadata (region 16 -> ir=2, 'neutron' -> ip=1), single bin checks
    new_idx = tally_data_indices(default_to_all=False, tally_metadata=tally_metadata, reg=16, part='neutron', ie=2, ierr=0)
    assert np.array_equal(
        tally_data[2, 0, 0, 2, 0, 0, 0, 1, 0, 0],
        tally_data[new_idx]
    )
    # np.s_ single-axis: particles [0,2]
    new_idx = tally_data_indices(ip=np.s_[[0, 2]])
    assert np.array_equal(
        tally_data[:, :, :, :, :, :, :, [0, 2], :, :],
        tally_data[new_idx]
    )
    # reverse energy slice
    new_idx = tally_data_indices(ie=slice(None, None, -1))
    assert np.array_equal(
        tally_data[:, :, :, ::-1, :, :, :, :, :, :],
        tally_data[new_idx]
    )
    # boolean mask on particle axis
    mask = np.array([True, False, True, False])
    new_idx = tally_data_indices(ip=mask)
    assert np.array_equal(
        tally_data[:, :, :, :, :, :, :, mask, :, :],
        tally_data[new_idx]
    )

    # Test programmed error messages
    # unknown axis
    with pytest.raises(KeyError):
        tally_data_indices(thisisnotvalidinput=1)
    # duplicate axis via canonical + alias
    with pytest.raises(ValueError):
        tally_data_indices(ir=1, ireg=2)
    # special alias without metadata
    with pytest.raises(ValueError):
        tally_data_indices(reg=16)
    # missing required metadata key
    tm_missing = {'part_groups': ['all', 'neutron', 'proton']}  # no 'reg_groups'
    with pytest.raises(ValueError):
        tally_data_indices(tally_metadata=tm_missing, reg=16)
    # metadata key present but None
    tm_none = {'reg_groups': None, 'part_groups': ['all', 'neutron', 'proton']}
    with pytest.raises(ValueError):
        tally_data_indices(tally_metadata=tm_none, reg=16)
    # value not found in tally_metadata['reg_groups']
    with pytest.raises(ValueError):
        tally_data_indices(tally_metadata=tally_metadata, reg=12345)
    # value not found in tally_metadata['part_groups']
    with pytest.raises(ValueError):
        tally_data_indices(tally_metadata=tally_metadata, part='muon')
    # Unsupported Ellipsis
    with pytest.raises(TypeError):
        tally_data_indices(ir=Ellipsis)


@pytest.mark.unit
def test_tally():
    data = [1, 4, 4, 7, 9]
    
    bin_edges = [0, 10]
    result = tally(data, bin_edges=bin_edges)
    assert result[0] == [5]
    assert all(result[1] == bin_edges)
    
    bin_edges = [0, 5, 10]
    result = tally(data, bin_edges=bin_edges)
    assert all(result[0] == [3, 2])
    assert all(result[1] == bin_edges)

    result = tally(data, min_bin_left_edge=0, max_bin_right_edge=10, nbins=2)
    assert all(result[0] == [3, 2])
    assert all(result[1] == bin_edges)

    result = tally(data, min_bin_left_edge=0, max_bin_right_edge=10, bin_width=5)
    assert all(result[0] == [3, 2])
    assert all(result[1] == bin_edges)
    
    bin_edges = [0, 4, 10]
    result = tally(data, bin_edges=bin_edges)
    assert all(result[0] == [1, 4])
    result = tally(data, bin_edges=bin_edges, return_event_indices_histogram=True)
    assert all(result[0] == [1, 4])
    assert result[2] == [[0], [1, 2, 3, 4]]
    result = tally(data, bin_edges=bin_edges, return_uncertainties=True)
    assert all(result[2] == [1, 2])
    result = tally(data, bin_edges=bin_edges, return_uncertainties=True, return_event_indices_histogram=True)
    assert all(result[0] == [1, 4])
    assert all(result[1] == bin_edges)
    assert all(result[2] == [1, 2])
    assert result[3] == [[0], [1, 2, 3, 4]]

    bin_edges = [2, 5, 8]
    result = tally(data, bin_edges=bin_edges, place_overflow_at_ends=True)
    assert all(result[0] == [3, 2])
    result = tally(data, bin_edges=bin_edges, place_overflow_at_ends=False)
    assert all(result[0] == [2, 1])
    result = tally(data, bin_edges=bin_edges, place_overflow_at_ends=True, return_event_indices_histogram=True)
    assert all(result[0] == [3, 2])
    assert result[2] == [[0, 1, 2], [3, 4]]
    result = tally(data, bin_edges=bin_edges, place_overflow_at_ends=False, return_event_indices_histogram=True)
    assert all(result[0] == [2, 1])
    assert result[2] == [[1, 2], [3]]

    bin_edges = [0, 5, 10]
    result = tally(data, bin_edges=bin_edges, divide_by_bin_width=True, return_uncertainties=True)
    assert all(result[0] == [3/5, 2/5])
    assert all(result[2] == [np.sqrt(3)/5, np.sqrt(2)/5])
    result = tally(data, bin_edges=bin_edges, normalization='unity-sum', return_uncertainties=True)
    assert all(result[0] == [3/5, 2/5])
    assert all(result[2] == [np.sqrt(3)/5, np.sqrt(2)/5])
    result = tally(data, bin_edges=bin_edges, normalization='unity-max-val', return_uncertainties=True)
    assert all(result[0] == [3/3, 2/3])
    assert all(result[2] == [np.sqrt(3)/3, np.sqrt(2)/3])
    result = tally(data, bin_edges=bin_edges, scaling_factor=2, return_uncertainties=True)
    assert all(result[0] == [3*2, 2*2])
    assert all(result[2] == [np.sqrt(3)*2, np.sqrt(2)*2])
    result = tally(data, bin_edges=bin_edges, divide_by_bin_width=True, normalization='unity-max-val', scaling_factor=2, return_uncertainties=True)
    bin_edges = np.array(bin_edges)
    expected_result = [np.array([3, 2]), np.array(bin_edges), np.sqrt(np.array([3, 2]))]
    expected_result[2] = expected_result[2]/(bin_edges[1:]-bin_edges[:-1])
    expected_result[2] = expected_result[2]/np.max(expected_result[0])
    expected_result[2] = expected_result[2]*2
    expected_result[0] = expected_result[0]/(bin_edges[1:]-bin_edges[:-1])
    expected_result[0] = expected_result[0]/np.max(expected_result[0])
    expected_result[0] = expected_result[0]*2
    assert all(result[0] == expected_result[0])
    assert all(result[2] == expected_result[2])

@pytest.mark.unit
def test_rebinner():
    input_xbins = [0, 2, 4, 6, 8, 10]
    input_ybins = [ 1, 2, 4, 8, 16]

    output_xbins = [0, 10]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [31])
    output_xbins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [0.5, 0.5, 1, 1, 2, 2, 4, 4, 8, 8])
    output_xbins = [0, 8, 10]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [15, 16])
    output_xbins = [2, 6]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [6])
    output_xbins = [1, 5, 7]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [4.5, 6])
    output_xbins = [-1, 5, 11]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [5, 26])
    output_xbins = [8, 8.5, 9, 10]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [4, 4, 8])
    output_xbins = [8, 8.5, 9, 10, 20, 30, 40]
    assert all(rebinner(output_xbins, input_xbins, input_ybins) == [4, 4, 8, 0, 0, 0])
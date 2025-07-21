import pytest 
from PHITS_tools import tally, rebinner
import numpy as np

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


def test_rebinner():
    input_ybins = []
    input_xbins = []
    
    output_xbins = []
    assert rebinner(output_xbins, input_xbins, input_ybins) == []
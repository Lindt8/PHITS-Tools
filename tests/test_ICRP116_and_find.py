import pytest 
from pytest import approx
from PHITS_tools import find, ICRP116_effective_dose_coeff

@pytest.mark.parametrize("test_list,test_target,expected", [
    ([0, 1, 2], 2, 2),
    ([0, 1, 2], 1, 1),
    ([0, 1, 2, 2, 2], 2, 2),
    ([0, 1, 2], 9, None),
    ([0, 1, 21, 12, 2, 3, 3, 3, 2], 2, 4),
    (['egg', 'bacon', 'cheese', 'egg', 'bacon', 'cheese'], 'bacon', 1),
    (['egg', 'bacon', 'cheese', 'egg', 'bacon', 'cheese'], 'biscuit', None),
])
def test_find(test_target, test_list, expected):
    assert find(test_target, test_list) == expected


def test_ICRP116_effective_dose_coeff():
    assert ICRP116_effective_dose_coeff(E=1.0, particle='photon', geometry='AP') == 4.49
    assert ICRP116_effective_dose_coeff(E=1.0, particle='iron') == None
    assert ICRP116_effective_dose_coeff(E=1.0, geometry='something') == None
    assert ICRP116_effective_dose_coeff(E=1.0, particle='proton', geometry='H*(10)') == None
    assert ICRP116_effective_dose_coeff(E=1.0, particle='negmuon', geometry='ROT') == None
    assert ICRP116_effective_dose_coeff(E=2.5, particle='negmuon', geometry='AP', interp_scale='linear', 
                                        interp_type='linear') == approx(186)
    assert ICRP116_effective_dose_coeff(E=2.5, particle='negmuon', geometry='AP', interp_scale='log', 
                                        interp_type='linear') == approx(186.190711)
    assert ICRP116_effective_dose_coeff(E=2.5, particle='negmuon', geometry='AP', interp_scale='linear', 
                                        interp_type='cubic') == approx(186.46186)
    assert ICRP116_effective_dose_coeff(E=2.5, particle='negmuon', geometry='AP', interp_scale='log', 
                                        interp_type='cubic') == approx(186.05657)
    assert ICRP116_effective_dose_coeff(E=0.5, particle='proton', geometry='AP', interp_scale='log',
                                        interp_type='cubic', extrapolation_on=False) == 0
    assert ICRP116_effective_dose_coeff(E=0.5, particle='proton', geometry='AP', interp_scale='linear',
                                        interp_type='linear', extrapolation_on=True) == approx(2.73)
    assert ICRP116_effective_dose_coeff(E=0.5, particle='proton', geometry='AP', interp_scale='log',
                                        interp_type='cubic', extrapolation_on=True) == approx(2.706809)
    assert ICRP116_effective_dose_coeff(E=20000.0, particle='proton', geometry='AP', interp_scale='log',
                                        interp_type='cubic', extrapolation_on=False) == 1.41E+03
    assert ICRP116_effective_dose_coeff(E=20000.0, particle='proton', geometry='AP', interp_scale='linear',
                                        interp_type='linear', extrapolation_on=True) == approx(1210.0)
    assert ICRP116_effective_dose_coeff(E=20000.0, particle='proton', geometry='AP', interp_scale='linear',
                                        interp_type='cubic', extrapolation_on=True) == approx(15874.11987)
    assert ICRP116_effective_dose_coeff(E=20000.0, particle='proton', geometry='AP', interp_scale='log',
                                        interp_type='cubic', extrapolation_on=True) == approx(2584.82498)
    assert ICRP116_effective_dose_coeff(E=0.0000001, particle='photon', geometry='AP') == 0
    




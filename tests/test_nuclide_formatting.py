import pytest 
from PHITS_tools import element_Z_to_symbol, element_symbol_to_Z, kfcode_to_common_name
from PHITS_tools import ZZZAAAM_to_nuclide_plain_str, nuclide_plain_str_to_ZZZAAAM, nuclide_plain_str_to_latex_str
from PHITS_tools import nuclide_Z_and_A_to_latex_str, element_Z_or_symbol_to_name, element_Z_or_symbol_to_mass
from PHITS_tools import Element_Z_to_Sym, Element_Sym_to_Z

@pytest.mark.unit
def test_element_Z_to_symbol():
    assert element_Z_to_symbol(1) == 'H'
    assert element_Z_to_symbol(92) == 'U'
    assert element_Z_to_symbol(7) == 'N'
    assert element_Z_to_symbol(52) == 'Te'
    assert element_Z_to_symbol(45) == 'Rh'
    assert element_Z_to_symbol(118) == 'Og'
    assert element_Z_to_symbol(0) == 'n'
    assert element_Z_to_symbol(-1) is None
    assert element_Z_to_symbol(119) is None

@pytest.mark.unit
def test_element_symbol_to_Z():
    assert element_symbol_to_Z('H') == 1
    assert element_symbol_to_Z('U') == 92
    assert element_symbol_to_Z('N') == 7
    assert element_symbol_to_Z('Te') == 52
    assert element_symbol_to_Z('Rh') == 45
    assert element_symbol_to_Z('Og') == 118
    assert element_symbol_to_Z('XX') == 0
    assert element_symbol_to_Z('test') == -1
    assert element_symbol_to_Z('AA') == -1
    assert element_symbol_to_Z('oG') == 118

@pytest.mark.unit
def test_kfcode_to_common_name():
    assert kfcode_to_common_name(2112) == 'neutron'
    assert kfcode_to_common_name(2212) == 'proton'
    assert kfcode_to_common_name(-13) == 'muon+'
    assert kfcode_to_common_name(8000016) == 'O-16'
    assert kfcode_to_common_name(118000294) == 'Og-294'
    assert kfcode_to_common_name(1000001) == 'H-1'
    assert kfcode_to_common_name(1000000) == '1000000'
    assert kfcode_to_common_name(123456) == '123456'

@pytest.mark.unit
def test_ZZZAAAM_to_nuclide_plain_str():
    assert ZZZAAAM_to_nuclide_plain_str(80160) == 'O-16'
    assert ZZZAAAM_to_nuclide_plain_str(8016, ZZZAAA=True) == 'O-16'
    assert ZZZAAAM_to_nuclide_plain_str(80160, include_Z=True) == '8-O-16'
    assert ZZZAAAM_to_nuclide_plain_str(430991) == 'Tc-99m1'
    assert ZZZAAAM_to_nuclide_plain_str(430991, include_Z=True) == '43-Tc-99m1'

@pytest.mark.unit
def test_nuclide_plain_str_to_ZZZAAAM():
    assert nuclide_plain_str_to_ZZZAAAM('O-16') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('O-nat') == 80000
    assert nuclide_plain_str_to_ZZZAAAM('O 16') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('O_16') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('O16') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('16O') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('16-O') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('natO') == 80000
    assert nuclide_plain_str_to_ZZZAAAM('O-16g') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('O-16m') == 80161
    assert nuclide_plain_str_to_ZZZAAAM('O-16m1') == 80161
    assert nuclide_plain_str_to_ZZZAAAM('O-16n') == 80162
    assert nuclide_plain_str_to_ZZZAAAM('O-16m2') == 80162
    assert nuclide_plain_str_to_ZZZAAAM('O-16o') == 80163
    assert nuclide_plain_str_to_ZZZAAAM('O-16p') == 80164
    assert nuclide_plain_str_to_ZZZAAAM('O-16q') == 80165
    assert nuclide_plain_str_to_ZZZAAAM('O-16m5') == 80165
    assert nuclide_plain_str_to_ZZZAAAM('O-16m9') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('O-16mx') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('16m1-O') == 80161
    assert nuclide_plain_str_to_ZZZAAAM('16m1O') == 80161
    assert nuclide_plain_str_to_ZZZAAAM('O-016') == 80160
    assert nuclide_plain_str_to_ZZZAAAM(' O - 16 ') == 80160
    assert nuclide_plain_str_to_ZZZAAAM('O') == 80000
    assert nuclide_plain_str_to_ZZZAAAM('n') == 10
    assert nuclide_plain_str_to_ZZZAAAM('p') == 10010
    assert nuclide_plain_str_to_ZZZAAAM('d') == 10020
    assert nuclide_plain_str_to_ZZZAAAM('t') == 10030
    assert nuclide_plain_str_to_ZZZAAAM('Oo-16') == None

@pytest.mark.unit
def test_nuclide_plain_str_to_latex_str():
    assert nuclide_plain_str_to_latex_str('O-16') == r'$^{16}$O'
    assert nuclide_plain_str_to_latex_str('O') == r'O'
    assert nuclide_plain_str_to_latex_str('O-nat') == r'$^{nat}$O'
    assert nuclide_plain_str_to_latex_str('O-16m') == r'$^{16m}$O'
    assert nuclide_plain_str_to_latex_str('O-16m1') == r'$^{16m1}$O'
    assert nuclide_plain_str_to_latex_str('O-16meta') == r'$^{16meta}$O'
    assert nuclide_plain_str_to_latex_str('O-16meta1') == r'$^{16meta1}$O'
    assert nuclide_plain_str_to_latex_str('O-52816') == r'$^{52816}$O'
    assert nuclide_plain_str_to_latex_str(' O - 16 ') == r'$^{16}$O'
    assert nuclide_plain_str_to_latex_str('O_16_') == r'$^{16}$O'
    assert nuclide_plain_str_to_latex_str('O-016') == r'$^{016}$O'
    assert nuclide_plain_str_to_latex_str('O-16', include_Z=True) == r'$^{16}_{8}$O'
    assert nuclide_plain_str_to_latex_str('16O') == r'$^{16}$O'
    assert nuclide_plain_str_to_latex_str('16-O') == r'$^{16}$O'
    assert nuclide_plain_str_to_latex_str('16m-O') == r'$^{16m}$O'
    assert nuclide_plain_str_to_latex_str('16m1-O') == r'$^{16m1}$O'
    assert nuclide_plain_str_to_latex_str('n') == r'$^{1}$n'
    assert nuclide_plain_str_to_latex_str('n', include_Z=True) == r'$^{1}_{0}$n'
    assert nuclide_plain_str_to_latex_str('p') == r'$^{1}$p'
    assert nuclide_plain_str_to_latex_str('p', include_Z=True) == r'$^{1}_{1}$p'
    assert nuclide_plain_str_to_latex_str('d', include_Z=True) == r'$^{2}_{1}$d'
    assert nuclide_plain_str_to_latex_str('t', include_Z=True) == r'$^{3}_{1}$t'

@pytest.mark.unit
def test_nuclide_Z_and_A_to_latex_str():
    assert nuclide_Z_and_A_to_latex_str(8, 16) == r'$^{16}$O'
    assert nuclide_Z_and_A_to_latex_str(8, 'nat') == r'$^{nat}$O'
    assert nuclide_Z_and_A_to_latex_str('O', 'nat') == r'$^{nat}$O'
    assert nuclide_Z_and_A_to_latex_str(8, 16, m='m') == r'$^{16m}$O'
    assert nuclide_Z_and_A_to_latex_str(8, 16, m=1) == r'$^{16m1}$O'
    assert nuclide_Z_and_A_to_latex_str(8, 16, m=1.0) == r'$^{16m1}$O'
    assert nuclide_Z_and_A_to_latex_str(8, 16, m='meta') == r'$^{16meta}$O'
    assert nuclide_Z_and_A_to_latex_str(8, 16, m='meta1') == r'$^{16meta1}$O'
    assert nuclide_Z_and_A_to_latex_str('O', 52816) == r'$^{52816}$O'
    assert nuclide_Z_and_A_to_latex_str(0, 1) == r'$^{1}$n'

@pytest.mark.unit
def test_element_Z_or_symbol_to_name():
    assert element_Z_or_symbol_to_name(0) == 'neutron'
    assert element_Z_or_symbol_to_name(1) == 'Hydrogen'
    assert element_Z_or_symbol_to_name('H') == 'Hydrogen'
    assert element_Z_or_symbol_to_name(8) == 'Oxygen'
    assert element_Z_or_symbol_to_name('O') == 'Oxygen'
    assert element_Z_or_symbol_to_name(117) == 'Tennessine'
    assert element_Z_or_symbol_to_name('Ts') == 'Tennessine'
    assert element_Z_or_symbol_to_name(118) == 'Oganesson'
    assert element_Z_or_symbol_to_name('Og') == 'Oganesson'

@pytest.mark.unit
def test_element_Z_or_symbol_to_mass():
    assert element_Z_or_symbol_to_mass(0) == 1.008664
    assert element_Z_or_symbol_to_mass(1) == 1.008
    assert element_Z_or_symbol_to_mass('H') == 1.008
    assert element_Z_or_symbol_to_mass(8) == 15.999
    assert element_Z_or_symbol_to_mass('O') == 15.999
    assert element_Z_or_symbol_to_mass(117) == 293
    assert element_Z_or_symbol_to_mass('Ts') == 293
    assert element_Z_or_symbol_to_mass(118) == 294
    assert element_Z_or_symbol_to_mass('Og') == 294

@pytest.mark.filterwarnings("ignore::FutureWarning")
@pytest.mark.unit
def test_Element_Z_to_Sym():
    assert Element_Z_to_Sym(1) == 'H'
    assert Element_Z_to_Sym(92) == 'U'
    assert Element_Z_to_Sym(7) == 'N'
    assert Element_Z_to_Sym(52) == 'Te'
    assert Element_Z_to_Sym(45) == 'Rh'
    assert Element_Z_to_Sym(118) == 'Og'
    assert Element_Z_to_Sym(0) == 'n'
    assert Element_Z_to_Sym(-1) is None
    assert Element_Z_to_Sym(119) is None

@pytest.mark.filterwarnings("ignore::FutureWarning")
@pytest.mark.unit
def test_Element_Sym_to_Z():
    assert Element_Sym_to_Z('H') == 1
    assert Element_Sym_to_Z('U') == 92
    assert Element_Sym_to_Z('N') == 7
    assert Element_Sym_to_Z('Te') == 52
    assert Element_Sym_to_Z('Rh') == 45
    assert Element_Sym_to_Z('Og') == 118
    assert Element_Sym_to_Z('XX') == 0
    assert Element_Sym_to_Z('test') == -1
    assert Element_Sym_to_Z('AA') == -1
    assert Element_Sym_to_Z('oG') == 118
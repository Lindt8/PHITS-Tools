import pytest 
from PHITS_tools import is_number, split_str_of_equalities, parse_group_string, extract_data_from_header_line, data_row_to_num_list

@pytest.mark.unit
@pytest.mark.parametrize("test_item,expected", [
    (1, True),
    ('1', True),
    ('1.', True),
    ('1.0', True),
    ('1.0E-8', True),
    ('-1.0E-8', True),
    ('1.0E+8', True),
    ('1.0D+8', False),
    ('1.0+8', False),
    ('1.E+8', True),
    ('f1.0E-8', False),
    ('2*5', False),
    ('pancakes', False),
])
def test_is_number(test_item,expected):
    assert is_number(test_item) == expected

@pytest.mark.unit
def test_split_str_of_equalities():
    assert split_str_of_equalities('x = 1') == ['x = 1']
    assert split_str_of_equalities('x = 1 y = 2') == ['x = 1', 'y = 2']
    assert split_str_of_equalities('nx = 1 ny = 2') == ['nx = 1', 'ny = 2']
    assert split_str_of_equalities('nx= 1 ny= 2') == ['nx = 1', 'ny = 2']
    assert split_str_of_equalities('nx=1 ny=2') == ['nx = 1', 'ny = 2']
    assert split_str_of_equalities('nx = 1, ny = 2') == ['nx = 1', 'ny = 2']
    assert split_str_of_equalities('# no. =*** nx=') == []
    assert split_str_of_equalities('  no. =*** nx=7') == ['no. = 999999999', 'nx = 7']
    assert split_str_of_equalities('(nx, ny = 1, 2)') == ['nx = 1', 'ny = 2']
    assert split_str_of_equalities("'no. =  1,  part = proton,  ie =  1'") == ['no. = 1', 'part = proton', 'ie = 1']

@pytest.mark.unit
def test_parse_group_string():
    assert parse_group_string('1 2 3 4') == ['1', '2', '3', '4']
    assert parse_group_string('proton neutron photon') == ['proton', 'neutron', 'photon']
    assert parse_group_string('( 1 4 )') == ['(1 4)']
    assert parse_group_string('( 1   4 )') == ['(1 4)']
    assert parse_group_string('( 1 4 ) 9 20') == ['(1 4)', '9', '20']
    assert parse_group_string('( 1 4 ) 9 -20') == ['(1 4)', '9', '-20']
    assert parse_group_string('1 2 ( 3 4 ) all') == ['1', '2', '(3 4)', 'all']
    assert parse_group_string('{ 1 - 4 } ( 1 4 )') == ['1', '2', '3', '4', '(1 4)']

@pytest.mark.unit
def test_extract_data_from_header_line():
    result = extract_data_from_header_line('     unit =    3            # unit is [1/source] : only for output=deposit')
    assert result == ('unit', 3)
    result = extract_data_from_header_line('    rdel =   2.500000      # mesh width of r-mesh points')
    assert result == ('rdel', 2.5)
    result = extract_data_from_header_line('   output = deposit     ')
    assert result == ('output', 'deposit')

@pytest.mark.unit
def test_data_row_to_num_list():
    line = ''
    assert data_row_to_num_list(line) == []
    line = '  0.000E+00  0.000E+00  1.000E-02  2.000E-02  0.000E+00  0.000E+00  0.000E+00  0.000E+00  9.900E-01  9.800E-01'
    assert data_row_to_num_list(line) == [0, 0, .01, .02, 0, 0, 0, 0, .99, .98]
    line = '   1.2589E-02   1.5849E-02   2.1621E-07  0.0159   1.7294E-11  1.0000'
    assert data_row_to_num_list(line) == [1.2589E-02, 1.5849E-02, 2.1621E-07, 0.0159, 1.7294E-11, 1.0]
    line = '   1.2589E-02   1.5849E-02   2.1621E-07990.0159   1.7294E-11551.0000'
    assert data_row_to_num_list(line) == [1.2589E-02, 1.5849E-02, 2.1621E-07, 990.0159, 1.7294E-11, 551.0]
    line = '   1.2589E-02   1.5849E-02   2.1621E-07********   1.7294E-11********'
    assert data_row_to_num_list(line) == [1.2589E-02, 1.5849E-02, 2.1621E-07, 999.9999, 1.7294E-11, 999.9999]
import pytest 
from PHITS_tools import is_number, split_str_of_equalities, parse_group_string, extract_data_from_header_line, data_row_to_num_list

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
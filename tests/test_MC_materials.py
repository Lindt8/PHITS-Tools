import pytest 
from PHITS_tools import fetch_MC_material

@pytest.mark.unit
def test_fetch_MC_material():
    db = 'Compiled_MC_materials'
    assert fetch_MC_material() is None
    mat_str = fetch_MC_material(matid=1, database_filename=db)
    assert 'A-150 Tissue-Equivalent Plastic' in mat_str
    mat_str = fetch_MC_material(matid=1, database_filename=db, prefer_user_data_folder=False)
    assert 'A-150 Tissue-Equivalent Plastic' in mat_str
    mat_str = fetch_MC_material(matname='Acetone', database_filename=db)
    assert '2   : Acetone' in mat_str
    mat_str = fetch_MC_material(matname='efauihygaljehfsgiy;lgf', database_filename=db)
    assert mat_str is None
    mat_str = fetch_MC_material(matname='A-150', database_filename=db)
    assert 'A-150 Tissue-Equivalent Plastic' in mat_str
    mat_str = fetch_MC_material(matname='Aluminum', database_filename=db)
    assert '6   : Aluminum' in mat_str
    mat_str = fetch_MC_material(matname='Aluminum, alloy', database_filename=db)
    assert '8   : Aluminum, alloy 2024-O' in mat_str
    mat_str = fetch_MC_material(matid=341, database_filename=db)
    assert 'Uranium, Depleted, Typical' in mat_str
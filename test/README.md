# Integration and Functional testing

This directory contains tests that: 

1. Require external files not distributed with PHITS Tools (more info below)
2. Test end-to-end workflows

Owing to the nature of these tests, it is difficult to have a "right answer" to compare outputs against.  Instead, these tests exist to verify if the code runs without error and, where reasonable, checks if the output has properties/formatting as expected.  Furthermore, unlike the unit tests, most of these are varying degrees of time-consuming.

## Testing instructions

Testing was developed with [`pytest`](https://pypi.org/project/pytest/) and [`pytest-cov`](https://pypi.org/project/pytest-cov/) (for coverage testing).  Configuration details can be found in [`pyproject.toml`](pyproject.toml) and common test execution commands in the [`Makefile`](Makefile).

Owing to PHITS being export controlled and requring a state-issued license from the Japan Atomic Energy Agency or the OECD Nuclear Energy Agency (NEA), no files distributed with PHITS are redistributed here.  That said, if you already have a PHITS installation, you will find an extensive set of sample PHITS inputs and outputs provided within the `phits/sample/` and `phits/recommendation/` directories and their nested subdirectories, totalling approximately 300 test output files to be parsed by this script.  Also note that the `phits/recommendation/` directory, complete with (approx. 50) PHITS output files, is publicly available for download on the PHITS website at the bottom of [this page under "Recommendation Settings"](https://phits.jaea.go.jp/rireki-manuale.html) ([direct download of ZIP file here](https://phits.jaea.go.jp/lec/recommendation.zip)).

### Mass functional testing

The [`test_overall_functionality.py`](test/test_overall_functionality.py) script tests the correct functioning of the `PHITS Tools` module in parsing a variety of PHITS output files.  It uses these distributed sample outputs as its testing suite; all you must do is make sure the `path_to_phits_base_folder` variable on line 6 correctly points to your PHITS installation's base folder (by default, `C:\phits\`). When the script is ran, `PHITS Tools` will attempt parsing all of these outputs and print its test results to the terminal and to `test.log`, saved to the current working directory.

### Options testing

The [`test_options_in_processing.py`](test/test_options_in_processing.py) script, rather than surveying many PHITS outputs all using the same function options as in [`test_overall_functionality.py`](test/test_overall_functionality.py), focuses on testing a small subset of the PHITS outputs but testing a variety of options/settings combinations not covered by [`test_overall_functionality.py`](test/test_overall_functionality.py).  Similarly though, you need to make sure the `path_to_phits_base_folder` variable on line 6 correctly points to your PHITS installation's base folder (by default, `C:\phits\`).  

For some of these tests to pass, you will need to run some of the PHITS/DCHAIN inputs distributed with PHITS whose outputs are not automatically included with the distribution.  This is explicitly detailed in the docstrings of the relevant functions.

## Expected coverage

The testing here was performed on the files distributed with PHITS version 3.35.

After executing `make test-all` to run all the tests in this directory and in [`tests/`](tests/), in the produced `htmlcov-full/function_index.html` coverage report expect something around 70% total coverage over all of PHITS Tools if you have `test_input_mode_parsing = True` and `test_autoplotting = True` set in [`test_overall_functionality.py`](test/test_overall_functionality.py), less if these are disabled.
# Integration and Functional testing

This directory contains tests that: 

1. Require external files not distributed with PHITS Tools (more info below)
2. Test end-to-end workflows

Owing to the nature of these tests, it is difficult to have a "right answer" to compare outputs against.  Instead, these tests exist to verify if the code runs without error and, where reasonable, checks if the output has properties/formatting as expected.  Furthermore, unlike the unit tests, most of these are varying degrees of time-consuming.

## Testing instructions

Testing was developed with [`pytest`](https://pypi.org/project/pytest/) and [`pytest-cov`](https://pypi.org/project/pytest-cov/) (for coverage testing).  Configuration details can be found in [`pyproject.toml`](../pyproject.toml) and common test execution commands in the [`Makefile`](../Makefile).

Owing to PHITS being export controlled and requring a state-issued license from the Japan Atomic Energy Agency or the OECD Nuclear Energy Agency (NEA), no files distributed with PHITS are redistributed here.  That said, if you already have a PHITS installation, you will find an extensive set of sample PHITS inputs and outputs provided within the `phits/sample/` and `phits/recommendation/` directories and their nested subdirectories, totalling approximately 300 test output files to be parsed by this script.  Also note that the `phits/recommendation/` directory, complete with (approx. 50) PHITS output files, is publicly available for download on the PHITS website at the bottom of [this page under "Recommendation Settings"](https://phits.jaea.go.jp/rireki-manuale.html) ([direct download of ZIP file here](https://phits.jaea.go.jp/lec/recommendation.zip)).

The testing scripts in this directory use these distributed sample and recommendation outputs as their testing suite. By default, `conftest.py` checks your system's PATH variable to find the path to the `phits/` directory containing these `sample` and `recommendation` directories to be parsed in testing.  Failing finding `phits` in PATH, the code will fall back to the PHITS default install location `C:\phits\`.  If you wish to perform testing on a copy of these directories outside of the main `phits/` directory, make sure in `conftest.py` to change lines 9 and 10 to `use_default_phits_dist_files_for_testing = False` and for `path_to_base_phits_test_dir` to point to your desired target testing path.

### Mass functional testing

The [`test_overall_functionality.py`](test_overall_functionality.py) script tests the correct functioning of the `PHITS Tools` module in parsing a variety of PHITS output files.  When the script is ran, `PHITS Tools` will attempt parsing all of the outputs in `phits/sample/` and `phits/recommendation/` and print its test results to the terminal and to `test_overall_functionality.log`, saved in this directory.

The [`test_input_mode_parsing.py`](test_input_mode_parsing.py) script is very similar to `test_overall_functionality.py` but instead will attempt parsing all of the PHITS _input files_ in `phits/sample/` and `phits/recommendation/` and then use `parse_all_tally_output_in_dir()` in _[INPUT_FILE mode]_ to process all of the outputs produced by each input.  It prints its test results to the terminal and to `test_input_mode_parsing.log`, saved in this directory.

### Options testing

The [`test_options_in_processing.py`](test_options_in_processing.py) script, rather than surveying many PHITS outputs all using the same function options as in [`test_overall_functionality.py`](test_overall_functionality.py), focuses on testing a small subset of the PHITS outputs but testing a variety of options/settings combinations not covered by [`test_overall_functionality.py`](test_overall_functionality.py).  

For some of these tests to pass, you will need to run some of the PHITS/DCHAIN inputs distributed with PHITS whose outputs are not automatically included with the distribution or modify and rerun some PHITS inputs to yield extra outputs for testing.  This is explicitly detailed in the docstrings of the relevant functions (namely, in `test_dump_file_options`, `test_dchain_sample_3_step_dose`, `test_2dtype_and_tcross_options`, and `test_tyield_chart_options`).

## Expected coverage

[![CI Tests](https://github.com/Lindt8/PHITS-Tools/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/Lindt8/PHITS-Tools/actions/workflows/ci-tests.yml "CI Tests")
 ° [![](https://img.shields.io/badge/Unit%20tests%20only-gray) ![Unit Tests](https://codecov.io/gh/Lindt8/PHITS-Tools/branch/feature/improve-testing/graph/badge.svg?flag=ci-unittests&label=Unit%20Tests)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=ci-unittests "Codecov unit tests only") 
 ° [![](https://img.shields.io/badge/Full%20test%20suite-gray) ![Full Suite](https://codecov.io/gh/Lindt8/PHITS-Tools/branch/feature/improve-testing/graph/badge.svg?flag=full-suite&label=Full%20Suite)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=full-suite "Codecov full test suite")
<!--
 ° [![](https://img.shields.io/badge/Unit%20tests%20only-gray) ![Unit Tests](https://codecov.io/gh/Lindt8/PHITS-Tools/graph/badge.svg?flag=ci-unittests&label=Unit%20Tests)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=ci-unittests)
 ° [![](https://img.shields.io/badge/Full%20test%20suite-gray) ![Full Suite](https://codecov.io/gh/Lindt8/PHITS-Tools/graph/badge.svg?flag=full-suite&label=Full%20Suite)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=full-suite)
/-->

The testing here was performed on the files distributed with PHITS version 3.35.  What code coverage you see will be highly dependent on what PHITS output files you have available in the `phits/sample/` and `phits/recommendation/` directories.  With the tested PHITS version here, both of these directories are distributed largely with outputs already generated; though this could change in the future with any efforts to further reduce the PHITS distribution's file size.  

The main exception is that `phits/sample/tally/` is presently only distributed with input files, no output files.  Given that tallies are the main source of diversity in PHITS outputs, it is crucial for testing to provide as many tally outputs to test as possible.  Thus, for the coverage figures reported here, in addition to the output files already distributed by default with PHITS, all of the PHITS inputs in `phits/sample/tally/` were also ran through PHITS, their outputs thus also included in the comprehensive scans conducted by [`test_overall_functionality.py`](test_overall_functionality.py).

After executing `make test-all` to run all the tests in this directory and in [`tests/`](../tests/), in the produced `htmlcov-full/function_index.html` coverage report expect something around 89% total coverage over all of PHITS Tools (with no individual function's coverage beneath 80%) if you:
- have `test_autoplotting = True` set in [`test_overall_functionality.py`](test_overall_functionality.py) and [`test_input_mode_parsing.py`](test_input_mode_parsing.py) (_note that this makes testing consume notably more time_)
- have ran through PHITS all of the inputs in `phits/sample/tally/` whose outputs are not already distributed by default
- have performed the required setup for full use of [`test_options_in_processing.py`](test_options_in_processing.py) by modifying/running extra PHITS simulations as noted in the docstrings (_this test script on its own, fully satisfied, should provide on the order of 65% total coverage_)


The coverage is of course lower if not satisfying all of these conditions.
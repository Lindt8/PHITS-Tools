# Unit Testing

This directory contains unit tests for various functions in PHITS Tools not requiring any externally distributed files (unlike those in [`test/`](test/)).

These tests principally aim to test the standalone functions in PHITS Tools that end-users are likely to utilize themselves, rather than those which are complex internal cogs in output file processing, which generally require real example outputs that have already undergone some form of processing by other functions in PHITS Tools.  (Some of the simpler of these "internal-use only" functions do have unit tests here though.)

Testing was developed with [`pytest`](https://pypi.org/project/pytest/) and [`pytest-cov`](https://pypi.org/project/pytest-cov/) (for coverage testing).  Configuration details can be found in [`pyproject.toml`](pyproject.toml) and common test execution commands in the [`Makefile`](Makefile).

## Expected coverage

After executing `make test-cov` to run all the tests in this directory, in the produced `htmlcov-unit/function_index.html` coverage report expect something around 17% total coverage (over all of PHITS Tools) but 90% or higher coverage individually for all of the functions tested by the unit tests here.
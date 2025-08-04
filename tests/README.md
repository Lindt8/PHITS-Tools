# Unit Testing

This directory contains unit tests for various functions in PHITS Tools not requiring any externally distributed files (unlike those in [`test/`](test/)).

These tests principally aim to test the standalone functions in PHITS Tools that end-users are likely to utilize themselves, rather than those which are complex internal cogs in output file processing, which generally require real example outputs that have already undergone some form of processing by other functions in PHITS Tools.  (Some of the simpler of these "internal-use only" functions do have unit tests here though.)

Testing was developed with [`pytest`](https://pypi.org/project/pytest/) and [`pytest-cov`](https://pypi.org/project/pytest-cov/) (for coverage testing).  Configuration details can be found in [`pyproject.toml`](pyproject.toml) and common test execution commands in the [`Makefile`](Makefile).

## Expected coverage

[![CI Tests](https://github.com/Lindt8/PHITS-Tools/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/Lindt8/PHITS-Tools/actions/workflows/ci-tests.yml)
| Unit tests only: [![Unit Tests](https://codecov.io/gh/Lindt8/PHITS-Tools/branch/feature/improve-testing/graph/badge.svg?flag=ci-unittests&label=Unit%20Tests)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=ci-unittests)
| Full test suite: [![Full Suite](https://codecov.io/gh/Lindt8/PHITS-Tools/branch/feature/improve-testing/graph/badge.svg?flag=full-suite&label=Full%20Suite)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=full-suite)
<!--
| Unit tests [![Unit Tests](https://codecov.io/gh/Lindt8/PHITS-Tools/graph/badge.svg?flag=ci-unittests&label=Unit%20Tests)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=ci-unittests)
| Full test suite [![Full Suite](https://codecov.io/gh/Lindt8/PHITS-Tools/graph/badge.svg?flag=full-suite&label=Full%20Suite)](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=full-suite)
/-->

After executing `make test-cov` to run all the tests in this directory, in the produced `htmlcov-unit/function_index.html` coverage report expect something around 19% total coverage (over all of PHITS Tools) but 90% or higher coverage individually for all of the functions tested by the unit tests here.
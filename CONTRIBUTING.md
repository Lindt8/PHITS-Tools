# Contributing to PHITS Tools  
Thank you for considering helping with the improvement of PHITS Tools!

## Reporting bugs and problem inputs
If you find a bug, please submit an [Issue on the PHITS Tools GitHub page](https://github.com/Lindt8/PHITS-Tools/issues) detailing the problem.

While extensive testing has been performed attempting to capture as many combinations of tally settings as possible, there still may be some usage/combinations of different settings not considered that may cause PHITS Tools to crash when attempting to parse a particular output file.  If you come across such an edge case&mdash;a standard PHITS tally output file that causes PHITS Tools to crash when attempting to parse it&mdash;please submit it as an [issue](https://github.com/Lindt8/PHITS-Tools/issues) and include the output file in question (and details on any potential extra steps for reproducing the problem), and I'll do my best to update the code to work with it!  Over time, hopefully all the possible edge cases can get stamped out this way. :)

## Feature/improvement suggestions
If you have any questions or ideas for improvements and/or feature suggestions, feel free to submit them as an [issue](https://github.com/Lindt8/PHITS-Tools/issues).

If you find anything in the [PHITS Tools documentation](https://lindt8.github.io/PHITS-Tools/) to be unclear or seemingly incomplete, please note that in an [issue](https://github.com/Lindt8/PHITS-Tools/issues) as well. (The PHITS Tools documentation is created from the main `PHITS_tools.py` module file using [pdoc](https://github.com/pdoc3/pdoc).)


## Contributing new/modified code
If you would like to contribute a new function or changes to any existing functions, feel free to fork this repository, make a new branch with your additions/changes, and make a pull request.  (GitHub has a [nice short guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) on this process.)

Owing to the slightly complicated/unorthodox approach used for integrating/structuring the `dchain_tools` and `manage_mc_materials` submodules (see [`pyproject.toml`](https://github.com/Lindt8/PHITS-Tools/blob/main/pyproject.toml) and [`PHITS_tools/__init__.py`](https://github.com/Lindt8/PHITS-Tools/blob/main/PHITS_tools/__init__.py)), any additions/changes to them should be made to their respective module files (with those to [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools) made in its repository).  Otherwise, source development should occur within the `PHITS_tools/` directory.

Please submit any pull requests to the `develop` branch.

## Testing

The testing for PHITS Tools is divided into two directories:

- [`tests/`](tests/) for unit tests: These are used for [CI testing]((https://github.com/Lindt8/PHITS-Tools/actions/workflows/ci-tests.yml)) and are automatically ran with pull requests to the `develop` and `main` branches.  This set of unit tests primarily is for the standalone functions in PHITS Tools that end-users are likely to use for additional results post-processing or independent use, rather than the functions which are complex internal cogs in output file processing.
- [`test/`](test/) for integration/functional tests: These require externally distributed PHITS output files (see [`test/README.md`](test/README.md) for full details) and test the start-to-finish function of PHITS Tools. These tests exist to verify if the code runs without error and, where reasonable, checks if the output has properties/formatting as expected.

Testing was developed with [`pytest`](https://pypi.org/project/pytest/) and [`pytest-cov`](https://pypi.org/project/pytest-cov/) (for coverage testing).  Configuration details can be found in [`pyproject.toml`](pyproject.toml) and common test execution commands in the [`Makefile`](Makefile), such as `make test` (run unit tests), `make test-cov` (coverage for unit tests), and `make test-all` (coverage for full test suite).  Coverage reports are also uploaded to [Codecov](https://app.codecov.io/github/lindt8/phits-tools); automatically [via CI](https://github.com/Lindt8/PHITS-Tools/actions/workflows/ci-tests.yml) for the unit tests (see flag [`ci-unittests`](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=ci-unittests)) and manually via the `make upload-full` command (which makes use of [`codecovcli`](https://pypi.org/project/codecov-cli/)) for the integration/functional tests (see flag [`full-suite`](https://app.codecov.io/github/lindt8/phits-tools?flags%5B0%5D=full-suite)), of course after running those tests with `make test-all`.

## Note about DCHAIN Tools and Git Submodules
Note that [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools) is included in PHITS Tools as a [Git Submodule](https://gist.github.com/gitaarik/8735255), and this has some implications.  First, any development for DCHAIN Tools should be pointed at the [DCHAIN Tools repository](https://github.com/Lindt8/DCHAIN-Tools) instead of here.  (Feel free to make suggestions for it in Issues either here or there, though with a preference for the DCHAIN Tools repo.)

If you wish to clone the PHITS-Tools repository and also grab the DCHAIN-Tools files, you need to add the `--recurse-submodules` flag to your `clone` command. 

`gh repo clone https://github.com/Lindt8/PHITS-Tools -- --recurse-submodules`

If, while developing, you need to synchronize DCHAIN Tools with the version pinned in PHITS Tools (to its most recent version), use `git submodule update --remote` from within the PHITS Tools project root directory.

<!--

## Testing, reporting issues, and contributing

I have extensively tested this module with a rather large number of PHITS output files with all sorts of different geometry settings, combinations of meshes, output options, and other settings to try to capture as a wide array of output files as I could (including the ~300 output files within the `phits/sample/` and `phits/recommendation/` directories included in the distributed PHITS release, which can be tested in an automated way with `test/test_overall_functionality.py` in this repository, along with a large number of supplemental variations to really test every option I could think of), but there still may be some usage/combinations of different settings I had not considered that may cause PHITS Tools to crash when attempting to parse a particular output file.  If you come across such an edge case&mdash;a standard PHITS tally output file that causes PHITS Tools to crash when attempting to parse it&mdash;please submit it as an issue and include the output file in question and I'll do my best to update the code to work with it!  Over time, hopefully all the possible edge cases can get stamped out this way. :)

Likewise, if you have any questions or ideas for improvements / feature suggestions, feel free to submit them as an [issue](https://github.com/Lindt8/PHITS-Tools/issues).  If you would like to contribute a new function or changes to any existing functions, feel free to fork this repository, make a new branch with your additions/changes, and make a pull request.  (GitHub has a [nice short guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) on this process.)

/-->

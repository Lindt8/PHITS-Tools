#### Online PHITS Tools documentation: [lindt8.github.io/PHITS-Tools/](https://lindt8.github.io/PHITS-Tools/)

# PHITS Tools
[![status](https://joss.theoj.org/papers/ef67acccadb883867ba60dc9e018ff70/status.svg)](https://joss.theoj.org/papers/ef67acccadb883867ba60dc9e018ff70)
[![PyPI - Version](https://img.shields.io/pypi/v/PHITS-Tools?logo=pypi&logoColor=fff&label=PyPI)](https://pypi.org/project/PHITS-Tools/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14262720.svg)](https://doi.org/10.5281/zenodo.14262720)
[![Documentation](https://img.shields.io/badge/Documentation-brightgreen)](https://lindt8.github.io/PHITS-Tools/)
[![PHITS forumn discussion on PHITS Tools](https://img.shields.io/badge/PHITS%20forum%20discussion%20-%20%2333a2d9)](https://meteor.nucl.kyushu-u.ac.jp/phitsforum/t/topic/3651/)



## Purpose

This module is a collection of Python 3 functions that serve to automatically process, organize, and visualize output from the PHITS general purpose Monte Carlo particle transport code (and ease/expedite further analyses) and interfaces for utilizing these parsing/processing functions.  PHITS can be obtained at [https://phits.jaea.go.jp/](https://phits.jaea.go.jp/).

Specifically, PHITS Tools seeks to be a universal PHITS output parser, supporting output from all tallies, both normal "standard" output as well as dump file outputs (in ASCII and binary formats), reading in the numeric data and metadata and storing them in Python objects for further use and analysis in Python.  PHITS Tools is also coupled to the [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools/) module and can import it to process DCHAIN output when the main tally output parsing function is provided DCHAIN-related files.  PHITS Tools also contains a number of functions for assisting in some types of further analyses.   You can read more about how to use PHITS Tools and its output in its online documentation: [lindt8.github.io/PHITS-Tools/](https://lindt8.github.io/PHITS-Tools/)

## Installation

### With `pip` (Python >= 3.10)

Install PHITS Tools:
`pip install PHITS-Tools`

Import PHITS Tools like any other Python module:
`import PHITS_tools` / `from PHITS_tools import *`

*Note:* To use the CLI/GUI, you must execute the `PHITS_tools.py` module file with `python`.  To find the installed location of the module file, execute: `pip show PHITS-Tools -f`

### Manually 

One may use the functions by first placing the PHITS_tools.py Python script into a folder in their PYTHONPATH system variable or in the active directory and then just importing them normally (`import PHITS_tools` / `from PHITS_tools import *`) or by executing the script `python PHITS_tools.py` with the PHITS output file to be parsed as the required argument (see `python PHITS_tools.py --help` for all CLI options) / without a file argument to be guided through with a GUI.

The short list of required package/library dependencies for PHITS Tools (and DCHAIN Tools) can be found in `requirements.txt` and installed by executing `pip install -r requirements.txt`.

## Primary usage/interfaces
There are three main ways one can use this Python module:

1. As an **imported Python module**
    - In your own Python scripts, you can import this module (`import PHITS_tools` / `from PHITS_tools import *`) and call its main functions or any of its other functions documented [here](https://lindt8.github.io/PHITS-Tools/).
2. As a **command line interface (CLI)**
    - This module can be ran on the command line with the individual PHITS output file to be parsed (or a directory containing multiple files to be parsed) as the required argument. Execute `python PHITS_tools.py --help` to see all of the different options that can be used with this module to parse standard or dump PHITS output files (individually and directories containing them) via the CLI.
3. As a **graphical user interface (GUI)** 
    - When the module is executed without any additional arguments, `python PHITS_tools.py`, (or with the `-g` or `--GUI` flag in the CLI) a GUI will be launched to step you through selecting what "mode" you would like to run PHITS Tools in (`STANDARD`, `DUMP`, or `DIRECTORY`), selecting a file to be parsed (or a directory containing multiple files to be parsed), and the various options for each mode.

Aside from the main PHITS output parsing function [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file) for general tally output, the [**`parse_tally_dump_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_dump_file) function for parsing tally dump file outputs, and the [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir) function for parsing all standard (and, optionally, dump) tally outputs in a directory, PHITS_tools.py also contains a number of other functions that may be of use for further analyses, such as tallying contents of dump files, rebinning historgrammed results, applying [ICRP 116 effective dose conversion coefficients](https://doi.org/10.1016/j.icrp.2011.10.001) to scored particle fluences, and retrieving PHITS-formatted [Material] section entries from a large database of materials (primarily from [PNNL-15870 Rev. 1](https://www.osti.gov/biblio/1023125)), among others.

The CLI and GUI options result in the parsed file's contents being saved to a [pickle](https://docs.python.org/3/library/pickle.html) file, which can be reopened and used later in a Python script. (The pickle files produced when parsing "dump" output files are by default compressed via Python's built-in [LZMA compression](https://docs.python.org/3/library/lzma.html), indicated with an additional `'.xz'` file extension.) When using the main functions within a Python script which has imported the PHITS_tools module, you can optionally choose not to save the pickle files (if desired) and only have the tally output/dump parsing functions return the data objects they produce (dictionaries, NumPy arrays, Pandas DataFrames, and *[only for dump outputs]* lists of [namedtuples](https://docs.python.org/3/library/collections.html#collections.namedtuple) / similarly functioning [NumPy recarray](https://numpy.org/doc/stable/reference/generated/numpy.recarray.html)s when saved to a pickle file) for your own further analyses.


Pictured below is the main PHITS Tools GUI window followed by the `[DIRECTORY mode]` GUI menu which shows all the options available not only for DIRECTORY mode but also for standard and dump tally output files, with the default options selected/populated.

![](/docs/PHITS_tools_GUI_main.png?raw=true "PHITS Tools GUI main window")

![](/docs/PHITS_tools_GUI_directory-mode.png?raw=true "PHITS Tools GUI 'DIRECTORY mode' window")

## CLI options

The CLI principally serves to interface with the core three functions of PHITS Tools: [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file), [**`parse_tally_dump_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_dump_file), and [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir).  The required `file` argument is checked to see if it is a directory or a file, and, if the latter, whether the `-d` option is used denoting a dump output file, otherwise defaulting to assuming it is a PHITS standard tally output file; then `file` and the relevant settings are sent to the corresponding main function.  Explicitly, inclusion of the various CLI options have the following effects on the main functions' arguments and settings:


- Affecting all functions
  - `file` is passed to `tally_output_filepath`, `path_to_dump_file`, or `tally_output_dirpath`
  - `-skip` sets `prefer_reading_existing_pickle = True` (`False` if excluded)
- [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file) (and passed to it via [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir))
  - `-np` sets `make_PandasDF = False` (`True` if excluded)
  - `-na` sets `calculate_absolute_errors = False` (`True` if excluded)
  - `-lzma` sets `compress_pickle_with_lzma = True` (`False` if excluded)
  - `-p` sets `autoplot_tally_output = True` (`False` if excluded)
- [**`parse_tally_dump_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_dump_file) (and passed to it via [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir))
  - `-d` tells the CLI that `file` should be processed as a dump file (if it's not a directory)
  - `-dvals` passes the provided sequence of values to `dump_data_sequence` (`None` if excluded)
  - `-dbin` specifies that the file is binary (that `dump_data_number=len(dump_data_sequence)` and *is positive*)
  - `-dnmax` passes its value to `max_entries_read` (`None` if excluded)
  - `-ddir` sets `return_directional_info = True` (`False` if excluded)
  - `-ddeg` sets `use_degrees = True` (`False` if excluded)
  - `-dnsl` sets `save_namedtuple_list = False` (`True` if excluded)
  - `-dnsp` sets `save_Pandas_dataframe = False` (`True` if excluded)
  - `-dmaxGB` passes its value to `split_binary_dumps_over_X_GB` (`20` GB if excluded)
  - `-dsplit` passes its value to `merge_split_dump_handling` (`0` if excluded)
- [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir) exclusively
  - `-r` sets `include_subdirectories = True` (`False` if excluded)
  - `-fpre` passes its value to `output_file_prefix` (`''` if excluded)
  - `-fsuf` passes its value to `output_file_suffix` (`'.out'` if excluded)
  - `-fstr` passes its value to `output_file_required_string` (`''` if excluded)
  - `-d` sets `include_dump_files = True` (`False` if excluded)
  - `-dnmmpi` sets `dump_merge_MPI_subdumps = False` (`True` if excluded)
  - `-dndmpi` sets `dump_delete_MPI_subdumps_post_merge = False` (`True` if excluded)
  - `-pa` sets `autoplot_all_tally_output_in_dir = True` (`False` if excluded)

Below is a picture of all of these options available for use within the CLI.  

![](/docs/PHITS_tools_CLI.png?raw=true "PHITS Tools CLI options")

## Testing, reporting issues, and contributing

I have extensively tested this module with a rather large number of PHITS output files with all sorts of different geometry settings, combinations of meshes, output options, and other settings to try to capture as a wide array of output files as I could (including the ~300 output files within the `phits/sample/` and `phits/recommendation/` directories included in the distributed PHITS release, which can be tested in an automated way with `test/test_PHITS_tools.py` in this repository, along with a large number of supplemental variations to really test every option I could think of), but there still may be some usage/combinations of different settings I had not considered that may cause PHITS Tools to crash when attempting to parse a particular output file.  If you come across such an edge case&mdash;a standard PHITS tally output file that causes PHITS Tools to crash when attempting to parse it&mdash;please submit it as an issue and include the output file in question and I'll do my best to update the code to work with it!  Over time, hopefully all the possible edge cases can get stamped out this way. :)

Likewise, if you have any questions or ideas for improvements / feature suggestions, feel free to submit them as an issue.  If you would like to contribute a new function or changes to any existing functions, feel free to fork this repository, make a new branch with your additions/changes, and make a pull request.  (GitHub has a [nice short guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) on this process.)


-----

If using [T-Dchain] in PHITS and/or the DCHAIN-PHITS code, the [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools/) repository contains a separate Python module for parsing and processing that related code output.  While PHITS Tools will import and use DCHAIN Tools if provided with DCHAIN-related files, direct usage of DCHAIN Tools may be desired if you want greater control of the various output parsing options within it or want to make use of some of its useful standalone functions. All of these functions are documented online at [lindt8.github.io/DCHAIN-Tools/](https://lindt8.github.io/DCHAIN-Tools/). 

DCHAIN Tools is distributed as a submodule of PHITS Tools.  If installing PHITS Tools via `pip install PHITS-Tools`, you can access DCHAIN Tools with `import PHITS_tools.dchain_tools as dchain_tools` / `from PHITS_tools.dchain_tools import *`.  If installing PHITS Tools manually, see `dchain_tools.py` in the `DCHAIN-Tools` directory/submodule link.

-----

These functions are tools I have developed over time to speed up my usage of PHITS; they are not officially supported by the PHITS development team.  All of the professionally-relevant Python modules I have developed are summarized [here](https://lindt8.github.io/professional-code-projects/), and more general information about me and the work I do / have done can be found on [my personal webpage](https://lindt8.github.io/).

<!-- The dchain_tools_manual.pdf document primarily covers usage of this main function but provides brief descriptions of the other available functions. /--> 

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
    - This module can be ran on the command line with the individual PHITS output file to be parsed (or a directory or PHITS input/phits.out file containing multiple files to be parsed) as the required argument. Execute `python PHITS_tools.py --help` to see all of the different options that can be used with this module to parse standard or dump PHITS output files (individually and directories containing them) via the CLI.  This functionality can be used to automatically process all PHITS output whenever PHITS is ran; see the **"Automatic processing at PHITS runtime"** section further below.
3. As a **graphical user interface (GUI)** 
    - When the module is executed without any additional arguments, `python PHITS_tools.py`, (or with the `-g` or `--GUI` flag in the CLI) a GUI will be launched to step you through selecting what "mode" you would like to run PHITS Tools in (`STANDARD`, `DUMP`, `DIRECTORY`, or `INPUT_FILE`), selecting a file to be parsed (or a directory containing multiple files to be parsed), and the various options for each mode.

Aside from the main PHITS output parsing function [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file) for general tally output, the [**`parse_tally_dump_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_dump_file) function for parsing tally dump file outputs, and the [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir) function for parsing all standard (and, optionally, dump) tally outputs in a directory, PHITS_tools.py also contains a number of other functions that may be of use for further analyses, such as tallying contents of dump files, rebinning historgrammed results, applying [ICRP 116 effective dose conversion coefficients](https://doi.org/10.1016/j.icrp.2011.10.001) to scored particle fluences, and retrieving PHITS-formatted [Material] section entries from a large database of materials (primarily from [PNNL-15870 Rev. 1](https://www.osti.gov/biblio/1023125)), among others.  It also is capable of automatically creating plots of tally results, as showcased in [test/test_tally_plots.pdf](https://github.com/Lindt8/PHITS-Tools/blob/main/test/test_tally_plots.pdf) ([view whole PDF here](https://github.com/Lindt8/PHITS-Tools/blob/main/test/test_tally_plots.pdf?raw=true)).

The CLI and GUI options result in the parsed file's contents being saved to a [pickle](https://docs.python.org/3/library/pickle.html) file, which can be reopened and used later in a Python script. (The pickle files produced when parsing "dump" output files are by default compressed via Python's built-in [LZMA compression](https://docs.python.org/3/library/lzma.html), indicated with an additional `'.xz'` file extension.) When using the main functions within a Python script which has imported the PHITS_tools module, you can optionally choose not to save the pickle files (if desired) and only have the tally output/dump parsing functions return the data objects they produce (dictionaries, NumPy arrays, Pandas DataFrames, and *[only for dump outputs]* lists of [namedtuples](https://docs.python.org/3/library/collections.html#collections.namedtuple) / similarly functioning [NumPy recarray](https://numpy.org/doc/stable/reference/generated/numpy.recarray.html)s when saved to a pickle file) for your own further analyses.


Pictured below is the main PHITS Tools GUI window followed by the `[DIRECTORY mode]` GUI menu which shows all the options available not only for DIRECTORY mode but also for standard and dump tally output files, with the default options selected/populated.

![](https://github.com/Lindt8/PHITS-Tools/blob/main/docs/PHITS_tools_GUI_main.png?raw=true "PHITS Tools GUI main window")

![](https://github.com/Lindt8/PHITS-Tools/blob/main/docs/PHITS_tools_GUI_directory-mode.png?raw=true "PHITS Tools GUI 'DIRECTORY mode' window")

## CLI options

The CLI principally serves to interface with the core three functions of PHITS Tools: [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file), [**`parse_tally_dump_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_dump_file), and [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir).  The required `file` argument is checked to see if it is a directory or a file, and, if the latter, whether the `-d` option is used denoting a dump output file, otherwise defaulting to assuming it is a PHITS standard tally output file; then `file` and the relevant settings are sent to the corresponding main function.  Explicitly, inclusion of the various CLI options have the following effects on the main functions' arguments and settings:


- Affecting all functions
  - `file` is passed to `tally_output_filepath`, `path_to_dump_file`, or `tally_output_dirpath`
  - `-skip` sets `prefer_reading_existing_pickle = True` (`False` if excluded)
- [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file) (and passed to it via [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir))
  - `-np` sets `make_PandasDF = False` (`True` if excluded)
  - `-na` sets `calculate_absolute_errors = False` (`True` if excluded)
  - `-lzma` sets `compress_pickle_with_lzma = True` (`False` if excluded)
  - `-po` sets `include_phitsout_in_metadata = True` (`False` if excluded)
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
  - `-m` sets `merge_tally_outputs = True` (`False` if excluded)
  - `-smo` sets `merge_tally_outputs = True` (`False` if excluded), `save_output_pickle = False` (`True` if excluded), and `save_pickle_of_merged_tally_outputs = True` (`None` if excluded)
  - `-pa` sets `autoplot_all_tally_output_in_dir = True` (`False` if excluded)

Below is a picture of all of these options available for use within the CLI.  

![](https://github.com/Lindt8/PHITS-Tools/blob/main/docs/PHITS_tools_CLI.png?raw=true "PHITS Tools CLI options")

## **Automatic processing at PHITS runtime**

PHITS Tools can be used to automatically process the output of every PHITS run executed with the "phits.bat" and "phits.sh" scripts found in the "phits/bin/" directory of your PHITS installation.  To do this, first you must identify the location of your "PHITS_tools.py" file.  If using the file directly downloaded from GitHub, this should be in a location of your choosing.  If you installed PHITS Tools via `pip install PHITS-Tools`, you can find its location with `pip show PHITS-Tools -f`. Once you have identified the location of PHITS_tools.py, for example "/path/locating/PHITS_Tools/PHITS_tools.py", you can add the following line to your PHITS execution script:

On Windows, using "phits/bin/phits.bat":

- Scroll down toward the bottom of the script, to the section with the line `rem - Your file processing starts here.`
- After the if statement (right before the `rem - Your file processing ends here` line), insert a new line with the following command:
- `python "C:\path\locating\PHITS_Tools\PHITS_tools.py" "%%~nxF" -po -m -d -ddir -ddeg -lzma -p -pa`

On Linux/Mac, using "phits/bin/phits.sh":

- Scroll down toward the bottom of the script, to the section titled `# Run PHITS`
- On the line after the end of the if statement `fi`, add the following command:
- `python "/path/locating/PHITS_Tools/PHITS_tools.py" $1 -po -m -d -ddir -ddeg -lzma -p -pa`

(Of course, if necessary, replace "`python`" with however you typically call python in your environment, e.g. `py`, `python3`, etc.)

Adding this line causes the following to happen:

- After PHITS finishes running normally, the PHITS input file is passed to PHITS Tools.
- Since it is a PHITS input file, the CLI will have [**`parse_all_tally_output_in_dir()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_all_tally_output_in_dir) handle it, in *[INPUT_FILE mode]*
- The input file and its produced "phits.out"-type file are scanned for output files from active tallies, including those inputted via the PHITS insert file function `infl:{}` too (using [**`extract_tally_outputs_from_phits_input()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.extract_tally_outputs_from_phits_input) and [**`parse_phitsout_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_phitsout_file)). 
   - This will include any dump files (**`-d`**) if present.
   - When the "phits.out" file (`file(6)` in the PHITS input [Parameters]) is parsed, its metadata&mdash;including the PHITS input echo&mdash;will be saved to a .pickle file, compressed with LZMA (**`-lzma`**) and with the extra ".xz" extension.
- Then, the standard tally outputs are processed.  For each standard tally output:
   - The [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file) function processes the tally output, producing a `tally_output` dictionary with keys for the produced NumPy array, Pandas DataFrame, and metadata dictionary.
   - The `tally_output['tally_metadata']` dictionary will have the phits.out metadata dictionary added to it (**`-po`**) under the `'phitsout'` key.
   - This `tally_output` dictionary object is saved to a .pickle file, compressed with LZMA (**`-lzma`**) and with the extra ".xz" extension.
   - A plot, saved in PDF and PNG formats, of the tally's output is generated (**`-p`**) by [**`autoplot_tally_results()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.autoplot_tally_results).
   - These files will share the same name as the tally output file, just with different extensions.
- Then, any encountered tally dump files are processed (**`-d`**).  For each tally dump output file:
   - The [**`parse_tally_dump_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_dump_file) function processes the dump file, automatically extracting the dump parameters from its parent tally's output file.
   - Provided direction vector information (u,v,w) is present, extra directional information is calculated (**`-ddir`**), using degrees for the unit of calculated angles (**`-ddeg`**)
   - The produced named tuple list and Pandas DataFrame are saved as two separate LZMA-compressed pickle files.
- Then, a merged (**`-m`**) dictionary object containing all of the `tally_output` dictionaries for each standard tally output processed is produced.
   - The dictionary is keyed with the `file` parameter of each tally in the PHITS input, with the values being the corresponding `tally_output` dictionaries.
   - This merged dictionary object is saved to a pickle file sharing the same name as the PHITS input file but ending in "_ALL_TALLY_OUTPUTS.pickle", compressed with LZMA (**`-lzma`**) and with the extra ".xz" extension.
- Then, a PDF containing plots from all standard tally outputs (**`-pa`**) is generated with [**`autoplot_tally_results()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.autoplot_tally_results).
   - This PDF of plots is saved to a file sharing the same name as the PHITS input file but ending in "_ALL_TALLY_OUTPUTS_PLOTTED.pdf"


You can edit the flags provided to the CLI for your desired default behavior.  For instance, to only save the pickle file of the merged output (rather than for every tally output too), replace `-m` with `-smo`. And to not bother with creating a merged output and only save the outputs for each individual tally, just omit `-m`.  Given that the plotting is easily the slowest part of the execution of PHITS Tools in most cases, it may be desirable to omit the `-p` and/or `-pa` flags to not save plots of the tally outputs individually or all together in a single PDF, respectively.  Since dump files can be very large and sometimes solely created for reusage by PHITS (e.g., with a `s-type=17` [Source] section), it may also be desirable to exclude dump files from automatic processing by omitting `-d`.  As an example, a more "minimal" automatic processing would result from:

- Windows: `python "C:\path\locating\PHITS_Tools\PHITS_tools.py" "%%~nxF" -po -smo -lzma -pa`
- Linux/Mac: `python "/path/locating/PHITS_Tools/PHITS_tools.py" $1 -po -smo -lzma -pa`

This would only create the ".pickle.xz" file of the merged standard tally outputs and the PDF containing all of their plots together, skipping any processing of dump files.

#### Automatic processing at DCHAIN runtime

Similarly, PHITS Tools can be used to automatically process output from the DCHAIN code, utilizing an import of the [DCHAIN Tools module](https://github.com/Lindt8/DCHAIN-Tools).

On Windows, using "phits/dchain-sp/bin/dchain.bat":

- Scroll down toward the bottom of the script, to the section with the line `rem - Your file processing ends here.`
- Right above that line (before the `goto :continue`), insert a new line with the following command:
- `python "C:\path\locating\PHITS_Tools\PHITS_tools.py" "%%~nxF" -po -lzma`

On Linux/Mac, using "phits/dchain-sp/bin/dchain.sh":

- Scroll down toward the bottom of the script, right before the line with `echo ' end of dchain '`
- On the line after the end of the if statement `fi`, add the following command:
- `python "/path/locating/PHITS_Tools/PHITS_tools.py" ${jnam} -po -lzma`

This will create a ".pickle.xz" file (with the same basename as the DCHAIN input file) of the processed DCHAIN outputs, as a dictionary object, with contents as described in the documentation for [**`parse_tally_output_file()`**](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file) under the "[T-Dchain] special case" section, also including an entry with a dictionary of information on the corresponding PHITS run via its "phits.out" file, if found.


## Testing, reporting issues, and contributing

I have extensively tested this module with a rather large number of PHITS output files with all sorts of different geometry settings, combinations of meshes, output options, and other settings to try to capture as a wide array of output files as I could (including the ~300 output files within the `phits/sample/` and `phits/recommendation/` directories included in the distributed PHITS release, which can be tested in an automated way with `test/test_PHITS_tools.py` in this repository, along with a large number of supplemental variations to really test every option I could think of), but there still may be some usage/combinations of different settings I had not considered that may cause PHITS Tools to crash when attempting to parse a particular output file.  If you come across such an edge case&mdash;a standard PHITS tally output file that causes PHITS Tools to crash when attempting to parse it&mdash;please submit it as an issue and include the output file in question and I'll do my best to update the code to work with it!  Over time, hopefully all the possible edge cases can get stamped out this way. :)

Likewise, if you have any questions or ideas for improvements / feature suggestions, feel free to submit them as an issue.  If you would like to contribute a new function or changes to any existing functions, feel free to fork this repository, make a new branch with your additions/changes, and make a pull request.  (GitHub has a [nice short guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) on this process.)


-----

If using [T-Dchain] in PHITS and/or the DCHAIN-PHITS code, the [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools/) repository contains a separate Python module for parsing and processing that related code output.  While PHITS Tools will import and use DCHAIN Tools if provided with DCHAIN-related files, direct usage of DCHAIN Tools may be desired if you want greater control of the various output parsing options within it or want to make use of some of its useful standalone functions. All of these functions are documented online at [lindt8.github.io/DCHAIN-Tools/](https://lindt8.github.io/DCHAIN-Tools/). 

DCHAIN Tools is distributed as a submodule of PHITS Tools.  If installing PHITS Tools via `pip install PHITS-Tools`, you can access DCHAIN Tools with `import PHITS_tools.dchain_tools as dchain_tools` / `from PHITS_tools.dchain_tools import *`.  If installing PHITS Tools manually, see `dchain_tools.py` in the `DCHAIN-Tools` directory/submodule link.

-----

These functions are tools I have developed over time to speed up my usage of PHITS; they are not officially supported by the PHITS development team.  All of the professionally-relevant Python modules I have developed are summarized [here](https://lindt8.github.io/professional-code-projects/), and more general information about me and the work I do / have done can be found on [my personal webpage](https://lindt8.github.io/).

<!-- The dchain_tools_manual.pdf document primarily covers usage of this main function but provides brief descriptions of the other available functions. /--> 

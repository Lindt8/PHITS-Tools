#### Online PHITS Tools documentation: [lindt8.github.io/PHITS-Tools/](https://lindt8.github.io/PHITS-Tools/)

# PHITS Tools

This module is a collection of Python 3 functions that serve to automatically process output from the PHITS general purpose Monte Carlo particle transport code, which can be obtained at [https://phits.jaea.go.jp/](https://phits.jaea.go.jp/), and interfaces for utilizing these parsing/processing functions.

Specifically, PHITS Tools seeks to be a (nearly) universal PHITS output parser, supporting output from all tallies, both normal "standard" output as well as dump file outputs (in ASCII and binary formats), reading in the numeric data and metadata and storing them in Python objects for further use and analysis in Python.  You can read more about how to use PHITS Tools and its output in its online documentation: [lindt8.github.io/PHITS-Tools/](https://lindt8.github.io/PHITS-Tools/)

There are three main ways one can use this Python module:

1. As an **imported Python module**
    - In your own Python scripts, you can import this module as `from PHITS_tools import *` and call its main functions or any of its other functions documented [here](https://lindt8.github.io/PHITS-Tools/).
2. As a **command line interface (CLI)**
    - This module can be ran on the command line with the individual PHITS output file to be parsed (or a directory containing multiple files to be parsed) as the required argument. Execute `python PHITS_tools.py --help` to see all of the different options that can be used with this module to parse standard or dump PHITS output files (individually and directories containing them) via the CLI.
3. As a **graphical user interface (GUI)** 
    - When the module is executed without any additional arguments, `python PHITS_tools.py`, (or with the `-g` or `--GUI` flag in the CLI) a GUI will be launched to step you through selecting what "mode" you would like to run PHITS Tools in (`STANDARD`, `DUMP`, or `DIRECTORY`), selecting a file to be parsed (or a directory containing multiple files to be parsed), and the various options for each mode.

Aside from the main PHITS output parsing function **`parse_tally_output_file()`** for general tally output, the **`parse_tally_dump_file()`** function for parsing tally dump file outputs, and the **`parse_all_tally_output_in_dir()`** function for parsing all standard (and, optionally, dump) tally outputs in a directory, PHITS_tools.py also contains a handful of other functions which individuals may find useful. 

The CLI and GUI options result in the parsed file's contents being saved to a [pickle](https://docs.python.org/3/library/pickle.html) (or [dill](https://pypi.org/project/dill/)) file, which can be reopened and used later in a Python script. When using the main functions within a Python script which has imported the PHITS_tools module, you can optionally choose not to save the pickle files (if desired) and only have the tally output/dump parsing functions return the data objects they produce (dictionaries, NumPy arrays, Pandas DataFrames, and *[only for dump outputs]* lists of NamedTuples) for your own further analyses.

One may use the functions by first placing the PHITS_tools.py Python script into a folder in their PYTHONPATH system variable or in the active directory and then just importing them normally (`from PHITS_tools import *`) or by executing the script `python PHITS_tools.py` with the PHITS output file to be parsed as the required argument (see `python PHITS_tools.py --help` for all CLI options) / without a file argument to be guided through with a GUI.

Pictured below is the main PHITS Tools GUI window followed by the `[DIRECTORY mode]` GUI menu which shows all the options available not only for DIRECTORY mode but also for standard and dump tally output files.

![](/docs/PHITS_tools_GUI_main.png?raw=true "PHITS Tools GUI main window")

![](/docs/PHITS_tools_GUI_directory-mode.png?raw=true "PHITS Tools GUI 'DIRECTORY mode' window")

Below is also a picture of all of the options available for use within the CLI:

![](/docs/PHITS_tools_CLI.png?raw=true "PHITS Tools CLI options")

I have tested this module with a rather extensive number of PHITS output files with all sorts of different geometry settings, combinations of meshes, output options, and other settings to try to capture as a wide array of output files as I could, but I am sure there are still some usage/combinations of different settings I had not considered that may cause PHITS Tools to crash when attempting to parse a particular output file.  If you come across such an edge case, a standard PHITS tally output file that causes PHITS Tools to crash when attempting to parse it, please submit it as an issue and include the output file in question and I'll do my best to update the code to work with it!  Over time, hopefully all the possible edge cases can get stamped out this way. :)


-----

If using [T-Dchain] in PHITS and/or the DCHAIN-PHITS code, the [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools/) repository contains a separate Python module for parsing and processing that related code output. All of these functions are documented online at [lindt8.github.io/DCHAIN-Tools/](https://lindt8.github.io/DCHAIN-Tools/)

-----

These functions are just tools I have developed over time to speed up my usage of PHITS; they are not officially supported by the PHITS development team.  They were developed to serve my own needs, and I am just publicly sharing them because others may also find utility in them.  All of the professionally-relevant Python modules I have developed are summarized [here](https://lindt8.github.io/professional-code-projects/), and more general information about me and the work I do / have done can be found on [my personal webpage](https://lindt8.github.io/).

<!-- The dchain_tools_manual.pdf document primarily covers usage of this main function but provides brief descriptions of the other available functions. /--> 

# Testing instructions

The `test_PHITS_tools.py` script can be ran to test the correct functioning of 
the `PHITS Tools` module in parsing a variety of PHITS output files.
Owing to PHITS being export controlled and requring a state-issued license from 
the Japan Atomic Energy Agency or the OECD Nuclear Energy Agency (NEA), 
no files distributed with PHITS are redistributed here.  That said, if you
already have a PHITS installation, you will find an extensive set of sample 
PHITS inputs and outputs provided within the `phits/sample/` and `phits/recommendation/`
directories and their nested subdirectories, totalling approximately 300 test 
output files to be parsed by this script.  `test_PHITS_tools.py` uses 
these distributed sample outputs as its testing suite; all you must do is 
make sure the `path_to_phits_base_folder` variable correctly points to your 
PHITS installation's base folder (by default, `C:\phits\`).  When the script 
is ran, `PHITS Tools` will attempt parsing all of these outputs and print 
its results to the terminal and `test.log`, saved to the current working directory.
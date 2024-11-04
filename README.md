#### Online documentation: [lindt8.github.io/PHITS-Tools/](https://lindt8.github.io/PHITS-Tools/)

# PHITS Tools

This module is just a collection of Python 3 functions which serve to automatically process output from the PHITS general purpose Monte Carlo particle transport code, which can be obtained at [https://phits.jaea.go.jp/](https://phits.jaea.go.jp/).

These functions are just tools I have developed over time to speed up my usage of PHITS; they are not officially supported by the PHITS development team.  They were developed to serve my own needs, and I am just publicly sharing them because others may also find utility in them.  I may more professionally repackage and redistribute these functions in the future in a more standard way.  For now, one may use the functions by first placing the PHITS_tools.py Python script into a folder in their PYTHONPATH system variable or in the active directory and then just importing them normally ( from PHITS_tools import * ).

Aside from the main PHITS output parsing function **parse_tally_output_file()** for general tally output and the **parse_tally_dump_file()** function for parsing tally dump file outputs, PHITS_tools.py also contains a handful other functions which individuals may find useful. 

If using [T-Dchain] in PHITS and/or the DCHAIN-PHITS code, the [DCHAIN Tools](https://github.com/Lindt8/DCHAIN-Tools/) repository contains a separate Python module for parsing and processing that related code output. All of these functions are documented online at [lindt8.github.io/PHITS-Tools/](https://lindt8.github.io/PHITS-Tools/)

All of the professionally-relevant Python modules I have developed are summarized [here](https://lindt8.github.io/professional-code-projects/), and more general information about me and the work I do / have done can be found on [my personal webpage](https://lindt8.github.io/).

<!-- The dchain_tools_manual.pdf document primarily covers usage of this main function but provides brief descriptions of the other available functions. /--> 

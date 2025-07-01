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


<!--

## Testing, reporting issues, and contributing

I have extensively tested this module with a rather large number of PHITS output files with all sorts of different geometry settings, combinations of meshes, output options, and other settings to try to capture as a wide array of output files as I could (including the ~300 output files within the `phits/sample/` and `phits/recommendation/` directories included in the distributed PHITS release, which can be tested in an automated way with `test/test_PHITS_tools.py` in this repository, along with a large number of supplemental variations to really test every option I could think of), but there still may be some usage/combinations of different settings I had not considered that may cause PHITS Tools to crash when attempting to parse a particular output file.  If you come across such an edge case&mdash;a standard PHITS tally output file that causes PHITS Tools to crash when attempting to parse it&mdash;please submit it as an issue and include the output file in question and I'll do my best to update the code to work with it!  Over time, hopefully all the possible edge cases can get stamped out this way. :)

Likewise, if you have any questions or ideas for improvements / feature suggestions, feel free to submit them as an [issue](https://github.com/Lindt8/PHITS-Tools/issues).  If you would like to contribute a new function or changes to any existing functions, feel free to fork this repository, make a new branch with your additions/changes, and make a pull request.  (GitHub has a [nice short guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) on this process.)

/-->

---
title: 'The PHITS Tools Python package for parsing, organizing, and analyzing results from the PHITS radiation transport and DCHAIN activation codes'
tags:
  - PHITS
  - DCHAIN
  - Monte Carlo
  - radiation transport
  - nuclear physics
  - nuclear activation
  - Python
authors:
  - name: Hunter N. Ratliff
    orcid: 0000-0003-3761-5415
    affiliation: '1'
affiliations:
  - name: Western Norway University of Applied Sciences, Inndalsveien 28, 5063 Bergen, Norway
    index: 1
    ror: 05phns765
date: 2 January 2025
bibliography: paper.bib


---

# Summary 

Various areas within the nuclear sciences&mdash;such as 
nuclear facility design, medical physics, experimental nuclear physics, and radiation protection&mdash;rely 
on complex codes employing nuclear data and physics models to simulate the
transport (and interactions) of radiation through matter to answer important questions, 
in both research and applied contexts. 
PHITS [@PHITS333_ref] (Particle and Heavy Ion Transport code System)
is one such general purpose Monte Carlo particle transport simulation code, presently with over 7400 users worldwide[^1].
Though PHITS can simulate a large variety of complex physics, it can only do so on the extremely short
time scales of nuclear reactions. To calculate the creation and destruction of nuclides
with time (activation, buildup, burnup, and decay) on any timescale (seconds to centuries),
distributed with and coupled to PHITS is the DCHAIN [@DCHAIN_ref] code[^2].

[^1]: For current PHITS userbase statistics, see: [https://phits.jaea.go.jp/usermap/PHITS_map_userbase.html](https://phits.jaea.go.jp/usermap/PHITS_map_userbase.html)
[^2]: PHITS and DCHAIN are distributed by the Japan Atomic Energy Agency and the OECD/NEA Data Bank. For more information, see: [https://phits.jaea.go.jp/howtoget.html](https://phits.jaea.go.jp/howtoget.html).  

Radiation transport simulations minimally require specifying the involved 
geometry (defined shapes, regions, and materials), radiation source terms, and "tallies" that 
filter and score the physical quantities of interest to be outputted.
PHITS's tallies can score 
the number of particles passing through a region or surface,
the frequency/products/timing of nuclear interactions,
deposition of energy/dose, radiation damage, and more.
Users provide the desired criteria and
binning for the tally histograms (e.g., specifying a range of energies and the number of bins spanning it),
and the code simulates the histories, or "lives", of many particles, outputting aggregate distributions for the
tallied quantities, which should be converged to the "true/real" distributions
provided a statistically sufficient number of histories were simulated (often on the order of millions or more).
For a few tallies, PHITS provides the option to output "dump" files where, additionally, for each scored particle/interaction
detailed raw event data are recorded to a text/binary file, allowing users to, in post-processing,
create even more complex tallies and analyses than possible with the stock PHITS tallies.

The DCHAIN code coupled to PHITS specializes in calculating nuclide inventories and derived quantities 
(activity, decay heat, decay gamma-ray emission spectra, and more) as a function of time for
any arbitrary irradiation schedule from any radiation source.

The package presented here automates the time-consuming task of extracting the 
numerical results and metadata from PHITS/DCHAIN simulations and organizes them into 
a standard format, easing and expediting further practical real-world analyses.
It also provides functions for some of the most common analyses one 
may wish to perform on simulation outputs.



# Statement of need

PHITS Tools and its DCHAIN Tools submodule serve as interfaces between the plaintext (and binary) outputs
of the PHITS and DCHAIN codes and Python&mdash;greatly expediting further programmatic analyses, 
comparisons, and visualization&mdash;and provide some extra analysis tools. 
The outputs of the PHITS code are, aside from the special binary "dump" files, plaintext files formatted 
for processing by a built-in custom visualization code, and those of the DCHAIN
code are formatted in a variety of tabular, human-readable structures.  

Historically, programmatic extraction of results/metadata often necessitated bespoke processing scripts.
PHITS Tools provides universal output parsers for the PHITS and DCHAIN codes,
capable of processing all relevant output files,
returning results and metadata in a consistent, standard format, and
also automatically making plots of tally results.
No similar comprehensive PHITS/DCHAIN output parsing utilities presently exist. 
The MCPL: Monte Carlo Particle Lists [@MCPL_ref] package can parse 
PHITS binary dump files if using one of two specific combinations of tally dump parameter settings, and 
recent developments to FLUKA's [@Fluka2024_ref] FLAIR utility [@Flair3_ref] 
involve ongoing integration efforts with PHITS.

The substantial number of combinations within PHITS of geometry specification, 
scoring axes (spatial, energy, time, angle, LET, etc.), tally types (scoring volumetric/surface crossing
particle fluxes, energy deposition, nuclide production, interactions, radiation damage, and more),
particle species, and various exceptions/edge cases for specific tallies/their settings
highlight the utility of such a universal processing code for PHITS. 
When parsing standard PHITS tally output, PHITS Tools returns a metadata dictionary, 
a 10-dimensional NumPy [@numpy_ref] array universally accommodating of all possible PHITS tally output
containing all numerical results (structure illustrated in \autoref{tally_output_struct}), and 
a Pandas [@pandas_ref] DataFrame of the same numerical information, for users preferring Pandas.

: Structure of returned parsed tally output (NumPy array axes/Pandas DataFrame columns) \label{tally_output_struct}

+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| axis              | description (using PHITS nomenclature, input syntax in `monospace` font)                                                                                     |
+:==================+:=============================================================================================================================================================+
| 0 / `ir`          | Geometry mesh: `reg` / `x` / `r` / `tet` *                                                                                                                   |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 1 / `iy`          | Geometry mesh: `1` / `y` / `1`                                                                                                                               |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 2 / `iz`          | Geometry mesh: `1` / `z` / `z` *                                                                                                                             |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 3 / `ie`          | Energy mesh: `eng` ([T-Deposit2] `eng1`)                                                                                                                     |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 4 / `it`          | Time mesh                                                                                                                                                    |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 5 / `ia`          | Angle mesh                                                                                                                                                   |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 6 / `il`          | LET mesh                                                                                                                                                     |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 7 / `ip`          | Particle type / group (`part =`)                                                                                                                             |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 8 / `ic`          | Special: [T-Deposit2] `eng2`, [T-Yield] `mass`/`charge`/`chart`, [T-Interact] `act`                                                                          |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 9 / `ierr`        | `= 0/1/2`, Value / relative uncertainty / absolute uncertainty *                                                                                             |
+===================+==============================================================================================================================================================+
| *exceptional behavior with [T-Cross] tally when `enclos = 0` is set; see [full documentation](https://lindt8.github.io/PHITS-Tools/#PHITS_tools.parse_tally_output_file)*        |
+===================+==============================================================================================================================================================+

PHITS Tools is also capable of parsing the "dump" outputs (both binary and plaintext formats)
available for some tallies, and it can automatically detect, parse, and process all PHITS
output files listed in a provided directory or PHITS input file too&mdash;very convenient
for simulations with multiple tallies, each with its own output file,
whose outputs are to be further studied, e.g., compared to experimental data or other simulations.
PHITS Tools can be used by:

1. importing it as a Python package in a script and calling its functions, 
2. running it in the command line via its CLI with a provided PHITS output
 file (or directory/input file) path and settings flags/options, or 
3. running it without any arguments or via the `PHITS-Tools-GUI` executable to launch a GUI and be 
stepped through the available output processing options and settings.

When used as an imported package, PHITS Tools provides a number of supplemental
functions aiding with further analyses, including tools for
constructing one's own tally over the history-by-history output of the "dump" files, 
rebinning histogrammed results to a different desired binning structure, 
applying effective dose conversion coefficients from ICRP 116 [@ICRP116_ref_withauthors] 
to tallied particle fluences, or 
retrieving a PHITS-input-formatted [Material] section entry (including 
its corresponding density) from a large database of over 350 materials
(primarily consisting of those within
the PNNL Compendium of Material Composition Data for Radiation Transport Modeling [@PNNL_materials_compendium]),
among other useful functions.

The DCHAIN Tools submodule handles the outputs of the DCHAIN code.  Its primary function 
parses all of the various DCHAIN output files and compiles the metadata
and numeric results&mdash;the confluence of the specified regions, output time steps, 
all nuclides and their inventories (and derived quantities), and complex decay chain 
schemes illustrating the production/destruction mechanisms for all nuclides&mdash;into 
a single unified dictionary object.  The DCHAIN Tools submodule includes some additional
useful functions such as retrieving neutron activation cross sections from DCHAIN's built-in 
nuclear data libraries, calculating flux-weighted single-group activation cross sections, 
and visualizing and summarizing the most significant nuclides (in terms of activity, 
decay heat, or gamma-ray dose) as a function of time. If PHITS Tools is provided DCHAIN-related 
files, DCHAIN Tools will be automatically imported and its primary function executed
on the DCHAIN output.

In all, the PHITS Tools package makes the results produced by the PHITS and DCHAIN codes 
far more accessible for further use, analyses, comparisons, and visualizations in 
Python, removing the initial hurdle of parsing and organizing the raw output from these codes, 
and provides some additional tools for easing further analyses and drawing conclusions from 
PHITS and DCHAIN results.


# Acknowledgements

A portion of this work has been completed by the author while under the 
support of European Innovation Council (EIC) grant agreement number 101130979.
The EIC receives support from the European Union's Horizon Europe research and innovation program.

# References

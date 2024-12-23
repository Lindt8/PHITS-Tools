---
title: 'PHITS Tools and DCHAIN Tools: Python modules for parsing and processing output from the PHITS radiation transport and DCHAIN activation codes'
tags:
  - Python
  - PHITS
  - DCHAIN
  - Monte Carlo
  - nuclear physics
  - nuclear activation
authors:
  - name: Hunter N. Ratliff
    orcid: 0000-0003-3761-5415
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
affiliations:
 - name: Western Norway University of Applied Sciences, Inndalsveien 28, 5063 Bergen, Norway
   index: 1
   ror: 05phns765
 - name: Japan Atomic Energy Agency, 2-4 Shirakata, Tokai, Naka, Ibaraki 319-1195, Japan
   index: 2
   ror: 05nf86y53
date: 2 January 2025
bibliography: paper.bib


---

# Summary 

Various areas within the nuclear sciences&mdash;such as 
nuclear facility design, medical physics, experimental nuclear physics, and radiation protection&mdash;rely 
on complex codes employing nuclear data and a large variety of physics models to simulate the 
transport (and interactions) of radiation through matter to answer important questions, 
in both research and applied contexts. 
For example: How should a shielding wall be designed to comply with radiation safety regulations? 
What is the expected dose an individual may receive in a particular exposure scenario?
After how long will an irradiated radioactive sample decay enough to become safe to handle?
How should an experiment be designed to make the most of limited time at an accelerator facility?

While simplified "rule of thumb" calculations and lookup tables can provide crude answers in some very basic scenarios,
often it is preferred or necessary (especially for higher-energy radiation) to fully model a radiation scenario 
to obtain a much more precise answer.  PHITS [@PHITS333_ref] (Particle and Heavy Ion Transport code System) 
is one such general purpose Monte Carlo particle transport simulation code, presently with over 6000 users worldwide.
Though PHITS can simulate a large variety of complex nuclear physics, it can only do so on the extremely short
time scales of nuclear reactions.  To calculate the activation, buildup, burnup, and decay of nuclides with time 
on any scale (seconds to centuries), distributed with and coupled to PHITS is the DCHAIN [@DCHAIN_ref] (or DCHAIN-PHITS) code.

Within PHITS (and other similar codes) are "tallies" which score various physical quantities
such as the number of particles passing through a region in space, the number of particles crossing a surface, 
the frequency and products of nuclear interactions of various types, deposition of energy, 
timing of interactions, displacements per atom (DPA), and more.  Users provide the desired
binning for the tally histograms to be created (such as specifying a range of energies of interest and 
how many bins the tally should have within that energy range), and the code will simulate the 
histories, or "lives", of many particles, outputting the aggregate distributions for the 
quantities being tallied, which should be converged to the "true" or "real" distributions 
provided a statistically sufficient number of histories were simulated (often on the order of millions or more).
For a few tallies, PHITS provides the option to output "dump" files where, in addition to the histograms, 
detailed raw history-by-history event data are recorded to an ASCII or binary file for every history 
satisfying the tally's criteria and being scored by it, allowing users to, in post, create 
even more complex tallies and analyses than possible with the stock tallies in PHITS.

The DCHAIN code coupled to PHITS specializes in calculating nuclide inventories and derived quantities 
(such as activity, decay heat, decay gamma-ray emission spectra, and more) as a function of time for 
any arbitrary irradiation schedule from any radiation source.



# Statement of need

`PHITS Tools` and `DCHAIN Tools` serve as an interface between the plaintext (and binary) outputs
of the PHITS and DCHAIN codes and Python, greatly expediting further programatic analysis, 
comparisons, and visualization in Python and providing some extra analysis tools. 
The outputs of the PHITS code are, aside from the special binary "dump" files, plaintext files formatted 
for processing by a custom closed-source visualization code (generating Encapsulated PostScript files) 
shipped with and automatically ran by PHITS, and those of the DCHAIN 
code are formatted in a variety of tabular, human-readable structures.  Historically, programatic
extraction and organization of numerical results (and metadata) from both codes often required 
writing a bespoke processing script for most individual simulations, 
possibly preceeded by manual data extraction/isolation too. 
`PHITS Tools` and `DCHAIN Tools` provide universal output parsers for the PHITS and DCHAIN codes, 
capable of processing all of the relevant output files produced by each code and
outputting the numerical results and metadata in a consistent, standardized output format.


The substantial number of combinations within PHITS of geometry specification, 
scoring axes (spatial, energy, time, angle, LET, etc.), tally types (scoring volumetric and surface crossing 
particle fluxes, energy deposition, nuclide production, interactions,  DPA, and more), potential 
particle species, and fair amount of "exceptions" or "edge cases" related to specific tallies and/or their settings 
highlight the utility of such a universal processing code for PHITS. 
When parsing standard PHITS tally output, `PHITS Tools` will return a metadata dictionary, 
a 10-dimensional NumPy array universally accomodating of all possible PHITS tally output
containing all numerical results (structured as shown in the table below), and 
a Pandas DataFrame containing the same numerical information, which
may be more user-friendly to those accustomed to working in Pandas.

+------+-----------+---------------------------------------------------------------------------------------+
| axis | name      | description                                                                           |
+:====:+:=========:+:======================================================================================+
| 0    | `ir`      | Geometry mesh: `reg` / `x` / `r` / `tet` *                                            |
+------+-----------+---------------------------------------------------------------------------------------+
| 1    | `iy`      | Geometry mesh: `1` / `y` / `1`                                                        |
+------+-----------+---------------------------------------------------------------------------------------+
| 2    | `iz`      | Geometry mesh: `1` / `z` / `z` *                                                      |
+------+-----------+---------------------------------------------------------------------------------------+
| 3    | `ie`      | Energy mesh: `eng` ([T-Deposit2] `eng1`)                                              |
+------+-----------+---------------------------------------------------------------------------------------+
| 4    | `it`      | Time mesh                                                                             |
+------+-----------+---------------------------------------------------------------------------------------+
| 5    | `ia`      | Angle mesh                                                                            |
+------+-----------+---------------------------------------------------------------------------------------+
| 6    | `il`      | LET mesh                                                                              |
+------+-----------+---------------------------------------------------------------------------------------+
| 7    | `ip`      | Particle type / group (`part =`)                                                      |
+------+-----------+---------------------------------------------------------------------------------------+
| 8    | `ic`      | Special: [T-Deposit2] `eng2`, [T-Yield] `mass`/`charge`/`chart`, [T-Interact] `act`   |
+------+-----------+---------------------------------------------------------------------------------------+
| 9    | `ierr`    | `= 0/1/2`, Value / relative uncertainty / absolute uncertainty *                      |
+======+===========+=======================================================================================+
| *exceptional behavior with [T-Cross] tally when `enclos = 0` is set; see full docs                       |
+======+===========+=======================================================================================+

`PHITS Tools` is also capable of parsing the "dump" output files (both binary and ASCII formats) 
that are available for some tallies, and it can also automatically detect, parse, and process all PHITS 
output files within a provided directory, very convenient for PHITS simulations employing 
multiple tallies (each with its own output file) whose output are to be studied in Python. 
The `PHITS Tools` module can be used either by 
(1) importing it as a Python module in a script and calling its functions, 
(2) running it in the command line via its CLI with a provided PHITS output
 file (or directory of files) and settings flags/options, or 
(3) running it without any arguments to launch a GUI stepping the user through 
the various output processing options and settings within `PHITS Tools`.

When used as an imported module, `PHITS Tools` provides a number of supplemental
functions aiding with further analyses, such as tools for constructing one's own 
tally over the history-by-history output of the "dump" files, rebinning histogrammed 
results to a different desired binning structure, applying effective dose 
conversion coefficients from ICRP 116 [@ICRP116_ref_withauthors] to tallied particle 
fluences, or retrieving a PHITS-input-formatted [Material] section entry (including 
its corresponding density) from a large database of over 300 materials (primarily
consisting of the selection of matierials within the PNNL Compendium of Material 
Composition Data for Radiation Transport Modeling [@PNNL_materials_compendium]),
among other useful side functions.

`DCHAIN Tools` is a separate Python module for handling the outputs of the DCHAIN code and 
is included as a submodule within the `PHITS Tools` repository.  Its primary function 
parses all of the various output files of the DCHAIN code and compiles the metadata
and numeric results&mdash;the confluence of the specified regions, output time steps, 
all nuclides and their inventories (and derived quantities), and complex decay chain 
schemes illustrating the production/destruction mechanisms for all nuclides&mdash;into 
a single unified dictionary object.  The `DCHAIN Tools` module includes some additional
useful functions such as retreiving neutron activation cross sections from DCHAIN's built-in 
nuclear data libraries, calculating flux-weighted single-group activation cross sections, 
and visualizing and summarizing the most signiifcant nuclides (in terms of activity, 
decay heat, or gamma-ray dose) as a function of time.

In all, the `PHITS Tools` and `DCHAIN Tools` modules make the results produced by the PHITS and DCHAIN codes 
far more accessible for futher use, analyses, comparisons, and visualizations in 
Python, removing the initial hurdle of parsing and organizing the raw output from these codes, 
and provides some additional tools for easing further analyses and drawing conclusions from 
the PHITS and DCHAIN results.


<!--
https://joss.theoj.org/about

https://joss.readthedocs.io/en/latest/example_paper.html

`Gala` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for `Gala` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. `Gala` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

`Gala` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in `Gala` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike.-->

<!--
# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }


-->

# Acknowledgements

A portion of this work has been completed by the author while under the 
support of European Innovation Council (EIC) grant agreement number 101130979.
The EIC receives support from the European Union’s Horizon Europe research and innovation programme.

# References
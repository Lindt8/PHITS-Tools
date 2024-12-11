# Monte Carlo materials

These files were assembled from a variety of sources over time;
they just seek to compile information for materials to be used in Monte Carlo 
particle transport calculations in an easily accessible plain-text format. 
The first 372 entries are from the Compendium of Material Composition Data for
Radiation Transport Modeling (Rev. 1), PNNL-15870 Rev. 1, published by the
Pacific Northwest National Laboratory.  That document can be found at:
https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-15870Rev1.pdf
The sources for other entries are specified.

The files named `"MC_materials_by_*_fraction_for_*.txt"` contain the full
collection of materials already formatted for use in the PHITS and MCNP
Monte Carlo particle transport codes, ready to be copy/pasted into an input file and used.
Choice between atom and weight fraction is up to the user, as one may be 
preferable to the other if one wishes to make any compositional modifications
to any of the materials.  The "for_photons" files contain materials 
specified by their elemental composition, assuming natural isotopic abundances.
The "for_neutrons" files instead substitute some of the natural element
specifications for the individual most naturally abundant isotopes for 
those elements and also manually specify isotopic distributions for 
specific materials.

Within the `PHITS Tools` Python module, the `fetch_MC_material()` function can be used 
to access these material compositions within a Python script.
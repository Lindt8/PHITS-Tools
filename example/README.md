# Example usage of PHITS Tools

In this example, `example_tproduct.inp` is the PHITS input file, and it features 
the [T-Product] tally, which scores what particles and nuclides are produced from particle 
interactions (in this case, nuclear interactions). [T-Product] is one of the 
three special tallies that can be used with the `dump` parameter to output 
an additional "dump" file of event-by-event data.

The `product.out` file is the standard tally output file, and `product.eps` is the 
visualized output file automatically produced by PHITS (which is made by a 
secondary program which processes the `*.out` file to create the `*.eps` file). 
The `product_dmp.out` file is the "dump" output file, with 11 columns of data 
in ASCII format (since the tally has set the parameter `dump = -11`).

In `example_PHITS_tools.[py/ipynb]`, PHITS Tools is used to parse both the standard 
tally output file and the dump file.  See the comments in the code to be 
stepped through instructions for what is being done.  The `*.pickle` and 
`*.pickle.xz` files are produced by PHITS Tools, containing the numerical results
and metadata extracted from the PHITS output files.  The PNG file is a plot 
made using the PHITS Tools extracted output recreating the EPS file automatically 
produced by PHITS.

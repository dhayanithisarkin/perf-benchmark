# perf-benchmark

### How to Run?
* Execute `./run.sh` in home directory
* Enter DID you wish to use
* Enter Start and End timescales for Current data and Base data in [YYYY-MM-DD-HH] format.
* This is internally pass these parameters to script `./benchmark/drivers.py` and it will generate CSV files in `tmp` directory.
* Script will also run `tex_template.tex` to generate pdf report named `tex_template.pdf` in `benchmark` directory. You will need `pdflatex` installed on your system. 

# perf-benchmark

* How to Run?
1. Execute `./run.sh` in home directory
2. Enter DID you wish to use
3. Enter Start and End timescales for Current data and Base data in [YYYY-MM-DD-HH] format.
4. This is internally pass these parameters to script `./benchmark/drivers.py` and it will generate CSV files in `tmp` directory.
5. Script will also run `tex_template.tex` to generate pdf report named `tex_template.pdf`

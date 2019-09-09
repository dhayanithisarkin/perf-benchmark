# perf-benchmark

### How to Run?
* Execute `./run.sh` in home directory
* Enter DID you wish to use
* Enter Enviroment you want to use for symphony wavefront.
* Enter Start and End timescales for Current data and Base data in [YYYY-MM-DD-HH] format.
* This is internally pass these parameters to script `./benchmark/drivers.py` and it will generate CSV files in `tmp` directory.
* Script will also run `tex_template.tex` to generate pdf report named `tex_template.pdf` in `benchmark` directory. You will need `pdflatex` installed on your system. 

* Alternatively, you can directly pass passmeter to `./benchmark/drivers.py` by command line arguments of `./run.sh`. Sample input can be as following,
```
./run.sh -did DPDEEJ8 -se jazz -cs 2019-08-30-00 -ce 2019-09-01-00 -bs 2019-09-02-00 -be 2019-09-04-00
```

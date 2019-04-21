# traces2LTL

The goal is to learn an LTL formula that separates set of positive (P) and negative (N) traces. The resulting formula should be a model for every trace in P and should not be a model for any of the traces from N.
There are two methods in this repository - one that encodes the problem as a satisfiability of Boolean formula and gives it to Z3 solver, and the other that is based on decision tree learning.

Webdemo is available at [flie.mpi-sws.org](https://flie.mpi-sws.org/)
 
## Setup
- setup a virtualenvironment for python 3.6 ([link](http://virtualenvwrapper.readthedocs.io/en/latest/)) and activate it (`workon ...`)
- run `pip install -r requirements.txt` to qinstall all necessary python packages available from pip
- install Z3 with python bindings ([link](https://github.com/Z3Prover/z3#python))

## Running
- to test on a single example (set of positive and negative traces), runt `python experiment.py` with `--test_dt_method` or `--test_sat_method` (or both) and with the path to the file with the example provided as an argument `--traces` 
- to test on set of examples, one can run `python measureSolvingTime.py` with `--test_dt_method` or `--test_sat_method` and with the path to the folder containing the examples provided as an argument `--test_traces_folder`
- running `python measureSolvingTime.py --test_dt_method --test_sat_method` with no additional parameters takes the traces from `traces/generatedTest` and produces results in `experiments/test/`
- additionally, to make sure everything runs as it should one can run `pytest`

### Experiment Trace File Format
Experiment traces file consists of:
  - accepted traces
  - rejected traces
  - operators that a program can use
  - max depth to explore
  - the expected formula that describes this trace

An example trace looks like this
`1,1;1,0;0,1::1` and means that there are two variables (`x0` and `x1`) whose values in different timesteps are
 - x0 : 1,(1,0)*  
 - x1: 1,(0,1)*

 The value after separator `::` denotes the start of lasso that is being repeated forever. If it is missing, it assumes that the whole sequence is repeated indefinitely.

 

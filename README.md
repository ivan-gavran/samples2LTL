# traces2LTL

This branch implements learning LTL formulas from the set of positive examples (P) and a set of safety
formulas (f_1, f_2,...,f_k). The end goal is to learn a formula that is modeled by all the examples from P and
that implies all safety formulas.

The approach was to learn a formula consistent with P, and then find a counterexample on the `a<->b`
ultimately periodic trace, where `a` is length of the initial part and `b` is length of the lasso part.

It turns out that the approach is mostly useless (at least for the small size of set P): there are many formulas
consistent with P that are simply avoiding saying anything about the safety restrictions. Alternatively,

 
## Setup
- setup a virtualenvironment for python 3.6 ([link](http://virtualenvwrapper.readthedocs.io/en/latest/)) and activate it (`workon ...`)
- run `pip install -r requirements.txt` to qinstall all necessary python packages available from pip
- install Z3 with python bindings ([link](https://github.com/Z3Prover/z3#python))

## Running
- to test on a single example, run `python experiment.py --test_sat_method --max_num_formulas=5`.
That will learn on the examples defined in the file `traces/dummy.json`. If you want to test it on a different file,
add it to the argument list, e.g. ` python experiment.py --traces=traces/anotherFile.json --test_sat_method`

### Experiment Trace File Format
 Options are specified in the JSON format. (Don't forget commas between every two properties!)

The properties to specify are:

   - literals: propositional variables that will be part of positive or negative traces (not obligatory. If omitted, will be filled by everything occurring in traces)
   - positive: traces (paths) that the formula should model. They are formatted as the initial and the lasso part, separated by a vertical bar (|). Both parts consist of timesteps separated by a semi-colon (;). Each timestep contains the literals (propositional variables) that hold true in it, separated by a comma (,). If none of the literals is true in a timestep, it should be either empty, or a reserved word "null".
   - safety-restrictions: a list of formulas that should not be satisfied. (i.e., a found formula should imply their negation)
   - number-of-formulas: how many formulas to find (counts when to stop searching, even if none is found that implies negations of all safety restrictions)
   - max-depth-of-formula: maximum depth of any formula found by flie (default: 5)
   - operators: a list of LTL operators allowed in a formula (default: ["F", "->", "&", "|", "U", "G", "X"])
   
An example file is [here](traces/dummy.json) 


 

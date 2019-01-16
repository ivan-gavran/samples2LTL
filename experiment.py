import pdb
from z3 import *
import argparse
from smtEncoding.dagSATEncoding import DagSATEncoding
import os
from solverRuns import run_solver, run_dt_solver
from utils.Traces import Trace, ExperimentTraces
from multiprocessing import Process, Queue
import logging

def helper(m, d, vars):
    tt = { k : m[vars[k]] for k in vars if k[0] == d }
    return tt



 
def main():
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", dest="tracesFileName", default="traces/dummy.trace")
    parser.add_argument("--max_depth", dest="maxDepth", default='8')
    parser.add_argument("--start_depth", dest="startDepth", default='1')
    parser.add_argument("--iteration_step", dest="iterationStep", default='1')
    parser.add_argument("--test_dt_method", dest="testDtMethod", default=False, action='store_true')
    parser.add_argument("--test_sat_method", dest="testSatMethod", default=False, action='store_true')
    parser.add_argument("--timeout", dest="timeout", default=600, help="timeout in seconds")
    parser.add_argument("--log", dest="loglevel", default="WARNING")
    args,unknown = parser.parse_known_args()
    tracesFileName = args.tracesFileName
    
    
    """
    traces is 
     - list of different recorded values (traces)
     - each trace is a list of recordings at time units (time points)
     - each time point is a list of variable values (x1,..., xk) 
    """
    
    numeric_level = args.loglevel.upper()
    logging.basicConfig(level=numeric_level)
    logging.info("logging works")
    
    maxDepth = int(args.maxDepth)
    startDepth = int(args.startDepth)
    traces = ExperimentTraces()
    iterationStep = int(args.iterationStep)
    traces.readTracesFromFile(args.tracesFileName)
    finalDepth = int(args.maxDepth)
    traces = ExperimentTraces()
    traces.readTracesFromFile(tracesFileName)
    solvingTimeout = int(args.timeout)
    print(traces)
    timeout = int(args.timeout)
    if args.testSatMethod == True:
        [formula, timePassed] = run_solver(finalDepth=maxDepth, traces=traces, startValue=startDepth, step=iterationStep)
        print("formula: "+str(formula)+", timePassed: "+str(timePassed))
        
    
    if args.testDtMethod == True:
        
        [timePassed, numAtoms, numPrimitives] = run_dt_solver(traces=traces)
        logging.info("timePassed: {0}, numAtoms: {1}, numPrimitives: {2}".format(str(timePassed), str(numAtoms), str(numPrimitives)))
        
    
    #print(traces)
    
#     if dtSolver == False:
#         run_solver()
#     
#     #for i in range(3,maxDepth):
#     for i in range(1,maxDepth):
#         fg = DagSATEncoding(i, traces)
#         fg.encodeFormula()
#         
#         
#         
#         if fg.solver.check() == sat:
#             
#             
#             print("depth %d: sat"%i)
#             m = fg.solver.model()
#             formula = fg.reconstructWholeFormula(m)
#             print(formula)
#             if not traces.isFormulaConsistent(formula):
#                 print("FORMULA NOT CONSISTENT")
#             #d = fg.readPropValue('c',1,0, m)
#             with open('log/model.txt', 'w') as debugFile:
#                 debugFile.write(repr(m))
#             break
#         elif fg.solver.check() == unsat:
#             print('depth %d: unsat'%i)
#         else:
#             print('unknown')
# 
#     with open('log/solver.txt', 'w') as debugFile:
#         debugFile.write(repr(fg.solver))
    
            

if __name__ == "__main__":
    main()


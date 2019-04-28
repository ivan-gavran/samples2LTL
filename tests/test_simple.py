import glob
import sys
import pdb
from z3 import *

from smtEncoding.treeSATEncoding import TreeSATEncoding
from smtEncoding.dagSATEncoding import DagSATEncoding
from utils.Traces import ExperimentTraces

from utils.SimpleTree import Formula



testTracesFolder ='traces/tests/'
maxDepth = 5



def test_run():
    run(TreeSATEncoding)
    run(DagSATEncoding)

def run(encoder):
    allFiles =glob.glob(testTracesFolder+'*') 
    
    for testFileName in allFiles:
        foundSat = False
        print(testFileName)
        if '~' in testFileName:
            continue
        
        #acceptedTraces, rejectedTraces, availableOperators, expectedResult, depth = readTestTraceFile(testFileName, maxDepth)
        
        traces = ExperimentTraces()
        traces.readTracesFromFile(testFileName)
        print(traces)
        
        if traces.depthOfSolution == None or traces.depthOfSolution < 0:
            finalDepth = maxDepth
        else:
            finalDepth = traces.depthOfSolution

        with open('log/solver.txt', 'w+') as debugFile:
            for i in range(1,finalDepth+1):
                fg = encoder(i, traces)
                fg.encodeFormula()

                debugFile.write(repr(fg.solver))
            if fg.solver.check() == sat:
                foundSat = True
                print("depth %d: sat"%i)
                m = fg.solver.model()
                with open('log/model.txt', 'w+') as debugFile:
                    debugFile.write(repr(m))
                
                formula = fg.reconstructWholeFormula(m)
                print(formula)
                assert(traces.isFormulaConsistent(formula))
                break
            elif fg.solver.check() == unsat:
                print("depth %d: unsat"% i)
                
                
            else:
                assert(False)
        if foundSat == False:
            print("unsat even after reaching max depth")
            assert(traces.isFormulaConsistent(None))
                    
if __name__ == "__main__":
    test_run()
    
        
        




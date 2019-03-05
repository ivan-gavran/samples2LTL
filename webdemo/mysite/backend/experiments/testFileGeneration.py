import pdb
import random

from utils.SimpleTree import SimpleTree, Formula
from utils.Traces import Trace, ExperimentTraces

operatorsAndArities = {'G':1, 'F':1, '!':1, 'U':2, '&':2,'|':2, '->':2, 'X':1, 'prop':0}

def generateTracesFromFormula(formula, lengthOfTrace, minNumberOfAccepting, minNumberOfRejecting, totalMax = 20, numSuperfluousVars=1, generateExactNumberOfTraces=False):
    allVars = formula.getAllVariables()
    allTraces = {"accepting":[], "rejecting":[]}
    numberOfVars = len(allVars) + numSuperfluousVars
    depthOfFormula = formula.getDepth()
    totalNumberOfTrials = 0
    random.seed()
    
    
    while (len(allTraces["accepting"]) <= minNumberOfAccepting or len(allTraces["rejecting"]) <= minNumberOfRejecting)\
    and len(allTraces["accepting"]) + len(allTraces["rejecting"]) < totalMax: 
        
        lassoStart = random.randint( 0, lengthOfTrace-1 )
        traceVector = [ [random.randint(0,1) for _ in range(numberOfVars)] for _ in range(lengthOfTrace) ] 
        
        trace = Trace(traceVector, lassoStart)
        totalNumberOfTrials += 1
        if generateExactNumberOfTraces == True and totalNumberOfTrials > totalMax:
            break
        if trace.evaluateFormulaOnTrace(formula) == True:
            if generateExactNumberOfTraces == True and len(allTraces["accepting"]) == minNumberOfAccepting:
                continue
            allTraces["accepting"].append(trace)
        else:
            if generateExactNumberOfTraces == True and len(allTraces["rejecting"]) == minNumberOfRejecting:
                continue
            allTraces["rejecting"].append(trace)
    
    traces = ExperimentTraces(tracesToAccept=allTraces["accepting"], tracesToReject=allTraces["rejecting"], depth = depthOfFormula, possibleSolution = formula)
    return traces

        
    
    


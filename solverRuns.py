import sys
from multiprocessing import Process, Queue
from smtEncoding.dagSATEncoding import DagSATEncoding
from pytictoc import TicToc
from z3 import *
import pdb
from utils import config
from formulaBuilder.DTFormulaBuilder import DTFormulaBuilder
from formulaBuilder.AtomBuilder import AtomBuilder, AtomBuildingStrategy

def run_solver(finalDepth, traces, startValue=1, step=1, q = None, encoder=DagSATEncoding):
    
    try:
        if q != None:
            separateProcess = True
        else:
            separateProcess = False
        t = TicToc()
        t.tic()
        foundSat = False
        
        for i in range(startValue,finalDepth+1, step):
            fg = encoder(i, traces)
            fg.encodeFormula()
            
            if fg.solver.check() == sat:
                foundSat = True
                print("depth %d: sat"%i)
                timePassed = t.tocvalue()
                m = fg.solver.model()
                
                formula = fg.reconstructWholeFormula(m)
                print(str(formula))
                if separateProcess == True:
                    q.put([formula, timePassed])
                    break
                else:
                    return [formula, timePassed]
                
                
            elif fg.solver.check() == unsat:
                print("depth %d: unsat"% i)
                
                
            else:
                assert(False)
        if foundSat == False:
            timePassed = t.tocvalue()
            print("unsat even after reaching max depth")
            if separateProcess == True:
                q.put([Formula("empty"), timePassed])
            else:
                return [Formula("empty"), timePassed]
    except Exception as e:
        print(e)
        sys.exit(1)        

def run_dt_solver(traces, subsetSize=config.DT_SUBSET_SIZE, txtFile="treeRepresentation.txt", strategy=config.DT_SAMPLING_STRATEGY, decreaseRate=config.DT_DECREASE_RATE,\
                  repetitionsInsideSampling=config.DT_REPETITIONS_INSIDE_SAMPLING, restartsOfSampling=config.DT_RESTARTS_OF_SAMPLING, q = None, encoder=DagSATEncoding,):

    #try:
        config.encoder = encoder
        if q != None:
            separateProcess = True
        else:
            separateProcess = False
        ab = AtomBuilder()
        ab.getExamplesFromTraces(traces)
        #samplingStrategy = config.DT_SAMPLING_STRATEGY
        samplingStrategy = strategy
        #decreaseRate = config.DT_DECREASE_RATE
        decreaseRate = decreaseRate
        t = TicToc()
        t.tic()
        (atoms, atomTraceEvaluation) = ab.buildAtoms(sizeOfPSubset=subsetSize, strategy = samplingStrategy, sizeOfNSubset=subsetSize, probabilityDecreaseRate=decreaseRate,\
                      numRepetitionsInsideSampling=repetitionsInsideSampling, numRestartsOfSampling = restartsOfSampling)
        fb = DTFormulaBuilder(features = ab.atoms, data = ab.getMatrixRepresentation(), labels = ab.getLabels())
        fb.createASeparatingFormula()
        timePassed = t.tocvalue()
        atomsFile = "atoms.txt"
        treeTxtFile = txtFile
        ab.writeAtomsIntoFile(atomsFile)
        
        
        numberOfUsedPrimitives = fb.numberOfNodes()
        fb.tree_to_text_file(treeTxtFile)
    #    return (timePassed, len(atoms), numberOfUsedPrimitives)
        if separateProcess == True:
            q.put([timePassed, len(atoms), numberOfUsedPrimitives])
        else:
            return [timePassed, len(atoms), numberOfUsedPrimitives]
#     except Exception as e:
#         print(e)
#         sys.exit(1)

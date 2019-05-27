import sys
from multiprocessing import Process, Queue
from smtEncoding.dagSATEncoding import DagSATEncoding
from smtEncoding.SATOfLTLEncoding import SATOfLTLEncoding
from pytictoc import TicToc
from z3 import *
import pdb
from utils import config
from formulaBuilder.DTFormulaBuilder import DTFormulaBuilder
from formulaBuilder.AtomBuilder import AtomBuilder, AtomBuildingStrategy
from formulaBuilder.satQuerying import get_models, get_models_with_safety_restrictions
from utils.SimpleTree import Formula


def run_solver(finalDepth, traces, maxNumOfFormulas=1, startValue=1, step=1, q=None, encoder=DagSATEncoding):


    if q is not None:
        separate_process = True
    else:
        separate_process = False

    t = TicToc()
    t.tic()

    try:
        safety_restrictions = traces.safety_restrictions
    except:
        safety_restrictions = None
    if safety_restrictions:
        results = get_models_with_safety_restrictions(safety_restrictions=safety_restrictions, traces = traces, final_depth=finalDepth,
                                                      literals=traces.literals, encoder=encoder, operators=traces.operators, max_num_solutions=maxNumOfFormulas)
    else:
        results = get_models(finalDepth, traces, startValue, step, encoder, maxNumOfFormulas)

    time_passed = t.tocvalue()

    if separate_process == True:
        q.put([results, time_passed])
    else:
        return [results, time_passed]


def run_dt_solver(traces, subsetSize=config.DT_SUBSET_SIZE, txtFile="treeRepresentation.txt",
                  strategy=config.DT_SAMPLING_STRATEGY, decreaseRate=config.DT_DECREASE_RATE, \
                  repetitionsInsideSampling=config.DT_REPETITIONS_INSIDE_SAMPLING,
                  restartsOfSampling=config.DT_RESTARTS_OF_SAMPLING, q=None, encoder=DagSATEncoding, ):
    # try:
    config.encoder = encoder
    if q != None:
        separateProcess = True
    else:
        separateProcess = False
    ab = AtomBuilder()
    ab.getExamplesFromTraces(traces)
    # samplingStrategy = config.DT_SAMPLING_STRATEGY
    samplingStrategy = strategy
    # decreaseRate = config.DT_DECREASE_RATE
    decreaseRate = decreaseRate
    t = TicToc()
    t.tic()
    (atoms, atomTraceEvaluation) = ab.buildAtoms(sizeOfPSubset=subsetSize, strategy=samplingStrategy,
                                                 sizeOfNSubset=subsetSize, probabilityDecreaseRate=decreaseRate, \
                                                 numRepetitionsInsideSampling=repetitionsInsideSampling,
                                                 numRestartsOfSampling=restartsOfSampling)
    fb = DTFormulaBuilder(features=ab.atoms, data=ab.getMatrixRepresentation(), labels=ab.getLabels())
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

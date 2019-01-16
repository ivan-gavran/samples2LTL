import glob
import sys
import pdb
from z3 import *
from pytictoc import TicToc
import csv
import os
import json
from smtEncoding.treeSATEncoding import TreeSATEncoding
from smtEncoding.dagSATEncoding import DagSATEncoding
from utils.Traces import ExperimentTraces
from utils.SimpleTree import Formula
from utils import config
from multiprocessing import Process, Queue
import time
import argparse
from _datetime import datetime
from doctest import testfile
from formulaBuilder.AtomBuilder import AtomBuilder, AtomBuildingStrategy
from formulaBuilder.DTFormulaBuilder import DTFormulaBuilder
import logging
from formulaBuilder.AtomBuildingStrategy import AtomBuildingStrategy
from solverRuns import run_solver, run_dt_solver




    


def test_run(encoder, outputFile, outputFolder, testTracesFolder, solvingTimeout, testName,\
             dtDecreaseRate, dtStrategy, dtRestarts, dtRepetitions, runSatMethod,runDecisionTreeMethod = True,\
             iterationStartValue=1, iterationStep=1):
    if not os.path.isfile(outputFile):
        headers = ["time of writing", "name of the test file", "number of accepting traces", "number or rejecting traces", "depth of formula", "number of variables",\
                                  "max length of traces", "specified formula"]
        
        if runSatMethod == True:
            headers += ["solving time sat", "obtained formula sat", "comment sat"]
        if runDecisionTreeMethod == True:
            headers += ["dt solving time", "dt num primitive candidates", "dt num primitives used", "dt subset sizes", "dt tree txt representation"]
        with open(outputFile, "w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
    allFiles =glob.glob(testTracesFolder+'*.trace')
    
    for testFileName in allFiles:
        logging.info("--- file: "+testFileName)
        try:
            comment = ""
            q = Queue()
            qDT = Queue()
            print(testFileName)
            if '~' in testFileName:
                continue
            
            traces = ExperimentTraces()
            traces.readTracesFromFile(testFileName)
            
            #this is due to different definition of depth in the naive, binary three encoding. now "depth" is overall number of formulas, while before it was the depth of the tree
            finalDepth = 2**traces.depthOfSolution + traces.numVariables
            
            assert(finalDepth != None)
            resultData = [datetime.now().strftime("%Y-%m-%d %H:%M"), testFileName, len(traces.acceptedTraces), len(traces.rejectedTraces), traces.depthOfSolution,\
                          traces.numVariables, traces.maxLengthOfTraces, str(traces.possibleSolution)]
            if runSatMethod == True:
                formula = None
                timePassed = 0
                p = Process(target = run_solver, args = (finalDepth, traces, iterationStartValue, iterationStep, q))
                p.start()
                 
                p.join(timeout=solvingTimeout)
                 
                p.terminate()
                 
                while p.exitcode == None:
                    print("going to sleep")
                    time.sleep(1)
                if p.exitcode == 0:
                    [formula, timePassed] = q.get()
                    if not traces.isFormulaConsistent(formula):
                        comment = "formula not consistent with data"
                   
                     
                else:
                    [formula, timePassed] = ["/", "/"]
                    comment = "timeout: "+str(solvingTimeout)
                #[formula, timePassed] = run_solver(finalDepth, traces)
                
    
                resultData += [timePassed, str(formula), comment]
            if runDecisionTreeMethod:
                
                subsetSize = config.DT_SUBSET_SIZE
                treeRepresentationFile = outputFolder+os.path.basename(testFileName).split('.')[0]+"_tree.txt"
                print(treeRepresentationFile)
                p = Process(target = run_dt_solver, args = (traces, subsetSize, treeRepresentationFile, dtStrategy, dtDecreaseRate,\
                                                            dtRepetitions, dtRestarts, qDT))
                #run_dt_solver(testFileName, subsetSize, treeRepresentationFile, dtStrategy, dtDecreaseRate, dtRepetitions, dtRestarts)
                p.start()
                
                p.join(timeout=solvingTimeout)
                p.terminate()
                while p.exitcode == None:
                    logging.info("dt going to sleep")
                    time.sleep(1)
                if p.exitcode == 0:
                    [timePassedDt, numberOfPrimitiveCandidates, numberOfPrimitivesUsed] = qDT.get()
                else:
                    [timePassedDt, numberOfPrimitiveCandidates, numberOfPrimitivesUsed] = ["/", "/", "/"]
                    
                #(timePassedDt, numberOfPrimitiveCandidates, numberOfPrimitivesUsed) = run_dt_solver(testFileName, subsetSize, treeRepresentationFile)
                resultData += [str(timePassedDt), str(numberOfPrimitiveCandidates), str(numberOfPrimitivesUsed), str(subsetSize), treeRepresentationFile] 
                                 
            
            with open(outputFile, "a+") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(resultData)
        except Exception as e:
            raise e
            with open(outputFile, "a+") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), testFileName, "/", "/", "/",\
                                  "/", "/", "/", "/", "/", "exception: "+str(e)])
            
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_traces_folder", dest="testTracesFolder", default='traces/generatedTest/')
    parser.add_argument("--timeout", dest="timeout", default=600, help="timeout in seconds")
    parser.add_argument("--test_name", dest="testName", default="test")
    parser.add_argument("--test_dt_method", dest="testDtMethod", default=False, action='store_true')
    parser.add_argument("--test_sat_method", dest="testSatMethod", default=False, action='store_true')
    parser.add_argument("--dt_subset_size", dest="dtSubsetSize", default=10)
    parser.add_argument("--dt_decrease_rate", dest="dtDecreaseRate", default=0.5)
    parser.add_argument("--dt_restarts_of_sampling", dest="dtRestartsOfSampling", default=3)
    parser.add_argument("--dt_repetitions_inside_sampling", dest="dtRepetitionsInsideSampling", default=3)
    parser.add_argument("--dt_strategy", dest="dtStrategy", default=2)
    parser.add_argument("--encoder", dest="encoder", default='dag')
    parser.add_argument("--iteration_start_value", dest="iterationStartValue", default=1, type=int)
    parser.add_argument("--iteration_step", dest="iterationStep", default=1, type=int)
    
    args,unknown = parser.parse_known_args()
    timeout = int(args.timeout)
    testTracesFolder = args.testTracesFolder
    
    if args.encoder == 'dag':
        config.encoder = DagSATEncoding
    else:
        config.encoder = TreeSATEncoding
    
    if not testTracesFolder[-1] == '/':
        testTracesFolder = testTracesFolder + "/"
    outputFile = config.EXPERIMENTS_FOLDER + args.testName + "/stats.csv"
    outputFolder = os.path.dirname(outputFile)
    os.makedirs(outputFolder, exist_ok=True)
    outputFolder = outputFolder + "/"
    config.DT_SUBSET_SIZE = int(args.dtSubsetSize)
    loggingFile = config.EXPERIMENTS_FOLDER+args.testName+"/info.log"
    
    logging.basicConfig(level=logging.DEBUG,\
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',\
                        datefmt='%m-%d %H:%M',\
                        filename=loggingFile,\
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    
    info = {"traces":testTracesFolder, "name":args.testName, "timeout":timeout, "satEncoding":args.encoder, "iterationStartValue":args.iterationStartValue,\
            "iterationStep":args.iterationStep}
    if args.testDtMethod:
        dtInfo = {"decrease":args.dtDecreaseRate, "sampling_strategy":args.dtStrategy, "subset_size":args.dtSubsetSize, "repetitions_inside_sampling":args.dtRepetitionsInsideSampling}
        info["dt"] = dtInfo
        
    infoFile = outputFolder+"info.json"
    with open(infoFile, "w") as jsonOut:
        json.dump(info, jsonOut)
        
    strategy = AtomBuildingStrategy(int(args.dtStrategy))
    
    test_run(encoder = config.encoder, outputFile = outputFile, outputFolder = outputFolder, testTracesFolder = testTracesFolder,\
              solvingTimeout = timeout, testName = args.testName, runSatMethod = args.testSatMethod, runDecisionTreeMethod = args.testDtMethod,\
              dtDecreaseRate=float(args.dtDecreaseRate), dtStrategy=strategy, dtRestarts=int(args.dtRestartsOfSampling), dtRepetitions=int(args.dtRepetitionsInsideSampling),\
              iterationStartValue=args.iterationStartValue, iterationStep=args.iterationStep)
    
        
        
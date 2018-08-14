from useCases.DependencyGraph import DependencyGraph
from useCases.DependencyGraph2 import DependencyGraph2
from useCases.StateOfNodesDependencyGraph import StateOfNodesDependencyGraph
from useCases.AlternativeReceives import AlternativeReceives
from useCases.ReceivesDependencyGraph import ReceivesDependencyGraph
from useCases.ModifiedReceivesDependencyGraph import ModifiedReceivesDependencyGraph
import argparse
import pdb
from utils.Traces import ExperimentTraces, Trace
import z3



"""
this file creates traces from the logs of leader-election executions. The logs are created by hand from the automatic ones (folder "evenMoreAlternative") [the question is 
what is the right representation. if the logs are passed "as-is", the returned formula is something like 
"F(proc1 declares himself as a leader AND proc2 declares himself as a follower)"

The result of running this script is a traces file (defined by --traces_out option) that can be used to obtain LTL formula from it. 

The way to run: 
 python buildFaultyExecutionsGraph.py --property_file_faulty useCases/PCTCP/evenMoreAlternative/faultyExample.execution --property_file_correct useCases/PCTCP/evenMoreAlternative/correctMirror.execution useCases/PCTCP/evenMoreAlternative/0ReceivedFrom1.execution useCases/PCTCP/evenMoreAlternative/0CommitsYetCorrect.execution useCases/PCTCP/evenMoreAlternative/correctAfterAll.execution --traces_out=traces/useCases/statePtcp/state.trace
"""        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--property_file_faulty", dest="propertyFileFaulty", nargs='+', default=[\
                                                                                                 "useCases/newPCTCPData/experiments/pctcp-d2-nocrash-modified/135/execution",\
                                                                                                 
                                                                                    
                                                                                      ])
    parser.add_argument("--property_file_correct", dest="propertyFileCorrect", nargs='+', default=[\
                                                                                                   #"useCases/newPCTCPData/experiments/pctcp-d2-nocrash/136/execution",\
                                                                                                   #"useCases/newPCTCPData/experiments/pctcp-d2-nocrash/816/execution",\
                                                                                                  # "useCases/newPCTCPData/experiments/pctcp-d2-nocrash/456/execution",\
                                                                                                  # "useCases/newPCTCPData/experiments/pctcp-d2-nocrash/208/execution",\
                                                                                                  # "useCases/newPCTCPData/experiments/pctcp-d2-nocrash/1/execution",\
                                                                                                   "useCases/newPCTCPData/experiments/pctcp-d2-nocrash-modified/2/execution",\
                                                                                                   #"useCases/newPCTCPData/experiments/pctcp-d2-nocrash/3/execution",\
                                                                                                   #"useCases/newPCTCPData/experiments/pctcp-d2-nocrash/4/execution",\
                                                                                      ])
    parser.add_argument("--traces_out", dest="tracesFileName", default="traces/useCases/ptcp-d2-nocrash/generated.trace")
    parser.add_argument("--num_linearization", dest="numTracesLinearizations", type=int, default=5)
    
    
    args,unknown = parser.parse_known_args()
    
    faultyTraces = None
    correctTraces = None
    faultyExecutions = args.propertyFileFaulty
    correctExecutions = args.propertyFileCorrect
    
    #depGraph = StateOfNodesDependencyGraph
    #depGraph = DependencyGraph
    #depGraph = ReceivesDependencyGraph
    #depGraph = AlternativeReceives
    depGraph = DependencyGraph2
    depGraph = ModifiedReceivesDependencyGraph
    for fileName in faultyExecutions:
        print(fileName)
        dgF = depGraph()
        dgF.readGraphFromPropertyFile(fileName)
        newTraces = dgF.generateTraces(maxNumberOfSolutions = args.numTracesLinearizations)
        if faultyTraces == None:
            faultyTraces = newTraces
        else:
            faultyTraces += newTraces
            
    for fileName in correctExecutions:
        dgF = depGraph()
        dgF.readGraphFromPropertyFile(fileName)
        newTraces = dgF.generateTraces(maxNumberOfSolutions = args.numTracesLinearizations)
        if correctTraces == None:
            correctTraces = newTraces
        else:
            correctTraces += newTraces
    
    
    
    experimentTraces = ExperimentTraces(tracesToAccept = [Trace(traceVector = faultyTr, lassoStart = (len(faultyTr)-1)) for faultyTr in faultyTraces],\
                                        tracesToReject = [Trace(traceVector = correctTr, lassoStart = (len(correctTr)-1)) for correctTr in correctTraces], depth = 10)
    
    for trace in correctTraces:
        if trace in faultyTraces:
            print("problem!")
            print(trace)
            pdb.set_trace()
    for trace in faultyTraces:
        if trace in correctTraces:
            print("problem2!")
            pdb.set_trace()
    fileToWrite = args.tracesFileName
    experimentTraces.writeTracesToFile(fileToWrite)


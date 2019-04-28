from utils.Traces import Trace, ExperimentTraces
import glob

testTracesFolder ='traces/tests/'



def test_next_and_future():
    allFiles =glob.glob(testTracesFolder+'*') 
    for testFileName in allFiles:
        print(testFileName)
        if 'And' not in testFileName or '~' in testFileName:
            continue
        
        #acceptedTraces, rejectedTraces, availableOperators, expectedResult, depth = readTestTraceFile(testFileName, maxDepth)
        traces = ExperimentTraces()
        traces.readTracesFromFile(testFileName)
        
        
        for trace in traces.acceptedTraces + traces.rejectedTraces:
            print("trace: \n%s" % repr(trace))
            for currentPos in range(trace.lengthOfTrace):
                
                print("current position %d"%currentPos)
                print("next: "+str(trace.nextPos(currentPos)))
                print("future: %s\n"%str(trace.futurePos(currentPos)))
            print("=========\n\n")
        
if __name__ == "__main__":
    test_next_and_future()
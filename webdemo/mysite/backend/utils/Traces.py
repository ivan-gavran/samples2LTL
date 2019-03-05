import pdb
from ..utils.SimpleTree import SimpleTree, Formula
import io


def lineToTrace(line):
        lassoStart = None
        try:
            traceData, lassoStart = line.split('::')
        except:
            traceData = line
        traceVector = [[bool(int(varValue)) for varValue in varsInTimestep.split(',')] for varsInTimestep in traceData.split(';')]
        trace = Trace(traceVector, lassoStart)
        return trace

class Trace:
    def __init__(self, traceVector, lassoStart = None, intendedEvaluation = None):
        self.lengthOfTrace = len(traceVector)
        self.intendedEvaluation = intendedEvaluation
        if lassoStart != None:
            self.lassoStart = int(lassoStart)
            if self.lassoStart >= self.lengthOfTrace:
                pdb.set_trace()
                raise Exception("lasso start = %s is greater than any value in trace (trace length = %s) -- must be smaller"%(self.lassoStart, self.lengthOfTrace))
        else:
            self.lassoStart = 0
        assert self.lengthOfTrace > 0 and self.lassoStart <= self.lengthOfTrace
        self.numVariables = len(traceVector[0])
        self.traceVector = traceVector
        
    def __repr__(self):
         return repr(self.traceVector) + "\n"+repr(self.lassoStart)+"\n\n"
    
    def nextPos(self, currentPos):
        if currentPos == self.lengthOfTrace - 1:
            return self.lassoStart
        else:
            return currentPos + 1
    
    """
    thought this function would be necessary, but didn't use it finally :)
    """
#     def valueAtIndex(self, n):
#         if n < self.lengthOfTrace:
#             return self.traceVector[n]
#         else:
#             lengthOfPrefix = self.lassoStart
#             lassoLength = self.lengthOfTrace - self.lassoStart
#             rightIndex = lengthOfPrefix + ((n - self.lengthOfTrace) % lassoLength)
#             return self.traceVector[rightIndex] 
            
    
    def futurePos(self, currentPos):
        futurePositions = []
        alreadyGathered = set()
        while currentPos not in alreadyGathered:
            futurePositions.append(currentPos)
            alreadyGathered.add(currentPos)
            currentPos = self.nextPos(currentPos)
        #always add a new one so that all the next-relations are captured
        futurePositions.append(currentPos)
        return futurePositions
    def evaluateFormulaOnTrace(self, formula):
        
        nodes = list(set(formula.getAllNodes()))
        self.truthAssignmentTable = { node : [None for _ in range(self.lengthOfTrace)] for node in nodes }
        # NOT ENFORCED assumption: formulas are named in order x0, x1, x2,...
        for i in range(self.numVariables):
            self.truthAssignmentTable[Formula("x"+str(i))] = [ bool(measurement[i]) for measurement in self.traceVector]
        
        return self.truthValue(formula, 0)
    
    
    def truthValue(self, formula, timestep):
        futureTracePositions = self.futurePos(timestep)
        tableValue = self.truthAssignmentTable[formula][timestep]
        if tableValue  !=  None:
            return tableValue
        else:
            label = formula.label
            if label == '&':
                return self.truthValue(formula.left, timestep) and self.truthValue(formula.right, timestep)
            elif label =='|':
                return self.truthValue(formula.left, timestep) or self.truthValue(formula.right, timestep)
            elif label == '!':
                return not self.truthValue(formula.left, timestep)
            elif label == '->':
                return not self.truthValue(formula.left, timestep) or self.truthValue(formula.right, timestep)
            elif label == 'F':
                return max( [ self.truthValue(formula.left, futureTimestep) for futureTimestep in futureTracePositions] )
                #return self.truthValue(formula.left, timestep) or self.truthValue(formula, self.nextPos(timestep))
            elif label == 'G':
                return min( [ self.truthValue(formula.left, futureTimestep) for futureTimestep in futureTracePositions] )
                #return self.truthValue(formula.left, timestep) and not self.truthValue(formula, self.nextPos(timestep))
            elif label == 'U':
                return    max([self.truthValue(formula.right, futureTimestep) for futureTimestep in futureTracePositions]) == True\
                    and(\
                      self.truthValue(formula.right, timestep)\
                      or \
                         (self.truthValue(formula.left, timestep) and self.truthValue(formula, self.nextPos(timestep)))\
                    )
            elif label == 'X':
                return self.truthValue(formula.left, self.nextPos(timestep))
        
defaultOperators = ['G', 'F', '!', 'U', '&','|', '->', 'X']   


class ExperimentTraces:
    def __init__(self, tracesToAccept = None, tracesToReject = None, operators = ['G', 'F', '!', 'U', '&','|', '->', 'X'], depth = None, possibleSolution = None):
        if tracesToAccept != None:
            self.acceptedTraces = tracesToAccept
            
        else:
             self.acceptedTraces = []
         
        if tracesToReject != None:
            self.rejectedTraces = tracesToReject
        else:
            self.rejectedTraces = []
        if tracesToAccept != None and tracesToAccept != None:
            self.maxLengthOfTraces = 0
            for trace in self.acceptedTraces + self.rejectedTraces:
                if trace.lengthOfTrace > self.maxLengthOfTraces:
                    self.maxLengthOfTraces = trace.lengthOfTrace
            
            try:
                self.numVariables = self.acceptedTraces[0].numVariables
            except:
                self.numVariables = self.rejectedTraces[0].numVariables
    
        
        self.operators = operators
        self.depthOfSolution = depth
        self.possibleSolution = possibleSolution
        
        
        
        
    
    def isFormulaConsistent(self, f):
        # not checking consistency in the case that traces are contradictory
        if f == None:
            return True
        for accTrace in self.acceptedTraces:
            if accTrace.evaluateFormulaOnTrace(f) == False:
                return False
        
        
        for rejTrace in self.rejectedTraces:
            if rejTrace.evaluateFormulaOnTrace(f) == True:
                return False
        return True
    
    def __repr__(self):
        returnString = ""
        returnString += "accepted traces:\n"
        for trace in self.acceptedTraces:
            returnString += repr(trace)
        returnString += "\nrejected traces:\n"
        
        for trace in self.rejectedTraces:
            returnString += repr(trace)
        returnString += "depth of solution: "+repr(self.depthOfSolution)+"\n"
        return returnString
    def writeTracesToFile(self, tracesFileName):
        with open(tracesFileName, "w") as tracesFile:
            for accTrace in self.acceptedTraces:
                line = ';'.join( ','.join( str(k) for k in t ) for t in accTrace.traceVector ) + "::"+str(accTrace.lassoStart)+"\n"
                tracesFile.write(line)
            tracesFile.write("---\n")
            for rejTrace in self.rejectedTraces:
                line = ';'.join( ','.join( str(k) for k in t ) for t in rejTrace.traceVector ) + "::"+str(rejTrace.lassoStart)+"\n"
                tracesFile.write(line)
            tracesFile.write("---\n")
            tracesFile.write( ','.join(self.operators) + '\n')
            tracesFile.write("---\n")
            tracesFile.write(str(self.depthOfSolution) + '\n')
            tracesFile.write("---\n")
            tracesFile.write(str(self.possibleSolution))
                      
    def readTracesFromString(self, s):
        stream = io.StringIO(s)
        self.readTracesFromStream(stream)

    def readTracesFromStream(self, stream):

        readingMode = 0


        operators = None
        for line in stream:
            lassoStart = None
            if '---' in line:
                readingMode += 1
            else:
                if readingMode == 0:

                    trace = lineToTrace(line)
                    trace.intendedEvaluation = True

                    self.acceptedTraces.append(trace)

                elif readingMode == 1:
                    trace = lineToTrace(line)
                    trace.intendedEvaluation = False
                    self.rejectedTraces.append(trace)

                elif readingMode == 2:
                    operators = [s.strip() for s in line.split(',')]

                elif readingMode == 3:
                    self.depthOfSolution = int(line)
                elif readingMode == 4:
                    possibleSolution = line.strip()
                    if possibleSolution.lower() == "none":
                        self.possibleSolution = None
                    else:
                        self.possibleSolution = Formula.convertTextToFormula(possibleSolution)

                else:
                    break
        if operators == None:
            self.operators = defaultOperators
        else:
            self.operators = operators

        self.maxLengthOfTraces = 0
        for trace in self.acceptedTraces + self.rejectedTraces:
            if trace.lengthOfTrace > self.maxLengthOfTraces:
                self.maxLengthOfTraces = trace.lengthOfTrace

        # an assumption that number of variables is the same across all the traces
        try:
            self.numVariables = self.acceptedTraces[0].numVariables
        except:
            self.numVariables = self.rejectedTraces[0].numVariables
        for trace in self.acceptedTraces + self.rejectedTraces:
            if trace.numVariables != self.numVariables:
                raise Exception("wrong number of variables")

    def readTracesFromFile(self, tracesFileName):
        
        pathToTracesFile = tracesFileName
        readingMode = 0

        with open(pathToTracesFile) as tracesFile:
            operators = None
            for line in tracesFile:
                lassoStart = None
                if '---' in line:
                    readingMode += 1
                else:
                    if readingMode == 0:
                        
                        trace = lineToTrace(line)
                        trace.intendedEvaluation = True
                        
                        self.acceptedTraces.append(trace)

                    elif readingMode == 1:
                        trace = lineToTrace(line)
                        trace.intendedEvaluation = False
                        self.rejectedTraces.append(trace)
                        
                    elif readingMode == 2:
                        operators = [s.strip() for s in line.split(',')]
                    
                    elif readingMode == 3:
                        self.depthOfSolution = int(line)
                    elif readingMode == 4:
                        possibleSolution = line.strip()
                        if possibleSolution.lower() == "none":
                            self.possibleSolution = None
                        else:
                            self.possibleSolution = Formula.convertTextToFormula(possibleSolution)
                    
                    else:
                        break
        if operators == None:
            self.operators = defaultOperators
        else:
            self.operators = operators
        
        
        self.maxLengthOfTraces = 0
        for trace in self.acceptedTraces + self.rejectedTraces:
            if trace.lengthOfTrace > self.maxLengthOfTraces:
                self.maxLengthOfTraces = trace.lengthOfTrace
       
        
        # an assumption that number of variables is the same across all the traces
        try:
            self.numVariables = self.acceptedTraces[0].numVariables
        except:
            self.numVariables = self.rejectedTraces[0].numVariables
        for trace in self.acceptedTraces + self.rejectedTraces:
            if trace.numVariables != self.numVariables:
                raise Exception("wrong num of variables")
        

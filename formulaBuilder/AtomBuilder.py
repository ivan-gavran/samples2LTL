from utils.Traces import lineToTrace, ExperimentTraces
from smtEncoding.treeSATEncoding import TreeSATEncoding

import random
import pdb
from z3 import *
import logging
from .AtomBuildingStrategy import AtomBuildingStrategy
from utils import config


maxDepth = 8


    

class AtomBuilder:
    
    def __init__(self):
        self.positiveExamples = []
        self.negativeExamples = []
        self.matrixRepresentation = None
        
        self.positiveExamplesProbabilities = {}
        self.negativeExamplesProbabilities = {}
        self.atoms = []
        
    def readExamples(self, fileName):
        
        with open(fileName) as examplesFile:
            setToFill = self.positiveExamples
            intendedEvaluation = True
            changedMode = False
            for line in examplesFile:
                if '---' in line:
                    if changedMode == False:
                        setToFill = self.negativeExamples
                        intendedEvaluation = False
                        changedMode = True
                    else:
                        break
                else:
                    trace = lineToTrace(line)
                    trace.intendedEvaluation = intendedEvaluation
                    setToFill.append(trace)
        self.separationDict = {(p, n): False for p in self.positiveExamples for n in self.negativeExamples} 
        self.totalNumberOfExamples = len(self.positiveExamples) + len(self.negativeExamples)
        
    def getExamplesFromTraces(self, traces):
        self.positiveExamples = traces.acceptedTraces
        self.negativeExamples = traces.rejectedTraces
        self.separationDict = {(p, n): False for p in self.positiveExamples for n in self.negativeExamples} 
        self.totalNumberOfExamples = len(self.positiveExamples) + len(self.negativeExamples)
    
    def getLabels(self):
        return [True for _ in self.positiveExamples]+[False for _ in self.negativeExamples]    
    def getMatrixRepresentation(self):
      
        if self.matrixRepresentation == None:
            self.matrixRepresentation = [[self.atomTraceEvaluation[formula][tr] for tr in self.positiveExamples+self.negativeExamples] for formula in self.atoms]
            self.matrixRepresentation = list(map(list, zip( *self.matrixRepresentation )))
        return self.matrixRepresentation
    
    def writeAtomsIntoFile(self, fileName):
        with open(fileName, "w") as output:
            logging.info("saving atoms into file %s"%output.name)
            for f in self.atoms:
                output.write(str(f)+"\n")
    
    def writeMatrixRepresentationIntoFile(self, fileName):
        m = self.getMatrixRepresentation()
        with open(fileName, 'w') as outputFile:
            logging.info("writing matrix representation into file %s"%outputFile.name)
            for primitiveFormulaValues in m:
                s = ",".join([str(int(k)) for k in primitiveFormulaValues])
                outputFile.write(s+"\n")
            
        
        
    """
    this functions builds atomic formulas (atoms) to be used in a decision trees. depending on a strategy it does:
     a) strategy = RANDOM_SAMPLING
        it samples (sizeOfPSubset, sizeOfNSubset) from all the traces. Encodes it into SAT and creates a formula distinguishing them. Then, it multiplies the probability of the chosen ones by
        `probabilityDecreaseRate` (<= 1) and normalizes the rest.
         
    b) strategy = BOOST_MISCLASSIFIED
        it samples (sizeOfPSubset, sizeOfNSubset) from all the traces. Encodes it into SAT and creates a formula distinguishing them. Then, it multiplies the probability of 
        the ones that are correctly classified under that formula by `probabilityDecreaseRate` (<= 1) and normalizes the rest (thus increasing the probability of the misclassified ones)
    
    c) strategy = CHOOSE_NOT_SEPARATED adds some pairs that were not distinguished by previous formulas and then some random subset of other formulas 
    In both cases the sampling is repeated `numRepetitionsInsideSampling` times and the whole process is restarted `numRestartsOfSampling` times
    """
    def buildAtoms(self, sizeOfPSubset, sizeOfNSubset, strategy = AtomBuildingStrategy.RANDOM_SAMPLING, probabilityDecreaseRate=1, \
                   numRepetitionsInsideSampling = 3, numRestartsOfSampling=3, insistOnCompleteSeparation = True):
        self.atomTraceEvaluation = {}
        numSeparatedByFormula = {}
        sampleRestarts = 0
        while min(self.separationDict.values()) == False:
        #while sampleRestarts < numRestartsOfSampling or min(self.separationDict.values()) == False:
            #pdb.set_trace()
            logging.info("sample restarts: {0}".format(sampleRestarts))
            #raise Exception("something went wrong")
            sampleRestarts += 1
            
            
            logging.info("starting new sampling session")
            if strategy == AtomBuildingStrategy.CHOOSE_NOT_SEPARATED and not sizeOfPSubset == sizeOfNSubset:
                raise ValueError('for strategy {0} P and N subsets have to be the same'.format(strategy))
            self.positiveExamplesProbabilities = {k : 1.0/len(self.positiveExamples) for k in self.positiveExamples}
            self.negativeExamplesProbabilities = {k : 1.0/len(self.negativeExamples) for k in self.negativeExamples}
            
            repetitions = 0
            negativeTraces = []
            positiveTraces= []    
            for _ in range(numRepetitionsInsideSampling):
                if min(self.separationDict.values()) == True:
                    break
                logging.info("sampling traces under strategy {0}".format(strategy))
                logging.info("size of the separationDict: {0}. size of separated part: {1}".format(len(self.separationDict), len([k for k in self.separationDict.keys() if self.separationDict[k] == True])))
                try:
                    if strategy == AtomBuildingStrategy.RANDOM_SAMPLING or strategy == AtomBuildingStrategy.BOOST_MISCLASSIFIED:
                        negativeTraces = random.choices(self.negativeExamples, weights = [ self.negativeExamplesProbabilities[ex] for ex in self.negativeExamples ], k = min(sizeOfNSubset, len(self.negativeExamples)))
                        positiveTraces = random.choices(self.positiveExamples, weights = [self.positiveExamplesProbabilities[ex] for ex in self.positiveExamples], k = min(sizeOfPSubset, len(self.positiveExamples)))
                    elif strategy == AtomBuildingStrategy.CHOOSE_NOT_SEPARATED:
                        if min(self.separationDict.values()) == True:
                            break
                        nonSeparatedPairs = random.choices([k for k in list(self.separationDict.keys()) if self.separationDict[k] == False], k = sizeOfPSubset)
                        
                        for pair in nonSeparatedPairs:
                            positiveTraces.append(pair[0])
                            negativeTraces.append(pair[1])
                except:
                    break
                    
                
                atomBuildingTraces = ExperimentTraces(tracesToAccept= positiveTraces, tracesToReject = negativeTraces)
                formula = None
                for d in range(1, maxDepth+1):
                    fg = config.encoder(d, atomBuildingTraces)
                    fg.encodeFormula()
                    
                    if fg.solver.check() == sat:
                        logging.info("depth %d: sat"%d)
                        m = fg.solver.model()
                        formula = fg.reconstructWholeFormula(m)
                        logging.info("obtained formula: %s"%formula)
                        self.atoms.append(formula)
                        break
                    elif fg.solver.check() == unsat:
                        logging.info("depth %d: unsat"% d)
                
                self.atomTraceEvaluation[formula] = {}
                for exampleTrace in self.positiveExamples+self.negativeExamples:
                    self.atomTraceEvaluation[formula][exampleTrace] = exampleTrace.evaluateFormulaOnTrace(formula)
                numSeparatedByFormula[formula] = 0
                for (posTrace, negTrace) in [(p, n) for p in self.atomTraceEvaluation[formula].keys() if p.intendedEvaluation == True and self.atomTraceEvaluation[formula][p] == True \
                                             for n in self.atomTraceEvaluation[formula].keys() if n.intendedEvaluation == False and self.atomTraceEvaluation[formula][n] == False]:
                    numSeparatedByFormula[formula] += 1
                    self.separationDict[(posTrace, negTrace)] = True
                logging.info("formula {0} separates {1} pairs".format(formula, numSeparatedByFormula[formula]))
                
                
                
                
                
                if strategy == AtomBuildingStrategy.RANDOM_SAMPLING:
                    examplesToDecreaseChanceOfBeingChosen = positiveTraces + negativeTraces
                elif strategy == AtomBuildingStrategy.BOOST_MISCLASSIFIED:
                    examplesToDecreaseChanceOfBeingChosen = []
                    for exampleTrace in self.positiveExamples:
                        if self.atomTraceEvaluation[formula][exampleTrace] == True:
                            examplesToDecreaseChanceOfBeingChosen.append(exampleTrace)
                       
                    
                    for exampleTrace in self.negativeExamples:
                        if self.atomTraceEvaluation[formula][exampleTrace] == False:
                            examplesToDecreaseChanceOfBeingChosen.append(exampleTrace)
                       
                        
                    
                
                if not strategy == AtomBuildingStrategy.CHOOSE_NOT_SEPARATED and not probabilityDecreaseRate == 1:
                    probabilityMassToRemoveFromChosen = (sizeOfPSubset + sizeOfNSubset) * probabilityDecreaseRate
                    individualProbabilityToAddToUnchosen = probabilityMassToRemoveFromChosen / (self.totalNumberOfExamples - (sizeOfPSubset+sizeOfNSubset))
                    
                    for tr in self.positiveExamples + self.negativeExamples:
                        if tr in examplesToDecreaseChanceOfBeingChosen:
                            try:
                                self.positiveExamplesProbabilities[tr] *= probabilityDecreaseRate
                            except:
                                self.negativeExamplesProbabilities[tr] *= probabilityDecreaseRate
                        else:
                            try:
                                self.positiveExamplesProbabilities[tr] += individualProbabilityToAddToUnchosen
                            except:
                                self.negativeExamplesProbabilities[tr] += individualProbabilityToAddToUnchosen 
        self.atoms = list(set(self.atoms))
        return (self.atoms, self.atomTraceEvaluation)
                
                
                
            
                
        
    
    
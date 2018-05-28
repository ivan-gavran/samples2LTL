import pdb
import argparse

from experiments import testFileGeneration
from utils.SimpleTree import Formula
from boto.cloudformation.stack import Output

operatorsAndArities = {'G':1, 'F':1, '!':1, 'U':2, '&':2,'|':2, '->':2, 'X':1, 'prop':0}


def generateFromFormulaFile(files, outputFolder, equalNumber, traceLengths, repetitions, counter=0):
    for fileName in files:
        with open(fileName) as fileWithFormulas:
            for line in fileWithFormulas:
                f = Formula.convertTextToFormula(line)
                for minRep in repetitions:
                    for traceLength in traceLengths:
                        generatedTraces = testFileGeneration.generateTracesFromFormula(f, traceLength, minRep, minRep, 50*minRep, generateExactNumberOfTraces = equalNumber)
                        patternName = fileName.split("/")[-1]
                        patternName = patternName.split(".")[0]                    
                        testName = outputFolder+"{:04}.trace".format(counter)
                        
                        if len(generatedTraces.acceptedTraces) > 0 and len(generatedTraces.rejectedTraces) > 0:
                            generatedTraces.writeTracesToFile(testName)
                        counter += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_folder", dest="outputFolder", default="traces/generated/")
    parser.add_argument("--counter_start", dest="counterStart", default=0)
    parser.add_argument("--pattern_files", dest="patternFile", default=["formulas/patterns/abscence.txt", "formulas/patterns/existence.txt", "formulas/patterns/universality.txt"],\
                        nargs='+', type=str)
    parser.add_argument("--equal_number_accepting_rejecting", dest="equalNumber", default=True, action='store_true')
    parser.add_argument("--traces_set_sizes", dest="tracesSetSizes", default=[5, 10, 50, 100, 150, 200, 500], nargs='+', type=int)
    parser.add_argument("--trace_lengths", dest="traceLengths", default=[5, 10, 15], nargs='+', type=int)
    args, unknown = parser.parse_known_args()
    
    
    outputFolder = args.outputFolder
    generateFromFormulaFile(args.patternFile, outputFolder, equalNumber=args.equalNumber,\
                             repetitions = args.tracesSetSizes, traceLengths=args.traceLengths, counter=int(args.counterStart))
    
if __name__ == "__main__":
    main()
#     f = Formula.convertTextToFormula("|(x0,!(x1))")
#     
#     allVars = f.getAllVariables()
    
    
    
    

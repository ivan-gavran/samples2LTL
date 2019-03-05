import pdb
from z3 import *
import argparse
import os
from formulaBuilder.AtomBuilder import AtomBuilder, AtomBuildingStrategy
from formulaBuilder.DTFormulaBuilder import DTFormulaBuilder
import logging
from unicodedata import numeric

sizeOfPSubset = 10
sizeOfNSubset = 10
numRepetitionsInsideSampling = 3 


    
def main():
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", dest="tracesFileName", default="traces/dummy.trace")
    parser.add_argument("--atoms_file", dest="atomsFile", default="atoms.txt")
    parser.add_argument("--log", dest="logLevel", default="info")
    parser.add_argument("--strategy", dest="strategy", default=0)
    parser.add_argument("--P_subset", dest="sizeOfPSubset", default=10)
    parser.add_argument("--N_subset", dest="sizeOfNSubset", default=10)
    parser.add_argument("--num_repetitions_inside_sampling", dest="numRepetitionsInsideSampling", default=3)
    parser.add_argument("--num_restarts_of_sampling", dest="numRestartsOfSampling", default=3)
    parser.add_argument("--dt_file", dest="dtFile", default="decisionTreeInput.txt")
    parser.add_argument("--dt_out_dot", dest="dtDotFile", default="decisionTreeOut.dot")
    parser.add_argument("--dt_out_txt", dest="dtTextFile", default="decisionTreeOut.txt")
    
    
    args,unknown = parser.parse_known_args()
    numeric_level=getattr(logging, args.logLevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level %s' % args.logLevel)
    logging.basicConfig(level=numeric_level)
    
    strategyNum = int(args.strategy)
    strategy = None
    if strategyNum == 0:
        strategy = AtomBuildingStrategy.RANDOM_SAMPLING
    elif strategyNum == 1:
        strategy = AtomBuildingStrategy.BOOST_MISCLASSIFIED
    elif strategyNum == 2:
        strategy = AtomBuildingStrategy.CHOOSE_NOT_SEPARATED

    
    
    tracesFileName = args.tracesFileName
    ab = AtomBuilder()
    ab.readExamples(tracesFileName)
    #ab.buildAtoms(sizeOfPSubset=sizeOfPSubset, sizeOfNSubset=sizeOfNSubset, numRepetitionsInsideSampling=numRepetitionsInsideSampling)
    (atoms, atomTraceEvaluation) = ab.buildAtoms(sizeOfPSubset=int(args.sizeOfPSubset), strategy = strategy, sizeOfNSubset=int(args.sizeOfNSubset), probabilityDecreaseRate=0.5,\
                  numRepetitionsInsideSampling=int(args.numRepetitionsInsideSampling), numRestartsOfSampling = int(args.numRestartsOfSampling))
    ab.writeMatrixRepresentationIntoFile(args.dtFile)
    ab.writeAtomsIntoFile(args.atomsFile)
    
    fb = DTFormulaBuilder(features = ab.atoms, data = ab.getMatrixRepresentation(), labels = ab.getLabels())
    fb.createASeparatingFormula()
    
    fb.tree_to_dot_file(args.dtDotFile)
    fb.tree_to_text_file(args.dtTextFile)
    
    
    
if __name__ == "__main__":
    main()


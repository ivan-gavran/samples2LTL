import glob
import sys
import pdb
from z3 import *
from pytictoc import TicToc
import csv
import os
import json
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


def findDTDepth(fileName):
    overallSubs = []
    overallDepth = 0
    with open(fileName) as dtFile:
        
        for line in dtFile:
            fText = (line.split(':')[0]).strip()
            if fText == '*':
                continue
            
            else:
                overallDepth += 1
                obtainedFormula = Formula.convertTextToFormula(fText)
                subs = obtainedFormula.getSetOfSubformulas()
                
                overallSubs += subs
    overallSubs = set(overallSubs)
    overallDepth += len(overallSubs)
    overallDepth -= 1 
    print(overallDepth, overallSubs)
    return overallDepth

def findSizeOfTextFormula(formulaText):
    try:
        formula = Formula.convertTextToFormula(formulaText)
        return len(formula.getSetOfSubformulas())
    except:
        return "/"

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--input_file", dest="inputFile", default='experiments/dtSubset3Strategy2/statsSubset3Strategy2.csv')
    parser.add_argument("--sat_input_file", dest="satInput", default='experiments/satTest5And10/completeStats.csv')
    args,unknown = parser.parse_known_args()
    outputFolder = os.path.dirname(args.inputFile)
    outputFile = outputFolder + "/dtDepths.csv"
    
    satFormulasLengths = {}
    with open(args.satInput) as satCsvInput:
        satReader = csv.reader(satCsvInput)
        satFormulasLengths = { os.path.basename(line[1]) : findSizeOfTextFormula(line[9]) for line in satReader }
    with open(args.inputFile) as csvInput:
        
        reader = csv.reader(csvInput)
        with open(outputFile, "w") as csvfile:
            
            writer = csv.writer(csvfile)
            
            for line in reader:
                try:
                    
                    dtReprFile = line[12]
                    dtDepth = findDTDepth(dtReprFile)
                    
                    formulaDepth = satFormulasLengths[os.path.basename(line[1])]
                    if not formulaDepth == "/":                    
                        writer.writerow([line[1], formulaDepth, dtDepth, dtDepth/(formulaDepth*1.0)])
                except:
                    print("failed with "+ repr(line))
    
    
    
    
        
if __name__ == "__main__":
    main()
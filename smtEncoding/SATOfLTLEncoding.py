from z3 import *
import pdb
from utils.SimpleTree import SimpleTree, Formula
import random
from utils.Traces import Trace
import logging

class SATOfLTLEncoding:
    """
    - D is the depth of the tree
    - lassoStartPosition denotes the position when the trace values start looping
    - traces is 
      - list of different recorded values (trace)
      - each trace is a list of recordings at time units (time point)
      - each time point is a list of variable values (x1,..., xk)
    """
    def __init__(self, f, init_part_length, lasso_part_length, operators, literals):
        
        defaultOperators = ['G', 'F', '!', 'U', '&','|', '->', 'X']
        unary = ['G', 'F', '!', 'X']
        binary = ['&', '|', 'U', '->']
        #except for the operators, the nodes of the "syntax table" are additionally the propositional variables 
        
        if operators == None:
            self.listOfOperators = list(defaultOperators)
        else:
            self.listOfOperators = list(operators)
        if '!' not in self.listOfOperators:
            self.listOfOperators.append('!')
        if '&' not in self.listOfOperators:
            self.listOfOperators.append('&')
        if 'true' not in self.listOfOperators:
            self.listOfOperators.append('true')
        if 'false' not in self.listOfOperators:
            self.listOfOperators.append('false')

        if 'prop' in self.listOfOperators:
            self.listOfOperators.remove('prop')

            
        
        self.unaryOperators = [op for op in self.listOfOperators if op in unary]
        self.binaryOperators = [op for op in self.listOfOperators if op in binary]
        self.solver = Solver()
        all_subformulas = f.getSetOfSubformulas()
        self.formulaDepth = len(all_subformulas)
        self.literals = literals

        self.listOfVariables = self.literals
        self.variablesToIntMapping = {self.literals[i] : i for i in range(len(self.literals))}
        # pdb.set_trace()
        self.lassoStart = init_part_length
        self.traceLength = init_part_length + lasso_part_length
        self.listOfSubformulas = sorted(list(all_subformulas))

        logging.info("subformulas of formula {0} are {1}".format(f, self.listOfSubformulas))
        self.indicesOfSubformulas = {self.listOfSubformulas[i] : i for i in range(len(self.listOfSubformulas))}
        logging.debug(self.indicesOfSubformulas)


    def _assignIndicesToSubformulas(self, number_of_subformulas):
        pass

    def getInformativeVariables(self):
        res = []
        res += [v for v in self.x.values()]
        res += [v for v in self.l.values()]
        res += [v for v in self.r.values()]


        return res
    """    
    the working variables are 
        - x[i][o]: i is a subformula (row) identifier, o is an operator or a propositional variable. Meaning is "subformula i is an operator (variable) o"
        - l[i][j]:  "left operand of subformula i is subformula j"
        - r[i][j]: "right operand of subformula i is subformula j"
        - y[i][t]: semantics of formula i in time point t
    """
    def encodeFormula(self, unsatCore=True):
        self.operatorsAndVariables = self.listOfOperators + self.listOfVariables
        
        self.x = { (i, o) : Bool('x_'+str(i)+'_'+str(o)) for i in range(self.formulaDepth) for o in self.operatorsAndVariables }

        self.l = {(parentOperator, childOperator) : Bool('l_'+str(parentOperator)+'_'+str(childOperator))\
                                                 for parentOperator in range(1, self.formulaDepth)\
                                                 for childOperator in range(parentOperator)}
        self.r = {(parentOperator, childOperator) : Bool('r_'+str(parentOperator)+'_'+str(childOperator))\
                                                 for parentOperator in range(1, self.formulaDepth)\
                                                 for childOperator in range(parentOperator)}

        self.y = { (i, timePoint) : Bool('y_'+str(i)+'_'+str(timePoint))\
                  for i in range(self.formulaDepth)\
                  for timePoint in range(self.traceLength)}

        self.counterexampleTrace = {(var, tmstp) : Bool('cex_'+str(var)+"_"+str(tmstp))\
                                    for var in self.listOfVariables\
                                    for tmstp in range(self.traceLength)}
        
        
        self.solver.set(unsat_core=unsatCore)


        self.setOperatorValues()



        self.propVariablesSemantics()


        self.operatorsSemantics()



        self.solver.assert_and_track(Not(self.y[(self.formulaDepth-1, 0)]), "evaluation should be false")

        
        
    
    
    def propVariablesSemantics(self):

        for (idx, subf) in enumerate(self.listOfSubformulas):
            if subf.label in self.listOfVariables:
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] == self.counterexampleTrace[(subf.label, tmstp)] for tmstp in range(self.traceLength)]),
                    "cex and y values connection at position {0} for var {1}".format(str(idx), subf.label)
                )


        
    

    
    def setOperatorValues(self):
        #pdb.set_trace()
        for (idx, subf) in enumerate(self.listOfSubformulas):
            self.solver.assert_and_track(self.x[(idx, subf.label)], "operator_"+str(subf.label)+"_at_"+str(idx))
            self.solver.add(And([Not(self.x[(idx, operator)]) for operator in self.operatorsAndVariables if not operator == subf.label]))
            if not subf.left is None:
                self.solver.assert_and_track(self.l[(idx, self.indicesOfSubformulas[subf.left])], "left_child_of_"+str(subf.label)+"_is_"+subf.left.label)
                self.solver.add(And([Not(self.l[(idx, i)]) for i in range(idx) if not i == self.indicesOfSubformulas[subf.left]]))
            else:
                self.solver.assert_and_track(And([Not(self.l[(idx, i)]) for i in range(idx)]), "formula_"+str(idx)+"_no_left_child")

            if not subf.right is None:
                self.solver.assert_and_track(self.r[(idx, self.indicesOfSubformulas[subf.right])], "right_child_of_"+str(idx)+"_is_"+str(self.indicesOfSubformulas[subf.right]))
                self.solver.add(And([Not(self.r[(idx, i)]) for i in range(idx)if not i == self.indicesOfSubformulas[subf.right]]))
            else:
                self.solver.assert_and_track(And([Not(self.r[(idx, i)]) for i in range(idx)]), "formula_"+str(idx)+"_no_right_child")



    def _nextPos(self, currentPos):
        if currentPos == self.traceLength - 1:
            return self.lassoStart
        else:
            return currentPos + 1
    def _futurePos(self, currentPos):
        futurePositions = []
        alreadyGathered = set()
        while currentPos not in alreadyGathered:
            futurePositions.append(currentPos)
            alreadyGathered.add(currentPos)
            currentPos = self._nextPos(currentPos)
        # always add a new one so that all the next-relations are captured
        futurePositions.append(currentPos)
        return futurePositions

    def operatorsSemantics(self):



        for (idx, subf) in enumerate(self.listOfSubformulas):
            explanation = "operator {0} at depth {1}".format(str(subf.label), idx)
            if subf.label == "|":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] ==
                         Or(\
                            self.y[(self.indicesOfSubformulas[subf.left], tmstp)],
                             self.y[(self.indicesOfSubformulas[subf.right], tmstp)]
                        )
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "false":
                self.solver.assert_and_track(
                    And([Not(self.y[(idx, tmstp)])
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "true":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)]
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "&":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] ==
                         And( \
                             self.y[(self.indicesOfSubformulas[subf.left], tmstp)],
                             self.y[(self.indicesOfSubformulas[subf.right], tmstp)]
                         )
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "!":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] ==
                         Not( \
                             self.y[(self.indicesOfSubformulas[subf.left], tmstp)]
                         )
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )
            elif subf.label == "->":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] ==
                         Implies( \
                             self.y[(self.indicesOfSubformulas[subf.left], tmstp)],
                             self.y[(self.indicesOfSubformulas[subf.right], tmstp)]
                         )
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "G":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] ==
                         And( [\
                              self.y[(self.indicesOfSubformulas[subf.left], futureTmstp)]
                             for futureTmstp in self._futurePos(tmstp)]
                         )
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "F":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] ==
                         Or( [\
                              self.y[(self.indicesOfSubformulas[subf.left], futureTmstp)]
                             for futureTmstp in self._futurePos(tmstp)]
                         )
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "X":
                self.solver.assert_and_track(
                    And([self.y[(idx, tmstp)] == self.y[(idx, self._nextPos(tmstp))]
                         for tmstp in range(self.traceLength)
                         ]),
                    explanation
                )

            elif subf.label == "U":
                self.solver.assert_and_track(
                    And([ \
                        self.y[(idx, tmstp)] == \
                        Or([ \
                            And( \
                                [self.y[(self.indicesOfSubformulas[subf.left], futurePos)] for futurePos in self._futurePos(tmstp)[0:qIndex]] + \
                                [self.y[(self.indicesOfSubformulas[subf.right], self._futurePos(tmstp)[qIndex])]] \
                                ) \
                            for qIndex in range(len(self._futurePos(tmstp))) \
                            ]) \
                        for tmstp in range(self.traceLength)] \
                        ),
                        explanation
                )



    def reconstructWholeFormula(self, model):
        return self.reconstructFormula(self.formulaDepth-1, model)

    def reconstructFormula(self, rowId, model):

        def getValue(row, vars):
            tt = [k[1] for k in vars if k[0] == row and model[vars[k]] == True]
            if len(tt) > 1:
                raise Exception("more than one true value")
            else:
                return tt[0]

        operator = getValue(rowId, self.x)
        if operator in self.listOfVariables:
            return Formula(self.traces.literals[int(operator)])

        elif operator in self.unaryOperators:
            leftChild = getValue(rowId, self.l)
            return Formula([operator, self.reconstructFormula(leftChild, model)])
        elif operator in self.binaryOperators:
            leftChild = getValue(rowId, self.l)
            rightChild = getValue(rowId, self.r)
            return Formula([operator, self.reconstructFormula(leftChild, model), self.reconstructFormula(rightChild, model)])

    def reconstructCounterexampleTraces(self, model, maxNumOfCounterexamples = 1):
        counterexamples = []
        for i in range(maxNumOfCounterexamples):
            counterexampleTraceVector = []

            for tmstp in range(self.traceLength):
                singleTimestepData = []
                for var in self.listOfVariables:

                    g = model[self.counterexampleTrace[(var, tmstp)]]

                    if g is None:
                        el = random.randint(0,1)
                    else:
                        if g == True:
                            el = 1
                        elif g == False:
                            el = 0
                        else:
                            pdb.set_trace()
                        logging.debug("counterexample: {0} at tmstp {1} has to be {2}".format(var, str(tmstp), str(el)))
                    singleTimestepData.append(el)

                counterexampleTraceVector.append(singleTimestepData)
            generatedTrace = Trace(counterexampleTraceVector, lassoStart=self.lassoStart, literals=self.listOfVariables)

            counterexamples.append(generatedTrace)
        return counterexamples




    
        
      

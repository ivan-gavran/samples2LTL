from z3 import *
import pdb
from utils.SimpleTree import SimpleTree, Formula

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
            self.listOfOperators = defaultOperators
        else:
            self.listOfOperators = operators
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
        self.lassStart = init_part_length
        self.traceLength = init_part_length + lasso_part_length
        self.listOfSubformulas = sorted(list(all_subformulas))

        print(self.listOfSubformulas)
        self.indicesOfSubformulas = {self.listOfSubformulas[i] : i for i in range(len(self.listOfSubformulas))}
        print(self.indicesOfSubformulas)


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
        
        
        self.solver.set(unsat_core=unsatCore)

        #self.exactlyOneOperator()
        self.setOperatorValues()
        pdb.set_trace()
        self.firstOperatorVariable()

        self.propVariablesSemantics()
         
        self.operatorsSemantics()
        self.noDanglingVariables()
        
        self.solver.assert_and_track(And( [ self.y[(self.formulaDepth - 1, traceIdx, 0)] for traceIdx in range(len(self.traces.acceptedTraces))] ), 'accepted traces should be accepting')
        self.solver.assert_and_track(And( [ Not(self.y[(self.formulaDepth - 1, traceIdx, 0)]) for traceIdx in range(len(self.traces.acceptedTraces), len(self.traces.acceptedTraces+self.traces.rejectedTraces))] ),\
                                     'rejecting traces should be rejected')
        
        
    
    
    def propVariablesSemantics(self):
        for i in range(self.formulaDepth):
            for p in self.listOfVariables:
                for traceIdx, tr in enumerate(self.traces.acceptedTraces + self.traces.rejectedTraces):
                    self.solver.assert_and_track(Implies(self.x[(i, p)],\
                                                          And([ self.y[(i,traceIdx, timestep)] if tr.traceVector[timestep][p] == True else Not(self.y[(i, traceIdx, timestep)])\
                                                               for timestep in range(tr.lengthOfTrace)])),\
                                                          "semantics of propositional variable depth_"+str(i)+' var _'+str(p)+'_trace_'+str(traceIdx))
                    
            

        
    
    def firstOperatorVariable(self):
        self.solver.assert_and_track(Or([self.x[k] for k in self.x if k[0] == 0 and k[1] in self.listOfVariables]),\
                                     'first operator a variable')

    def noDanglingVariables(self):
        if self.formulaDepth > 0:
            self.solver.assert_and_track(
                And([
                    Or(
                        AtLeast([self.l[(rowId, i)] for rowId in range(i+1, self.formulaDepth)]+ [1]),
                        AtLeast([self.r[(rowId, i)] for rowId in range(i+1, self.formulaDepth)] + [1])
                    )
                    for i in range(self.formulaDepth - 1)]
                ),
                "no dangling variables"
            )
    
    def setOperatorValues(self):
        #pdb.set_trace()
        for (idx, subf) in enumerate(self.listOfSubformulas):
            self.solver.assert_and_track(self.x[(idx, subf.label)], "operator_"+str(subf.label)+"_at_"+str(idx))
            self.solver.add(And([Not(self.x[(idx, operator)]) for operator in self.operatorsAndVariables if not operator == subf.label]))
            if not subf.left is None:
                self.solver.assert_and_track(self.l[(idx, self.indicesOfSubformulas[subf.left])], "left_child_of_"+str(subf.label)+"_is_"+subf.left.label)
                self.solver.add(And([Not(self.l[(idx, i)]) for i in range(idx)]))
            else:
                self.solver.assert_and_track(And([Not(self.l[(idx, i)]) for i in range(idx)]), "formula_"+str(idx)+"_no_left_child")

            if not subf.right is None:
                self.solver.assert_and_track(self.r[(idx, self.indicesOfSubformulas[subf.right])], "right_child_of_"+str(idx)+"_is_"+str(self.indicesOfSubformulas[subf.right]))
                self.solver.add(And([Not(self.r[(idx, i)]) for i in range(idx)]))
            else:
                self.solver.assert_and_track(And([Not(self.r[(idx, i)]) for i in range(idx)]), "formula_"+str(idx)+"_no_right_child")

    def operatorsSemantics(self):


        for traceIdx, tr in enumerate(self.traces.acceptedTraces + self.traces.rejectedTraces):
            for i in range(1, self.formulaDepth):
                
                if '|' in self.listOfOperators:
                    #disjunction
                     self.solver.assert_and_track(Implies(self.x[(i, '|')],\
                                                            And([ Implies(\
                                                                           And(\
                                                                               [self.l[i, leftArg], self.r[i, rightArg]]\
                                                                               ),\
                                                                           And(\
                                                                               [ self.y[(i, traceIdx, timestep)]\
                                                                                ==\
                                                                                Or(\
                                                                                   [ self.y[(leftArg, traceIdx, timestep)],\
                                                                                    self.y[(rightArg, traceIdx, timestep)]]\
                                                                                   )\
                                                                                 for timestep in range(tr.lengthOfTrace)]\
                                                                               )\
                                                                           )\
                                                                          for leftArg in range(i) for rightArg in range(i) ])),\
                                                             'semantics of disjunction for trace %d and depth %d'%(traceIdx, i))
                if '&' in self.listOfOperators:
                      #conjunction
                     self.solver.assert_and_track(Implies(self.x[(i, '&')],\
                                                            And([ Implies(\
                                                                           And(\
                                                                               [self.l[i, leftArg], self.r[i, rightArg]]\
                                                                               ),\
                                                                           And(\
                                                                               [ self.y[(i, traceIdx, timestep)]\
                                                                                ==\
                                                                                And(\
                                                                                   [ self.y[(leftArg, traceIdx, timestep)],\
                                                                                    self.y[(rightArg, traceIdx, timestep)]]\
                                                                                   )\
                                                                                 for timestep in range(tr.lengthOfTrace)]\
                                                                               )\
                                                                           )\
                                                                          for leftArg in range(i) for rightArg in range(i) ])),\
                                                             'semantics of conjunction for trace %d and depth %d'%(traceIdx, i))
                     
                if '->' in self.listOfOperators:
                       
                      #implication
                     self.solver.assert_and_track(Implies(self.x[(i, '->')],\
                                                            And([ Implies(\
                                                                           And(\
                                                                               [self.l[i, leftArg], self.r[i, rightArg]]\
                                                                               ),\
                                                                           And(\
                                                                               [ self.y[(i, traceIdx, timestep)]\
                                                                                ==\
                                                                                Implies(\
                                                                                  self.y[(leftArg, traceIdx, timestep)],\
                                                                                  self.y[(rightArg, traceIdx, timestep)]\
                                                                                   )\
                                                                                 for timestep in range(tr.lengthOfTrace)]\
                                                                               )\
                                                                           )\
                                                                          for leftArg in range(i) for rightArg in range(i) ])),\
                                                             'semantics of implication for trace %d and depth %d'%(traceIdx, i))
                if '!' in self.listOfOperators:
                      #negation
                     self.solver.assert_and_track(Implies(self.x[(i, '!')],\
                                                           And([\
                                                               Implies(\
                                                                         self.l[(i,onlyArg)],\
                                                                         And([\
                                                                              self.y[(i, traceIdx, timestep)] == Not(self.y[(onlyArg, traceIdx, timestep)])\
                                                                              for timestep in range(tr.lengthOfTrace)\
                                                                              ])\
                                                                          )\
                                                               for onlyArg in range(i)\
                                                               ])\
                                                           ),\
                                                   'semantics of negation for trace %d and depth %d' % (traceIdx, i)\
                                                   )
                if 'G' in self.listOfOperators:
                      #globally                
                     self.solver.assert_and_track(Implies(self.x[(i, 'G')],\
                                                           And([\
                                                               Implies(\
                                                                         self.l[(i,onlyArg)],\
                                                                         And([\
                                                                              self.y[(i, traceIdx, timestep)] ==\
                                                                              And([self.y[(onlyArg, traceIdx, futureTimestep)] for futureTimestep in tr.futurePos(timestep) ])\
                                                                              for timestep in range(tr.lengthOfTrace)\
                                                                              ])\
                                                                          )\
                                                               for onlyArg in range(i)\
                                                               ])\
                                                           ),\
                                                   'semantics of globally operator for trace %d and depth %d' % (traceIdx, i)\
                                                   )

                if 'F' in self.listOfOperators:                  
                      #finally                
                     self.solver.assert_and_track(Implies(self.x[(i, 'F')],\
                                                           And([\
                                                               Implies(\
                                                                         self.l[(i,onlyArg)],\
                                                                         And([\
                                                                              self.y[(i, traceIdx, timestep)] ==\
                                                                              Or([self.y[(onlyArg, traceIdx, futureTimestep)] for futureTimestep in tr.futurePos(timestep) ])\
                                                                              for timestep in range(tr.lengthOfTrace)\
                                                                              ])\
                                                                          )\
                                                               for onlyArg in range(i)\
                                                               ])\
                                                           ),\
                                                   'semantics of finally operator for trace %d and depth %d' % (traceIdx, i)\
                                                   )
                  
                if 'X' in self.listOfOperators:
                      #next                
                     self.solver.assert_and_track(Implies(self.x[(i, 'X')],\
                                                           And([\
                                                               Implies(\
                                                                         self.l[(i,onlyArg)],\
                                                                         And([\
                                                                              self.y[(i, traceIdx, timestep)] ==\
                                                                              self.y[(onlyArg, traceIdx, tr.nextPos(timestep))]\
                                                                              for timestep in range(tr.lengthOfTrace)\
                                                                              ])\
                                                                          )\
                                                               for onlyArg in range(i)\
                                                               ])\
                                                           ),\
                                                   'semantics of neXt operator for trace %d and depth %d' % (traceIdx, i)\
                                                   )
                if 'U' in self.listOfOperators:
                    #until
                     self.solver.assert_and_track(Implies(self.x[(i, 'U')],\
                                                          And([ Implies(\
                                                                         And(\
                                                                             [self.l[i, leftArg], self.r[i, rightArg]]\
                                                                             ),\
                                                                         And([\
                                                                            self.y[(i, traceIdx, timestep)] ==\
                                                                            Or([\
                                                                                And(\
                                                                                    [self.y[(leftArg, traceIdx, futurePos)] for futurePos in tr.futurePos(timestep)[0:qIndex]]+\
                                                                                    [self.y[(rightArg, traceIdx, tr.futurePos(timestep)[qIndex])]]\
                                                                                    )\
                                                                                for qIndex in range(len(tr.futurePos(timestep)))\
                                                                                ])\
                                                                            for timestep in range(tr.lengthOfTrace)]\
                                                                             )\
                                                                         )\
                                                                for leftArg in range(i) for rightArg in range(i) ])),\
                                                    'semantics of Until operator for trace %d and depth %d'%(traceIdx, i))
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
        
    
        
      

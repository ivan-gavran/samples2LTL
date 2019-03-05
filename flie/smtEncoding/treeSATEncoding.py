from z3 import *
import pdb
from utils.SimpleTree import SimpleTree, Formula

class TreeSATEncoding:
    """
    - D is the depth of the tree
    - lassoStartPosition denotes the position when the trace values start looping
    - traces is 
      - list of different recorded values (trace)
      - each trace is a list of recordings at time units (time point)
      - each time point is a list of variable values (x1,..., xk)
    """
    def __init__(self, D, testTraces): 
        
            
        defaultOperators = ['G', 'F', '!', 'U', '&','|', '->', 'X', 'prop']
        
        if testTraces.operators == None:
            self.listOfOperators = defaultOperators
        else:
            self.listOfOperators = testTraces.operators
        if not 'prop' in self.listOfOperators:
            self.listOfOperators.append('prop')
        self.noneOperator = 'none'
        self.solver = Solver()
        self.formulaDepth = D
        
        
        #traces = [t.traceVector for t in testTraces.acceptedTraces + testTraces.rejectedTraces]
        
        self.traces = testTraces

        
        
        
        
        
        #keeping track of which positions in a tree (and in time) are visited, so that constraints are not generated twice
        self.visitedPositions = set()
       
   
    def encodeFormula(self, unsatCore=True):
        self.solver.set(unsat_core=unsatCore)
        
        self.solver.add(Bool('c_0_0_none') == False)
        self.everyLevelMeaningfulRestrictions()
        self.generateVariableConsistencyRestrictions()
        #self.generatePropositionsRestrictions()
        for traceNumber, acceptedTrace in enumerate(self.traces.acceptedTraces):
            traceId = 'Acc'+repr(traceNumber)
            self.solver.add(Bool('p_level0_k0_tmstp0_trace' + traceId))
            
            
            self.generateRestrictions(0, 0, 0, traceId, acceptedTrace)
            
            
        for traceNumber, rejectedTrace in enumerate(self.traces.rejectedTraces):
            traceId = 'Rej'+repr(traceNumber)
            self.solver.add(Bool('p_level0_k0_tmstp0_trace' + traceId) == False)
            
            self.generateRestrictions(0, 0, 0, traceId, rejectedTrace)
             
                
    def reconstructWholeFormula(self, model):
        return self.reconstructFormula(0,0,model)   
        
    def reconstructFormula(self, level, k, model):
        operatorToAskFor = 'c_%d_%d'%(level, k)
        operatorCode = 'c'
        operatorValue = self.readPropValue(operatorCode, level, k, model)
        
        
        
        if operatorValue == 'prop':
            return Formula(self.readPropValue('propValue',level, k, model))
        elif operatorValue == 'none':
            return None
            
        else:
            formulaTree = Formula(operatorValue)
            children = self.children(level, k)
            formulaTree.addChildren(self.reconstructFormula(children[0][0], children[0][1], model), self.reconstructFormula(children[1][0], children[1][1], model))
            return formulaTree
        
        
        
    
    
    def readPropValue(self, propCode, propLevel, propPosition, model):
        
        candidates = [t.name().split('_') for t in model.decls() if t.name().split('_')[0] == propCode and t.name().split('_')[1] == str(propLevel) and t.name().split('_')[2] == str(propPosition) and model[t] == True]
        
        operators = list(set([(t[0], t[1], t[2], t[3]) for t in candidates]))
        if len(operators) == 1:
            operatorName = operators[0][3]
            return operatorName
        else:
            pdb.set_trace()
            raise Exception("there are none or multiple values for this operator")
        
        
    """
    function that encodes that at every level of the tree, at least one connective is not-none (otherwise the depth would collapse).
    the way it does it is by saying that at most number-1 can be none
    """   
    def everyLevelMeaningfulRestrictions(self):
        for level in range(self.formulaDepth + 1):
            self.solver.assert_and_track(AtMost( [Bool('c_%d_%d_none' % (level, levelPos)) for levelPos in range(2**level) ] + [2**level - 1]), 'atLeastOneConnectiveNotNone_%d'%level)
        
                
    def generateVariableConsistencyRestrictions(self):
        
        #this part says that if a position in a tree is a variable, it should be like that all the time
        for level in range(self.formulaDepth + 1):
            for positionAtLevel in range(2**level):
                for variable in range(self.traces.numVariables):
                    self.solver.assert_and_track(Or(\
                                        And([ Bool('propValue_%d_%d_x%d_%d' % (level, positionAtLevel, variable, positionAtTrace)) for positionAtTrace in range(self.traces.maxLengthOfTraces)]),\
                                        And([ Not(Bool('propValue_%d_%d_x%d_%d' % (level, positionAtLevel, variable, positionAtTrace))) for positionAtTrace in range(self.traces.maxLengthOfTraces)])
                                     )\
                                 , 'variableTimeConsistency_%d_%d_%d'%(level, positionAtLevel, variable))
        

        # this part says that for a given position, there can be exactly one variable
        for level in range(self.formulaDepth + 1):
            for positionAtLevel in range(2**level):
                for positionAtTrace in range(self.traces.maxLengthOfTraces):
                    
                    #should this also be implied by the fact that node (connective) is a proposition?
                    self.solver.assert_and_track(AtMost(\
                                           [Bool('propValue_%d_%d_x%d_%d' % (level, positionAtLevel, variable, positionAtTrace)) for variable in range(self.traces.numVariables)]\
                                           + [1]
                                           )
                                ,'only_one_variable_%d_%d_%d'%(level, positionAtLevel, positionAtTrace))
        
                    self.solver.assert_and_track(Implies(\
                                                         Bool('c_%d_%d_prop'%(level, positionAtLevel)),\
                                                         AtLeast([Bool('propValue_%d_%d_x%d_%d' % (level, positionAtLevel, variable, positionAtTrace)) for variable in range(self.traces.numVariables)]+[1])\
                                                         )\
                                                 ,'ifPropositionnConnectiveThenSomeProposition_%d_%d_%d'%(level, positionAtLevel, positionAtTrace)
                                                 )
        
           
    def children(self, level, k):
        
        childrenLevel = level + 1
        childrenPos1 = 2 * k
        childrenPos2 = 2 * k + 1
        return [(childrenLevel, childrenPos1), (childrenLevel, childrenPos2)]

    def parent(self, level, k):
        if level < 1:
            raise ValueError("no parent")
        parentLevel = level - 1
        parentPos = k // 2
        return (parentLevel, parentPos)



    def listIndexToLevelPos(self, listIndex):
        k = 0
        
        while (2**(k+1)-1) < listIndex + 1:
            k += 1
        
        level = k
        position = listIndex - (2**(k+1-1)-1) 
        return (level, position) 


    
    def arityOfOperatorRestrictions(self, arity, operator, leftChildNoneConnector, rightChildNoneConnector):
        possibleOperators = self.possibleOperators
        if arity == 2:
            self.solver.add(Implies(possibleOperators[operator], leftChildNoneConnector == False))
            self.solver.add(Implies(possibleOperators[operator], rightChildNoneConnector == False))
        elif arity == 1:
            self.solver.add(Implies(possibleOperators[operator], leftChildNoneConnector == False))
            self.solver.add(Implies(possibleOperators[operator], rightChildNoneConnector == True))
        else:
            print("arityOfOperatorRestrictions: unsupported arity -"+str(arity))


        
                    
    
    def generateRestrictions(self, level, positionAtLevel, positionAtTrace, traceId, trace):
        
        
        
        
        for timePointIdx, timePoint in enumerate(trace.traceVector):
            for propIdx, propValue in enumerate(timePoint):
                self.solver.add(Bool('prop_tr%s_tmstp%d_x%d' % (traceId, timePointIdx, propIdx)) == propValue)
        
        if (level, positionAtLevel, positionAtTrace, traceId) in self.visitedPositions:
            return
        
        self.visitedPositions.add((level, positionAtLevel, positionAtTrace, traceId))
        if level > self.formulaDepth:
            return
        elif level == self.formulaDepth:
            #at the last level we only allow propositions
            possibleOperators = {'prop':Bool('c_%d_%d_prop' % (level, positionAtLevel))}
        else:
            possibleOperators = {k:Bool('c_%d_%d_%s' % (level, positionAtLevel, k))  for k in self.listOfOperators}
        self.possibleOperators = possibleOperators
        
        # represents the value assigned to current "node" of the tree
        currentNodeVariable = Bool('p_level%d_k%d_tmstp%d_trace%s' % (level, positionAtLevel, positionAtTrace, traceId))
        noneOperator = Bool('c_%d_%d_none' % (level, positionAtLevel))
        
        
                                                                           
        
        
        # we should choose exactly one connective
        self.solver.add(AtMost(list(possibleOperators.values()) + [noneOperator] + [1]))
        self.solver.add(AtLeast(list(possibleOperators.values()) + [noneOperator] + [1]))
        
        childrenLevelAndPos = self.children(level, positionAtLevel)
        
        
        
        leftChildAtSameTracePosition = Bool('p_level%d_k%d_tmstp%d_trace%s' % (childrenLevelAndPos[0][0], childrenLevelAndPos[0][1], positionAtTrace, traceId))
        rightChildAtSameTracePosition = Bool('p_level%d_k%d_tmstp%d_trace%s' % (childrenLevelAndPos[1][0], childrenLevelAndPos[1][1], positionAtTrace, traceId))
        
        leftChildAtSameTracePositionNoneConnector = Bool('c_%d_%d_none' % (childrenLevelAndPos[0][0], childrenLevelAndPos[0][1]))
        rightChildAtSameTracePositionNoneConnector = Bool('c_%d_%d_none' % (childrenLevelAndPos[1][0], childrenLevelAndPos[1][1]))
        
        

        futureTracePositions = trace.futurePos(positionAtTrace)
        
        
        
        futureNodeVariablesLeftChild = [Bool('p_level%d_k%d_tmstp%d_trace%s' % (childrenLevelAndPos[0][0], childrenLevelAndPos[0][1], i, traceId))\
                                         for i in futureTracePositions]
        futureNodeVariablesRightChild = [Bool('p_level%d_k%d_tmstp%d_trace%s' % (childrenLevelAndPos[1][0], childrenLevelAndPos[1][1], i, traceId))\
                                         for i in futureTracePositions]
        

        for operator in possibleOperators:
            if operator == '!': 
                self.solver.assert_and_track(Implies(possibleOperators['!'], (currentNodeVariable == Not(leftChildAtSameTracePosition) ) ), 'negationOperator_'+str(currentNodeVariable) )
                
                #defining by default that the right child should be none (only one - left - child)
                self.solver.add(Implies(possibleOperators['!'], leftChildAtSameTracePositionNoneConnector == False))
                self.solver.add(Implies(possibleOperators['!'], rightChildAtSameTracePositionNoneConnector == True))
                self.arityOfOperatorRestrictions(1, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
                            
    
             
            elif operator == '|':
                self.solver.add(Implies(possibleOperators['|'], (currentNodeVariable == Or(leftChildAtSameTracePosition, rightChildAtSameTracePosition))))
                self.arityOfOperatorRestrictions(2, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
                
            elif operator == '&':
                self.solver.add(Implies(possibleOperators['&'], (currentNodeVariable == And(leftChildAtSameTracePosition, rightChildAtSameTracePosition))))
                self.arityOfOperatorRestrictions(2, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
            
            elif operator == '->':
                self.solver.add(Implies(possibleOperators['->'], (currentNodeVariable == Implies(leftChildAtSameTracePosition, rightChildAtSameTracePosition))))
                self.arityOfOperatorRestrictions(2, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
                
            elif operator == 'F':
                self.solver.add(Implies(possibleOperators['F'], currentNodeVariable == Or(futureNodeVariablesLeftChild) ))
                self.arityOfOperatorRestrictions(1, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
            
            elif operator == 'G':
                self.solver.add(Implies(possibleOperators['G'], currentNodeVariable == And(futureNodeVariablesLeftChild)))
                self.arityOfOperatorRestrictions(1, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
            elif operator == 'X':
                # there will always be at least two elements in futureNodeVariables... list (due to definition of futurePos function)
                self.solver.add(Implies(possibleOperators['X'], currentNodeVariable == futureNodeVariablesLeftChild[1]))
                self.arityOfOperatorRestrictions(1, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
            elif operator == 'U':
                self.solver.add(Implies(possibleOperators['U'], currentNodeVariable == Or([\
                                                                                          And( futureNodeVariablesLeftChild[0:qIndex] + [futureNodeVariablesRightChild[qIndex]] )\
                                                                                          for qIndex in range(len(futureTracePositions))\
                                                                                          ])\
                                        )\
                                )
                self.arityOfOperatorRestrictions(2, operator, leftChildAtSameTracePositionNoneConnector, rightChildAtSameTracePositionNoneConnector)
                
            
            
            elif operator == 'prop':
                
                
                for v in range(trace.numVariables):
                    #propValue is used to identify which proposition. this encodes that propValue implies that the connector is prop
                    self.solver.assert_and_track(Implies(\
                                                         Bool('propValue_%d_%d_x%d_%d' % (level, positionAtLevel, v, positionAtTrace)),\
                                                         possibleOperators['prop']
                                        ),\
                                        'propositionsEquality'+str(currentNodeVariable)+'_x'+str(v)
                                    )
                
                
                    # encode that if the variable xi is chosen as proposition, then in that trace truthfulness of the node (p_) has to be aligned to truthfulness of the data point (prop_)
                    self.solver.assert_and_track(Implies(\
                                                         Bool('propValue_%d_%d_x%d_%d' % (level, positionAtLevel, v, positionAtTrace)),\
                                                         currentNodeVariable ==Bool('prop_tr%s_tmstp%d_x%d'%(traceId, positionAtTrace, v))\
                                                         ),\
                                                  'dataPointEqualToNodeValue_level%d_k%d_x%d_tmstp%d_trace%s'%(level, positionAtLevel, v, positionAtTrace, traceId))
                
                # add the restriction that if the variable is prop, its children should be nones
                
                self.solver.add(Implies(possibleOperators['prop'], leftChildAtSameTracePositionNoneConnector == True))
                self.solver.add(Implies(possibleOperators['prop'], rightChildAtSameTracePositionNoneConnector == True))
            
         
        
        
        
        
        # would it be more elegant to replace this by a single next position?
        for i in futureTracePositions:
            self.generateRestrictions(level+1, childrenLevelAndPos[0][1], i, traceId, trace)
            self.generateRestrictions(level+1, childrenLevelAndPos[1][1], i, traceId,trace)
        
       
        
                    
                    
            
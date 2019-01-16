import pdb
import re
from lark import Lark, Transformer

class SimpleTree:
    def __init__(self, label = "dummy"):
        self.left = None
        self.right = None
        self.label = label
    
    def __hash__(self):
        return hash((self.label, self.left, self.right))
    
    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.label == other.label and self.left == other.left and self.right == other.right
    
    def __ne__(self, other):
        return not self == other
    
    def _isLeaf(self):
        return self.right == None and self.left == None
    
    def _addLeftChild(self, child):
        if child == None:
            return
        if type(child) is str:
            child = SimpleTree(child)
        self.left = child
        
    def _addRightChild(self, child):
        if type(child) is str:
            child = SimpleTree(child)
        self.right = child
    
    def addChildren(self, leftChild = None, rightChild = None): 
        self._addLeftChild(leftChild)
        self._addRightChild(rightChild)
        
        
    def addChild(self, child):
        self._addLeftChild(child)
        
    def getAllNodes(self):
        leftNodes = []
        rightNodes = []
        
        if self.left != None:
            leftNodes = self.left.getAllNodes()
        if self.right != None:
            rightNodes = self.right.getAllNodes()
        return [self] + leftNodes + rightNodes

    def getAllLabels(self):
        if self.left != None:
            leftLabels = self.left.getAllLabels()
        else:
            leftLabels = []
            
        if self.right != None:
            rightLabels = self.right.getAllLabels()
        else:
            rightLabels = []
        return [self.label] + leftLabels + rightLabels

    def __repr__(self):
        if self.left == None and self.right == None:
            return self.label
        
        # the (not enforced assumption) is that if a node has only one child, that is the left one
        elif self.left != None and self.right == None:
            return self.label + '(' + self.left.__repr__() + ')'
        
        elif self.left != None and self.right != None:
            return self.label + '(' + self.left.__repr__() + ',' + self.right.__repr__() + ')'


class Formula(SimpleTree):
    
    def __init__(self, formulaArg = "dummyF"):
        
        if not isinstance(formulaArg, str):
            self.label = formulaArg[0]
            self.left = formulaArg[1]
            try:
                self.right = formulaArg[2]
            except:
                self.right = None
        else:
            super().__init__(formulaArg)
    
    @classmethod
    def convertTextToFormula(cls, formulaText):
        
        f = Formula()
        try:
            formula_parser = Lark(r"""
                ?formula: _binary_expression
                        |_unary_expression
                        | constant
                        | variable
                !constant: "true"
                        | "false"
                _binary_expression: binary_operator "(" formula "," formula ")"
                _unary_expression: unary_operator "(" formula ")"
                variable: /x[0-9]*/
                !binary_operator: "&" | "|" | "->" | "U"
                !unary_operator: "F" | "G" | "!" | "X"
                
                %import common.SIGNED_NUMBER
                %import common.WS
                %ignore WS 
             """, start = 'formula')
        
            
            tree = formula_parser.parse(formulaText)
            #print(tree.pretty())
            
        except Exception as e:
            print("can't parse formula %s" %formulaText)
            print("error: %s" %e)
            
        
        f = TreeToFormula().transform(tree)
        return f
    
    
    
    def getAllVariables(self):
        allNodes = list(set(self.getAllNodes()))
        return [ node for node in allNodes if node._isLeaf() == True ]
    def getDepth(self):
        if self.left == None and self.right == None:
            return 0
        leftValue = -1
        rightValue = -1
        if self.left != None:
            leftValue = self.left.getDepth()
        if self.right != None:
            rightValue = self.right.getDepth()
        return 1 + max(leftValue, rightValue)
    
    def getNumberOfSubformulas(self):
        return len(self.getSetOfSubformulas())
    
    def getSetOfSubformulas(self):
        if self.left == None and self.right == None:
            return [repr(self)]
        leftValue = []
        rightValue = []
        if self.left != None:
            leftValue = self.left.getSetOfSubformulas()
        if self.right != None:
            rightValue = self.right.getSetOfSubformulas()
        return list(set([repr(self)] + leftValue + rightValue))
        
             

class TreeToFormula(Transformer):
        def formula(self, formulaArgs):
            
            return Formula(formulaArgs)
        def variable(self, varName):
            return Formula([str(varName[0]), None, None])
        def constant(self, arg):
            if str(arg[0]) == "true":
                connector = "|"
            elif str(arg[0]) == "false":
                connector = "&"
            return Formula([connector, Formula(["x0", None, None]), Formula(["!", Formula(["x0", None, None] ), None])])
                
        def binary_operator(self, args):
            return str(args[0])
        def unary_operator(self, args):
            return str(args[0])
    
        
        
        
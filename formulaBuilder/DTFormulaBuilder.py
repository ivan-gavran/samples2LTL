from sklearn import tree
from sklearn.tree import _tree
import pdb
import graphviz
from collections import deque
#from boto.cloudformation.stack import Output
import os

class DTFormulaBuilder:
    def __init__(self, features=None, data=None, labels=None):
        self.features = features
        self.data = [[self.convertData(k) for k in traceValuesPerFormulas] for traceValuesPerFormulas in data] 
        self.labels = [self.convertData(l) for l in labels]
    
    def convertData(self, x):
        if int(x) > 0:
            return 1
        else:
            return -1

    def readDataFromFile(self, fileName):
        self.data = []
        with open(fileName) as inputFile:
            for line in inputFile:
                self.data.append(convertData(k) for k in line.split(','))

    def readLabelsFromFile(self, fileName):
        self.labels = []
        with open(fileName) as inputFile:
            for line in inputFile:
                self.labels.append(convertData(line))

    def readDataFeaturesFile(self, fileName):
        self.features = []
        with open(fileName) as inputFile:
            for line in inputFile:
                self.features.append(line)
                
    def createASeparatingFormula(self):
        if self.data == None or self.labels == None:
            raise ValueError("missing needed data")
        self.classifier = tree.DecisionTreeClassifier().fit(self.data, self.labels)
        
    def tree_to_dot_file(self, outputFile):
        treeDotFormat = tree.export_graphviz(self.classifier, out_file=outputFile, feature_names = self.features, filled=True)
    
    def tree_to_text_file(self, outputFile):
        
        treeQueue = deque([(0,1)])
        inputTree = self.classifier
        tree_ = inputTree.tree_
        feature_names = [
            str(self.features[i]) if i != _tree.TREE_UNDEFINED else "*"
            for i in tree_.feature
        ]
        try:
            os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        except:
            pass
        with open(outputFile, "w") as out:
            while treeQueue:
                (node, depth) = treeQueue.pop()
                
                indent = "  " * depth
                decisionFormula = feature_names[node]
                out.write("{}{} : {}\n".format(indent, decisionFormula, tree_.n_node_samples[node]))
                if tree_.feature[node] != _tree.TREE_UNDEFINED:
                    treeQueue.append((tree_.children_left[node], depth+1))
                    treeQueue.append((tree_.children_right[node], depth+1))
    
    
    
    def numberOfNodes(self):
        tree_ = self.classifier.tree_
        return len([i for i in tree_.feature if i != _tree.TREE_UNDEFINED])
        
        
        
        
        
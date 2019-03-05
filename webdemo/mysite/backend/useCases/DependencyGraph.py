import pdb
import json
import yaml
import z3


class DependencyGraph:
    def __init__(self,  numMachines = 3):
        self.numMachines = numMachines
        self.nodes = []
        self.idToNodes = {}
        self.lastActionByNode = {}
    
    def addANode(self, newNode):
        self.nodes.append(newNode)
        self.idToNodes[newNode.eventId] = newNode 
        
    def readGraphFromPropertyFile(self, propertyFileName):
        with open(propertyFileName) as propertyFile:
            for line in propertyFile:
                if line.startswith("MessageEvent"):
                    infoString = line[len("MessageEvent"):-1]
                    infoString = infoString.replace("=", ": ")
                    infoStringYaml = yaml.load(infoString)
                    newNode = DependencyGraphNode(id = infoStringYaml['id'], label=("message", infoStringYaml["from"], infoStringYaml["to"]))
                    self.lastActionByNode[infoStringYaml["from"]] = infoStringYaml["id"]
                    for pred in infoStringYaml["predecessors"]:
                        newNode.addPredecessor(self.idToNodes[pred])
                    self.addANode(newNode)
                elif line.startswith("NodeStartEvent"):
                    infoString = line[len("NodeStartEvent"):-1]
                    infoString = infoString.replace("=", ": ")
                    infoStringYaml = yaml.load(infoString)
                    newNode = DependencyGraphNode(id = infoStringYaml['id'], label=("nodeRestart", infoStringYaml["nodeId"]))
                    try:
                        newNode.addPredecessor(self.idToNodes[self.lastActionByNode[infoStringYaml["nodeId"]]])
                    except Exception as e:
                        print(e)                                        
                    self.addANode(newNode)
    
        self.lengthOfLongestChain = max( [ node.positionInChain for node in self.nodes ] ) + 1
        
    
    
    def generateTraces(self, maxNumberOfSolutions = 3):
        def propositionToEvent(proposition, allEvents):
            node = self.idToNodes[int(proposition)]
           
            return allEvents[node.label]
        
        
        allSolutions = []
        allEvents = [("message", i, j) for i in range(self.numMachines) for j in range(self.numMachines)]        
        allEvents += [("nodeRestart", i) for i in range(self.numMachines)]
        allEvents = { allEvents[i] : i for i in range(len(allEvents)) }
        print(allEvents)
        propositions = { node.eventId : z3.Int(repr(node.eventId)) for node in self.nodes }
        sol = z3.Solver()
        for node in self.nodes:
            sol.add(propositions[node.eventId] < self.lengthOfLongestChain)
            sol.add(propositions[node.eventId] >= 0)
            for pred in node.preds:
                sol.add(propositions[ pred ] < propositions[node.eventId])
            
            
        while len(allSolutions) < maxNumberOfSolutions and sol.check() == z3.sat:
            model = sol.model()
            allSolutions.append(model)
            forbidExistingSolution = [ d() != model[d] for d in model ]
            sol.add(z3.Or(forbidExistingSolution))
        
        traces = []
        for solution in allSolutions:
            trace = [[0 for _ in range(len(allEvents))] for _ in range(self.lengthOfLongestChain)]
            for p in propositions:
                el = propositions[p]
                trace[int(solution[el].as_string())][propositionToEvent(p, allEvents)] = 1
            traces.append(trace)
        return traces
            
        
                
        

class DependencyGraphNode:
    def __init__(self, id = "dummy", label = "dummy"):
        self.preds = []
        self.eventId = id
        self.label=label
        self.positionInChain = 0
    
    
    def addPredecessor(self, pred):
        self.preds.append(pred.eventId)
        if pred.positionInChain + 1 > self.positionInChain:
            self.positionInChain = pred.positionInChain + 1

    def __repr__(self):
        s = "id = "+repr(self.eventId)+", preds = "+repr(self.preds) + ", label = "+repr(self.label)+", positionInChain= "+repr(self.positionInChain) + "\n"
        return s
        
    
        
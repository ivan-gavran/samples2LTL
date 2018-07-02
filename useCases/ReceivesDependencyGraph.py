import pdb
import json
import yaml
import z3


class ReceivesDependencyGraph:
    def __init__(self,  numMachines = 3):
        self.numMachines = numMachines
        self.nodes = []
        self.idToNodes = {}
        self.lastActionByNode = {}
    
    def addANode(self, newNode):
        self.nodes.append(newNode)
        self.idToNodes[newNode.eventId] = newNode 
        
    def readGraphFromPropertyFile(self, propertyFileName):
        self.labelsToIds = {}
        print(propertyFileName)
        with open(propertyFileName) as propertyFile:
            for line in propertyFile:
                line = line.replace("=", ": ")
                infoStringYaml = yaml.load(line)
                
                if infoStringYaml["stateArg"] == -1:
                    nodeLabel = (infoStringYaml["node"], infoStringYaml["sender"], "end")
                else:
                    nodeLabel = (infoStringYaml["node"], infoStringYaml["sender"])
                if nodeLabel in self.labelsToIds:
                    self.labelsToIds[nodeLabel].append(infoStringYaml["id"])
                else:
                    self.labelsToIds[nodeLabel] = [infoStringYaml["id"]]
                newNode = DependencyGraphNode(id = infoStringYaml['id'], label = nodeLabel)
                self.lastActionByNode[infoStringYaml["node"]] = infoStringYaml["id"]
                for pred in infoStringYaml["predecessors"]:
                    newNode.addPredecessor(self.idToNodes[pred])
                self.addANode(newNode)
            
    
        self.lengthOfLongestChain = max( [ node.positionInChain for node in self.nodes ] ) + 1
        
    
    
    def generateTraces(self, maxNumberOfSolutions = 3):
        
        def propositionToEvent(proposition, allEvents):
            node = self.idToNodes[int(proposition)]
           
            return allEvents[node.label]
        
        
        allSolutions = []
#         allEvents = [("message", i, j) for i in range(self.numMachines) for j in range(self.numMachines)]        
#         allEvents += [("nodeRestart", i) for i in range(self.numMachines)]
#         allEvents = { allEvents[i] : i for i in range(len(allEvents)) }
        propositions = { node.eventId : z3.Int(repr(node.eventId)) for node in self.nodes }
#         propositions = { node.eventId : z3.Int("var_"+repr(node.eventId)+"_"+repr(node.label))\
#                         for node in self.nodes}
        
        sol = z3.Solver()
        self.lengthOfTrace = self.lengthOfLongestChain + 4
        
                    
            
        
        for node in self.nodes:
            propKey = node.eventId
            sol.add(propositions[propKey] >= 0)
            sol.add(propositions[propKey] < self.lengthOfTrace)
            for pred in node.preds:
                sol.add((propositions[node.eventId] > propositions[pred]))
            
        while len(allSolutions) < maxNumberOfSolutions and sol.check() == z3.sat:
            model = sol.model()
            allSolutions.append(model)
            forbidExistingSolution = [ d() != model[d] for d in model ]
            sol.add(z3.Or(forbidExistingSolution))
        
        traces = []
        allStates = [(actorNode, sender) for actorNode in range(self.numMachines) for sender in range(self.numMachines)]
        allStates += [(actorNode, actorNode, "end") for actorNode in range(self.numMachines)]
        
        
        allStates = { allStates[i] : i for i in range(len(allStates)) }
        print(allStates)
        for solution in allSolutions:
            trace = [[0 for _ in range(len(allStates))] for _ in range(self.lengthOfTrace)]
            
            for p in propositions:
                el = propositions[p]
                try:
                    trace[int(solution[el].as_string())][propositionToEvent(p, allStates)] = 1
                except:
                    pdb.set_trace()
            
            traces.append(trace)
        
        return traces
            
        
                
        

class DependencyGraphNode:
    def __init__(self, id = "dummy", label = "dummy"):
        self.preds = []
        self.eventId = id
        self.label=label
        self.positionInChain = 0
        self.lastOnProcess = True
    
    
    def addPredecessor(self, pred):
        self.preds.append(pred.eventId)
        if pred.positionInChain + 1 > self.positionInChain:
            self.positionInChain = pred.positionInChain + 1
        if pred.label[0] == self.label[0]:
            pred.lastOnProcess = False
        

    def __repr__(self):
        s = "id = "+repr(self.eventId)+", preds = "+repr(self.preds) + ", label = "+repr(self.label)+", positionInChain= "+repr(self.positionInChain) + ", last on process = "+repr(self.lastOnProcess)+ "\n"
        return s
        
    
        
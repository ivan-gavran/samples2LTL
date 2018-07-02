import pdb
import json
import yaml
import z3


class StateOfNodesDependencyGraph:
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
                
                if infoStringYaml["state"] == "crash" or infoStringYaml["state"]=="end":
                    nodeLabel = (infoStringYaml["node"], infoStringYaml["state"])
                else:
                    nodeLabel = (infoStringYaml["node"], infoStringYaml["state"], infoStringYaml["stateArg"])
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
        
        def stateToRangeOfExistence(state, propositions, solution):
            try:
                stateIds = self.labelsToIds[state]
            except:
                return []
            coveredTimesteps = []
            for id in stateIds:
                coveredTimesteps += [i for i in range(int(solution[propositions[id][0]].as_string()), int(solution[propositions[id][1]].as_string()) + 1)]
            return coveredTimesteps
        
        
        allSolutions = []
#         allEvents = [("message", i, j) for i in range(self.numMachines) for j in range(self.numMachines)]        
#         allEvents += [("nodeRestart", i) for i in range(self.numMachines)]
#         allEvents = { allEvents[i] : i for i in range(len(allEvents)) }
        
        propositions = { node.eventId : (z3.Int("var_"+repr(node.eventId)+"_"+repr(node.label)+"_start"), z3.Int("var_"+repr(node.eventId)+"_"+repr(node.label)+"_end"))\
                        for node in self.nodes}
        
        sol = z3.Solver()
        self.lengthOfTrace = self.lengthOfLongestChain + 4
        
                    
            
        
        for node in self.nodes:
            propKey = node.eventId
            sol.add(propositions[propKey][0] <= propositions[propKey][1])
            sol.add(propositions[propKey][0] >= 0)
            sol.add(propositions[propKey][1] <= self.lengthOfTrace)
            for pred in node.preds:
                if node.label[0] == self.idToNodes[pred].label[0]:
                    sol.add(propositions[ pred ][1] + 1 == propositions[node.eventId][0])
                else:
                    sol.add((propositions[node.eventId][0] > propositions[pred][0]))
            if node.lastOnProcess == True:
                sol.add( propositions[propKey][1] == self.lengthOfTrace - 1 )
        while len(allSolutions) < maxNumberOfSolutions and sol.check() == z3.sat:
            model = sol.model()
            allSolutions.append(model)
            forbidExistingSolution = [ d() != model[d] for d in model ]
            sol.add(z3.Or(forbidExistingSolution))
        
        traces = []
        allStates = [(machineId, stateKind, stateArg) for stateKind in ["expect", "ready"] for stateArg in range(self.numMachines) for machineId in range(self.numMachines)]
        allStates += [ (machineId, ev) for machineId in range(self.numMachines) for ev in ["crash", "end"]]
        
        allStates = sorted(allStates)
        print({idx: allStates[idx] for idx in range(len(allStates))})
        
        for solution in allSolutions:
            trace = [[0 for _ in range(len(allStates))] for _ in range(self.lengthOfTrace)]
            
            for idx, state in enumerate(allStates):
                coveredRange = stateToRangeOfExistence(state, propositions, solution)
                for trueTimestep in coveredRange:
                    trace[trueTimestep][idx] = 1
            
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
        
    
        
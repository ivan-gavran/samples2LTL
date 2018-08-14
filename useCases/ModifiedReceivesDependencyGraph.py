import pdb
import json
import yaml
import re
import z3


class ModifiedReceivesDependencyGraph:
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
        with open(propertyFileName) as propertyFile:
            for line in propertyFile:
                line = line.replace("=", ": ")
                if "MessageReceived" in line:                    
                    line = line[len("MessageReceived"):]
                    infoStringYaml = yaml.load(line)
                    nodeLabel = (infoStringYaml["from"], infoStringYaml["to"])
                    
                    
                if "Decision" in line:
                    line = line[len("Decision"):]
                    infoStringYaml = yaml.load(line)
                    nodeLabel = (infoStringYaml["nodeId"], "DECISION")
                    
                
                if nodeLabel in self.labelsToIds:
                    self.labelsToIds[nodeLabel].append(infoStringYaml["id"])
                else:
                    self.labelsToIds[nodeLabel] = [infoStringYaml["id"]]
                newNode = DependencyGraphNode(id = infoStringYaml['id'], label = nodeLabel)
                    # we are considering an event being "receiving a message". that is justified when there are no crashes
                try:
                    #the case of received message
                    self.lastActionByNode[infoStringYaml["to"]] = infoStringYaml["id"]
                except:
                    #the case of a decision made
                    self.lastActionByNode[infoStringYaml["nodeId"]] = infoStringYaml["id"]
                for pred in infoStringYaml["predecessors"]:
                    newNode.addPredecessor(self.idToNodes[pred])
                self.addANode(newNode)
                
            
    
        self.lengthOfLongestChain = max( [ node.positionInChain for node in self.nodes ] ) + 1
        
    
    
    def generateTraces(self, maxNumberOfSolutions = 3):
        
        def propositionToEvent(proposition, allEvents):
            try:
                node = self.idToNodes[int(proposition)]
            except:
                node = self.idToNodes[proposition]                        
            return allEvents[node.label]
        
        
        allSolutions = []
        propositions = { node.eventId : z3.Int(repr(node.eventId)) for node in self.nodes }
        
        #print("number of propositions = %d" % len(propositions))
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
        allStates = [
            #(sender, recipient, senderState, senderVote)
            #(sender, recipient, senderState)
            (sender, recipient) 
                     for recipient in range(self.numMachines) 
                     for sender in range(self.numMachines) 
                     #for senderVote in range(self.numMachines)
                     #for senderState in ["LOOKING", "DECIDED"]
                     ]
        for node in range(self.numMachines):
            allStates.append((node, "DECISION"))
        
        allStatesDict = { allStates[i] : i for i in range(len(allStates)) }
        allStatesReverseDict = {i : allStates[i] for i in range(len(allStates))}
        print(allStatesReverseDict)
        #print(self.labelsToIds)
       # print(allStates)
        #print(propositions)
        
        for solution in allSolutions:
            trace = [[0 for _ in range(len(allStatesDict))] for _ in range(self.lengthOfTrace)]
            illustrationTrace = {}
            
            for p in propositions:
                el = propositions[p]
                try:
                    #print("setting 1 to [%d][%d]"%(int(solution[el].as_string()), propositionToEvent(p, allStates) ))
                    
                    # trace [moment][prop]
                    desc = self.idToNodes[p].label
                    if int(solution[el].as_string()) in illustrationTrace:
                        illustrationTrace[int(solution[el].as_string())].append(desc)
                    else:
                        illustrationTrace[int(solution[el].as_string())] = [desc]
                    trace[int(solution[el].as_string())][propositionToEvent(p, allStatesDict)] = 1
                except:
                    pdb.set_trace()
#             print("-----------")
#             print(illustrationTrace)
            #pdb.set_trace()
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
        
    
        

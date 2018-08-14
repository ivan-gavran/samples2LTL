import glob
import argparse
import pdb
import re


def isNodeALeader(fileName, node):
    with open(fileName) as file:
        for line in file:
        
        
            leaderProclamation = "Node "+repr(node)+" state: LEADING" 
            if  leaderProclamation in line:
                return True
        return False
def isNodeRestarted(fileName, node):
    with open(fileName) as file:
        nodeCrashLine =  "nodeId="+repr(node)
        for line in file:
            if  "NodeCrashEvent" in line and nodeCrashLine in line:
                return True
        return False

def isNodeRestartedAfterItSentMessageToItself(fileName, node):
    phase = 0
    with open(fileName) as file:
        nodeCrashLine =  "nodeId="+repr(node)
        nodeMessageLine = "from=1, to=1"
        for line in file:
            if nodeMessageLine in line:
                phase = 1
            if  "NodeCrashEvent" in line and nodeCrashLine in line and phase == 1:
                return True
        return False


def isExecutionFaulty(fileName):
    with open(fileName) as file:
        leaderVotes = {0:0, 1:0, 2:0}
        numLeaders = 0
        for line in file:
            if "final vote:" in line:
                m = re.search("(?<=leader=)[012]", line)
                chosenLeader = m.group(0)
                leaderVotes[int(chosenLeader)] += 1
        maxVotes = max(leaderVotes.values())
        if maxVotes < len(leaderVotes.keys()):
        #if maxVotes == len(leaderVotes.keys()) and (leaderVotes[1] > 0 or leaderVotes[0] > 0):
            #print(leaderVotes)
            
            return True
        else:
            return False
            
        

def findFaults(folderContainingExperimentsResults):
    allResultFiles = glob.glob(folderContainingExperimentsResults+"*/execution")
    for file in allResultFiles:
        #if isNodeRestartedAfterItSentMessageToItself(file,1) == True and isExecutionFaulty(file) == False:
        if isExecutionFaulty(file) == True:
            fileNumber = file.split("/")[-2]
            print(fileNumber)
            print("\n")
            #print(file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_data_folder", dest="testDataFolder", default="useCases/PCTCP/pctcp-d1/")
    
    args,unknown = parser.parse_known_args()
    findFaults(args.testDataFolder)



'''
The organization of all currently available machines
'''
class Machine:
    allMachines = []

    # initializing a machine ID, type, and capacity to every machine available
    def __init__(self, machineID, type, totalCapacity, currentCapacity, log):
        self.machineID = machineID               # assigns a unique ID to every available machine
        self.type = type                         # convenience for finding type which is attached to its ID
        self.totalCapacity = totalCapacity       # convenience for finding capacity which is attached to its ID 
        self.currentCapacity = currentCapacity   # keeps track of current capacity in respect to time
        self.log = log                           # tracks time periods of usage for specific machine. Format: <startTime, endTime>

    # getters and setters

    def getType(self):
        return self.type
    
    def getCapacity(self):
        return self.totalCapacity
    
    def getTypeId(id):
        for machine in Machine.allMachines:
            if machine.machineID == id:
                return machine.type

    def getLog(self):
        return self.log
    
    def setLog(self, timeRange):
        self.log = timeRange

    def getCurrentCapacity(self):
        return self.currentCapacity
    
    def getTotalCapacity(self):
        return self.totalCapacity

    def incrementCurrentCapacity(self, size):
        self.currentCapacity += size
    
    def clearCapacity(self):
        self.currentCapacity = 0

'''
The organization of all desired products
'''
class Batch:
    allProducts = []
    copyAllProducts = []

    # initializing ingredients and processing times of all products desired
    def __init__(self, batchID, ingredUsed, timeUsed, machinesUsed = 0, currentTime = 0):
        self.batchID = batchID             # assigns each batch a unique ID
        self.ingredUsed = ingredUsed       # format: arr[mashing, boiling, fermenting, filtering] (separated by ingred needed during processes)
        self.timeUsed = timeUsed           # format: arr[mashing, boiling, fermenting, filtering] (seperated by time needed during processes)
        self.machinesUsed = machinesUsed   # used to keep batch progess in regards to how many machines the batch passed through
        self.currentTime = currentTime     # used to keep batch progress in regards to time
    
    # getters and setters

    def getMachinesUsed(self):
        return self.machinesUsed
            
    def getCurrentTime(self):
        return self.currentTime
    
    def getTimeUsed(self, type):
        return self.timeUsed[type]
    
    def getID(self):
        return self.batchID
    
    def setCurrentTime(self, newTime):
        self.currentTime = newTime
    
    def incrementMachinesUsed(self):
        self.machinesUsed += 1

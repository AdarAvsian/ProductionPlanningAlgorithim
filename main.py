from classes import *
import random
import math
from generateChart import createVisual
from generateAnimation import createAnimation

# CONSTANTS
TIME_BETWEEN_USE = 3 # in hours
START_HOUR = 9
END_HOUR = 17

# keeps track of all machines and their properties, Id matches index **IMPORTANT
Machine.allMachines =[Machine(0, "brewhouse", 45, 0, None),  Machine(1, "brewhouse", 45, 0, None), Machine(2, "boiling", 90, 0, None), Machine(3, "boiling", 90, 0, None), Machine(4, "fermenting", 180, 0, None), Machine(5, "fermenting", 180, 0, None), Machine(5, "filtering", 180, 0, None), Machine(6, "filtering", 180, 0, None)]

# machine dict
machineDict = {"brewhouse": 0, "boiling": 1, "fermenting": 2, "filtering": 3}
inverseDict = {0: "brewhouse", 1: "boiling", 2: "fermenting", 3: "filtering"}

ingredList = []
totalArr = [0, 0, 0] # grains, hops, yeast
ingredDict = {0 : "Grains", 1 : "Hops", 2 : "Yeast", 3 : "Hops"}
totalIngredDict = {"Grains": 0, "Hops": 1, "Yeast": 2}

finishTimes = [] # keeps track of finish times of all batches
allTime = [] # keeps track of final finish time (finish time of last batch)

# initializes all batches
def initProducts(): # 8 test batches
    # return [Batch(0, [100, 20, 20, 10], [10, 100, 200, 20]), Batch(1, [100, 20, 20, 10], [10, 100, 200, 20])]
    return [Batch(0, [100, 20, 20, 0], [3, 120, 240, 24]), Batch(1, [100, 20, 20, 0], [3, 120, 240, 24]),
            Batch(2, [100, 20, 20, 0], [3, 120, 240, 24]), Batch(3, [100, 20, 20, 0], [3, 120, 240, 24]),
            Batch(4, [100, 20, 20, 0], [3, 120, 240, 24]), Batch(5, [100, 20, 20, 0], [3, 120, 240, 24]),
            Batch(6, [100, 20, 20, 0], [3, 120, 240, 24]), Batch(7, [100, 20, 20, 0], [3, 120, 240, 24])]

# DO NOT MODIFY (that is what copyAllProducts is for). This is static storage of batch info
Batch.allProducts = initProducts()

'''
Encoding all properties of a schedule to create a chromosome
    - Consists of machine ID, batch ID, start time of machine
    - Sorted by start time
    - Ex.     00            00             00000         00099                  01             01             00100         00200         ....
    -     Machine ID     Batch Id       Start time      End Time            Machine ID      Batch Id       Start time      End time       ....
    -                           Element 0                                                          Element 1                              ....
    -
    - ASSUMPTIONS: Machine ID and Batch ID do not exceed 99. Start time does not exceed 99999. Decimals are counted as a gene
'''
def encode(machineID, batchID, startTime, endTime):
    encodedStr = ""
    encodedStr += machineID if len(machineID) == 2 else ("0" + machineID)
    encodedStr += batchID if len(batchID) == 2 else ("0" + batchID)

    numZeros = 5 - len(startTime)
    for i in range(numZeros): encodedStr += "0"
    encodedStr += startTime

    numZeros = 5 - len(endTime)
    for i in range(numZeros): encodedStr += "0"
    encodedStr += endTime
    return encodedStr

'''
Decode a standardized encoded string
'''
def decode(chromosome):
    # decode format: [[machineId, batchId, startTime, endTime], ....] Elements of higher level array will be separated by processes
    highArr = [] # outer array (what will be returned)
    for process in chromosome:
        lowArr = [] # for iterative/cleansing purposes
        lowArr.append(process[0:2])
        lowArr.append(process[2:4])
        lowArr.append(process[4:9])
        lowArr.append(process[9:14])
        anotherArr = [] # what will contain individual components (the elements of highArr)
        for block in lowArr:
            gene = 0
            while gene < len(block):
                if block[gene] == "0" and gene != len(block) - 1:
                    block = block[gene + 1:]
                else:
                    anotherArr.append(block) # cleansed component is added
                    break
        highArr.append(anotherArr) # components of a single process is added as an element
    return highArr

'''
Working hours constraint
'''
def workHours(hour):
    hourOfDay = hour % 24
    if hourOfDay < START_HOUR:
        hour += (START_HOUR-hourOfDay)
    elif hourOfDay>END_HOUR:
        hour += (24-hourOfDay + START_HOUR) 
    return hour

'''
Outputs ingreds. info
'''

def encodeBlocks(preMachineArr, randomBatch):
    global blocksHistory
    for i in range (0, len(preMachineArr), 3):
        blocksHistory.append(encode(str(preMachineArr[i + 2]), str(randomBatch.getID()), str(preMachineArr[i]), str(preMachineArr[i + 1])))
    global previousPreMachineArrLengths
    previousPreMachineArrLengths.append(len(preMachineArr)/3)

def appendToIngredList(decodedArr):
    for process in decodedArr:
        type = machineDict[Machine.allMachines[int(process[0])].type]
        ingredient = ingredDict[type]
        getIngred = Batch.allProducts[int(process[1])]
        ingredLine = "Ingredient: " + ingredient + ",   Quantity: " + str(getIngred.ingredUsed[type]) + ",   Time of Use: " + str(process[2])
        ingredList.append(ingredLine)
        totalArr[totalIngredDict[ingredient]] += getIngred.ingredUsed[type]
    
    for ingred in ingredList:
        print(ingred)
    print("Grains: " + str(totalArr[0]))
    print("Hops: " + str(totalArr[1]))
    print("Yeast: " + str(totalArr[2]))
    print("\n")

'''
Finds best machine based on machine logs and currentTime. Machine with lowest time and most optimal capacity (current machine only) is chosen.
'''
def getBestMachine(randomBatch, currentTime, next=0, currentCapacity = 0, totalCapacity = 0):
    possibleMachines = [] # format: <machineID, nextOpeningTime>
    typeOfProcess = randomBatch.machinesUsed + next

    # append machines of specific process and their appropriate times of availability
    for machineIndex in range(len(Machine.allMachines)):
        machineObj = Machine.allMachines[machineIndex] # grabs object based on Id/index
        if machineDict[machineObj.type] == typeOfProcess: #if machine type matches next step of batch
            if machineObj.log and machineObj.log >= currentTime: # if last process finishes after currentTime
                possibleMachines.append((machineIndex, machineObj.log))
            else: 
                possibleMachines.append((machineIndex, currentTime))
    minTime = math.inf # initial value
    minCap = 0 # initial value

    # first iterates to find machine of lowest time, and then finds machine with most optimal capacity
    for machine in possibleMachines:
        if machine[1] < minTime:
            minTime = machine[1]
            machineID = machine[0]
    # only optimizes capacity if searching for a current machine
    if not next:
        for machine in possibleMachines:
            obj = Machine.allMachines[machine[0]]
            if machine[1] == minTime and obj.totalCapacity >= minCap and obj.totalCapacity + currentCapacity <= totalCapacity:
                machineID = machine[0]
                minCap = obj.totalCapacity
    bestMachine = Machine.allMachines[machineID]
    return bestMachine, minTime, machineID

'''
Updates process times based on the assumption that next machine has to be available after current first turn finish (for storage)
'''
def pushUp(randomBatch, processesArr, firstTurnFinish): # processesArr format: [startTimeOfMachine, endTime, machineID,  ....]
    difference = processesArr[-3] - firstTurnFinish # difference between end of current first turn and start of next machine process
    for i in range (0, len(processesArr), 3):
        if difference > 0 and i + 3 != len(processesArr): # add difference so that nexMachine start process = first turn endTime of current machine
            processesArr[i] += difference
            processesArr[i+1] += difference
        if i + 3 == len(processesArr): # when nextMachine start process <= first turn endTime of current machine,
                                       # push up next Machine's start time to equal end time of current process
            duration = processesArr[-2] - processesArr[-3]
            processesArr[-3] = processesArr[-5]
            processesArr[-2] = processesArr[-3] + duration

        # working hours constraint
        hourDifference = abs(processesArr[i] -  workHours(processesArr[i]))
        if hourDifference > 0:
            for j in range (i, len(processesArr), 3):
                if j==i: processesArr[j] =  workHours(processesArr[j])
                else: processesArr[j] += hourDifference
                processesArr[j+1] += hourDifference

        Machine.allMachines[processesArr[i + 2]].setLog(processesArr[i + 1]) # machine logs are updated 
        randomBatch.setCurrentTime(processesArr[-2]) # batch currentTime is updated
    return processesArr

'''
Schedule is randomly generated (batches are randomly chosen until all are completed)
'''
def createChromosome():
    finishTimes = [] # keeps track of finish times of all generated chromosomes
    copyAllProducts = initProducts() # copy of all batches which will be modified
    chromosome = [] # all processes will be appended here
    global blocksHistory
    blocksHistory = []
    global previousPreMachineArrLengths
    previousPreMachineArrLengths = []

    # continue until a full chromosome (schedule) is created
    while True: # iterating through batches
        if not len(copyAllProducts): # if all batches are completed
            for machine in Machine.allMachines:
                machine.log = [] # reset logs on all machines
            allTime.append(max(finishTimes)) # append final finish time
            return chromosome, blocksHistory, previousPreMachineArrLengths # base case
        
        # variable initializations and randomization of batches
        ID = random.randint(0, len(copyAllProducts) - 1) if len(copyAllProducts) >  1 else 0
        randomBatch = copyAllProducts[ID]
        numTurns = 0
        preMachineArr = []
        nextMachine = []
        firstTurnFinish = []
        following = None
        while True: # iterate through batch
            if randomBatch.machinesUsed == 3: # next machine already added to schedule, finish batch
                endtime = preMachineArr[-2]
                finishTimes.append(endtime) # appends finish time of batch
                del copyAllProducts[ID] # delete object from modifiable array (for maximum effiency in randomization process)
                for i in range (0, len(preMachineArr), 3):
                    # append encoded processes
                    chromosome.append(encode(str(preMachineArr[i + 2]), str(randomBatch.batchID), str(preMachineArr[i]), str(preMachineArr[i + 1] - TIME_BETWEEN_USE)))
                break
            else: # batch is not finished
                if randomBatch.machinesUsed == 0 or numTurns > 0: # find best current machine
                    following = getBestMachine(randomBatch, randomBatch.currentTime, next = 1) # find best next machine
                    machineObj, minTimeAllMachines, machineID = getBestMachine(randomBatch, randomBatch.currentTime, 0, following[0].currentCapacity, following[0].totalCapacity)
                    machineObj.setLog(minTimeAllMachines + randomBatch.timeUsed[randomBatch.machinesUsed] + TIME_BETWEEN_USE)
                else: # if current machine is already existing due to nextMachine of previous iteration.
                    following = getBestMachine(randomBatch, randomBatch.currentTime, next = 1) # find best next machine

                if numTurns > 0 or randomBatch.machinesUsed == 0: # append if not appended during previous iteration or on first process
                    preMachineArr.append(minTimeAllMachines)
                    preMachineArr.append(minTimeAllMachines + randomBatch.timeUsed[randomBatch.machinesUsed] + TIME_BETWEEN_USE)
                    preMachineArr.append(machineID)

                if numTurns == 0: # where nextMachine info and end of first turn of current process is held
                    logTime = machineObj.log
                    if len(nextMachine) == 0:
                        nextMachine.append(following)
                        firstTurnFinish.append(logTime)
                    else:
                        if nextMachine[-1][0].type != following[0].type: # conditional for preventing nested process turns from erasing data needed
                            nextMachine.append(following)
                            firstTurnFinish.append(logTime)

                nextMachine[-1][0].incrementCurrentCapacity(machineObj.totalCapacity) # incrementing capacity of next machine                 
                if nextMachine[-1][0].totalCapacity <= nextMachine[-1][0].currentCapacity: # if next machine is full
                    nextMachine[-1][0].clearCapacity() # clear capacity of machine
                    durationNextMachine = randomBatch.timeUsed[randomBatch.machinesUsed + 1] + TIME_BETWEEN_USE # duration of next machine
                    preMachineArr.append(nextMachine[-1][1]) # appends nextMachine info
                    preMachineArr.append(nextMachine[-1][1] + durationNextMachine)
                    preMachineArr.append(nextMachine[-1][2])
                    encodeBlocks(preMachineArr, randomBatch)
                    preMachineArr = pushUp(randomBatch, preMachineArr, firstTurnFinish[-1]) # modify current machine process times if necessary
                    encodeBlocks(preMachineArr, randomBatch)
                    numTurns = 0 # reset number of turns
                    randomBatch.incrementMachinesUsed() # increase process of batch
                    machineObj, minTimeAllMachines, machineID = nextMachine[-1] # set next iteration's current machine to current iteration's next machine
                    # erase irrelevant data
                    nextMachine.pop()
                    firstTurnFinish.pop()
                else: 
                    # if machinesUsed > 0, go back a process
                    if randomBatch.machinesUsed > 0:
                        randomBatch.machinesUsed = 0
                    else : numTurns += 1 # if already on first process, increase turns

'''
Creates list of randomized schedules
'''         
def initialPop():
    populationArr = [] # all chromosomes will be appended to this arr. Each element is a chromosome (a possible solution)

    # Continue until chromosomes in n range are created
    for n in range(100): 
        populationArr.append(createChromosome())
    return populationArr # returns n number of chromosomes (schedules)


'''
Called when script is run
'''
def main(): # testing
    arr = initialPop() # array of generated schedules
    winningTime = str(min(allTime)) # the least finish time of all schedules
    winningSchedule = allTime.index(int(winningTime)) # finds best schedule based on indexing
    winningScheduleArr = arr[winningSchedule] # decodes schedule 
    appendToIngredList(decode(winningScheduleArr[0])) # appends ingreds. info
    print("Best time: " + winningTime)
    createVisual(decode(winningScheduleArr[0]), START_HOUR, END_HOUR) # creates visual of best schedule
    createAnimation(decode(winningScheduleArr[1]), winningScheduleArr[2], START_HOUR, END_HOUR)

main() # begins algorithm
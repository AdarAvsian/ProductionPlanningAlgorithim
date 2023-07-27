# Importing the matplotlib.pyplot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from classes import Machine
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import animation
import copy
import seaborn as sns

'''
Create Animation takes in decodedArr which consists of all the blocks before AND after they go though the pushup function. This is necessary so the animation can show how the algorithim works.

decodeArr format: [[machineId, batchId, startTime, endTime], ....]
previousPreMachineArrLengths format: [previousPreMachineARRLength#1, ...]
'''

def createAnimation(decodedArr, previousPreMachineArrLengths, START_HOUR, END_HOUR):
    
    #Getting number of machines and batches
    numOfMachines = -1
    numOfBatches = -1
    for process in decodedArr:
        if int(process[0]) > numOfMachines:
            numOfMachines = int(process[0])
        if int(process[1]) > numOfBatches:
            numOfBatches = int(process[1])
    numOfMachines += 1
    numOfBatches += 1
    
    #Subtratcing TIME_BETWEEN_USE
    for process in decodedArr:
        process[3] = int(process[3]) -3
    
    blockIDs = [] #format: [[machineID, batchID, startTime]]
    modifiedArr = [] 
    blockID = 0 #
    placementHolder = 0
    batchHistory = []

    '''
    Assigning the block before and after they go thorugh push up method the same blockID. This is done so that the animation function knows which block needs to be update on the chart.
    ''' 
    for i in range(len(previousPreMachineArrLengths)+1):
        if i == len(previousPreMachineArrLengths) or (i != 0 and int(previousPreMachineArrLengths[i]) < int(previousPreMachineArrLengths[i-1])): #once batch is done
            for col in range(len(batchHistory[-1])):
                for row in range(len(batchHistory)):
                    if col < len(batchHistory[row]):
                        block = batchHistory[row][col]
                        tempBlock = copy.deepcopy(block)
                        if tempBlock not in blockIDs:
                            blockIDs.append(tempBlock)
                            block.append(int(col) + int(blockID))
                            modifiedArr.append(block)
            blockID += len(batchHistory[-1])
            batchHistory = []

        placementHolder = 0
        for length in previousPreMachineArrLengths[:i]:
            placementHolder += int(length)
        cycle = []
        if i != len(previousPreMachineArrLengths):
            for j in range(int(placementHolder), int(previousPreMachineArrLengths[i]) + int(placementHolder)):
                block = decodedArr[j]
                cycle.append(block)
            batchHistory.append(cycle)

    colorDict = sns.color_palette("Set2")
    
    # Labelling tickes of y-axis
    yLabels = []
    yLabelsDict = {}
    for i in range(numOfMachines):
        j = 1
        if (i>0 and Machine.allMachines[i].type == Machine.allMachines[i-1].type): j +=1
        value = str(Machine.allMachines[i].type) + " #" + str(j) + " (" + str(Machine.allMachines[i].totalCapacity) + ")"
        yLabelsDict[i] = value
        yLabels.append(value)

    y_data = [] #which machine
    x_data = [] #duration
    left_data = [] #starttime
    bar_indexes = [] #block IDS
    color_data = [] #which color (color represents batch)
    
    for process in modifiedArr:
        y_data.append(process[0])
        x_data.append(int(process[3]) - int(process[2]))
        left_data.append(int(process[2]))
        color_data.append(process[1])
        bar_indexes.append(process[4])

    '''
    These variables will be passed into the inital creation of the plot (first frame in the animation).
    '''

    original_y_data = [] 
    original_x_data = []
    blockID_locations = []
    for process in modifiedArr:
        blockID_locations.append(process[4])

    for i in range(blockID):
        index = blockID_locations.index(i)
        original_y_data.append(yLabelsDict[int(modifiedArr[index][0])])
        original_x_data.append(int(modifiedArr[index][3]) - int(modifiedArr[index][2]))

    '''
    Creating the chart
    '''

    fig, ax = plt.subplots(figsize=(20,8))

    ax.set_xlim(0, int(decodedArr[-1][3]) + 24)

    labels = np.arange(0, int(decodedArr[-1][3])/24 + 1,1).astype(int) # x axis by # of days

    # newLabels = []
    # dayDict = {0:"Mon", 1:"Tue", 2:"Wed", 3:"Thur", 4:"Fri", 5:"Sat", 6:"Sun", }

    # for day in labels:
    #     newLabels.append(dayDict[day%7]) # x axis by days of the week

    # ax.set_xticks(np.arange(0, int(decodedArr[-1][3])+24, 24), newLabels)
    ax.set_xticks(np.arange(0, int(decodedArr[-1][3])+24, 24), labels)

    '''
    Setting the tick marks as the working hours per each day
    '''

    minorXTicks = []
    startHours = np.arange(START_HOUR, int(decodedArr[-1][3])+24, 24)
    endHours = np.arange(END_HOUR, int(decodedArr[-1][3])+24 + (END_HOUR-START_HOUR), 24)
    for i in range(len(startHours)):
        minorXTicks.append(startHours[i])
        minorXTicks.append(endHours[i])

    ax.set_xticks(minorXTicks, minor=True)

    ax.set_ylabel('Machines')
    ax.set_xlabel('Number of Days since Start')
    ax.grid(True)

    bars = plt.barh(original_y_data, original_x_data, left=-5000, color="white")

    '''
    Animation is called for each frame where i is the number of frames.
    '''
    def animate(i):
        index = bar_indexes[i]
        bars[index].set_x(left_data[i])
        bars[index].set_color(colorDict[int(color_data[i])])

    anim = animation.FuncAnimation(fig, animate, frames=len(left_data), interval=300, repeat=False)
    
    anim.save('animation.gif')


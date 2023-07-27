import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from classes import Machine
import matplotlib.colors as mcolors
import numpy as np
import seaborn as sns

'''
decode format: [[machineId, batchId, startTime, endTime], ....] Elements of higher level array will be separated by processes
'''

def createVisual(decodedArr, START_HOUR, END_HOUR):
    numOfMachines = -1
    numOfBatches = -1
    for process in decodedArr:
        if int(process[0]) > numOfMachines:
            numOfMachines = int(process[0])
        if int(process[1]) > numOfBatches:
            numOfBatches = int(process[1])
    numOfMachines += 1
    numOfBatches += 1

    colorDict = sns.color_palette("Set2")
        
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots(figsize=(20, 8))

    # plt.rcParams.update({'font.size': 32})

    # Setting Y-axis limits
    gnt.set_ylim(0, 10 * numOfMachines + 20)

    # Setting X-axis limits
    gnt.set_xlim(0, int(decodedArr[-1][3]) + 24)
    labels = np.arange(0, int(decodedArr[-1][3])/24 + 1,1).astype(int) # x axis as # of days
    
    # newLabels = []
    # dayDict = {0:"Mon", 1:"Tue", 2:"Wed", 3:"Thur", 4:"Fri", 5:"Sat", 6:"Sun", }
    # for day in labels:
    #     newLabels.append(dayDict[day%7]) # x axis as the day of the week

    gnt.set_xticks(np.arange(0, int(decodedArr[-1][3])+24, 24), labels)

    # Setting min tick marks as working hours
    minorXTicks = []
    startHours = np.arange(START_HOUR, int(decodedArr[-1][3])+24, 24)
    endHours = np.arange(END_HOUR, int(decodedArr[-1][3])+24 + (END_HOUR-START_HOUR), 24)

    for i in range(len(startHours)):
        minorXTicks.append(startHours[i])
        minorXTicks.append(endHours[i])

    gnt.set_xticks(minorXTicks, minor=True)
    # gnt.tick_params(which='minor', length=4, color='r')

    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('Number of Days since Start')
    gnt.set_ylabel('Machines')

    # Setting ticks on y-axis
    gnt.set_yticks([i for i in range(10, numOfMachines * 10 + 1, 10)])

    # Labelling ticks of y-axis
    yLabels = []
    for i in range(numOfMachines):
        j = 1
        if (i>0 and Machine.allMachines[i].type == Machine.allMachines[i-1].type): j +=1
        yLabels.append(str(Machine.allMachines[i].type) + " #" + str(j) + " (" + str(Machine.allMachines[i].totalCapacity) + ")")

    gnt.set_yticklabels(yLabels)

    # Setting graph attribute
    gnt.grid(True)

    # adding processes to ghantt chart
    for process in decodedArr:
        gnt.broken_barh([(int(process[2]), int(process[3]) - int(process[2]))], (10 * (int(process[0]) + 1) - 5, 9), facecolors =(colorDict[int(process[1])]))

    # when saving, specify the DPI
    plt.savefig("gantt.png")



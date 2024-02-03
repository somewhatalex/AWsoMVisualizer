import math
import numpy as np
from config_local import *

def magnitude(arr):
    """
    REQUIRES:
    - arr: 3-value array [x, y, z]

    EFFECTS: returns magnitude
    """
    return math.sqrt(float(arr[0])**2 + float(arr[1])**2 + float(arr[2])**2)

def multiplyArr(arr, constant):
    """
    REQUIRES:
    - arr: array of any length
    - constant: value to multiply all values in array by

    EFFECTS: returns array with all values multiplied by constant
    """
    for i in range(len(arr)):
        arr[i] = float(arr[i]) * constant

    return arr

def mse(simTimestamps, simValues, dataTimestamps, dataValues):
    """
    Calculates mean squared error

    NOTE: timestamps must be converted to int format

    REQUIRES:
    - simTimestamps, simValues: arrays with simulation timestamps and values
    - dataTimestamps, dataValues: arrays with data timestamps and values

    EFFECTS: returns value of mean squared error between the two datasets
    """
    
    # replace all nan values in original data with 0
    nanMask = ~np.isnan(dataValues)
    dataValues = np.array(dataValues)
    dataTimestamps = np.array(dataTimestamps)
    dataTimestamps = dataTimestamps[nanMask]
    dataValues = dataValues[nanMask]

    interpSimValues = interpolate(dataTimestamps, simTimestamps, simValues)

    # calculate mse
    n = len(dataTimestamps)
    squaredDiff = [(actual - predicted)**2 for actual, predicted in zip(dataValues, interpSimValues)]
    mse = sum(squaredDiff) / n

    return mse

def interpolate(x1, x2, y2):
    """
    REQUIRES:
    - x1: 1st dataset x axis
    - x2, y2: 2nd dataset

    EFFECTS: interpolates dataset 2 onto x1
    """
    interpY2 = np.interp(x1, x2, y2)

    return np.array(interpY2)

def findPlotOpacities(arr):
    """
    REQUIRES:
    - arr: array to calculate opacity values for

    EFFECTS: interpolates min and max values to assign opacity values to each arr item. The opacity range is 
    specified in config_local, and the min and max values will be assigned to the min and max values in the arr.
    """
    arr = np.array(arr)

    # replace nan with negative inf
    arr[np.isnan(arr)] = -np.inf

    # get indices that would sort the array
    sorted_indices = np.argsort(arr)

    # create array of ranks based on the sorted indices
    ranks = np.empty_like(sorted_indices)
    ranks[sorted_indices] = np.arange(1, len(arr) + 1)

    # make nan values last place
    ranks[arr == -np.inf] = np.max(ranks) + 1

    # get opacity range
    minOpacity = configs["simLineOpacityRange"][0]
    maxOpacity = configs["simLineOpacityRange"][1]

    # calculate difference in opacity between 2 ranks
    opacityStep = (maxOpacity - minOpacity) / (np.max(ranks - 1))

    opacities = []

    # calculate individual opacities
    for rank in ranks:
        opacities.append(maxOpacity - opacityStep * (rank - 1))

    return opacities

def normalizeData(data):
    """
    REQUIRES:
    - data: input data

    EFFECTS: Normalizes each value in data as a proportion of the max value
    """
    return [x / max(data) for x in data]

def calculate2DArrayAverage(arr):
    """
    REQUIRES:
    - arr: input 2d array
    Nested arrays MUST be of equal length!

    EFFECTS: Averages all nested arrays in arr to form a single array
    """
    numRows = len(arr)
    numCols = len(arr[0])

    averages = [0] * numCols

    for col in range(numCols):
        colSum = sum(row[col] for row in arr)
        averages[col] = colSum / numRows

    return averages

def indexOfMinValue(arr):
    """
    REQUIRES:
    - arr: input array

    EFFECTS: Returns index of min value in array
    """
    maxVal = min(arr)
    maxIndex = arr.index(maxVal)
    return maxIndex

def filterDatasetByVarName(dataset, variables, varsToKeep):
    """
    REQUIRES:
    - dataset: array of values
    - variables: indices of variables MUST correlate to dataset
        ie. dataset[2] is the value for variables[2]
    - varsToKeep: variables whose corresponding value in dataset will be kept

    EFFECTS: Returns [newVarList, filteredDataset] where the indices of
    newVarList correspond to the items in filteredDataset
    """
    filteredDataset = []
    newVarList = []

    for i in range(len(varsToKeep)):
        filteredDataset.append(dataset[variables.index(varsToKeep[i])])
        newVarList.append(varsToKeep[i])

    return [newVarList, filteredDataset]
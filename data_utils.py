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
    simTimestamps = np.array(simTimestamps)
    dataTimestamps = np.array(dataTimestamps)
    
    interpValues = interpolate(simTimestamps, simValues, dataTimestamps, dataValues)

    # calculate mse
    n = len(dataTimestamps)
    squaredDiff = [(actual - predicted)**2 for actual, predicted in zip(interpValues[1], interpValues[0])]
    mse = sum(squaredDiff) / n
    
    return mse

def interpolate(x1, y1, x2, y2):
    """
    REQUIRES:
    - x1, y1: 1st dataset
    - x2, y2: 2nd dataset

    EFFECTS: returns interpolation of 2 data sets in [Y1, Y2, X] with all 3 objects being arrays
    """
    # get interpolation bounds
    minX = max(min(x1), min(x2))
    maxX = min(max(x1), max(x2))

    # create new x range for interpolation
    interpX = np.linspace(minX, maxX, num = 25, endpoint=True)
    
    interpY1 = np.interp(interpX, x1, y1)
    interpY2 = np.interp(interpX, x2, y2)

    return [np.array(interpY1), np.array(interpY2), np.array(interpX)]

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
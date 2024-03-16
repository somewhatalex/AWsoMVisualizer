import math
import numpy as np
from config_local import *
from scipy.stats import spearmanr

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

class datafile:
    """
    Manages output file generation. Output files include rows of data (usually differences)
    """
    rotationFile = ""
    
    def __init__(self, rotationFile):
        self.rotationFile = configs["outputDataFolder"] + "/" + rotationFile
        self.clear()
    
    def clear(self):
        with open(self.rotationFile + '.txt', 'w') as file:
            pass

    def add(self, content):
        with open(self.rotationFile + '.txt', 'a') as file:
            file.write(str(content) + " ")
            
    def newLine(self):
        with open(self.rotationFile + '.txt', 'rb+') as file:
            file.seek(0, 2)
            if file.tell() == 0:
                return
            file.seek(-1, 2)
            if file.read(1) == b' ':
                file.seek(-1, 2)
                file.truncate()
                file.write(b'\n')
    
    def close(self):
        with open(self.rotationFile + '.txt', 'rb+') as file:
            file.seek(0, 2)
            if file.tell() == 0:
                return
            file.seek(-1, 2)
            if file.read(1) == b' ' or file.read(1) == b'\n':
                file.seek(-1, 2)
                file.truncate()

def difference_sim_obs(simTimestamps, simValues, dataTimestamps, dataValues, method):
    """
    Calculates difference between sim and obs results using given method

    NOTE: timestamps must be converted to int format

    REQUIRES:
    - simTimestamps, simValues: arrays with simulation timestamps and values
    - dataTimestamps, dataValues: arrays with data timestamps and values
    - method: method to use (see METHODS)
    
    EFFECTS: returns value of difference between the two datasets
    
    -- METHODS --
    mse: mean squared error (default)
    mae: mean absolute error
    scc: spearman correlation coefficient
    curve_distance: curve distance
    """
    
    # removes all timestamps with no observation data (NaN)
    nanMask = ~np.isnan(dataValues)
    dataValues = np.array(dataValues)
    dataTimestamps = np.array(dataTimestamps)
    dataTimestamps = dataTimestamps[nanMask]
    dataValues = dataValues[nanMask]

    interpSimValues = interpolate(dataTimestamps, simTimestamps, simValues)

    if method == "mae":
        # mean absolute error
        n = len(dataTimestamps)
        squaredDiff = [np.abs(actual - predicted) for actual, predicted in zip(dataValues, interpSimValues)]
        mse = sum(squaredDiff) / n

        return mse
    elif method == "scc":
        # spearman correlation coefficient
        scc, pvalue = spearmanr(dataValues, interpSimValues)
        
        return scc
    elif method == "curve_distance":
        L1 = max(dataTimestamps) - min(dataTimestamps)
        
        # D 1, 2
        # Precompute the array of points for interpSimValues
        interp_points = np.array([(dataTimestamps[j], point2) for j, point2 in enumerate(interpSimValues)])
        
        total_distance_1 = 0.0
        
        # Vectorize the distance calculations
        for i, point1 in enumerate(dataValues):
            point1_array = np.array([dataTimestamps[i], point1])
            distances = np.linalg.norm(interp_points - point1_array, axis=1)
            min_distance = np.min(distances)
            total_distance_1 += min_distance
        
        total_distance_1 = total_distance_1 / L1
            
        # flip to get D 2, 1
        temp = interpSimValues
        interpSimValues = dataValues
        dataValues = temp
        
        interp_points = np.array([(dataTimestamps[j], point2) for j, point2 in enumerate(interpSimValues)])
        
        total_distance_2 = 0.0
        
        # Vectorize the distance calculations
        for i, point1 in enumerate(dataValues):
            point1_array = np.array([dataTimestamps[i], point1])
            distances = np.linalg.norm(interp_points - point1_array, axis=1)
            min_distance = np.min(distances)
            total_distance_2 += min_distance
        
        total_distance_2 = total_distance_2 / L1
        
        return (total_distance_1 + total_distance_2) / L1
    else:
        # mean squared error
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
    if configs["diffCalcMethod"] == "scc": # spearman cc has highest rank when closest to 1/-1
        arr = 1 - np.abs(arr)

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
    if configs["diffCalcMethod"] == "scc": # spearman cc should NOT be normalized
        return data
    
    minValue = min(data)
    maxValue = max(data)
    
    return [(x - minValue) / (maxValue - minValue) for x in data]

def calculate2DArrayAverage(arr):
    """
    REQUIRES:
    - arr: input 2d array
    Nested arrays MUST be of equal length!

    EFFECTS: Averages all nested arrays in arr to form a single array
    """
    numRows = len(arr)
    numCols = len(arr[0])
    
    if configs["diffCalcMethod"] == "scc": # normalizes spearman cc so best has lowest val and worst has highest
        arr =  1 - np.abs(arr)

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
    if configs["diffCalcMethod"] == "scc": # normalizes spearman cc so best has lowest val and worst has highest
        arr = [1 - abs(val) for val in arr]
        
    minVal = min(arr)
    minIndex = arr.index(minVal)
    return minIndex

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
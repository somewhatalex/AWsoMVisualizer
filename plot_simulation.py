from config_local import *
import os
import numpy as np
import math
import argparse
from plot_gen import *
from data_utils import *
from data_parser import *

simDirectory = configs["simDirectory"]
#NOTE: configs["plotSaveFolder"] must be accessed directly in this file so it can be overriden by cmd arguments
#This value is then used in different modules

#parses user command line input with flags
plotRotation = ""
if __name__ == "__main__":
    #add arguments to parse
    parser = argparse.ArgumentParser(description = "Plot simulation results given a rotation date.")
    parser.add_argument("-t", help = "Rotation date (ex. 20120516).")
    parser.add_argument("-sp", help = "Enter simulation path, default is " + simDirectory)
    parser.add_argument("-o", help = "Folder to output plots, default is " + configs["plotSaveFolder"])
    parser.add_argument("-showplot", action = "store_true", help = "Opens graph as new window when the script finishes")

    #parse resulting args
    args = parser.parse_args()
    plotRotation = args.t
    openPlotWindow = args.showplot

    #overrides default config value if sim directory is specified via cmd
    if args.sp is not None:
        simDirectory = args.sp

    #overrides default config value if output folder location is specified via cmd
    if args.o is not None:
        configs["plotSaveFolder"] = args.o

#validates user configs and input
if not os.path.isdir(simDirectory):
    raise FileNotFoundError(f"Directory \"{simDirectory}\" wasn't found.")

#simFolders is a list of all runs' folders
simFolders = [name for name in os.listdir(simDirectory) if os.path.isdir(os.path.join(simDirectory, name))]

# rotationData Structure:
# 20110201
# |-- run001_AWSoM 
#     |-- it
#     |-- timestamp
#     |-- earthCoords, etc.
# |-- run002_AwSom ...
#
# Example: rotationData["20110201"]["run001_AWSoM"]["timestamp"] will return a list of values
rotationData = dict()

#loop through and index all simulation folder contents
for run in simFolders:
    with open(f"./{simDirectory}/{run}/{configs['simParamLocation']}", "r") as file:
        fileContents = file.readlines()

        #param structure: model, map, PoyntingFluxPerBSi, realizations
        params = {}
        for line in fileContents:
            key, value = line.strip().split("=")
            params[key.strip()] = value.strip()

        #gets rotation name from params list
        rotation = params["map"].split("/")[1].split("_")[1]

        simResults = parseSimRunResults(f"./{simDirectory}/{run}/{configs['simResultsLocation']}")

        #add folder and results to its corresponding rotation name key in rotationData
        if rotation in rotationData:
            #if the rotation already exists, do not create another rotation dict key
            #instead, add the run name to the existing key
            rotationData[rotation][run] = simResults
        else:
            #otherwise, create a new rotation key and make simResults the first value
            rotationData[rotation] = {run: simResults}
        
print(f"Indexed {len(rotationData)} rotations:")
print(list(rotationData.keys()))

#plot all rotations and terminate program if no rotation specified
if plotRotation is None:
    print(f"\nNo rotation specified, plotting all {len(rotationData)}")

    #loop through each rotation stored in rotationData and plot it
    #the attributes to plot are specified in config_local
    for rotationName in rotationData.keys():
        plotResults(rotationName, rotationData)

    raise SystemExit

#check if rotation exists
if plotRotation in rotationData:
    #if it does, plot the data for it
    print(f"\nCreating plot for rotation {plotRotation}...")
    plotResults(plotRotation, rotationData, openPlotWindow)
else:
    print(f"\nError: no sim data for rotation {plotRotation} found. Typo?")
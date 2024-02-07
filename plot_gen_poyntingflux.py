from config_local import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from data_utils import *
import os

def plotPoyntingFluxGraph(avgMseValues, allMseData, poyntingFluxValues, rotation, saveFolder, showPlots = False):
    """
    REQUIRES:
    - avgMseValues, poyntingFluxValues: two arrays of equal length
    - allMseData: 2d array containing individual vars' MSE values to plot, each array inside must have equal length
    
    - rotation: name of rotation
    - saveFolder: folder to save in, saves to configs["plotSaveFolder"]/analysis_results/[rotation]_result.png when
        called in plot_gen
    - showPlots (default = false): whether or not to open plot in a new window

    EFFECTS: plots (avgMseValues, poyntingFluxValues) on (x, y) for all items in arrays

    Graphs show correlation between poynting flux values and their simulation accuracy
    """
    saveFolder = f"{saveFolder}/analysis_results"
    if not os.path.exists(saveFolder):
        os.makedirs(saveFolder)
        print(f"Created output folder at {saveFolder}")
        
    plt.figure(figsize = configs["plotDimensions"])
    
    #plots each individual variable's data points
    for i, data in enumerate(allMseData):
        ax = plt.subplot(len(allMseData) + 1, 1, i + 1)
        ax.plot(poyntingFluxValues, data, color = configs["msePlotColor"])
        
        #plots title on first graph
        if i == 0:
            plt.title(f"Correlation between Poynting Flux and Simulation Accuracy For Rotation {rotation}")
        
        minIndex = np.argmin(data)
        
        plt.text(0.5, 0.95, f"Best: {poyntingFluxValues[minIndex]} (MSE={round(np.min(data), 6)})", transform=plt.gca().transAxes, fontsize=10, ha='center', va='top')
        
        plotColors = [configs["mseBestPointColor"] if i == minIndex else configs["msePlotColor"] for i in range(len(avgMseValues))]
        scatterPlot = ax.scatter(poyntingFluxValues, data, color = plotColors)
        scatterPlot.set_zorder(10)
        
        plt.grid(True, linestyle = "--", alpha = 0.5)
        ax.set_ylabel(f"MSE Value ({configs['importantParams'][i]})")

        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    
    #plots overall average MSE values in last subplot
    plt.subplot(len(allMseData) + 1, 1, len(allMseData) + 1)
    
    #sets min point to a different color
    minIndex = np.argmin(avgMseValues)
    plotColors = [configs["mseBestPointColor"] if i == minIndex else configs["msePlotColor"] for i in range(len(avgMseValues))]

    plt.plot(poyntingFluxValues, avgMseValues, color = configs["msePlotColor"])
    scatterPlot = plt.scatter(poyntingFluxValues, avgMseValues, color = plotColors)
    scatterPlot.set_zorder(10)
    
    plt.text(0.5, 0.95, f"Best: {poyntingFluxValues[minIndex]} (MSE={round(np.min(avgMseValues), 6)})", transform=plt.gca().transAxes, fontsize=10, ha='center', va='top')

    plt.xlabel("Poynting Flux Values")
    plt.ylabel("Avg. MSE Value")

    plt.grid(True, linestyle = "--", alpha = 0.5)

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    
    if showPlots:
        plt.show()
        
    plt.savefig(f"{saveFolder}/{rotation}_result.png", dpi = 300)
    plt.close()
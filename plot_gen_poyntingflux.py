from config_local import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from data_utils import *
import os

def plotPoyntingFluxGraph(avgDiffValues, allDiffData, poyntingFluxValues, rotation, saveFolder, showPlots = False):
    """
    REQUIRES:
    - avgDiffValues, poyntingFluxValues: two arrays of equal length
    - allDiffData: 2d array containing individual vars' difference values to plot, each array inside must have equal length
    
    - rotation: name of rotation
    - saveFolder: folder to save in, saves to configs["plotSaveFolder"]/analysis_results/[rotation]_result.png when
        called in plot_gen
    - showPlots (default = false): whether or not to open plot in a new window

    EFFECTS: plots (avgDiffValues, poyntingFluxValues) on (x, y) for all items in arrays

    Graphs show correlation between poynting flux values and their simulation accuracy
    """
    saveFolder = f"{saveFolder}/analysis_results"
    if not os.path.exists(saveFolder):
        os.makedirs(saveFolder)
        print(f"Created output folder at {saveFolder}")
        
    plt.figure(figsize = configs["plotDimensions"])
    
    #plots each individual variable's data points
    for i, data in enumerate(allDiffData):
        ax = plt.subplot(len(allDiffData) + 1, 1, i + 1)
        ax.plot(poyntingFluxValues, data, color = configs["diffPlotColor"])
        
        #plots title on first graph
        if i == 0:
            plt.title(f"Correlation between Poynting Flux and Simulation Accuracy For Rotation {rotation}")
        
        minIndex = np.argmin(data)
        
        plt.text(0.5, 0.95, f"Best: {poyntingFluxValues[minIndex]} (Diff={round(np.min(data), 6)})", transform=plt.gca().transAxes, fontsize=10, ha='center', va='top')
        
        plotColors = [configs["diffBestPointColor"] if i == minIndex else configs["diffPlotColor"] for i in range(len(avgDiffValues))]
        scatterPlot = ax.scatter(poyntingFluxValues, data, color = plotColors)
        scatterPlot.set_zorder(10)
        
        plt.grid(True, linestyle = "--", alpha = 0.5)
        ax.set_ylabel(f"Diff Value ({configs['importantParams'][i]})")

        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=configs["diffValueBins"]))
    
    #plots overall average diff values in last subplot
    plt.subplot(len(allDiffData) + 1, 1, len(allDiffData) + 1)
    
    #sets min point to a different color
    minIndex = np.argmin(avgDiffValues)
    plotColors = [configs["diffBestPointColor"] if i == minIndex else configs["diffPlotColor"] for i in range(len(avgDiffValues))]

    plt.plot(poyntingFluxValues, avgDiffValues, color = configs["diffPlotColor"])
    scatterPlot = plt.scatter(poyntingFluxValues, avgDiffValues, color = plotColors)
    scatterPlot.set_zorder(10)
    
    plt.text(0.5, 0.95, f"Best: {poyntingFluxValues[minIndex]} (Diff={round(np.min(avgDiffValues), 6)})", transform=plt.gca().transAxes, fontsize=10, ha='center', va='top')

    plt.xlabel("Poynting Flux Values")
    plt.ylabel("Avg. Diff Value")

    plt.grid(True, linestyle = "--", alpha = 0.5)

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=configs["diffValueBins"]))
    
    if showPlots:
        plt.show()
        
    plt.savefig(f"{saveFolder}/{rotation}_result.png", dpi = 300)
    plt.close()
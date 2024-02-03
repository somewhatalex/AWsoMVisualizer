from config_local import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from data_utils import *
import os

def plotPoyntingFluxGraph(mseValues, poyntingFluxValues, rotation, saveFolder, showPlots = False):
    """
    REQUIRES:
    - mseValues, poyntingFluxValues: two arrays of equal length
    - rotation: name of rotation
    - saveFolder: folder to save in, saves to configs["plotSaveFolder"]/analysis_results/[rotation]_result.png when
        called in plot_gen
    - showPlots (default = false): whether or not to open plot in a new window

    EFFECTS: plots (mseValues, poyntingFluxValues) on (x, y) for all items in arrays

    Graphs show correlation between poynting flux values and their simulation accuracy
    """
    saveFolder = f"{saveFolder}/analysis_results"
    if not os.path.exists(saveFolder):
        os.makedirs(saveFolder)
        print(f"Created output folder at {saveFolder}")
        
    plt.figure(figsize = configs["plotDimensions"])
    
    #sets min point to a different color
    minIndex = np.argmin(mseValues)
    plotColors = [configs["mseBestPointColor"] if i == minIndex else configs["msePlotColor"] for i in range(len(mseValues))]

    plt.plot(poyntingFluxValues, mseValues, color = configs["msePlotColor"])
    scatterPlot = plt.scatter(poyntingFluxValues, mseValues, color = plotColors)
    scatterPlot.set_zorder(10)
    

    plt.xlabel("Poynting Flux Values")
    plt.ylabel("Parameter Average Mean Squared Error (MSE)")
    plt.title(f"Correlation between Poynting Flux and Simulation Accuracy For Rotation {rotation}")

    plt.grid(True, linestyle = "--", alpha = 0.5)

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    
    if showPlots:
        plt.show()
        
    plt.savefig(f"{saveFolder}/{rotation}_result.png", dpi = 300)
    plt.close()
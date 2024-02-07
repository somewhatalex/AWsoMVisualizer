from config_local import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
from scrape_data import scrapeData
from datetime import datetime, timedelta
from data_utils import *
from plot_gen_poyntingflux import *

def plotResults(plotRotation, rotationData, openPlotWindow = False):
    """
    REQUIRES:
    - plotRotation: string with the rotation name to plot (ex. 20140902)
    - rotationData: dict containing data for ALL rotations, format specified in main file
    - openPlotwindow (default = false): whether or not to open plot in a new window

    EFFECTS: plots variables in rotationData (specified in config_local),
    saves plots to plotSaveFolder (also specified in config_local)

    Plots one rotation at a time.

    NOTE: Plot params and appearance can be configured in config_local
    """
    plotSaveDirectory = configs["plotSaveFolder"]
    runResults = rotationData[plotRotation]
    dataToPlot = configs["dataToPlot"]

    # sets up output folder (specified in config_local)
    if not os.path.exists(plotSaveDirectory):
        os.makedirs(plotSaveDirectory)
        print(f"Created output folder at {plotSaveDirectory}")

    # loops through every sim result, then plots specified values into each subplot before moving to the next
    # plt.figure resets the plot so each function call works on a clean slate
    plt.figure(figsize = configs['plotDimensions'])

    # the indices for each array are the same for each plot
    # ie. simLines[1] has the run name at simRunNames[1]
    simLines = [[] for i in range(len(dataToPlot))] # contains data for each line in the plot
    mseValues = [[] for i in range(len(dataToPlot))]
    simRunNames = []
    poyntingFluxes = []

    #TODO: replace above arrays with structured dict
    # plotData Structure:
    # Var1
    # |-- simLines
    # |-- mseValues
    # |-- simRunNames
    # |-- poyntingFluxes
    # Var2
    # |-- simLines ...
    #
    # All subkeys are arrays with indices that correspond to each other
    plotData = dict()
    
    # loop through all sim runs in the rotation
    for runIter, run in enumerate(runResults):
        # sets start and end times for data scraping
        startTime = min(runResults[run]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        endTime = max(runResults[run]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

        simRunNames.append(run)
        poyntingFluxes.append(runResults[run]["poyntingFlux"])

        # shifts the scraping timeframe back by 4.5 hours to account for delay in start/end of data collection vs sim timeframe
        startTimeDT = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S') - timedelta(hours = 4.5)
        alteredStartTime = startTimeDT.strftime('%Y-%m-%d %H:%M:%S')
        endTimeDT = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S') - timedelta(hours = 4.5)
        alteredEndTime = endTimeDT.strftime('%Y-%m-%d %H:%M:%S')

        # NOTE: This will run for EVERY iteration, thus making identical requests
        # HOWEVER, scrapeData will cache requests so repeat requests are returned immediately w/o scraping
        scrapedData = scrapeData(configs["varsToScrape"], alteredStartTime, alteredEndTime)

        #in each sim run, loop through each data value specified in config_local
        for i, data in enumerate(dataToPlot):
            #subplot config
            plt.subplot(len(dataToPlot), 1, i + 1)
            plt.grid(axis = "x", linestyle = "--")
            plt.ylabel(configs['yLabels'][i])
            plt.gca().xaxis.set_major_locator(MaxNLocator(nbins = configs['plotSimDateBins'])) # sets number of bins
            plt.margins(0) # removes left and right margins on graph
            plt.xlim(min(runResults[run]['timestamp']), max(runResults[run]['timestamp'])) # bounds x axis to start and end times to avoid overflow

            # if it's not the last plot...
            if i + 1 != len(dataToPlot):
                plt.gca().set_xticklabels([]) #clears x axis tick labels
            else:
                # is the last plot, do not clear x axis tick labels and add start time label
                plt.xlabel(f"Start time: {min(runResults[run]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

            # use log scaling when applicable
            if configs['isLogGraph'][i] == True:
                plt.yscale("log")

            # plot data in corresponding subplot. If data already exists, it'll add on to the graph
            # and create a plot with multiple lines
            simTimestamps = runResults[run]["timestamp"]
            simValues = runResults[run][data]
            currentSimLine = plt.plot(np.array(simTimestamps), np.array(simValues), c = configs['plotSimLineColor'], linewidth = configs['plotSimLineWidth'])
            simLines[i].append(currentSimLine)

            #dataVar contains the current scraped variable being plotted
            dataVar = configs["varsToScrape"][i]

            #overlays scraped data onto current subplot
            dataTimestamps = scrapedData[dataVar]["timestamps"]
            dataValues = scrapedData[dataVar]["data"]

            #only plot the scraped data on the LAST iteration as further plotting will only overlap the previous plot
            #last iteration is used as it'll stack the plot on top of all sim lines
            if runIter == len(runResults) - 1:
                plt.plot(np.array(dataTimestamps), np.array(dataValues), c = configs["plotDataLineColor"], linewidth = configs["plotDataLineWidth"])

            #--MSE CALCULATION--
            #normalize timestamps into int format (for calculating mean squared error)
            simTimestamps = [int(dt.timestamp()) for dt in simTimestamps]
            dataTimestamps = dataTimestamps.astype(str)
            dataTimestamps = [ts.split(".")[0] for ts in dataTimestamps] #removes unnecessary subsecond precision
            dataTimestamps = [int(datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S').timestamp()) for ts in dataTimestamps]
            
            #calculate mean squared error
            lineMseValue = mse(simTimestamps, simValues, dataTimestamps, dataValues)
            mseValues[i].append(lineMseValue)

            #save values to plotData dict
            #TODO: reformat old code to accept the new data format and delete legacy arrays
            #NOTE: until then, this code has no purpose
            if data not in plotData:
                plotData[data] = {
                    "simLines": [],
                    "mseValues": [],
                    "simRunNames": [],
                    "poyntingFluxes": [],
                }
            
            currentPlotData = plotData[data]
            currentPlotData["simLines"].append(currentSimLine)
            currentPlotData["mseValues"].append(lineMseValue)
            currentPlotData["simRunNames"].append(run)
            currentPlotData["poyntingFluxes"].append(runResults[run]["poyntingFlux"])
    
    # calculates line opacities and line of best fit
    for i, valueSet in enumerate(mseValues):
        opacityValues = findPlotOpacities(valueSet)

        # normalizes mse values for the specific plot
        mseValues[i] = normalizeData(valueSet)

        for j, line in enumerate(simLines[i]):
            opacity = opacityValues[j]

            if(opacity == 1):
                line[0].set_color(configs["bestPlotFitLineColor"])
                line[0].set_linewidth(configs["bestPlotFitLineWidth"])
                line[0].set_zorder(len(simLines[i]) + 1) # move best fit line to front

            line[0].set_alpha(opacityValues[j])
    
    # only keep important param mse data in mseValues (other params will be ignore in calculation)
    mseValues = filterDatasetByVarName(mseValues, configs["dataToPlot"], configs["importantParams"])[1]

    # finds and plots overall best line
    mseAverages = calculate2DArrayAverage(mseValues)
    indexOfBestLine = indexOfMinValue(mseAverages)

    # sets maximum y-axis data cutoff
    axes = plt.gcf().get_axes()
    for i, ax in enumerate(axes):
        originalYLim = ax.get_ylim()
        maxYAxis = configs["paramMaxValues"][i]
        if maxYAxis != None:
            if originalYLim[1] > maxYAxis:
                ax.set_ylim(originalYLim[0], maxYAxis)
    
    for i in range(len(configs["dataToPlot"])):
        bestOverallLine = simLines[i][indexOfBestLine][0]

        bestOverallLine.set_color(configs["bestOverallFitLineColor"])
        bestOverallLine.set_linewidth(configs["bestOverallFitLineWidth"])
        bestOverallLine.set_zorder(len(simLines[i]) + 2) # move best fit line to front

        bestOverallLine.set_alpha(1)
    
    bestRunName = simRunNames[indexOfBestLine]
    bestPoyntingFlux = runResults[bestRunName]["poyntingFlux"]

    print(f"[Rotation = {plotRotation}] Plotted {len(dataToPlot)} quantities from {len(runResults)} simulation results.")
    print(f"Best simulation run: {bestRunName} (poyntingFlux = {bestPoyntingFlux})")

    # launches plot as new window if openPlotWindow is true
    # value passed by -showplot flag via cmd
    if openPlotWindow:
        plt.show()

    plt.savefig(f"{plotSaveDirectory}/{plotRotation}.png", dpi = 300)
    plt.close()
    
    # Plot poynting flux value vs mse
    plotPoyntingFluxGraph(mseAverages, mseValues, plotData[next(iter(plotData))]["poyntingFluxes"], plotRotation, plotSaveDirectory, openPlotWindow)
    
    print("----------")
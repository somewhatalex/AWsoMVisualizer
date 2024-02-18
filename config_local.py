configs = {
    #sim file access configs
    "simDirectory": "./simulations",
    "simParamLocation": "key_params.txt", #where sim parameter data is stored
    "simResultsLocation": "./run01/IH/trj_earth_n00005000.sat", #in folder run###_AWSoM

    #plot appearance
    "plotSimLineColor": "#0362fc", #line color of sim run results in the final plots
    "plotSimLineWidth": "0.7",
    "plotSimDateBins": 7, #aka number of tick marks on the x axis plus 1
    "simLineOpacityRange": [0.3, 1], #the min and max opacities of the best and worst fitting sim plot lines
    "plotDimensions": [9, 7], #[width, height]

    "plotDataLineColor": "black", # "Data" refers to the scraped CDAS data plots
    "plotDataLineWidth": "1",

    "bestPlotFitLineColor": "#f2a600", # line of best fit for the individual plot only
    "bestPlotFitLineWidth": "1.4",
    "bestOverallFitLineColor": "red", # line of best fit overall the entire rotation
    "bestOverallFitLineWidth": "2",
    
    #plot properties
    "dataToPlot": ["U", "n", "ti", "B"],
    "importantParams": ["U", "n"], # only include these params for best run calculation
    "yLabels": ["U (km/s)", "Np (cm^-3)", "Temperature (K)", "B (nT)"],
    "paramMaxValues": [1000, 100, 10**7, 25], # the graph gets cut off above these values
    "isLogGraph": [False, False, True, False],
    "plotSaveFolder": "./output_plots", # where plot images should be saved

    #scraping configs
    "varsToScrape": ["V", "N", "T", "ABS_B"], # NOTE: vars must match corresponding variables in "dataToPlot"
    
    #poynting flux vs difference from actual plot properties
    "diffPlotColor": "blue",
    "diffBestPointColor": "red",
    "diffValueBins": 7, # number of tick marks on y axis of poynting flux plot
    "diffCalcMethod": "mse"
}

#constants
protonMass = 1.67*1e-24
k = 1.3807e-23
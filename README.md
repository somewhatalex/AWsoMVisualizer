# AWsoMVisualizer
**An AWsoM Solar Wind Simulation Result Vizualization Tool**

![Example plot](./examples/20120516.png)

## About
This utility can plot and visualize simulation data from the AWsoM Solar Wind Model. It is able to create plots for several variables on hundreds of simulation runs at once and compare them to real data from [NASA's CDAWeb](https://cdaweb.gsfc.nasa.gov/).

Additionally, analysis plots that show the best Poynting Flux parameter value for different Carrington rotation simulation runs will also be generated. The best run results for each rotation are calculated by the following steps:
1. The simulation data is interpolated onto the actual data.
2. Mean squared error (MSE) for each run is calculated between the simulation and actual data.
3. The important parameters sepcified in config_local.py are used to find overall MSE values for each run across variables.
4. The simulation runs are ranked by MSE values and the lowest MSE value run is determined.

## Setup
To setup, please install the following Python libraries. You should also have [Python 3.12](https://www.python.org/downloads/) or higher installed.
```
pip install -u xarray cdflib cdasws matplotlib numpy
```
Customizable user preferences can be found in [config_local.py](config_local.py). "config_local.py" contains a Python dict of editable values. The presets can be edited before running the program.

## Usage
You will need a folder containing properly-formatted simulation data, an example of which can be found [here](./examples/run001_AWSoM/).

To run the program:
```
python plot_simulation.py
```

### Program Flags
| Option     | Description                                       |
|------------|---------------------------------------------------|
| -h, --help | Display this help message                   |
| -t       | Specify rotation date to plot (ex. 20120516)                     |
| -sp     | Set  simulation path, default is ./simulations  |
| -o       | Set folder to output plots, default is ./output_plots|
| -showplot  | Opens graph as a new window when script finishes  |
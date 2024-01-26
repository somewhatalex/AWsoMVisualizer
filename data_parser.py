from datetime import datetime
import re
from config_local import *
from data_utils import *

def parseSimRunResults(file):
    """
    REQUIRES:
    - file: string where sim run data is stored

    EFFECTS: returns run results from rotation as a sorted dict
    - Key = file header variables, value = array of all values for that variable
    """

    runResults = {
        "it": [],
        "timestamp": [],
        "earthCoords": [],
        "rho": [],
        "velocityVector": [],
        "U": [],
        "magneticVector": [],
        "B": [],
        "p": [],
        "pe": [],
        "ehot": [],
        "I01": [],
        "I02": [],
        "n": [],
        "ti": []
    }

    #read the input data file line by line
    with open(file, "r") as file:
        fileContents = file.readlines()

        for i, line in enumerate(fileContents):
            if i >= 2: #ignore first 2 lines which are headers
                row = line.strip()
                row = re.sub(r'\s+', ' ', row)
                row = row.split(" ")

                #it [year mo dy hr mn sc msc] [X Y Z] rho [ux uy uz] [bx by bz] p pe ehot I01 I02
                runResults["it"].append(row[0])
                timestampStr = " ".join(row[1:8])
                timestamp = datetime.strptime(timestampStr, '%Y %m %d %H %M %S %f')
                runResults["timestamp"].append(timestamp)
                runResults["earthCoords"].append(row[8:11])
                runResults["rho"].append(row[11])
                runResults["velocityVector"].append(row[12:15])
                runResults["magneticVector"].append(row[15:18])
                runResults["p"].append(row[18])
                runResults["pe"].append(row[19])
                runResults["ehot"].append(row[20])
                runResults["I01"].append(row[21])
                runResults["I02"].append(row[22])

                #quantity conversions
                rho = float(row[11])
                p = float(row[18])
                runResults["U"].append(magnitude(row[12:15])) #convert velocityVector to magnitudes
                runResults["B"].append(magnitude(multiplyArr(row[15:18], 1e5))) #convert magneticVector to magnitudes, then from microtesla (assumed) to nT
                runResults["n"].append(rho / protonMass) #rho/protonMass
                runResults["ti"].append(p * protonMass / rho / k * 1.e-7) #rho/protonMass

    return runResults
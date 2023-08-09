# gets test datasets + thresholds
def getDatasets(data, datasets, sets, testOptions, order):
    colors = ['#0099CC', '#6600CC', '#006600', '#FF9933', '#660033']
    for i in range(len(sets)):
        keySet = {}
        keySet["type"] = "line"
        keySet["label"] = testOptions[sets[i]]["title"]
        keySet["data"] = data[sets[i]].tolist()
        keySet["yAxisID"] = testOptions[sets[i]]["axisID"]
        keySet["borderColor"] = colors[i]
        keySet["pointBackgroundColor"] = colors[i]
        keySet["pointHoverRadius"] = 6
        keySet["pointHoverBorderWidth"] = 4
        keySet["pointHoverBackgroundColor"] = "transparent"
        keySet["order"] = order
        order += 1
        
        datasets.append(keySet)
        
        if testOptions[sets[i]]["thresholdFill"] != "none":
            thresholdList = getThreshold(data, sets[i], testOptions[sets[i]], order, colors[i])
            for t in thresholdList:
                datasets.append(t)
                
    return datasets

# gets test warning threshold
def getThreshold(data, setName, testOptions, order, color):
    thresholdList = []
    
    threshold = {}
    threshold["type"] = "line"
    threshold["label"] = testOptions["title"] + " Threshold"
    threshold["yAxisID"] = testOptions["axisID"]
    threshold["borderColor"] = "transparent"
    threshold["backgroundColor"] = color + "50"
    threshold["pointBackgroundColor"] = [color + "50"] * len(data[setName].tolist())
    threshold["pointRadius"] = 0
    threshold["pointHoverRadius"] = 0
    threshold["pointHoverBorderWidth"] = 0
    threshold["hidden"] = True
    
    if testOptions["thresholdType"] == "custom":
        threshold["data"] = testOptions["thresholdData"]
    elif testOptions["thresholdType"] == "exists":
        threshold["data"] = testOptions["thresholdData"]
    elif "2" in testOptions["title"]:
        threshold["data"] = testOptions["thresholdData"][1]
    elif testOptions["thresholdType"] == "abs":
        threshold["data"] = testOptions["thresholdData"][0]
    else:
        threshold["data"] = testOptions["thresholdData"]

    if testOptions["thresholdFill"] == "above":
        threshold["fill"] = "end"
    elif testOptions["thresholdFill"] == "below" or "2" in testOptions["title"]:
        threshold["fill"] = "start"
    elif testOptions["thresholdFill"] == "between":
        threshold["fill"] = {"value": testOptions["thresholdData"][1][0]}
    elif testOptions["thresholdFill"] == "split":
        threshold["fill"] = "end"
        testOptions["title"] = testOptions["title"] + "2"
        thresholdList.append(getThreshold(data, setName, testOptions, order + 5, color)[0])
    elif testOptions["thresholdFill"] == "all":
        threshold["fill"] = "end"
        testOptions["title"] = testOptions["title"] + "2"
        thresholdList.append(getThreshold(data, setName, testOptions, order + 5, color)[0])
        
    threshold["order"] = order + 10
    thresholdList.append(threshold)
    return thresholdList

# gets test error/warning/binary datasets
def getErrorSets(output, data, datasets, errorSet, warningSet, sets, testOptions):
    binDatasets = []
    
    data.loc[:, "error"] = data["date"].apply(lambda x: "error" if x in set(errorSet["date"]) else "passed")
    data.loc[:, "warning"] = data["date"].apply(lambda x: "warning" if x in set(warningSet["date"]) else "none")
    
    binError = {}
    binError["type"] = "line"
    binError["borderWidth"] = 10
    binError["label"] = "Pass/Fail"
    binError["data"] = ["Status"] * len(data[sets[0]].tolist())
    binError["yAxisID"] = "binY"
    binError["order"] = 10
    binError["pointBackgroundColor"] = []
    binError["pointRadius"] = 0
    binError["pointHoverRadius"] = 0
    
    order = 0
    dates = data.date.astype(str).tolist()
    for s in sets:
        error, warning = setErrorOptions(testOptions[s], order)
        error, warning, binError = getErrorPoints(data, dates, s, error, warning, binError)
        
        datasets.append(warning)
        datasets.append(error)
        
        order += 2
    
    if errorSet.shape[0] == 0 and warningSet.shape[0] == 0:
        binError["borderColor"] = "#00A61E"
    elif errorSet.shape[0] == data.shape[0]:
        binError["borderColor"] = "#FF0000"
    elif warningSet.shape[0] == data.shape[0]:
        binError["borderColor"] = "#FFC107"
    binDatasets.append(binError)
    output["binDatasets"] = binDatasets

    return (datasets, order, output)

# sets the graph options for error/warning
def setErrorOptions(testOptions, order):
    error = {}
    error["type"] = "line"
    error["label"] = "Error Point"
    error["fill"] = False
    error["showLine"] = False
    error["data"] = []
    error["yAxisID"] = testOptions["axisID"]
    error["backgroundColor"] = "#FF0000"
    error["order"] = order
    error["pointBackgroundColor"] = []
    error["pointRadius"] = []
    
    warning = {}
    warning["type"] = "line"
    warning["label"] = "Warning Point"
    warning["fill"] = False
    warning["showLine"] = False
    warning["data"] = []
    warning["yAxisID"] = testOptions["axisID"]
    warning["backgroundColor"] = "#FFC107"
    warning["order"] = order + 1
    warning["pointBackgroundColor"] = []
    warning["pointRadius"] = []
    
    return error, warning

# sets the point values and colors for error/warning/binary
def getErrorPoints(data, dates, setName, error, warning, binError):
    # color-code warning points
    for i in range(data.shape[0]):
        point = {"x": dates[i], "y": data[setName].iloc[i]}
        error["data"].append(point)
        warning["data"].append(point)
            
        if data["error"].iloc[i] == "error":
            error["pointBackgroundColor"].append('#FF0000')
            error["pointRadius"].append(3)
            warning["pointBackgroundColor"].append("transparent")
            warning["pointRadius"].append(0)
            if len(binError) != data.shape[0]:
                binError["pointBackgroundColor"].append("#FF0000")
        elif data["warning"].iloc[i] == "warning":
            warning["pointBackgroundColor"].append("#FFC107")
            warning["pointRadius"].append(3)
            error["pointBackgroundColor"].append("transparent")
            error["pointRadius"].append(0)
            if len(binError) != data.shape[0]:
                binError["pointBackgroundColor"].append("#FFC107")
        else:
            warning["pointBackgroundColor"].append("transparent")
            warning["pointRadius"].append(0)
            error["pointBackgroundColor"].append("transparent")
            error["pointRadius"].append(0)
            if len(binError) != data.shape[0]:
                binError["pointBackgroundColor"].append("#00A61E")
                
    return error, warning, binError

# gets axis settings
def getAxes(output, axisTitles, axisPositions):
    for p in axisPositions:
        axis = {}
        axis["type"] = "linear"
        axis["position"] = p
        axis["display"] = "auto"
        axis["grace"] = "5%"
        title = {}
        title["text"] = axisTitles[p]
        title["display"] = True
        axis["title"] = title
        output[p] = axis
        
    return output
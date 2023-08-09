import json
import pandas as pd
import createTest
import executeTest

# formats test data
def cleanRawData(rawData, interval):
    rawData = json.loads(rawData)
    cleanData = []
    for i in range(len(rawData)):

        if(rawData[i]["receivedData"]["data"] != None):
            row = {}
            
            # date
            date = rawData[i]["receivedDate"]
            date = date.replace('T', ' ')
            date = date.replace('Z', '')
            row["date"] = date
    
            # supply/outlet
            supply = rawData[i]["receivedData"]["data"]["supply"]
            supply = int(supply) / 10
            row["supply"] = supply
    
            # inlet
            inlet = rawData[i]["receivedData"]["data"]["return"]
            inlet = int(inlet) / 10
            row["inlet"] = inlet
    
            # stack/exhaust
            stack = rawData[i]["receivedData"]["data"]["stack"]
            stack = int(stack) / 10
            row["stack"] = stack
    
            # header
            header = rawData[i]["receivedData"]["data"]["header"]
            header = int(header) / 10
            row["header"] = header
    
            # hx -- heat exchanger
            hx = rawData[i]["receivedData"]["data"]["hx"]
            hx = int(hx) / 10
            row["hx"] = hx
    
            # oda -- outdoor air temperature
            oda = rawData[i]["receivedData"]["data"]["oda"]
            oda = int(oda) / 10
            row["oda"] = oda
    
            # flame
            flame = rawData[i]["receivedData"]["data"]["flame"]
            flame = int(flame) / 100
            row["flame"] = flame
    
            # fan
            fan = rawData[i]["receivedData"]["data"]["fan"]
            fan = int(fan) / 3
            row["fan"] = fan
    
            # firerate
            firerate = rawData[i]["receivedData"]["data"]["firerate"]
            firerate = int(firerate) / 2
            row["firerate"] = firerate
    
            # chsetpoint -- central heating?
            chsetpoint = rawData[i]["receivedData"]["data"]["chsetpoint"]
            chsetpoint = int(chsetpoint) / 10
            row["chsetpoint"] = chsetpoint
            
            # dhw -- domestic hot water
            dhw = rawData[i]["receivedData"]["data"]["dhw"]
            dhw = int(dhw) / 10
            row["dhw"] = dhw
            
            # dhwsetpoint
            dhwsetpoint = rawData[i]["receivedData"]["data"]["dhwsetpoint"]
            dhwsetpoint = int(dhwsetpoint) / 10
            row["dhwsetpoint"] = dhwsetpoint
            
            # dhwtanksetpoint
            dhwtanksetpoint = rawData[i]["receivedData"]["data"]["dhwtanksetpoint"]
            dhwtanksetpoint = int(dhwtanksetpoint) / 10
            row["dhwtanksetpoint"] = dhwtanksetpoint
    
            cleanData.append(row)

    # create pandas dataframe and new columns
    cleanData = pd.DataFrame(cleanData)
    cleanData['date'] = pd.to_datetime(cleanData.date)
    cleanData.sort_values(by = 'date', ascending = True, inplace = True)
    cleanData["difference"] = cleanData['supply'].sub(cleanData['inlet'], axis = 0)
    cleanData['hx_diff'] = cleanData[["hx"]] - cleanData[["hx"]].shift(1)
    cleanData['stack_diff'] = cleanData[["stack"]] - cleanData[["stack"]].shift(1)
    cleanData['fan_diff'] = cleanData[["fan"]] - cleanData[["fan"]].shift(1)
    cleanData['flame_diff'] = cleanData[["flame"]] - cleanData[["flame"]].shift(1)
    cleanData['firerate_diff'] = cleanData[["firerate"]] - cleanData[["firerate"]].shift(1)
    cleanData['date_diff'] = cleanData[["date"]] - cleanData[["date"]].shift(1)

    return cleanData

# gets all test options needed to execute test
def getTest(data, dailyWeather, hourlyWeather, test):
    if "difference" in test["type"]:
        data = data.iloc[1:]        # skip first row because NAN (no difference found for first value)
    
    if "daily" in test["type"] or "all" in test["type"]:
        data = createTest.addWeatherData(data, dailyWeather)
    if "hourly" in test["type"] or "all" in test["type"]:
        data = createTest.addWeatherData(data, hourlyWeather)
    
    errorSet = createTest.getConditionSet(data, test["error"])
    if "duration" in test["type"]:
        if test["errorDuration"]["compare"] == ">":
            errorSet = createTest.checkDuration(errorSet, data, test["errorDuration"]["value"], createTest.overLimit)
        else:
            errorSet = createTest.checkDuration(errorSet, data, test["errorDuration"]["value"], createTest.underLimit)
         
    warningSet = createTest.getConditionSet(data, test["warning"])
    if "duration" in test["type"]:
        if test["warningDuration"]["compare"] == ">":
            warningSet = createTest.checkDuration(warningSet, data, test["warningDuration"]["value"], createTest.overLimit)
        else:
            warningSet = createTest.checkDuration(warningSet, data, test["warningDuration"]["value"], createTest.underLimit)
    
    title = test["title"].capitalize()
    sets = test["sets"]
    testOptions = {}
    for s in sets:
        testOptions[s] = {}
        testOptions[s]["title"] = test["options"][s]["title"]
        testOptions[s]["axisID"] = test["options"][s]["axisID"]
        testOptions[s]["thresholdLabel"] = test["options"][s]["thresholdLabel"]
        testOptions[s]["thresholdType"] = test["options"][s]["thresholdType"]
        testOptions[s]["thresholdFill"] = test["options"][s]["thresholdFill"]
        testOptions[s]["thresholdData"] = createTest.getThresholdData(data, test, s)
        
    axisTitles = test["axisTitles"]
    errorMsg = test["causes"].capitalize()
    
    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

# gets test datasets to execute (error + warning + thresholds + data points)
def runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg):
    warningSet = pd.merge(warningSet, errorSet, indicator = True, how = "outer").query('_merge == "left_only"').drop('_merge', axis = 1)        # remove error points
    output = {}
    output["title"] = title
    output["error_ct"] = errorSet.shape[0]
    output["warning_ct"] = warningSet.shape[0]
    output["total_ct"] = data.shape[0]
    output["labels"] = data.date.astype(str).tolist()
    datasets = []
    
    if (round(((errorSet.shape[0] / data.shape[0]) * 100), 2) == 0):
        output["status"] = "green"
    elif (round(((errorSet.shape[0] / data.shape[0]) * 100), 2) > 25):
        output["status"] = "red"
    elif (round(((errorSet.shape[0] / data.shape[0]) * 100), 2) > 0):
        output["status"] = "yellow"
    else:
        output["status"] = "unknown"
        
    thresholdLabels = {}
    thresholdTypes = {}
    thresholdFills = {}
    for s in sets:
        thresholdLabels[testOptions[s]["title"] + " Threshold"] = testOptions[s]["thresholdLabel"]
        thresholdTypes[testOptions[s]["title"] + " Threshold"] = testOptions[s]["thresholdType"]
        thresholdFills[testOptions[s]["title"] + " Threshold"] = testOptions[s]["thresholdFill"]
    
    datasets, order, output = executeTest.getErrorSets(output, data, datasets, errorSet, warningSet, sets, testOptions)
    output = executeTest.getAxes(output, axisTitles, ["left", "right"])
    datasets = executeTest.getDatasets(data, datasets, sets, testOptions, order)

    output["datasets"] = datasets
    output["thresholdLabels"] = thresholdLabels
    output["thresholdTypes"] = thresholdTypes
    output["thresholdFills"] = thresholdFills
    output["errorMsg"] = errorMsg
    return output
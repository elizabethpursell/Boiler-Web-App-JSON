import pandas as pd

# call with checkDuration to remove points that are over duration limit
def underLimit(value, limit):
    return value > limit

# call with checkDuration to remove points that are under duration limit
def overLimit(value, limit):
    return value < limit

# used with duration tests
def checkDuration(checkSet, data, timeLimit, checkLimit):
    dates = data.date.tolist()
    removeDuration = False
    durationSet = []
    removeRows = []
    
    for i in range(checkSet.shape[0] - 1, 0, -1):       # reverse loop through errorSet
        index = dates.index(checkSet["date"].iloc[i])
        prevDate = dates[index - 1]
        if prevDate == checkSet["date"].iloc[i - 1]:      # consecutive points
            durationSet.append(i)
            if i == 1:
                durationSet.append(0)
            duration = pd.Timedelta(checkSet["date"].iloc[durationSet[0]] - checkSet["date"].iloc[i]).seconds / 60.0    # duration in min
            if(checkLimit(duration, timeLimit)):       # check duration condition
                removeDuration = True
            else:
                removeDuration = False
        else:
            if removeDuration:      # remove duration points if over 10 min
                removeRows += durationSet
            durationSet = [i]
            removeDuration = False

    if removeDuration:
        removeRows += durationSet
        
    checkSet = checkSet.drop([checkSet.index[j] for j in removeRows])
    return checkSet

# adds dailyWeather/hourlyWeather to data
def addWeatherData(data, weatherData):
        
    def f(row, date, value, default, setName):
        if row["date"] >= date and row["status"] == "default":
            return value
        elif row["status"] == "filled":
            return row[setName]
        else:
            return default
    
    def g(row, date):
        if row["date"] >= date:
            return "filled"
        else:
            return "default"
    
    # add values to all times between weatherData rows
    for col in weatherData.columns:
        data["status"] = "default"
        for date in reversed(weatherData.index):
            default = float(weatherData[col].iloc[0])
            value = float(weatherData[col].loc[date])
            data.loc[:, col] = data.apply(f, args=(date, value, default, col), axis=1)
            data.loc[:, "status"] = data.apply(g, args=([date]), axis=1)
        
    return data

# gets errorSet/warningSet for custom condition types
def getCustomCondition(data, c):
    if c["compare"] == ">":
        if c["set2"]["operation"] == "+":
            return data[data[c["set1"]] > (data[c["set2"]["name"]] + c["set2"]["value"])]
        elif c["set2"]["operation"] == "-":
            return data[data[c["set1"]] > (data[c["set2"]["name"]] - c["set2"]["value"])]
        elif c["set2"]["operation"] == "*":
            return data[data[c["set1"]] > (data[c["set2"]["name"]] * c["set2"]["value"])]
        elif c["set2"]["operation"] == "/":
            return data[data[c["set1"]] > (data[c["set2"]["name"]] / c["set2"]["value"])]
    elif c["compare"] == ">=":
        if c["set2"]["operation"] == "+":
            return data[data[c["set1"]] >= (data[c["set2"]["name"]] + c["set2"]["value"])]
        elif c["set2"]["operation"] == "-":
            return data[data[c["set1"]] >= (data[c["set2"]["name"]] - c["set2"]["value"])]
        elif c["set2"]["operation"] == "*":
            return data[data[c["set1"]] >= (data[c["set2"]["name"]] * c["set2"]["value"])]
        elif c["set2"]["operation"] == "/":
            return data[data[c["set1"]] >= (data[c["set2"]["name"]] / c["set2"]["value"])]
    elif c["compare"] == "<":
        if c["set2"]["operation"] == "+":
            return data[data[c["set1"]] < (data[c["set2"]["name"]] + c["set2"]["value"])]
        elif c["set2"]["operation"] == "-":
            return data[data[c["set1"]] < (data[c["set2"]["name"]] - c["set2"]["value"])]
        elif c["set2"]["operation"] == "*":
            return data[data[c["set1"]] < (data[c["set2"]["name"]] * c["set2"]["value"])]
        elif c["set2"]["operation"] == "/":
            return data[data[c["set1"]] < (data[c["set2"]["name"]] / c["set2"]["value"])]
    elif c["compare"] == "<=":
        if c["set2"]["operation"] == "+":
            return data[data[c["set1"]] <= (data[c["set2"]["name"]] + c["set2"]["value"])]
        elif c["set2"]["operation"] == "-":
            return data[data[c["set1"]] <= (data[c["set2"]["name"]] - c["set2"]["value"])]
        elif c["set2"]["operation"] == "*":
            return data[data[c["set1"]] <= (data[c["set2"]["name"]] * c["set2"]["value"])]
        elif c["set2"]["operation"] == "/":
            return data[data[c["set1"]] <= (data[c["set2"]["name"]] / c["set2"]["value"])]
    elif c["compare"] == "==":
        if c["set2"]["operation"] == "+":
            return data[data[c["set1"]] == (data[c["set2"]["name"]] + c["set2"]["value"])]
        elif c["set2"]["operation"] == "-":
            return data[data[c["set1"]] == (data[c["set2"]["name"]] - c["set2"]["value"])]
        elif c["set2"]["operation"] == "*":
            return data[data[c["set1"]] == (data[c["set2"]["name"]] * c["set2"]["value"])]
        elif c["set2"]["operation"] == "/":
            return data[data[c["set1"]] == (data[c["set2"]["name"]] / c["set2"]["value"])]
    elif c["compare"] == "!=":
        if c["set2"]["operation"] == "+":
            return data[data[c["set1"]] != (data[c["set2"]["name"]] + c["set2"]["value"])]
        elif c["set2"]["operation"] == "-":
            return data[data[c["set1"]] != (data[c["set2"]["name"]] - c["set2"]["value"])]
        elif c["set2"]["operation"] == "*":
            return data[data[c["set1"]] != (data[c["set2"]["name"]] * c["set2"]["value"])]
        elif c["set2"]["operation"] == "/":
            return data[data[c["set1"]] != (data[c["set2"]["name"]] / c["set2"]["value"])]

# gets errorSet/WarningSet for compound conditions
def getHelperCondition(data, c):
    if c["type"] == "value":
        if c["compare"] == ">":
            return data[data[c["set1"]] > c["set2"]["value"]]
        elif c["compare"] == ">=":
            return data[data[c["set1"]] >= c["set2"]["value"]]
        elif c["compare"] == "<":
            return data[data[c["set1"]] < c["set2"]["value"]]
        elif c["compare"] == "<=":
            return data[data[c["set1"]] <= c["set2"]["value"]]
        elif c["compare"] == "==":
            return data[data[c["set1"]] == c["set2"]["value"]]
        elif c["compare"] == "!=":
            return data[data[c["set1"]] != c["set2"]["value"]]
    elif c["type"] == "set":
        if c["compare"] == ">":
            return data[data[c["set1"]] > data[c["set2"]["name"]]]
        elif c["compare"] == ">=":
            return data[data[c["set1"]] >= data[c["set2"]["name"]]]
        elif c["compare"] == "<":
            return data[data[c["set1"]] < data[c["set2"]["name"]]]
        elif c["compare"] == "<=":
            return data[data[c["set1"]] <= data[c["set2"]["name"]]]
        elif c["compare"] == "==":
            return data[data[c["set1"]] == data[c["set2"]["name"]]]
        elif c["compare"] == "!=":
            return data[data[c["set1"]] != data[c["set2"]["name"]]]
    elif c["type"] == "custom":
        return getCustomCondition(data, c)
    elif c["type"] == "abs":
        if c["compare"] == ">":
            return data[abs(data[c["set1"]]) > c["set2"]["value"]]
        elif c["compare"] == ">=":
            return data[abs(data[c["set1"]]) >= c["set2"]["value"]]
        elif c["compare"] == "<":
            return data[abs(data[c["set1"]]) < c["set2"]["value"]]
        elif c["compare"] == "<=":
            return data[abs(data[c["set1"]]) <= c["set2"]["value"]]
                
# gets errorSet/warningSet
def getConditionSet(data, condition):
    conditionSet = pd.DataFrame()
    helperSet = pd.DataFrame()
    connect = ""
    i = 0
    for c in condition:
        if c == "and" or c == "or":
            connect = c
        elif conditionSet.empty and connect == "":
            conditionSet = getHelperCondition(data, c)
        else:
            helperSet = getHelperCondition(data, c)
                
            if connect == "and":
                conditionSet = data[data.index.isin(conditionSet.index) & data.index.isin(helperSet.index)]
            elif connect == "or":
                if len(condition[i:len(condition)]) > 1:
                    helperSet = getConditionSet(data, condition[i:len(condition)])
                    
                return data[data.index.isin(conditionSet.index) | data.index.isin(helperSet.index)]
        i += 1
                
    return conditionSet

# gets data to graph threshold
def getThresholdData(data, test, s):
    if test["options"][s]["thresholdType"] == "exists":
        return [0] * len(data["date"].tolist())
    for c in test["warning"]:
            if c != "and" and c != "or":
                if c["set1"] == s:
                    if test["options"][s]["thresholdType"] == "value":
                        return [c["set2"]["value"]] * len(data[c["set1"]].tolist())
                    elif test["options"][s]["thresholdType"] == "set":
                        return data[c["set2"]["name"]].tolist()
                    elif test["options"][s]["thresholdType"] == "custom":
                        if c["set2"]["operation"] == "+":
                            return [y + c["set2"]["value"] for y in data[c["set2"]["name"]].tolist()]
                        elif c["set2"]["operation"] == "-":
                            return [y - c["set2"]["value"] for y in data[c["set2"]["name"]].tolist()]
                        elif c["set2"]["operation"] == "*":
                            return [y * c["set2"]["value"] for y in data[c["set2"]["name"]].tolist()]
                        elif c["set2"]["operation"] == "/":
                            return [y / c["set2"]["value"] for y in data[c["set2"]["name"]].tolist()]
                    elif test["options"][s]["thresholdType"] == "abs":
                        return [c["set2"]["value"]] * len(data[c["set1"]].tolist()), [(-1) * c["set2"]["value"]] * len(data[c["set1"]].tolist())
    return []
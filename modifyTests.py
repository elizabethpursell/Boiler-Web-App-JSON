import json

def mainMenu():
    print("\n***************************************************\n")
    print("     Welcome to the NURO Analysis Test Menu!")
    print("Use this menu to add/remove tests and update sets")
    print("\n***************************************************\n")
    
    print("Main Menu:\n")
    print("1. Add a test")
    print("2. Remove a test")
    print("3. Update sets")
    
    valid = False
    while valid == False:
        mode = input("\nSelect an option: ").lower()
        if mode == "1" or mode == "add":
            valid = True
            addTest()
        elif mode == "2" or mode == "remove":
            valid = True
            removeTest()
        elif mode == "3" or mode == "update":
            valid = True
            updateSets()
        else:
            print("Invalid Input -- Please enter 1, 2, or 3")
        
def addTest():
    print("\nOpening add menu...\n")
    
    test = {}
    testNum = getTestNum()
    
    print("\n** The test title should describe the error condition")
    test["title"] = input("What is the test's title? ")
    
    showSetsMenu()
    test["sets"] = getSets()
    
    test["type"] = setTestType(test["sets"])
    
    test["error"] = getConditionsList(test["sets"], "error")
    if test["type"] == "duration":
        test["errorDuration"] = getDuration(test["error"], "error")
    else:
        test["errorDuration"] = { "value": "", "compare": "" }
        
    test["warning"] = getConditionsList(test["sets"], "warning")
    if test["type"] == "duration":
        test["warningDuration"] = getDuration(test["error"], "warning")
    else:
        test["warningDuration"] = { "value": "", "compare": "" }
        
    options = getOptions(test["sets"], test["warning"], test["type"], test["warningDuration"])
    
    test["axisTitles"], test["options"] = getAxes(test["sets"], options)
    
    print("\nOpening test explanation menu...\n")
    test["causes"] = input("What causes this test to fail? ")
    test["importance"] = input("Why is it important to fix this test failure? ")
    
    try:
        with open("testOptions.json", "r+") as file:
            fileData = json.load(file)
            fileData["tests"][testNum] = test
            file.seek(0)
            json.dump(fileData, file, indent = 4)
    except:
        with open("testOptions.json", "w") as file:
            tests = {"tests": {testNum: test}}
            json.dump(tests, file, indent = 4)
            
    print("\nThe test has been successfully added.")
    
def removeTest():
    print("\nOpening remove menu...\n")
    
    with open("testOptions.json", "r") as file:
        data = json.load(file)
    
    testNum = 0
    test = None
    validNum = False
    while validNum == False:
        testInput = input("What is the test number that you want to remove? ")
        try:
            testNum = int(testInput)
            try:
                test = data["tests"][str(testNum)]
                validNum = True
            except:
                print("Invalid Input -- Please enter a valid test number\n")
        except:
            print("Invalid Input -- Please enter an integer\n")
            
    print("\nSelected Test:", test["title"])
    
    valid = False
    while valid == False:
        userInput = input("Are you sure that you want to delete Test " + str(testNum) + "? ")
        if userInput.lower() == "yes":
            valid = True
            del data["tests"][str(testNum)]
            with open("testOptions.json", "w") as file:
                json.dump(data, file)
                
            print("\nThe test has been successfully removed.")
        elif userInput.lower() == "no":
            valid = True
            print("Test", testNum, "was not removed.")
        else:
            print("Invalid Input -- Please enter yes or no\n")
    
def updateSets():
    print("\nOpening update menu...\n")
    print("** Before using this menu, be sure the follow the code manual for the preliminary set up\n")
    
    setData = {}
    
    valid = False
    setName = ""
    while valid == False:
        setName = input("What is the keyword for that set that was added? ")
        if len(setName.split(" ")) == 1:
            valid = True
        else:
            print("Invalid Input -- Please enter a valid set keyword\n")
    
    setData["title"] = input("\nWhat is the legend label for " + setName + "? ")
    
    valid = False
    dataset = ""
    validSets = ["data", "dailyWeather", "hourlyWeather"]
    print("\nDatasets:", validSets)
    while valid == False:
        dataset = input("Which dataset is the set from? ")
        if dataset in validSets:
            valid = True
        else:
            print("Invalid Input -- Please enter a valid dataset name. Typically data is chosen.\n")
    
    valid = False
    measure = ["default", "setpoint", "difference", "metric", "metric difference"]
    print("\nMeasurement Types:", measure)
    while valid == False:
        measureType = input("What type of measurement is this set? ").lower()
        if measureType in measure:
            valid = True
            setData["measurement"] = measureType
        else:
            print("Invalid Input -- Please enter a valid measurement type\n")
            
    valid = False
    unitTypes = ["temperature", "current", "frequency", "pressure", "height", "degrees", "percent", "speed", "other"]
    print("\nUnit Types:", unitTypes)
    while valid == False:
        unitType = input("What type of unit is this set? ").lower()
        if unitType in unitTypes:
            valid = True
            setData["unitType"] = unitType
            if unitType == "other":
                setData["units"] = input("Please enter the set's units: ")
            else:
                setData["units"] = getUnits(measureType, unitType)
        else:
            print("Invalid Input -- Please enter a valid unit type\n")
    
    try:
        with open("setOptions.json", "r+") as file:
            fileData = json.load(file)
            fileData["sets"][dataset][setName] = setData
            file.seek(0)
            json.dump(fileData, file, indent = 4)
    except:
        with open("setOptions.json", "r+") as file:
            fileData = json.load(file)
            fileData["sets"][dataset] = { setName: setData }
            file.seek(0)
            json.dump(fileData, file, indent = 4)
            
    print("\nThe set has been successfully added.")
            
def getUnits(measureType, unitType):
    imperial = {"temperature": "\N{DEGREE SIGN}F", "current": "mA / V / %", "frequency": "RPM", "pressure": "psi",
                "height": "in", "degrees": "\N{DEGREE SIGN}", "percent": "%", "speed": "mph"}
    metric = {"temperature": "\N{DEGREE SIGN}C", "current": "mA / V / %", "frequency": "RPM", "pressure": "hPa",
              "height": "mm", "degrees": "\N{DEGREE SIGN}", "percent": "%", "speed": "km / h"}
    units = ""
    if measureType == "default" or measureType == "setpoint" or measureType == "difference":
        units = imperial[unitType]
    elif measureType == "metric" or "metric difference":
        units = metric[unitType]
    else:
        return input("Please enter the set's units: ")
        
    valid = False
    while valid == False:
        userInput = input("The autogenerated units for this set are " + units + ". Is this correct? ")
        if userInput == "yes":
            return units
        elif userInput == "no":
            valid = True
            return input("What are the correct units? ")
        else:
            print("Invalid Input -- Please enter yes or no\n")
        
def getTestNum():
    testNum = 0
    try:
        with open("testOptions.json", encoding="utf8") as file:
            data = json.load(file)
            testNum = len(data["tests"]) + 1
    except:
        testNum = 1
        
    print("The autogenerated test number is", testNum)      
    
    return testNum

def getSets():
    sets = []
    
    setList = []
    with open("setOptions.json", encoding="utf8") as file:
            data = json.load(file)
            for dataset, s in data["sets"].items():
                setList += data["sets"][dataset].keys()
    
    repeat = True
    print("\n** Enter done to when finished entering sets")
    while repeat == True:
        setName = input("Enter a set's keyword to add to the test: ")
        if setName in setList:
            sets.append(setName)
        elif setName.lower() == "done":
            repeat = False
            print("\n** The first set in the list has priority for the left axis")
            print("Final Set List: ", sets)
            valid = False
            while valid == False:
                user_input = input("Is this set list correct? ").lower()
                if user_input == "no":
                    valid = True
                    print("\nThe set list has been reset.")
                    return getSets()
                elif user_input == "yes":
                    valid = True
                else:
                    print("Invalid Input -- Please enter yes or no\n")
        else:
            print("Invalid Input -- Please enter a keyword from the list above\n")
    
    return sets

def setTestType(sets):
    testType = ""
    dailySets = []
    hourlySets = []
    diffSets = []
    
    with open("setOptions.json", encoding="utf8") as file:
        data = json.load(file)
        for dataset, setName in data["sets"].items():
            for s in setName.keys():
                if data["sets"][dataset][s]["measurement"] == "difference":
                    diffSets.append(s)
                elif dataset == "dailyWeather":
                    dailySets.append(s)
                elif dataset == "hourlyWeather":
                    hourlySets.append(s)
    
    valid = False
    while valid == False:
        user_input = input("\nWould you like to check the duration of the error and warning conditions? ").lower()
        if user_input == "no":
            valid = True
        elif user_input == "yes":
            valid = True
            testType += "duration"
        else:
            print("Invalid Input -- Please enter yes or no\n")
    
    daily = False
    hourly = False
    difference = False
    for s in sets:
        if s in dailySets:
            daily = True
        elif s in hourlySets:
            hourly = True
        elif s in diffSets:
            difference = True
            
    if daily == True and hourly == True:
        testType += "all"
    elif daily == True:
        testType += "daily"
    elif hourly == True:
        testType += "hourly"
            
    if difference == True:
        testType += "difference"
        
    if testType == "":
        testType += "default"
    
    return testType

def showSetList(dataset, measurement, unitType, colMax):
    with open("setOptions.json", encoding="utf8") as file:
        data = json.load(file)
        col = 1
        for s in data["sets"][dataset]:
            correctTypes = (data["sets"][dataset][s]["unitType"] == unitType and data["sets"][dataset][s]["measurement"] == measurement)
            allMeasurementTypes = (measurement == "all" and data["sets"][dataset][s]["unitType"] == unitType)
            allUnitTypes = (unitType == "all" and data["sets"][dataset][s]["measurement"] == measurement)
            if correctTypes or allUnitTypes or allMeasurementTypes:
                if col < colMax:
                    print("\t-", data["sets"][dataset][s]["title"], "(" + s + ")", end="")
                else:
                    print("\t-", data["sets"][dataset][s]["title"], "(" + s + ")")
                    col = 0
                col += 1
        if col <= colMax and colMax != 1 and col != 1:
            print()
    
def showSetsMenu():
    print("\n---------------------------------------------------------------------------\n")
    print(" Sets to choose from:")
    print(" ** Use the keywords in the parentheses when selecting a set\n")
    
    print(" Temperatures:")
    showSetList("data", "default", "temperature", 2)
    
    print("\n Temperature Setpoints:")
    showSetList("data", "setpoint", "temperature", 2)
    
    print("\n Temperature Differences:")
    showSetList("data", "difference", "temperature", 1)
    
    print("\n Current:")
    showSetList("data", "all", "current", 1)
    
    print("\n Frequency:")
    showSetList("data", "all", "frequency", 2)
    
    print("\n Daily Weather (Imperial Units):")
    showSetList("dailyWeather", "default", "all", 2)
    
    print("\n Daily Weather (Metric Units):")
    showSetList("dailyWeather", "metric", "all", 2)
    
    print("\n Other Daily Weather:")
    showSetList("dailyWeather", "default", "other", 2)
        
    print("\n Hourly Weather (Imperial Units):")
    showSetList("hourlyWeather", "default", "all", 2)
        
    print("\n Hourly Weather (Metric Units):")
    showSetList("hourlyWeather", "metric", "all", 2)
    
    print("\n Other Hourly Weather:")
    showSetList("hourlyWeather", "default", "other", 2)
    
    print("\n---------------------------------------------------------------------------")
    
def getConditionsList(sets, conditionType):
    print("\nOpening " + conditionType + " condition generation menu...")
    
    conditions = []
    
    repeat = True
    while repeat == True:
        conditions.append(getCondition(sets, conditionType))
        valid = False
        while valid == False:
            userInput = input("\nWould you like to add another " + conditionType + " condition to the test? ").lower()
            if userInput == "no":
                repeat = False
                valid = True
                
                conditionStr = ""
                for c in conditions:
                    if c == "and" or c == "or":
                        conditionStr += (" " + c + " ")
                    else:
                        set1 = c["set1"]
                        if c["type"] == "abs":
                            set1 = "abs(" + set1 + ")"
                        conditionStr += (set1 + " " + c["compare"] + " " + c["set2"]["name"] + c["set2"]["operation"] + str(c["set2"]["value"]))
                
                print("\nFinished Conditions: ", conditionStr)
                inputValid = False
                while inputValid == False:
                    userInput = input("Are these " + conditionType + " conditions correct? ")
                    if userInput == "yes":
                        inputValid = True
                    elif userInput == "no":
                        inputValid = True
                        print("\nThe", conditionType, "conditions have been reset.")
                        return getConditionsList(sets, conditionType)
                    else:
                        print("Invalid Input -- Please enter yes or no\n")
            elif userInput == "yes":
                valid = True
                inputValid = False
                while inputValid == False:
                    userInput = input("Would you like to AND or OR the two conditions together? ").lower()
                    if userInput == "and":
                        inputValid = True
                        conditions.append("and")
                    elif userInput == "or":
                        inputValid = True
                        conditions.append("or")
                    else:
                        print("Invalid Input -- Please enter AND or OR. Typically AND is chosen.\n")
            else:
                print("Invalid Input -- Please enter yes or no")
            
    return conditions

def getCondition(sets, conditionType):
    condition = {}
    condition["set2"] = {}
    
    print("\nSet List: ", sets)
    valid = False
    while valid == False:
        userSet1 = input("Choose a set to start a new " + conditionType + " condition: ")
        if userSet1 in sets:
            valid = True
            condition["set1"] = userSet1
        else:
            print("Invalid Input -- Please enter a set from the set list\n")
            
    valid = False
    while valid == False:
        userCompare = input("Would you like to compare " + condition["set1"] + " to a value, set, or custom? ").lower()
        if userCompare == "value":
            valid = True
            condition["type"] = userCompare
            inputValid = False
            while inputValid == False:
                userInput = input("Do you want to use the absolute value of " + condition["set1"] + " in the comparison? ").lower()
                if userInput == "yes":
                    condition["type"] = "abs"
                    inputValid = True
                elif userInput == "no":
                    inputValid = True
                else:
                    print("Invalid Input -- Please enter yes or no\n")
            inputValid = False
            while inputValid == False:
                userInput = input("What value would you like to compare " + condition["set1"] + " to? ")
                try:
                    condition["set2"]["name"] = ""
                    condition["set2"]["value"] = float(userInput)
                    condition["set2"]["operation"] = ""
                    inputValid = True
                except:
                    print("Invalid Input -- Please enter a number\n")
        elif userCompare == "set":
            valid = True
            condition["type"] = userCompare
            setValid = False
            while setValid == False:
                userInput = input("Which set would you like to compare " + condition["set1"] + " to? ")
                if userInput in sets and userInput != condition["set1"]:
                    setValid = True
                    condition["set2"]["name"] = userInput
                    condition["set2"]["value"] = ""
                    condition["set2"]["operation"] = ""
                elif userInput == condition["set1"]:
                    print("Invalid Input -- Please enter a different set than " + condition["set1"] + "\n")
                else:
                    print("Invalid Input -- Please enter a set from the set list\n")
        elif userCompare == "custom":
            valid = True
            condition["type"] = userCompare
            setValid = False
            while setValid == False:
                userInput = input("Which set would you like to compare " + condition["set1"] + " to? ")
                if userInput in sets and userInput != condition["set1"]:
                    setValid = True
                    condition["set2"]["name"] = userInput
                elif userInput == condition["set1"]:
                    print("Invalid Input -- Please enter a different set than " + condition["set1"] + "\n")
                else:
                    print("Invalid Input -- Please enter a set from the set list\n")
            constValid = False
            while constValid == False:
                userInput = input("What constant value would you like to adjust " + condition["set2"]["name"] + " by? ")
                try:
                    condition["set2"]["value"] = float(userInput)
                    constValid = True
                except:
                    print("Invalid Input -- Please enter a number\n")
            opValid = False
            operations = ["+", "-", "*", "/"]
            print("\nValid Operations:", operations)
            while opValid == False:
                userInput = input("Select an operation to adjust " + condition["set1"] + " by " + str(condition["set2"]["value"]) + ": ")
                if userInput in operations:
                    opValid = True
                    condition["set2"]["operation"] = userInput
                else:
                    print("Invalid Input -- Please enter valid operation\n")
        else:
            print("Invalid Input -- Please enter value, set, or custom\n")
                    
    if "abs" in condition["set1"]:
        options = [">", "<", ">=", "<="]
        print("\nComparison Options:", options)
    else:
        options = [">", "<", "==", ">=", "<=", "!="]
        print("\nComparison Options: >, <, ==, >=, <=, != (not equal)")
    valid = False
    while valid == False:
        set1 = condition["set1"]
        if condition["type"] == "abs":
            set1 = "abs(" + set1 + ")"
        userCompare = input("How would you like to compare " + set1 + " to " + condition["set2"]["name"] + condition["set2"]["operation"] + str(condition["set2"]["value"]) + "? ")
        if userCompare in options:
            valid = True
            condition["compare"] = userCompare
            conditionStr = set1 + " " + condition["compare"] + " " + condition["set2"]["name"] + condition["set2"]["operation"] + str(condition["set2"]["value"])
            print("\nFinished Condition:", conditionStr)
            inputValid = False
            while inputValid == False:
                userInput = input("Is this " + conditionType + " condition correct? ")
                if userInput == "yes":
                    inputValid = True
                elif userInput == "no":
                    inputValid = True
                    print("\nThe condition has been reset.")
                    return getCondition(sets, conditionType)
                else:
                    print("Invalid Input -- Please enter yes or no\n")
        else:
            print("Invalid Input -- Please enter a valid comparison option\n")
                
    return condition
        
def getDuration(condition, conditionType):
    print("\n** Duration is the amount of MINUTES where the condition is met before changing to passing status")

    duration = {}
    
    conditionStr = ""
    for c in condition:
        if c == "and" or c == "or":
            conditionStr += (" " + c + " ")
        else:
            set1 = c["set1"]
            if c["type"] == "abs":
                set1 = "abs(" + set1 + ")"
            conditionStr += (set1 + " " + c["compare"] + " " + c["set2"]["name"] + c["set2"]["operation"] + str(c["set2"]["value"]))
    print(conditionType.capitalize(), "Condition:", conditionStr)
    
    valid = False
    while valid == False:
        inputVal = input("For what duration would you like to check the " + conditionType + " condition? ")
        try:
            duration["value"] = float(inputVal)
            valid = True
        except:
            print("Invalid Input -- Please enter a number\n")
    
    valid = False
    while valid == False:
        userCompare = input("Would you like to check if the duration is over or under " + str(duration["value"]) + " minutes? ").lower()
        if userCompare == "over":
            duration["compare"] = ">"
            valid = True
        elif userCompare == "under":
            duration["compare"] = "<"
            valid = True
        else:
            print("Invalid Input -- Please enter over or under\n")
            
    valid = False
    print("\nFinished", conditionType.capitalize(), "Duration Condition:", duration["compare"], duration["value"], "minutes")
    while valid == False:
        userInput = input("Is this " + conditionType + " duration condition correct? ")
        if userInput == "yes":
            valid = True
        elif userInput == "no":
            valid = True
            print("\nThe duration condition has been reset.")
            return getDuration(condition, conditionType)
        else:
            print("Invalid Input -- Please enter yes or no\n")
            
    return duration

def getOptions(sets, warningCondition, testType, duration):
    print()
    
    defaultTitles = {}
    with open("setOptions.json", encoding="utf8") as file:
        data = json.load(file)
        for dataset, setName in data["sets"].items():
            for s in setName.keys():
                defaultTitles[s] = data["sets"][dataset][s]["title"]
    
    options = {}
    for s in sets:
        title = defaultTitles[s]
        
        valid = False
        while valid == False:
            userInput = input("The autogenerated dataset label for " + s + " is " + title + ". Is this correct? ")
            if userInput.lower() == "yes":
                valid = True
            elif userInput.lower() == "no":
                valid = True
                title = input("What is the correct dataset label? ")
            else:
                print("Invalid Input -- Please enter yes or no\n")

        options[s] = {"title": title}
        
        options[s]["units"] = getSetUnits(s, False)[0]
        
        hasWarningCondition = False
        isCustom = False
        for c in warningCondition:
            if c != "and" and c != "or":
                if c["type"] == "custom":
                    isCustom = True
                if c["set1"] == s:
                    hasWarningCondition = True
                    if c["compare"] == "!=" and c["set2"]["value"] == 0:
                        options[s]["thresholdType"] = "exists"
                        options[s]["thresholdFill"] = "all"
                        options[s]["thresholdLabel"] = "any"
                    elif c["type"] == "abs":
                        options[s]["thresholdType"] = "abs"
                        if c["compare"] == ">":
                            options[s]["thresholdFill"] = "split"
                            options[s]["thresholdLabel"] = "> " + str(c["set2"]["value"]) + " or < -" + str(c["set2"]["value"])
                        elif c["compare"] == ">=":
                            options[s]["thresholdFill"] = "split"
                            options[s]["thresholdLabel"] = ">= " + str(c["set2"]["value"]) + " or <= -" + str(c["set2"]["value"])
                        elif c["compare"] == "<":
                            options[s]["thresholdFill"] = "between"
                            options[s]["thresholdLabel"] = "< " + str(c["set2"]["value"]) + " and > -" + str(c["set2"]["value"])
                        elif c["compare"] == "<=":
                            options[s]["thresholdFill"] = "between"
                            options[s]["thresholdLabel"] = "<= " + str(c["set2"]["value"]) + " and >= -" + str(c["set2"]["value"])
                        else:
                            options[s]["thresholdType"] = "none"
                            options[s]["thresholdLabel"] = "n/a"
                    elif c["type"] == "set":
                        options[s]["thresholdType"] = "set"
                        if c["compare"] == ">" or c["compare"] == ">=":
                            options[s]["thresholdFill"] = "above"
                            options[s]["thresholdLabel"] = c["compare"] + " " + defaultTitles[c["set2"]["name"]]
                        elif c["compare"] == "<" or c["compare"] == "<=":
                            options[s]["thresholdFill"] = "below"
                            options[s]["thresholdLabel"] = c["compare"] + " " + defaultTitles[c["set2"]["name"]]
                        else:
                            options[s]["thresholdFill"] = "none"
                            options[s]["thresholdLabel"] = c["compare"] + " " + defaultTitles[c["set2"]["name"]]
                    elif c["type"] == "custom":
                        options[s]["thresholdType"] = "custom"
                        if c["compare"] == ">" or c["compare"] == ">=":
                            options[s]["thresholdFill"] = "above"
                            options[s]["thresholdLabel"] = c["compare"] + " " + defaultTitles[c["set2"]["name"]] + c["set2"]["operation"] + str(c["set2"]["value"])
                        elif c["compare"] == "<" or c["compare"] == "<=":
                            options[s]["thresholdFill"] = "below"
                            options[s]["thresholdLabel"] = c["compare"] + " " + defaultTitles[c["set2"]["name"]] + c["set2"]["operation"] + str(c["set2"]["value"])
                        else:
                            options[s]["thresholdFill"] = "none"
                            options[s]["thresholdLabel"] = c["compare"] + " " + defaultTitles[c["set2"]["name"]] + c["set2"]["operation"] + str(c["set2"]["value"])
                    elif c["type"] == "value":
                        options[s]["thresholdType"] = "value"
                        if c["compare"] == ">" or c["compare"] == ">=":
                            options[s]["thresholdFill"] = "above"
                            options[s]["thresholdLabel"] = c["compare"] + " " + str(c["set2"]["value"])
                        elif c["compare"] == "<" or c["compare"] == "<=":
                            options[s]["thresholdFill"] = "below"
                            options[s]["thresholdLabel"] = c["compare"] + " " + str(c["set2"]["value"])
                        else:
                            options[s]["thresholdFill"] = "none"
                            options[s]["thresholdLabel"] = c["compare"] + " " + str(c["set2"]["value"])
                    else:
                        options[s]["thresholdType"] = "none"
                        options[s]["thresholdFill"] = "none"
                        options[s]["thresholdLabel"] = "n/a"
                        
                    if testType == "duration":
                        options[s]["thresholdLabel"] += (" for " + duration["compare"] + " " + str(duration["value"]) + " minutes" )
                    break

        if isCustom == True and hasWarningCondition == False:     # override none threshold for custom test types
            options[s]["thresholdType"] = "custom"
            options[s]["thresholdFill"] = "none"
            conditionStr = ""
            for c in warningCondition:
                if c == "and" or c == "or":
                    conditionStr += (" " + c + " ")
                else:
                    set1 = defaultTitles[c["set1"]]
                    if c["type"] == "abs":
                        set1 = "abs(" + set1 + ")"
                    conditionStr += (set1 + " " + c["compare"] + " " + defaultTitles[c["set2"]["name"]] + c["set2"]["operation"] + str(c["set2"]["value"]))
            options[s]["thresholdLabel"] = conditionStr
        elif hasWarningCondition == False:
            options[s]["thresholdType"] = "exists"
            options[s]["thresholdFill"] = "all"
            options[s]["thresholdLabel"] = "any"
        
    return options

def getAxes(sets, options):
    diffSets = []
    
    with open("setOptions.json", encoding="utf8") as file:
        data = json.load(file)
        for dataset, setName in data["sets"].items():
            for s in setName.keys():
                if data["sets"][dataset][s]["measurement"] == "difference":
                    diffSets.append(s)
    
    leftUnits = []
    leftSets = []
    rightUnits = []
    rightSets = []
    diffCountL = 0
    diffCountR = 0
    for s in sets:
        if options[s]["units"] in leftUnits:
            leftSets.append(s)
            if s in diffSets:
                diffCountL += 1
        elif options[s]["units"] in rightUnits:
            rightSets.append(s)
            if s in diffSets:
                diffCountR += 1
        else:
            if len(leftSets) == 0:
                leftUnits.append(options[s]["units"])
                leftSets.append(s)
                if s in diffSets:
                    diffCountL += 1
            else:
                rightUnits.append(options[s]["units"])
                rightSets.append(s)
                if s in diffSets:
                    diffCountR += 1
                
    axisTitles = {}
    if len(leftSets) == 1:
        axisTitles["left"] = options[leftSets[0]]["title"] + " (" + leftUnits[0] + ")"
    else:
        axisTitles["left"] = getSetUnits(leftSets[0], diffCountL == len(leftSets))[1] + " (" + leftUnits[0] + ")"
            
    if len(rightSets) == 0:
        axisTitles["right"] = axisTitles["left"]
    elif len(rightSets) == 1:
        axisTitles["right"] = options[rightSets[0]]["title"] + " (" + rightUnits[0] + ")"
    else:
        axisTitles["right"] = getSetUnits(rightSets[0], diffCountR == len(rightSets))[1] + " (" + rightUnits[0] + ")"
        
    print("\nLeft Axis Title:", axisTitles["left"])
    print("Left Axis Sets:", leftSets)
    if axisTitles["left"] != axisTitles["right"]:
        print("Right Axis Title:", axisTitles["right"])
        print("Right Axis Sets:", rightSets)
    else:
        print("Right axis is not needed")
    valid = False
    while valid == False:
        userInput = input("Are these autogenerated axes correct? ")
        if userInput.lower() == "yes":
            valid = True
            for s in leftSets:
                options[s]["axisID"] = "left"
            for s in rightSets:
                options[s]["axisID"] = "right"
        elif userInput.lower() == "no":
            valid = True
            axisTitles, options = getCustomAxes(sets, options)
        else:
            print("Invalid Input -- Please enter yes or no\n")
    
    return axisTitles, options

def getCustomAxes(sets, options):
    axisTitles = {}
    left = []
    right = []
    print()
    for s in sets:
        valid = False
        while valid == False:
            userInput = input("Should " + s + " use the left or right axis? ").lower()
            if userInput == "left":
                valid = True
                left.append(s)
                options[s]["axisID"] = "left"
            elif userInput == "right":
                valid = True
                right.append(s)
                options[s]["axisID"] = "right"
            else:
                print("Invalid Input -- Please enter left or right\n")
                
    print("\n** Please include units in the title")
    print("Left Axis Sets:", left)
    axisTitles["left"] = input("What should the left axis be titled? ")
    
    if len(right) == 0:
        axisTitles["right"] = axisTitles["left"]
        print("Right axis is not needed")
    else:
        print("Right Axis Sets:", right)
        axisTitles["right"] = input("What should the right axis be titled? ")
                
    return axisTitles, options

def getSetUnits(setName, isDiff):
    
    with open("setOptions.json", encoding="utf8") as file:
        data = json.load(file)
        for dataset, sets in data["sets"].items():
            for s in sets.keys():
                if s == setName:
                    if isDiff == True:
                        return data["sets"][dataset][s]["units"], data["sets"][dataset][s]["unitType"].capitalize() + " Difference"
                    return data["sets"][dataset][s]["units"], data["sets"][dataset][s]["unitType"].capitalize()
        
    return input("What are the units for " + setName + "? ")

if __name__ == "__main__":
    mainMenu()
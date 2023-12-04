def extract_var(sentence):
    variables = []
    number = ""
    for i in range(len(sentence) - 1):
        if (
            sentence[i].isalpha()
            and sentence[i + 1] in [",", " ", ":", "="]
            and not sentence[i - 1].isalpha()
        ):
            variables.append(sentence[i])
        if sentence[i].isdigit() or sentence[i] == ".":
            number += sentence[i]
        elif number != "":
            variables.append(number)
            number = ""
        if i == len(sentence) - 1 and number != "":
            variables.append(number)
            number = ""
    result = []
    var_num = 0
    flag = 0
    for item in variables:
        if item.isalpha():
            result.append([item])
            if flag == 1:
                var_num = 0
                flag = 0
            var_num += 1
        else:
            # if "." in item:
            #     item = float(item)
            # elif not item.isalpha():
            #     item = int(item)
            result = result[::-1]
            for i in range(var_num):
                result[i].append(item)
            flag = 1
            result = result[::-1]
    return result


def check_inv(model_name, power_range, model_input):
    print(model_name, power_range, model_input)
    for power in power_range:
        vars = extract_var(power)
        for model in model_name:
            for var in vars:
                if var[0] in model:
                    for i in range(1, len(var)):
                        name = model.replace(var[0], str(var[i]))
                        if name in model_input:
                            return True
    return False


def check_INV_tests(text):
    tests = {
        "Safety Qualification": [],
        "EMC": [],
        "Grid connection": [],
    }

    # for safety
    if "IEC 62109-1" in text:
        tests["Safety Qualification"].append("IEC 62109-1")
    if "IEC 62109-2" in text:
        tests["Safety Qualification"].append("IEC 62109-2")

    # for EMC
    if "IEC 61000-3-2" in text:
        tests["EMC"].append("IEC 61000-3-2")
    if "IEC 61000-3-3" in text:
        tests["EMC"].append("IEC 61000-3-3")

    if "IEC 61000-3-4" in text:
        tests["EMC"].append("IEC 61000-3-4")
    if "IEC 61000-3-5" in text:
        tests["EMC"].append("IEC 61000-3-5")

    if "IEC 61000-3-12" in text:
        tests["EMC"].append("IEC 61000-3-12")
    if "IEC 61000-3-11" in text:
        tests["EMC"].append("IEC 61000-3-11")

    if "VDE-ARN 4105" in text:
        tests["EMC"].append("VDE-ARN 4105")

    # Grid connection
    if "IEC 62116" in text:
        tests["Grid connection"].append("IEC 62116")
    if "IEC 61727" in text:
        tests["Grid connection"].append("IEC 61727")

    if "VDE-ARN 4105" in text:
        tests["Grid connection"].append("VDE-ARN 4105")

    if "G83/2" in text:
        tests["Grid connection"].append("G83/2")

    if "G59/3" in text:
        tests["Grid connection"].append("G59/3")
    if "EN 50438" in text:
        tests["Grid connection"].append("EN 50438")
    if "En 50549-1" in text:
        tests["Grid connection"].append("En 50549-1")

    if "As/NZS4777.2" in text:
        tests["Grid connection"].append("As/NZS4777.2")
    if "AS/NZS4777.3" in text:
        tests["Grid connection"].append("AS/NZS4777.3")

    return tests


def checkTests(tests):
    count = 0
    summary = {
        "Safety Qualification": 0,
        "EMC": 0,
        "Grid connection": 0,
    }

    for test in tests:
        if len(tests[test]) > 0:
            if "IEC 62109-1" in tests[test] and "IEC 62109-2" in tests[test]:
                summary["Safety Qualification"] += 1
            if (
                ("IEC 61000-3-2" in tests[test] and "IEC 61000-3-3" in tests[test])
                or ("IEC 61000-3-4" in tests[test] and "IEC 61000-3-5" in tests[test])
                or ("IEC 61000-3-12" in tests[test] and "IEC 61000-3-11" in tests[test])
                or "VDE-ARN 4105" in tests[test]
            ):
                summary["EMC"] += 1
            if (
                ("IEC 62116" in tests[test] and "IEC 61727" in tests[test])
                or ("VDE-ARN 4105" in tests[test])
                or ("G83/2" in tests[test])
                or ("G59/3" in tests[test])
                or ("EN 50438" in tests[test] and "En 50549-1" in tests[test])
                or ("As/NZS4777.2" in tests[test] and "AS/NZS4777.3" in tests[test])
            ):
                summary["Grid connection"] += 1

    return summary
    # for result in summary:
    #     if summary[result] > 0:
    #         count += 1
    #     else:
    #         mess.append(result)
    # if count == 3:
    #     return True

    # return mess

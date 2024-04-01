import pandas
import json

files_to_convert = ["AlAs_parameters.csv", "AlInSb_bowing_parameters.csv", "AlSb_parameters.csv",
                    "GaAs_parameters.csv", "GaInAs_bowing_parameters.csv", "InAs_parameters.csv", "InSb_parameters.csv"]
material_names = ["AlAs", "AlInSb", "AlSb", "GaAs", "GaInAs", "InAs", "InSb"]

parameter_dictionary = {}
for n in range(len(files_to_convert)):
    file = files_to_convert[n]
    items = pandas.read_csv(file)
    # print(items)
    # print(items["Parameter"])
    # print(items['Parameter'])
    parameter_list = items['Parameter'].tolist()
    values_list = items['Recommended values'].tolist()
    # print(parameter_list)
    # print(values_list)
    parameter_dictionary.update({material_names[n]: {parameter: value for (parameter, value) in zip(parameter_list,
         values_list)}})

print(parameter_dictionary)
with open("parameters.json", "w") as file:
    json.dump(parameter_dictionary, file, indent=4)

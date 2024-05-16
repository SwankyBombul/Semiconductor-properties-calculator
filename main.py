import json
import function_library as f
import numpy as np


with open("parameters.json", "r") as file:
    material_constants = json.load(file)

# no_pressure_series = f.no_pressure_band_offset(material="AlInSb", temperature=200)
#
# pressure_series = f.pressure_band_offset(material="AlInSb", base="InSb", temperature=200)
#
# x = np.linspace(0, 1, 100)

f.quantum_well(0.5, 15, "AlInSb", 100, number_of_points=1000, is_tertiary=True, x=0.8, y=0.4)


# f.draw_diagram(no_pressure_series[0], no_pressure_series[1], pressure_series[0], pressure_series[1], pressure_series[
#     2], label_1="Pasmo przewodzenia bez naprężeń", label_2="Pasmo walencyjne bez naprężeń", label_3="Pasmo "
#                                                                                                     "przewodzenia", label_4="Pasmo ciężkich dziur", label_5="Pasmo lekkich dziur")
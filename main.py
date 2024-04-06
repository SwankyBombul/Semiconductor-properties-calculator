import json
import function_library as f
import numpy as np


with open("parameters.json", "r") as file:
    material_constants = json.load(file)

no_pressure_series = f.no_pressure_band_offset(material="GaInAs", temperature=300)

pressure_series = f.pressure_band_offset(material="GaInAs", base="GaAs")

x = np.linspace(0, 1, 100)


f.draw_diagram(no_pressure_series[0], no_pressure_series[1], pressure_series[0], pressure_series[1], pressure_series[2], label_1="Pasmo przewozenia bez naprężeń", label_2="Pasmo walencyjne bez naprężeń", label_3="Pasm przewodzdenia", label_4="Pasmo ciężkich dziur", label_5="Pasmo lekkich dziur")
import json
import function_library as f
import numpy as np


with open("parameters.json", "r") as file:
    material_constants = json.load(file)

no_pressure_series = f.no_pressure_band_offset(material="GaInAs", consider_temperature=True, temperature=300)

pressure_series = f.pressure_band_offset(material="GaInAs", base="GaAs", consider_temperature=True, temperature=300)

x = np.linspace(0, 1, 100)

series_1 = (no_pressure_series[0], "Valence band without pressure correction", "dashed", 2)
series_2 = (no_pressure_series[1], "Conduction band without pressure correction", "--", 2)
series_3 = (pressure_series[0], "Valence band with pressure correction", "-", 2)
series_4 = (pressure_series[1], "Heavy hole band with pressure correction", "dashdot", 2)
series_5 = (pressure_series[2], "Light hole band with pressure correction", "dotted", 2)

f.draw_diagram(series_1, series_2, series_3, series_4, series_5)
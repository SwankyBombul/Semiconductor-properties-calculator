import numpy as np
import matplotlib.pyplot as plt
import json


# 
def mix_properties(alloy_type="2_1", include_bowing=True, **kwargs: str):
    """Calculates linear interpolation of a property for a chosen alloy, with bowing parameter if possible, unless include_bowing is changed"""
    data=json.load(open("parameters.json", "r"))
    try:
        material = kwargs["material"]
        value_name = kwargs["variable"]
        component_material1 = data[material]["component_1"]
        value_1 = data[component_material1][value_name]
        component_material2 = data[material]["component_2"]
        value_2 = data[component_material2][value_name]
        if alloy_type != "2_1": # Currently just a placeholder for when the 4 - element functionality gets added
            component_material3 = data[material]["component_3"]
    except KeyError:
        print("Wrong inputs. Please check the use of function 'mix_properties'")

    else:
        try:
            bowing_parameter = data[material][value_name]
        except KeyError:
            bowing_parameter = 0

        finally:
            x = np.linspace(0, 1, 100)
            if alloy_type == "2_1":
                mixing_result = (1 - x) * value_1 + x * value_2 - x * (1 - x) * bowing_parameter

                return mixing_result



def no_pressure_band_offset(material: str, consider_temperature: bool, temperature=0):
    """Calculates the band offset without the pressure correction"""
    x = np.linspace(0, 1, 100)
    vbo_0 = mix_properties(material=material, type="2_1", variable="VBO")
    Eg = mix_properties(material=material, variable="Eg_Gamma")
    if consider_temperature:
        alpha = mix_properties(material=material, variable="a(Gamma)")
        alpha = alpha / 1000 # Converting units to basic SI
        beta = mix_properties(material=material, variable="b(Gamma)")
        temperature_correction = alpha * temperature**2 / (temperature + beta)
        Eg -= temperature_correction
    
    cbo_0 = vbo_0 + Eg
    print(x[0], -vbo_0[0]+cbo_0[0], -vbo_0[-1] + cbo_0[-1])
    return (vbo_0, cbo_0)


def pressure_band_offset(material: str, base: str, consider_temperature: bool, temperature=0):
    """Calculates the band offset with the pressure correction"""
    data=json.load(open("parameters.json"))
    (vbo_0, cbo_0) = no_pressure_band_offset(material, consider_temperature, temperature)
    alpha_mat = mix_properties(material=material, variable="a_lc", type="2_1")
    alpha_base = data[base]["a_lc"]
    eps_x = (alpha_base - alpha_mat) / alpha_mat
    eps_y = eps_x
    eps_z = -2 * mix_properties(material=material, variable="c_12", type="2_1") / mix_properties(material=material,
                                                                                                 variable="c_11",
                                                                                                 type="2_1") * eps_x
    multiplier = eps_x + eps_y + eps_z
    delta_conduction_band = mix_properties(material=material, variable="a_c", type="2_1") * multiplier
    delta_valence_band = mix_properties(material=material, variable="a_v", type = "2_1") * multiplier
    delta_internal_valence_band = -mix_properties(material=material, variable="b", type="2_1") * (eps_z - eps_x)

    cbo_with_pressure = cbo_0 + delta_conduction_band
    vbo_with_pressure_hh = vbo_0 + delta_valence_band + delta_internal_valence_band
    vbo_with_pressure_lh = vbo_0 + delta_valence_band - delta_internal_valence_band
    return_values = (cbo_with_pressure, vbo_with_pressure_hh, vbo_with_pressure_lh)
    return return_values


def draw_diagram(*args):
    """Draws a diagram including data series given as tuples in format (series_values, legend_label, line_style, line_width)"""
    x = np.linspace(0, 1, 100)
    for n in range(0, len(args)):
        data_series = args[n][0]

        try:
            series_label = args[n][1]
            series_line_style = args[n][2]
            series_line_width = args[n][3]
            if not isinstance(series_line_width, int):
                raise TypeError
            
        except TypeError:
            print(f"Incorrect diagram style parameters for series {n+1}. Using default values")
            plt.plot(x, args[n][0], label=f"Series {n+1}", linewidth=2)
            
        else:
            plt.plot(x, args[n][0], label=args[n][1], linestyle=args[n][2], linewidth=args[n][3])

    plt.title("$Ga_{1-x}In_xAs$ na podłożu $GaAs$ w temperaturze 300K")
    plt.xlabel("x")
    plt.ylabel("Eg (eV)")
    plt.legend()
    plt.show()

def get_components(material:str):
    """Returns the component materials for a compound material"""
    data=json.load(open("parameters.json", "r"))
    return data[material]["component_1"], data[material]["component_2"]

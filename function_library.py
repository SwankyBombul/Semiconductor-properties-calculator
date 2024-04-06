import numpy as np
import matplotlib.pyplot as plt
import json



def mix_properties(data=json.load(open("parameters.json", "r")), alloy_type="2_1", **kwargs):
    try:
        material = kwargs["material"]
        value_name = kwargs["variable"]
        component_material1 = data[material]["component_1"]
        value_1 = data[component_material1][value_name]
        component_material2 = data[material]["component_2"]
        value_2 = data[component_material2][value_name]
        if alloy_type != "2_1":
            component_material3 = data[material]["component_3"]
    except KeyError:
        print("Wrong inputs. Please check the use of the function 'mix_properties'")

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


def no_pressure_band_offset(material, temperature):
    x = np.linspace(0, 1, 100)
    vbo_0 = mix_properties(material=material, type="2_1", variable="VBO")
    alpha = mix_properties(material=material, variable="a(Gamma)")
    alpha = alpha / 1000
    beta = mix_properties(material=material, variable="b(Gamma)")
    Eg_0 = mix_properties(material=material, variable="Eg_Gamma")
    Eg = Eg_0 - alpha * temperature**2 / (temperature + beta)
    cbo_0 = vbo_0 + Eg
    print(x[0], -vbo_0[0]+cbo_0[0], -vbo_0[-1] + cbo_0[-1])
    return (vbo_0, cbo_0)


def pressure_band_offset(material, base, data=json.load(open("parameters.json"))):
    (vbo_0, cbo_0) = no_pressure_band_offset(material, temperature=300)
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


def draw_diagram(*args, **kwargs):
    x = np.linspace(0, 1, 100)
    labels = ["--", "--", "-", "dashdot", "dashdot"]
    for n in range(0, len(args)):
        print(n, len(args))

        plt.plot(x, args[n], label=kwargs[f"label_{n+1}"], linestyle=labels[n])

    plt.title("$Ga_{1-x}In_xAs$ na podłożu $GaAs$ w temperaturze 300K")
    plt.xlabel("x")
    plt.ylabel("Eg (eV)")
    plt.legend()
    plt.show()

def get_components(material):
    data=json.load(open("parameters.json", "r"))
    return data[material]["component_1"], data[material]["component_2"]

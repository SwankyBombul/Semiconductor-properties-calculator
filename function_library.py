import numpy as np
import matplotlib.pyplot as plt
import json


def interpolate(x, value_1, value_2, bowing_parameter):
    return (1 - x) * value_1 + x * value_2 - x * (1 - x) * bowing_parameter


def interpolate_tertiary(x, y, variable):
    data = json.load(open("parameters.json", "r"))

    materials = ("AlAs", "AlSb", "InAs", "InSb")

    return (x * y * data[materials[0]][variable] + x * (1 - y) * data[materials[1]][variable] + (1 - x) * y *
            data[materials[2]][variable] + (1 - x) * (
                1 - y) * data[materials[3]][variable])


def mix_properties(number_of_points, data=json.load(open("parameters.json", "r")), alloy_type="2_1",  **kwargs):
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
            x = np.linspace(0, 1, number_of_points)
            if alloy_type == "2_1":
                mixing_result = interpolate(x, value_1, value_2, bowing_parameter)
                return mixing_result


def no_pressure_band_offset(material, temperature, number_of_points):
    x = np.linspace(0, 1, number_of_points)
    vbo_0 = mix_properties(material=material, type="2_1", variable="VBO", number_of_points=number_of_points)
    alpha = mix_properties(material=material, variable="a(Gamma)", number_of_points=number_of_points)
    alpha = alpha / 1000
    beta = mix_properties(material=material, variable="b(Gamma)", number_of_points=number_of_points)
    Eg_0 = mix_properties(material=material, variable="Eg_Gamma", number_of_points=number_of_points)
    Eg = Eg_0 - alpha * temperature**2 / (temperature + beta)
    cbo_0 = vbo_0 + Eg
    print(x[0], -vbo_0[0]+cbo_0[0], -vbo_0[-1] + cbo_0[-1])
    return (vbo_0, cbo_0)


def pressure_band_offset(material, base, temperature, number_of_points, data=json.load(open("parameters.json"))):
    (vbo_0, cbo_0) = no_pressure_band_offset(material, temperature=temperature, number_of_points=number_of_points)
    alpha_mat = mix_properties(material=material, variable="a_lc", type="2_1", number_of_points=number_of_points)
    alpha_base = data[base]["a_lc"]
    eps_x = (alpha_base - alpha_mat) / alpha_mat
    eps_y = eps_x
    eps_z = (-2 * mix_properties(number_of_points=number_of_points, material=material, variable="c_12", type="2_1") /
             mix_properties(number_of_points=number_of_points, material=material, variable="c_11", type="2_1") * eps_x)
    multiplier = eps_x + eps_y + eps_z
    delta_conduction_band = mix_properties(material=material, variable="a_c", type="2_1", number_of_points=number_of_points) * multiplier
    delta_valence_band = mix_properties(material=material, variable="a_v", type = "2_1", number_of_points=number_of_points) * multiplier
    delta_internal_valence_band = -mix_properties(material=material, variable="b", type="2_1", number_of_points=number_of_points) * (eps_z - eps_x)

    cbo_with_pressure = cbo_0 + delta_conduction_band
    vbo_with_pressure_hh = vbo_0 + delta_valence_band + delta_internal_valence_band
    vbo_with_pressure_lh = vbo_0 + delta_valence_band - delta_internal_valence_band
    return_values = (cbo_with_pressure, vbo_with_pressure_hh, vbo_with_pressure_lh)
    return return_values


def quantum_well(proportion, well_size, material, temperature, number_of_points, is_tertiary, x, y):
    data = json.load(open("parameters.json", "r"))
    base_data = data["InSb"]
    base_values = (base_data["VBO"],base_data["Eg_Gamma"]-base_data["a(Gamma)"]/1000 * temperature**2 /(temperature +
                                                                                                base_data["b(Gamma)"]
                                                                                                )+base_data["VBO"])
    proportion_index = number_of_points * proportion

    if not is_tertiary:
        with_pressure = pressure_band_offset(material=material, base="InSb", temperature=temperature, number_of_points=number_of_points)

        material_pres_cbo = with_pressure[0][int(proportion_index)]
        material_pres_vbo = max(with_pressure[1][int(proportion_index)], with_pressure[2][int(proportion_index)])

    else:
        alpha = interpolate_tertiary(x, y, variable="a(Gamma)")
        alpha = alpha / 1000
        beta = interpolate_tertiary(x, y, variable="b(Gamma)")

        tertiary_vbo_0 = interpolate_tertiary(x, y, "VBO")
        tertiary_cbo_0 = interpolate_tertiary(x, y, "Eg_Gamma") - alpha * temperature**2 / (temperature + beta) + interpolate_tertiary(x, y, "VBO")

        alpha_mat = interpolate_tertiary(x, y, variable="a_lc")
        alpha_base = data["InSb"]["a_lc"]
        eps_x = (alpha_base - alpha_mat) / alpha_mat
        eps_y = eps_x
        eps_z = (-2 * interpolate_tertiary(x, y, variable="c_12",) / interpolate_tertiary(
            x, y, variable="c_11") * eps_x)
        multiplier = eps_x + eps_y + eps_z
        delta_conduction_band = interpolate_tertiary(x, y, variable="a_c") * multiplier
        delta_valence_band = interpolate_tertiary(x, y, variable="a_v") * multiplier
        delta_internal_valence_band = -interpolate_tertiary(x, y, variable="b") * (eps_z - eps_x)

        cbo_with_pressure = tertiary_cbo_0 + delta_conduction_band
        vbo_with_pressure_hh = tertiary_vbo_0 + delta_valence_band + delta_internal_valence_band
        vbo_with_pressure_lh = tertiary_vbo_0 + delta_valence_band - delta_internal_valence_band

        material_pres_cbo = cbo_with_pressure
        material_pres_vbo = max(vbo_with_pressure_lh, vbo_with_pressure_hh)
    x_range = np.linspace(0, 3 * well_size, number_of_points)
    y_vbo = []
    y_cbo = []
    for x in x_range:
        if not(x < well_size or x > 2 * well_size):
            y_vbo.append(base_values[0])
            y_cbo.append(base_values[1])
        else:
            y_vbo.append(material_pres_vbo)
            y_cbo.append(material_pres_cbo)

    plt.plot(x_range, y_vbo, label="VBO", linewidth=2, color="blue", linestyle="-")
    plt.plot(x_range, y_cbo, label="CBO", linewidth=2, color="red", linestyle="-")

    plt.title(f"Al$_{{{x}}}$In$_{{{1-x}}}$As$_{{{y}}}$Sb na podłożu InSb dla T = {temperature}K", fontsize=16)
    plt.xlabel("x [nm]", fontsize=14)
    plt.ylabel("E [eV]", fontsize=14)

    plt.grid(True)
    plt.legend()

    plt.axvline(x=well_size, color="gray", linestyle="--")
    plt.axvline(x=2*well_size, color="gray", linestyle="--")

    # plt.axvline(x=1.5*well_size, ymin=y_vbo[int(number_of_points/2)], ymax=y_cbo[int(number_of_points/2)],
    #             color="pink",
    #             linestyle=":")
    plt.text(1.5*well_size, 0.2, f"Eg = {round(y_cbo[int(number_of_points/2)] - y_vbo[int(number_of_points/2)], 2)}")

    # plt.axvline(x=2.2 * well_size, ymin=y_vbo[int(number_of_points * 0.75)], ymax=y_cbo[int(number_of_points * 0.75)],
    #             color="pink",
    #             linestyle=":")
    plt.text(2.2*well_size, 0.2, f"Eg = "
                                 f"{round(y_cbo[int(number_of_points*0.75)] - y_vbo[int(number_of_points*0.75)], 2)}")

    plt.show()


def draw_diagram(*args, **kwargs):
    x = np.linspace(0, 1, 100)
    labels = ["--", "--", "-", "dashdot", "dashdot"]
    for n in range(0, len(args)):

        plt.plot(x, args[n], label=kwargs[f"label_{n+1}"], linestyle=labels[n])

    plt.title("$Al_{1-x}In_xSb$ na podłożu $InSb$ w temperaturze 600K")
    plt.xlabel("x")
    plt.ylabel("Eg (eV)")
    plt.legend()
    plt.show()


def get_components(material):
    data=json.load(open("parameters.json", "r"))
    return data[material]["component_1"], data[material]["component_2"]

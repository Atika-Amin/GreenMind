def estimate_local_energy(task, device):


    complexity = task["complexity"]

    capability = device.get(
        "device_capability",
        "medium"
    )


    energy = 0



    # Complexity impact

    if complexity == "Low":

        energy += 0.1


    elif complexity == "Medium":

        energy += 0.8


    else:

        energy += 2.5



    # Device capability impact

    if capability == "low":

        energy *= 1.5


    elif capability == "high":

        energy *= 0.7



    return round(energy,3)




def estimate_cloud_energy(task):


    complexity = task["complexity"]


    if complexity=="Low":

        energy = 0.2


    elif complexity=="Medium":

        energy = 0.7


    else:

        energy = 1.2



    return energy





def energy_decision(
        task_analysis,
        device_info
):


    local_energy = estimate_local_energy(

        task_analysis,

        device_info

    )


    cloud_energy = estimate_cloud_energy(

        task_analysis

    )



    network_cost = device_info.get(

        "network_cost",

        0.2

    )


    total_cloud_energy = (
        cloud_energy +
        network_cost
    )



    local_carbon = local_energy * 0.02


    cloud_carbon = total_cloud_energy * 0.02



    return {


        "local_energy":

        local_energy,


        "cloud_energy":

        round(total_cloud_energy,3),


        "network_cost":

        network_cost,


        "local_carbon":

        round(local_carbon,4),


        "cloud_carbon":

        round(cloud_carbon,4)

    }
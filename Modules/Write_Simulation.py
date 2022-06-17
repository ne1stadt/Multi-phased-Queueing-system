import os

def writeSimulation(final, unstaionary, node_state_dataframe, arrival_rate, array_of_departure_rates,
                    array_of_queue_lengths, finish_drop_window, dynamic, dynamic_window, number_of_samples,
                    dynamic_after_stationary_number_of_samples, simulation_duration, PATH):
    print('Saving data...')

    directory_path = makePath(arrival_rate, array_of_departure_rates, array_of_queue_lengths, PATH)
    os.mkdir(directory_path)

    # final.csv
    final.to_csv(directory_path + '/final.csv', index=False)

    # node_state_dataframe.csv
    node_state_dataframe.to_csv(directory_path + '/node_states.csv', index=False)

    # unstaionary.csv
    if (len(unstaionary) != 0):
        unstaionary.to_csv(directory_path + '/unstationary.csv', index=False)

    # configuration.txt
    with open(directory_path + "/configuration.txt", "w+") as text_file:
        configuration_txt = makeConfigurationTXT(arrival_rate, array_of_departure_rates, array_of_queue_lengths,
                                                 finish_drop_window, dynamic, dynamic_window,
                                                 number_of_samples,
                                                 dynamic_after_stationary_number_of_samples, simulation_duration, len(node_state_dataframe))
        text_file.write(configuration_txt)

    print('Results are placed in ' + directory_path + ' folder.')


def makePath(arrival_rate, array_of_departure_rates, array_of_queue_lengths, PATH):
    return PATH + r'\RUNS\RUN_rho' + str(round(arrival_rate/(array_of_departure_rates[0]), 2)) + '_n' + str(array_of_queue_lengths[0]) + '_m' + str(len(array_of_queue_lengths))
    #return 'RUNS\RUN_' + time.strftime("%d_%m_%Y_%H_%M_%S")


def makeConfigurationTXT(lambd, mus, queue_lengths, drop_window, dynamic, dynamic_window, number_of_samples,
                         dynamic_after_stationary_number_of_samples, simulation_duration, num_of_iterations):
    string = 'Simulation Configuration\n\n'
    string = string + 'Arrival Rate: ' + str(lambd) + '\n'
    lenmus = len(mus)
    for i in range(lenmus):
        string = string + 'Node ' + str(i) + ' departure rate: ' + str(mus[i]) + ', max queue length: ' + str(
            queue_lengths[i]) + '\n'
    if (dynamic == True):
        string = string + 'Simulation is dynamic. Parameters:' + '\n'
        string = string + 'Drop Window: ' + str(drop_window) + '\n\n'
        string = string + 'Dynamic Window: ' + str(dynamic_window) + '\n'
        string = string + 'Stationary Samples Number: ' + str(dynamic_after_stationary_number_of_samples)
    else:
        string = string + 'Simulation is static. Parameters:' + '\n'
        string = string + 'Drop Window: ' + str(drop_window) + '\n'
        string = string + 'Number of Signals: ' + str(number_of_samples)
    string = string + '\n\nSimulation Duration: ' + str(simulation_duration) + '\n'
    string = string + 'Iterations: ' + str(num_of_iterations)
    return string
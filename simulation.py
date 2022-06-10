import pandas as pd
import numpy as np
import time
import warnings
import os

warnings.filterwarnings("ignore")

# SIMULATION PARAMETERS
arrival_rate = 1
array_of_departure_rates = [1.5] * 4
array_of_queue_lengths = [2, 3, 4, 5]

finish_drop_window = 20

isdynamic = True
discrepancy = 0.1  # absolute value, not percentage!!
dynamic_window = 500
number_of_samples = 5000
dynamic_after_stationary_number_of_samples = 100


def go(lambd, mus, queue_lenghts, drop_window=100, isdynamic=False, discrepancy=0.001, dynamic_window=100, \
       number_of_samples=1000, dynamic_after_stationary_number_of_samples=1000):
    # Validation
    if (len(mus) != len(queue_lenghts)):
        print("Array of Mus and array of queue_lenghts must be of the same size.")
        return 0

    lenmus = len(mus)
    stationary = False
    last_unstationary_index = 0
    dynamic = isdynamic

    if (dynamic):
        number_of_samples = dynamic_after_stationary_number_of_samples

    # consider generator as a 0 node
    intensivities = np.append([lambd], mus)
    queue_lenghts = np.append([0], queue_lenghts)
    node_states = np.append(1, [0] * lenmus)

    node_queue_states = np.append(1, [0] * lenmus)
    # 0 doesn't mean node is empty, it is determined by node_states array

    # first signal comes to system
    upcoming_event_times = np.append([np.random.exponential(1 / intensivities[0])], [0] * lenmus)
    current_innode_signal_index = [0] * (lenmus + 1)

    d = {'start_time': [upcoming_event_times[0]], 'innode': [0], 'inqueue': [0], 'status': [0]}
    # Status enum table:
    # Not Started - 0
    # In Queue - 1
    # In Progress - 2
    # Terminated - 3
    # Finished - 4
    data = pd.DataFrame(data=d)
    for n in range(1, lenmus + 1):
        enter_name = 'node_' + str(n) + '_startprogress'
        data[enter_name] = -1
        end_name = 'node_' + str(n) + '_end'
        data[end_name] = -1

    d_for_node_state = {'time': [0]}
    node_state_dataframe = pd.DataFrame(data=d_for_node_state)
    for n in range(0, lenmus + 1):
        name = 'node_' + str(n)
        node_state_dataframe[name] = 0

    last_probabilities = []
    for i in range(lenmus):
        last_probabilities.append([0] * (queue_lenghts[i + 1] + 2))

    finished = data.drop(0)
    unstationary_data = finished.drop(finished.index)

    t = 0
    iterator = 0
    process_is_not_finished = True
    avg_innode_time = [0] * lenmus
    simulation_start_time = time.time()
    while (process_is_not_finished):

        t, node_event = nextEvent(node_states, upcoming_event_times)

        if (node_event == 0):  # case generator
            if (finished.index.empty):
                max_finished_index = -1
            else:
                max_finished_index = max(finished.index)
            data, node_states, node_queue_states, upcoming_event_times, current_innode_signal_index = \
                updateGenerator(data, t, node_event, intensivities, queue_lenghts, node_states, node_queue_states, \
                                upcoming_event_times, current_innode_signal_index, lenmus, max_finished_index)
        else:
            if (node_event != lenmus):  # case not last node
                data, node_states, node_queue_states, upcoming_event_times, current_innode_signal_index = \
                    updateNode(data, t, node_event, intensivities, queue_lenghts, node_states, node_queue_states, \
                               upcoming_event_times, current_innode_signal_index)
            else:  # case last node
                data, node_states, node_queue_states, upcoming_event_times, \
                current_innode_signal_index = updateLastNode(data, t, node_event, intensivities, queue_lenghts, \
                                                             node_states, node_queue_states, upcoming_event_times,
                                                             current_innode_signal_index)

        node_state_dataframe.loc[iterator + 1] = np.append([t], np.add(node_states, node_queue_states))

        if (iterator % drop_window == 1):
            finished = pd.concat([finished, data[data['status'] >= 3]])
            data = data.drop(data[data['status'] >= 3].index)
            if (dynamic == False):
                process_is_not_finished = processIsNotFinishedStatic(finished, number_of_samples)

        if (dynamic == True):
            if (iterator % dynamic_window == 1):
                stationary, last_probabilities = isStationary(node_state_dataframe, last_probabilities, \
                                                              discrepancy, dynamic_window, lenmus, iterator)
                if (stationary):
                    dynamic = False
                    unstationary_data = finished.sort_index()
                    finished = finished.drop(finished[finished.index < max(finished.index)].index)
                    last_unstationary_index = max(unstationary_data.index)
                    print("Stationary State detected. Starting static simulation.")

        iterator = iterator + 1
    folder_path = makePath()
    writeSimulation(finished, unstationary_data, node_state_dataframe.drop('node_0', axis=1), lambd, intensivities[1:], \
                    queue_lenghts[1:], drop_window, isdynamic, discrepancy, dynamic_window, number_of_samples, \
                    dynamic_after_stationary_number_of_samples, folder_path)

    simulation_duration = round(time.time() - simulation_start_time)
    print("Simulation duration: " + str(simulation_duration) + " seconds")
    finished = pd.concat([finished, data])
    return finished, unstationary_data, node_state_dataframe.drop('node_0', axis=1), folder_path


def nextEvent(node_states, upcoming_event_times):
    array = np.multiply(upcoming_event_times, node_states)
    indexes = np.where(array == 0)
    temp_max = max(array)
    for i in indexes:
        array[i] = temp_max
    new_time = min(array)
    node_event = np.where(upcoming_event_times == new_time)[0][0]

    return new_time, node_event


def updateGenerator(data, t, node_event, intensivities, queue_lenghts, node_states, node_queue_states, \
                    upcoming_event_times, current_innode_signal_index, lenmus, max_index_of_finished):
    new_signal = np.append([upcoming_event_times[0], 0, 0, 0], [-1] * 2 * lenmus)
    index_of_new_signal = max(np.append(data.index, [max_index_of_finished])) + 1
    data.loc[index_of_new_signal] = new_signal
    current_innode_signal_index[0] = index_of_new_signal

    if (node_queue_states[1] == queue_lenghts[1]):
        # Terminate signal
        data.loc[index_of_new_signal, 'status'] = 3
    else:
        if (node_states[1] == 0):
            # Move to progress on node 1
            data.loc[index_of_new_signal, 'status'] = 2
            data.loc[index_of_new_signal, 'innode'] = 1
            data.loc[index_of_new_signal, 'node_1_startprogress'] = t

            # Change state of node_event+1 to 1
            node_states[1] = 1
            # Give new upcoming_event_time to node_event+1
            upcoming_event_times[1] = t + np.random.exponential(1 / intensivities[1])
            current_innode_signal_index[1] = current_innode_signal_index[0]

        else:
            # Move to queue
            data.loc[index_of_new_signal, 'status'] = 1
            data.loc[index_of_new_signal, 'innode'] = 1
            data.loc[index_of_new_signal, 'inqueue'] = node_queue_states[1] + 1
            data.loc[index_of_new_signal, 'node_1_end'] = t
            node_queue_states[1] = node_queue_states[1] + 1

    # Give new upcoming_event_time to generator
    upcoming_event_times[0] = t + np.random.exponential(1 / intensivities[0])

    return data, node_states, node_queue_states, upcoming_event_times, current_innode_signal_index


def updateNode(data, t, node_event, intensivities, queue_lenghts, node_states, node_queue_states, \
               upcoming_event_times, current_innode_signal_index):
    index_of_signal = current_innode_signal_index[node_event]

    data.loc[index_of_signal, 'node_' + str(node_event) + '_end'] = t
    if (node_queue_states[node_event + 1] == queue_lenghts[node_event + 1]):
        # Terminate signal
        data.loc[index_of_signal, 'status'] = 3
    else:
        if (node_states[node_event + 1] == 0):
            # Move to progress
            data.loc[index_of_signal, 'status'] = 2
            data.loc[index_of_signal, 'innode'] = node_event + 1
            data.loc[index_of_signal, 'node_' + str(node_event + 1) + '_startprogress'] = t

            # Change state of node_event+1 to 1
            node_states[node_event + 1] = 1
            # Give new upcoming_event_time to node_event+1
            upcoming_event_times[node_event + 1] = t + np.random.exponential(1 / intensivities[node_event + 1])
            current_innode_signal_index[node_event + 1] = current_innode_signal_index[node_event]
        else:
            # Move to queue
            data.loc[index_of_signal, 'status'] = 1
            data.loc[index_of_signal, 'innode'] = node_event + 1
            data.loc[index_of_signal, 'inqueue'] = node_queue_states[node_event + 1] + 1
            node_queue_states[node_event + 1] = node_queue_states[node_event + 1] + 1

    if (node_queue_states[node_event] == 0):
        # Set State of node_event to 0
        node_states[node_event] = 0
    else:
        # Move queue
        queue_indexes = data[data['innode'] == node_event][data['status'] == 1].index
        for i in queue_indexes:
            previous = data.loc[i, 'inqueue'].item()
            data.loc[i, 'inqueue'] = previous - 1

        upcoming_signal_from_queue_index = queue_indexes[0]
        data.loc[upcoming_signal_from_queue_index, 'status'] = 2
        data.loc[upcoming_signal_from_queue_index, 'node_' + str(node_event) + '_startprogress'] = t
        current_innode_signal_index[node_event] = upcoming_signal_from_queue_index

        # Give new upcoming_event_time to node_event
        upcoming_event_times[node_event] = t + np.random.exponential(1 / intensivities[node_event])
        node_queue_states[node_event] = node_queue_states[node_event] - 1

    return data, node_states, node_queue_states, upcoming_event_times, current_innode_signal_index


def updateLastNode(data, t, node_event, intensivities, queue_lenghts, node_states, node_queue_states, \
                   upcoming_event_times, current_innode_signal_index):
    index_of_signal = current_innode_signal_index[node_event]
    data.loc[index_of_signal, 'status'] = 4
    data.loc[index_of_signal, 'node_' + str(node_event) + '_end'] = t

    if (node_queue_states[node_event] == 0):
        # Set State of node_event to 0
        node_states[node_event] = 0
    else:
        # Move queue
        queue_indexes = data[data['innode'] == node_event][data['status'] == 1].index
        for i in queue_indexes:
            previous = data.loc[i, 'inqueue'].item()
            data.loc[i, 'inqueue'] = previous - 1

        upcoming_signal_from_queue_index = queue_indexes[0]
        data.loc[upcoming_signal_from_queue_index, 'status'] = 2
        data.loc[upcoming_signal_from_queue_index, 'node_' + str(node_event) + '_startprogress'] = t
        current_innode_signal_index[node_event] = upcoming_signal_from_queue_index

        # Give new upcoming_event_time to node_event
        upcoming_event_times[node_event] = t + np.random.exponential(1 / intensivities[node_event])
        node_queue_states[node_event] = node_queue_states[node_event] - 1

    return data, node_states, node_queue_states, upcoming_event_times, current_innode_signal_index


def isStationary(node_state_dataframe, last_probabilities, discrepancy, dynamic_window, lenmus, iterator):
    new_probabilities = getProbabilities(node_state_dataframe, dynamic_window, last_probabilities, lenmus)

    discrepancies = []
    stationary_list = []
    for i in range(lenmus):
        discrepancies.append(np.abs(np.subtract(new_probabilities[i], last_probabilities[i])))
        l = len(new_probabilities[i])
        stationary_boolean_temp_array = [False] * l
        for j in range(l):
            if (discrepancies[i][j] <= discrepancy):
                stationary_boolean_temp_array[j] = True
            else:
                stationary_boolean_temp_array[j] = False
        stationary_list.append(stationary_boolean_temp_array)

    stationary_list_per_node = [False] * lenmus
    for k in range(lenmus):
        if (False in stationary_list[k]):
            stationary_list_per_node[k] = False
        else:
            stationary_list_per_node[k] = True

    print(stationary_list_per_node)
    if (False in stationary_list_per_node):
        return False, new_probabilities
    else:
        return True, new_probabilities


def getProbabilities(node_state_dataframe, dynamic_window, last_probabilities, lenmus):
    max_index = max(node_state_dataframe.index)

    # Create temp array of only last dynamic_window signals
    if (max_index < dynamic_window):
        temp = node_state_dataframe
    else:
        temp = node_state_dataframe.drop(
            node_state_dataframe[node_state_dataframe.index < max_index - dynamic_window].index)
    iter_array = np.delete(temp.index.to_numpy(), -1)

    # Set relative time
    for i in iter_array:
        temp.loc[i, 'time'] = temp.loc[i + 1, 'time'] - temp.loc[i, 'time']
    temp = temp.drop(max_index)

    full_time = np.sum(temp['time'])
    new_probabilities = []
    for temp_arr_iter in last_probabilities:
        new_probabilities.append(
            temp_arr_iter.copy())  # Must use this, otherwise changing new_probabilities affects last_probabilities

    for i in range(lenmus):
        l = len(new_probabilities[i])
        for j in range(l):
            # i - number of node
            # j - state
            new_probabilities[i][j] = np.sum(temp['time'][temp['node_' + str(i + 1)] == j]) / full_time

    return new_probabilities


def processIsNotFinishedStatic(finished, number_of_samples):
    l = len(finished)
    # label = Label()
    if (l >= number_of_samples):
        print('Progress: 100%')
        return False
    else:
        print('Progress: ' + str(round(l * 100 / number_of_samples, 2)))
        return True


def writeSimulation(final, unstaionary, node_state_dataframe, arrival_rate, array_of_departure_rates, \
                    array_of_queue_lengths, finish_drop_window, dynamic, discrepancy, dynamic_window, number_of_samples, \
                    dynamic_after_stationary_number_of_samples, folder_path):
    print('Analysing data...')

    directory_path = folder_path
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
        configuration_txt = makeConfigurationTXT(arrival_rate, array_of_departure_rates, array_of_queue_lengths, \
                                                 finish_drop_window, dynamic, discrepancy, dynamic_window,
                                                 number_of_samples, \
                                                 dynamic_after_stationary_number_of_samples)
        text_file.write(configuration_txt)

    # result.xlsx
    result_paramters, result_states = makeResult()
    result_paramters.to_excel(directory_path + '/result.xlsx', sheet_name='Parameters', index=False)
    result_states.to_excel(directory_path + '/result.xlsx', sheet_name='States', index=False)

    print('Results are placed in ' + directory_path + ' folder.')
    print('Have a good day!')


def makePath():
    return 'RUNS\RUN_' + time.strftime("%d_%m_%Y_%H_%M_%S")


def makeConfigurationTXT(lambd, mus, queue_lengths, drop_window, dynamic, discrepancy, dynamic_window,
                         number_of_samples, \
                         dynamic_after_stationary_number_of_samples):
    string = 'Simulation Configuration\n\n'
    string = string + 'Arrival Rate: ' + str(lambd) + '\n'
    lenmus = len(mus)
    for i in range(lenmus):
        string = string + 'Node ' + str(i) + ' departure rate: ' + str(mus[i]) + ', max queue length: ' + str(
            queue_lengths[i]) + '\n'
    if (dynamic == True):
        string = string + 'Simulation is dynamic. Parameters:' + '\n'
        string = string + 'Drop Window: ' + str(drop_window) + '\n\n'
        string = string + 'Discrepancy Threshold: ' + str(discrepancy) + '\n'
        string = string + 'Discrepancy Window: ' + str(dynamic_window) + '\n'
        string = string + 'Stationary Samples Number: ' + str(dynamic_after_stationary_number_of_samples)
    else:
        string = string + 'Simulation is static. Parameters:' + '\n'
        string = string + 'Drop Window: ' + str(drop_window) + '\n\n'
        string = string + 'Number of Signals: ' + str(number_of_samples)
    return string


def makeResult():
    d = {'time': [0]}
    a = pd.DataFrame(d)
    b = pd.DataFrame(d)
    return a, b

go(arrival_rate, array_of_departure_rates, array_of_queue_lengths, finish_drop_window, isdynamic, discrepancy, dynamic_window, \
       number_of_samples, dynamic_after_stationary_number_of_samples)
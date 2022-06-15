import time
import warnings
import pandas as pd

from Modules.Update_Node import *
from Modules.Updatge_Generator import *
from Modules.Update_Last_Node import *
from Modules.Next_Event import *
from Modules.Dynamic import *
from Modules.Static import *

warnings.filterwarnings("ignore")


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

    temp_col_for_probabilities = []
    for i in range(1, lenmus + 1):
        n = queue_lenghts[i]
        for j in range(n + 2):
            temp_col_for_probabilities.append('pi_' + str(i) + '_' + str(j))
    probabilities = pd.DataFrame(columns=temp_col_for_probabilities)

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
                data, node_states, node_queue_states, upcoming_event_times, current_innode_signal_index = updateLastNode(data, t, node_event, intensivities, queue_lenghts,
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
                stationary, probabilities = isStationary(node_state_dataframe, probabilities, \
                                                              discrepancy, dynamic_window, lenmus, queue_lenghts, iterator)
                if (stationary):
                    dynamic = False
                    unstationary_data = finished.sort_index()
                    finished = finished.drop(finished[finished.index < max(finished.index)].index)
                    last_unstationary_index = max(unstationary_data.index)
                    print("Stationary State detected. Starting static simulation.")

        iterator = iterator + 1

    simulation_duration = round(time.time() - simulation_start_time)
    print("Simulation duration: " + str(simulation_duration) + " seconds")
    finished = pd.concat([finished, data])
    return finished, unstationary_data, node_state_dataframe.drop('node_0', axis=1), simulation_duration
import numpy as np

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
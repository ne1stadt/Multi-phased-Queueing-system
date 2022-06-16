import numpy as np


def updateNode(data, t, node_event, intensivities, queue_lenghts, node_states, node_queue_states,
               upcoming_event_times, current_innode_signal_index):
    index_of_signal = current_innode_signal_index[node_event]

    data.loc[index_of_signal, 'node_' + str(node_event) + '_end'] = t
    if node_queue_states[node_event + 1] == queue_lenghts[node_event + 1]:
        # Terminate signal
        data.loc[index_of_signal, 'status'] = 3
    else:
        if node_states[node_event + 1] == 0:
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

    if node_queue_states[node_event] == 0:
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

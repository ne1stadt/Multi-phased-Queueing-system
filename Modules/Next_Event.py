import numpy as np

def nextEvent(node_states, upcoming_event_times):
    array = np.multiply(upcoming_event_times, node_states)
    indexes = np.where(array == 0)
    temp_max = max(array)
    for i in indexes:
        array[i] = temp_max
    new_time = min(array)
    node_event = np.where(upcoming_event_times == new_time)[0][0]

    return new_time, node_event

import numpy as np

def isStationary(node_state_dataframe, probabilities, dynamic_window, lenmus, queue_lenghts):
    probabilities = setNewProbabilities(node_state_dataframe, dynamic_window, probabilities, lenmus, queue_lenghts)

    if len(node_state_dataframe) <= dynamic_window*5:
        print('Need more data for Stationary Check...')
        return False, probabilities
    else:
        std_max = probabilities[-5:].std().max()
        std_mean = probabilities[-5:].std().mean()
        if std_max < 0.02 and std_mean < 0.0125:
            return True, probabilities
        else:
            print([std_mean, std_max])
            return False, probabilities


def setNewProbabilities(node_state_dataframe, dynamic_window, probabilities, lenmus, queue_lenghts):
    max_index = max(node_state_dataframe.index)

    # Create temp array of only last dynamic_window signals
    if (max_index < dynamic_window):
        temp = node_state_dataframe
    else:
        temp = node_state_dataframe.drop(node_state_dataframe[node_state_dataframe.index < max_index - dynamic_window].index)

    temp['time'] = (temp - temp.shift(fill_value=0))['time']
    temp = temp[1:]
    full_time = np.sum(temp['time'])

    if (probabilities.empty):
        new_index = 0
    else:
        new_index = max(probabilities.index) + 1

    for i in range(1, lenmus + 1):
        n = queue_lenghts[i]
        for j in range(n + 2):
            # i - number of node
            # j - state
            probabilities.loc[new_index, 'pi_' + str(i) + '_' + str(j)] = np.sum(temp['time'][temp['node_' + str(i)] == j]) / full_time

    return probabilities

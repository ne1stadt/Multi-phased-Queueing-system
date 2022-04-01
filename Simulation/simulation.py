import pandas as pd
import numpy as np
import math
import time
import warnings

warnings.filterwarnings("ignore")


# SIMULATION PARAMETERS
arrival_rate = 1
number_of_arriving_signals = 20000
array_of_mean_service_times = [1.5]*12
queue_length = 6
loggerEnabled = False
writeStatistics = True

def generate_traffic(lam, number_of_samples, number_of_nodes):
    beta = 1/lam
    arr = np.random.exponential(beta, number_of_samples)
    l = len(arr)
    for i in range(1, l):
        arr[i] = arr[i] + arr[i-1]
    d = {'start_time': arr, 'innode': [0]*l, 'inqueue': [0]*l, 'status': [0]*l}
    data = pd.DataFrame(data=d)
    for n in range(1, number_of_nodes+1):
        enter_name = 'node_' + str(n) + '_start'
        data[enter_name] = -1
        end_name = 'node_' + str(n) + '_end'
        data[end_name] = -1
    return data
    
def generate_execution_time(mu, number_of_samples):
    beta = 1/mu
    arr = np.random.exponential(beta, number_of_samples)
    return arr
    
# Status enum table:
# Not Started - 0
# In Queue - 1
# In Progress - 2
# Terminated - 3
# Finished - 4


def go(lam, number_of_samples, mus, queue_length, loggerEnabled, writeStatistics):    
    
    logger = ''
        
    if (loggerEnabled):
        with open("log.txt", "w+") as text_file:
            text_file.truncate(0)
    
    number_of_nodes = len(mus)
    
    data = generate_traffic(lam, number_of_samples, number_of_nodes)
    execution_times = np.array([generate_execution_time(mus[0], number_of_samples)])
    
    print("SIMULATION STARTED!")
    if (loggerEnabled):
        logger = logger + "SIMULATION STARTED!\n"
    
    if (number_of_nodes > 1):
        for i in range(1, number_of_nodes):
            execution_times = np.vstack([execution_times, generate_execution_time(mus[i], number_of_samples)])
    
    t = 0
    iterations = 0
    simulation_start_time = time.time()
    
    while (ProcessIsNotFinished(data)):
        data, templog = UpdateIncome(data, t, queue_length)
        if (loggerEnabled):
            logger = logger + templog
        for n in range(1, number_of_nodes+1):
            data, execution_times[n-1], templog = UpdateNode(data, t, n, execution_times[n-1], queue_length, number_of_nodes)
            if (loggerEnabled):
                logger = logger + templog
        for n in range(1, number_of_nodes+1): 
            data, templog = UpdateQueue(data, t, n)    
            if (loggerEnabled):
                logger = logger + templog            
        
        PrintProgress(data, number_of_samples)
        
        t_new = UpdateTime(data, lam, execution_times, t, number_of_nodes)
        if (loggerEnabled):
            logger = logger + "-----------------------\n" + "Time update: " + str(t_new) + "\n"
            
        if (iterations % 100 == 0):
            if (loggerEnabled):
                with open("log.txt", "a") as text_file:
                    text_file.write(logger)
            logger = ''
        
        iterations = iterations + 1
        if (t == t_new):
            return data
        else:
            t = t_new
    
    print("-----------------------")
    print("-----------------------")
    print("SIMULATION FINISHED SUCCESSFULLY!")
    print("-----------------------")
    print("Arrival Rate: " + str(lam))
    if (loggerEnabled):
        logger = logger + "-----------------------\n-----------------------\nSIMULATION FINISHED SUCCESSFULLY!\n-----------------------\n" + "Arrival Rate: " + str(lam) + "\n"
    service_times = str(mus[0])
    for i in range(1, number_of_nodes):
        service_times = service_times + ', ' + str(mus[i])
    print(str(number_of_nodes) + " Nodes with respective mean service times: " + service_times)
    print("Number of iterations: " + str(iterations))
    if (loggerEnabled):
        logger = logger + str(number_of_nodes) + " Nodes with respective mean service times: " + service_times + "\nNumber of iterations: " + str(iterations) + "\n"
    simulation_duration = round(time.time() - simulation_start_time)
    print("Simulation duration: " + str(simulation_duration) + " seconds")
    print("-----------------------")
    print()
    if (loggerEnabled):
        logger = logger + "Simulation duration: " + str(simulation_duration) + " seconds\n" + "-----------------------\n\n"
    
    PrintStatistics(data, number_of_samples, number_of_nodes, writeStatistics)
    
    if (loggerEnabled):
        with open("log.txt", "a") as text_file:
            text_file.write(logger)

    return data
    
def UpdateIncome(data, t, queue_length):
    indexes = data[data['status'] == 0][data['start_time'] <= t].index
    templog = ''
    if (indexes.empty):
        return data, templog
    else:
        for i in indexes:
            if (ifQueueFull(data, 1, queue_length)):
                data.loc[i, 'status'] = 3
                if (loggerEnabled):
                    templog = templog + "Signal " + str(i) + " was terminated\n"
            else:
                data.loc[i, 'innode'] = 1
                data.loc[i, 'inqueue'] = getQueueLength(data, 1) + 1
                data.loc[i, 'status'] = 1
                if (loggerEnabled):
                    templog = templog + "Signal " + str(i) + " started and moved to Node 1 with queue number " + str(data.loc[i, 'inqueue'].item()) + "\n"
        return data, templog

def UpdateNode(data, t, n, execution_times, queue_length, number_of_nodes):
    upcoming_execution_time_index = getFirstNonNegativeNumberIndex(execution_times)
    upcoming_execution_time = execution_times[upcoming_execution_time_index]
    index = data[data['status'] == 2][data['innode'] == n].index
    templog = ''
    if (index.empty):
        return data, execution_times, templog
    elif (data.loc[index[0], 'node_' + str(n) + '_start'] + upcoming_execution_time > t):
        return data, execution_times, templog
    else:
        if (n == number_of_nodes):
            data.loc[index, 'status'] = 4
            data.loc[index, 'node_' + str(n) + '_end'] = t
            if (loggerEnabled):
                templog = templog + "Signal " + str(index[0]) + " has finished.\n"
        else:
            if (ifQueueFull(data, n+1, queue_length)):
                data.loc[index, 'status'] = 3
                data.loc[index, 'node_' + str(n) + '_end'] = t
                if (loggerEnabled):
                    templog = templog + "Signal " + str(index) + " was terminated\n"
            else:
                data.loc[index, 'innode'] = n + 1
                data.loc[index, 'inqueue'] = getQueueLength(data, n+1) + 1
                data.loc[index, 'status'] = 1
                data.loc[index, 'node_' + str(n) + '_end'] = t
                if (loggerEnabled):
                    templog = templog + "Signal " + str(index[0]) + " ended and moved to Node " + str(n + 1) + " with queue number " + str(data.loc[index, 'inqueue'].item()) + "\n"
        execution_times[upcoming_execution_time_index] = -1
        return data, execution_times, templog
    
def UpdateQueue(data, t, n):
    templog = ''
    if (data[data['innode'] == n][data['status'] == 2].empty):
        if (data[data['innode'] == n][data['status'] == 1].empty):
            return data, templog
        else: 
            increment = min(data[data['innode'] == n][data['status'] == 1]['inqueue'].values)
        
            index_of_first = data[data['innode'] == n][data['status'] == 1][data['inqueue'] == increment].index[0]
            data.loc[index_of_first, 'inqueue'] = 0
            data.loc[index_of_first, 'status'] = 2
            data.loc[index_of_first, 'node_' + str(n) + '_start'] = t
            if (loggerEnabled):
                templog = templog + "Signal " + str(index_of_first) + " started Progress on Node " + str(data.loc[index_of_first, 'innode'].item()) + "\n"

            other_indexes = data[data['innode'] == n][data['status'] == 1].index
            for i in other_indexes:
                previous = data.loc[i, 'inqueue'].item()
                data.loc[i, 'inqueue'] = previous - increment
                if (loggerEnabled):
                    templog = templog + "Signal " + str(i) + " reached queue number " + str(previous - increment) + " on Node " + str(n) + "\n"
            return data, templog
    else:
        return data, templog
        
def UpdateTime(data, lam, execution_times, t, number_of_nodes):
    if (data[data['status'] == 0].empty):
        answer = t + (1/lam)
    else:
        answer = data[data['status'] == 0]['start_time'].values[0]
    
    if (t > answer):
        print("Non-iterable process exception")
        return 0
    
    for n in range(1, number_of_nodes+1):
        execution_time = execution_times[n-1]
        upcoming_execution_time = execution_time[getFirstNonNegativeNumberIndex(execution_time)]
        skipper = False
        if (data[data['innode'] == n][data['status'] == 2].empty):
            skipper = True
        else:
            upcoming_signal_time = data[data['innode'] == n][data['status'] == 2]['node_' + str(n) + '_start'].item()
    
        if (skipper == False):
            if (upcoming_execution_time + upcoming_signal_time <= answer):
                answer = upcoming_execution_time + upcoming_signal_time
        else:
            skipper = False
    return answer
    
def ProcessIsNotFinished(data):
    statuses = pd.unique(data['status'])
    if ((0 in statuses) or (2 in statuses) or (1 in statuses)):
        return True
    else:
        return False
        
def ifQueueFull(data, n, queue_length):
    if (getQueueLength(data, n) == queue_length):
        return True
    else:
        return False
    
def getQueueLength(data, n):
    if (data[data['innode'] == n][data['status'] == 1].empty):
        return 0
    else:
        return max(data[data['innode'] == n][data['status'] == 1]['inqueue'].values)
    
def getFirstNonNegativeNumberIndex(arr):
    l = len(arr)
    for i in range(l):
        if (arr[i] >= 0):
            return i
        
def PrintProgress(data, number_of_samples):
    a = len(data[data['status'] == 4])
    b = len(data[data['status'] == 3])
    pr = round((a+b)*100/number_of_samples, 1)
    print('Progress: ' + str(pr) + '%')
    return 0

def PrintStatistics(data, number_of_samples, number_of_nodes, writeStatistics):
    stat = ""
    print('TERMINATION RATE:')
    print('Note that signal is considered terminated in Node k if it finished Node k and didn\'t fit in node k+1')
    print('So last Node Termination Rate is Always 0%')
    termination_rate = len(data[data['status'] == 3][data['innode'] == 0])*100/number_of_samples
    print('Not Started Termination Rate: ' + str(termination_rate) + '%')
    stat = stat + 'TERMINATION RATE:\n' + 'Note that signal is considered terminated in Node k if it finished Node k and didn\'t fit in node k+1\n' + 'So last Node Termination Rate is Always 0%\n'
    stat = stat + 'Not Started Termination Rate: ' + str(termination_rate) + '%\n'
    if (number_of_nodes > 1):
        for i in range(1, number_of_nodes):
            node_termination_rate = len(data[data['status'] == 3][data['innode'] == i])*100/number_of_samples
            print('Node ' + str(i) + ' Termination Rate: ' + str(node_termination_rate) + '%')
            stat = stat + 'Node ' + str(i) + ' Termination Rate: ' + str(node_termination_rate) + '%\n'
            termination_rate = termination_rate + node_termination_rate
    print('Total Termination Rate: ' + str(termination_rate) + '%')
    print()
    stat = stat + 'Total Termination Rate: ' + str(termination_rate) + '%\n\n'
    
    print('AVERAGE NODE TIME:')
    stat = stat + 'AVERAGE NODE TIME:\n'
    temp = data[data['innode'] > 0]
    temp['node_queue_time'] = temp['node_1_start'] - temp['start_time']
    temp['innode_time'] = temp['node_1_end'] - temp['start_time']
    avg_node_queue_time = np.average(temp['node_queue_time'])
    avg_innode_time = np.average(temp['innode_time'])
    print('Average Queue Time in Node 1: ' + str(avg_node_queue_time))
    print('Average Full Time in Node 1: ' + str(avg_innode_time))
    stat = stat + 'Average Queue Time in Node 1: ' + str(avg_node_queue_time) + "\n" + 'Average Full Time in Node 1: ' + str(avg_innode_time) + "\n"
    if (number_of_nodes > 1):
        for i in range(2, number_of_nodes + 1):
            temp = data[data['innode'] > i-1]
            temp['node_queue_time'] = temp['node_' + str(i) + '_start'] - temp['node_' + str(i-1) + '_end']
            temp['innode_time'] = temp['node_' + str(i) + '_end'] - temp['node_' + str(i-1) + '_end']
            avg_node_queue_time = np.average(temp['node_queue_time'])
            avg_innode_time = np.average(temp['innode_time'])
            print('Average Queue Time in Node ' + str(i) + ': ' + str(avg_node_queue_time))
            print('Average Full Time in Node ' + str(i) + ': ' + str(avg_innode_time))
            stat = stat + 'Average Queue Time in Node ' + str(i) + ': ' + str(avg_node_queue_time) + "\n" + 'Average Full Time in Node ' + str(i) + ': ' + str(avg_innode_time) + "\n"
    temp = data[data['status'] == 4]
    temp['full_time'] = temp['node_' + str(number_of_nodes) + '_end'] - temp['start_time']
    system_successful_time = np.average(temp['full_time'])
    print('Average Signal in System time (only Finished): ' + str(system_successful_time))
    stat = stat + 'Average Signal in System time (only Finished): ' + str(system_successful_time) + "\n"
    
    if (writeStatistics):
        with open("statistics.txt", "w+") as text_file:
            text_file.truncate(0)
            text_file.write(stat)
            

# 1 - lambda
# 2 - number of samples
# 3 - array of mus
# 4 - queue length
# 5 - create log file
# 6 - create statistics file

data = go(arrival_rate, number_of_arriving_signals, array_of_mean_service_times, queue_length, loggerEnabled, writeStatistics)

data.to_csv('simulation.csv', index = False)
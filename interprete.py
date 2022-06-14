import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
#import matplotlib.pyplot as plt


# THIS IS ONLY APPLICABLE FOR SIMPLE CASE OF ALL NODES HAVING SAME MU's AND SAME QUEUE LENGTHS


PATH = r'C:\Users\koni0321\PycharmProjects\Multi-phased-Queueing-system\RUNS\RUN_rho0.5_n1'

data = pd.read_csv(PATH + r'\final.csv')
data = data[:10000]
states = pd.read_csv(PATH + r'\node_states.csv')
n = 1
rho = 0.5
mu = 1
lambd = mu*rho

m = len(states.columns) - 1
stationary_states = states[len(states) - len(data)*m*n:]

temp_arr = stationary_states
temp_arr['time'] = (stationary_states - stationary_states.shift(fill_value=0))['time']
temp_arr = temp_arr[1:]
temp_arr['system'] = temp_arr['node_1']
for i in range(2, m+1):
    temp_arr['system'] = temp_arr['system'] + temp_arr['node_' + str(i)]
full_time = sum(temp_arr['time'])


# Probabilities
sim_probabilities = pd.DataFrame(columns = stationary_states.columns[1:])
for i in range(m):
    for j in range(n+2):
        exact_temp_states = temp_arr[temp_arr['node_' + str(i + 1)] == j]
        sim_probabilities.loc[j, 'node_' + str(i+1)] = np.sum(exact_temp_states['time']) / full_time

# Other Parameters
sim_stats = pd.DataFrame(columns = sim_probabilities.columns)

# Avg Node State - 0
sim_stats.loc[0, 'Parameter'] = 'Avg Node State'
for i in range(m):
    sim_stats.loc[0, 'node_' + str(i+1)] = np.dot(sim_probabilities['node_' + str(i+1)], range(n+2))
sim_stats.loc[0, 'system'] = np.dot(temp_arr['system'], temp_arr['time'])/full_time

# P Loss - 1
sim_stats.loc[1, 'Parameter'] = 'P Loss'
for i in range(m):
    sim_stats.loc[1, 'node_' + str(i+1)] = len(data[data['innode'] == i])/len(data[data['innode'] >= i])
sim_stats.loc[1, 'system'] = len(data[data['status'] == 3])/len(data)

# Queue Wait - 2
sim_stats.loc[2, 'Parameter'] = 'Queue Wait'
sim_stats.loc[2, 'node_1'] = np.average(data[data['innode'] >= 1]['node_1_startprogress'] - data[data['innode'] >= 1]['start_time'])
for i in range(1, m):
    sim_stats.loc[2, 'node_' + str(i+1)] = np.average(data[data['innode'] >= i+1]['node_' + str(i+1) + '_startprogress'] - data[data['innode'] >= i+1]['node_' + str(i) + '_end'])

# Full Wait - 3
sim_stats.loc[3, 'Parameter'] = 'Full Wait'
sim_stats.loc[3, 'node_1'] = np.average(data[data['innode'] >= 1]['node_1_end'] - data[data['innode'] >= 1]['start_time'])
for i in range(1, m):
    sim_stats.loc[3, 'node_' + str(i+1)] = np.average(data[data['innode'] >= i+1]['node_' + str(i+1) + '_end'] - data[data['innode'] >= i+1]['node_' + str(i) + '_end'])

# Full Wait - 4
sim_stats.loc[4, 'Parameter'] = 'Full Wait w Termination'
indexes = data.index
for index in indexes:
    innode = round(data.loc[index, 'innode'])
    if (innode == 0):
        data.loc[index, 'full_time'] = 0
    else:
        data.loc[index, 'full_time'] = data.loc[index, 'node_' + str(innode) + '_end'] - data.loc[index, 'start_time']
sim_stats.loc[4, 'system'] = np.average(data['full_time'])




# ANALYTICAL PART
an_probabilities = pd.DataFrame(columns = sim_probabilities.columns)
an_stats = pd.DataFrame(columns = sim_stats.columns)
an_stats.loc[0, 'Parameter'] = 'Avg Node State'
an_stats.loc[1, 'Parameter'] = 'P Loss'
an_stats.loc[2, 'Parameter'] = 'Queue Wait'
an_stats.loc[3, 'Parameter'] = 'Full Wait'
an_stats.loc[4, 'Parameter'] = 'Full Wait w Termination'

par_lambd = lambd
par_rho = rho
par_phi = 0

for node in range(1, m+1):
    for j in range(n + 2):
        an_probabilities.loc[j, 'node_' + str(node)] = (par_rho**(j))*(1-par_rho)/(1-(par_rho**(n+1)))
    an_stats.loc[0, 'node_' + str(node)] = np.dot(an_probabilities['node_' + str(node)], range(n + 2))
    an_stats.loc[1, 'node_' + str(node)] = par_rho**(n)*(1-par_rho)/(1-(par_rho**(n+1)))
    an_stats.loc[2, 'node_' + str(node)] = (1 - an_probabilities.loc[0, 'node_' + str(node)])/(m*mu*(1-par_rho))
    an_stats.loc[3, 'node_' + str(node)] = an_stats.loc[2, 'node_' + str(node)] + 1/mu

    par_lambd = par_lambd*(np.cosh(par_phi)**2) - mu*(np.sinh(par_phi)**2)
    par_rho = par_lambd/mu
    par_phi = np.arctanh(par_rho**((n+1)/2))


with pd.ExcelWriter(PATH + r'\RESULT.xlsx') as writer:
    sim_probabilities.to_excel(writer, sheet_name='sim_probabilities')
    sim_stats.to_excel(writer, sheet_name='sim_stats')
    an_probabilities.to_excel(writer, sheet_name='an_probabilities')
    an_stats.to_excel(writer, sheet_name='an_stats')
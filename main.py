from Modules.Go import go
from Modules.Write_Simulation import writeSimulation
from simulation_grid import get_parameters_by_grid_number
import time

GRID_NUMBER = 1                                                                     # PARAMETERS FOR CHANGE
PATH = r'C:\Users\koni0321\PycharmProjects\Multi-phased-Queueing-system'            # PARAMETERS FOR CHANGE

grid_rho, grid_n = get_parameters_by_grid_number(GRID_NUMBER)

number_of_nodes = 8

iteration_ansamble = 1
grid_start_time = time.time()
for rho in grid_rho:
    for n in grid_n:
        print('GRID: rho = ' + str(round(rho, 2)) + ', n = ' + str(n) + ' (simulation ' + str(iteration_ansamble) + ' of 18)')
        finished, unstationary_data, node_state_dataframe, simulation_duration = go(rho, [1]*number_of_nodes, [n]*number_of_nodes, 30, True, 10000, 10000)
        writeSimulation(finished, unstationary_data, node_state_dataframe, rho, [1]*number_of_nodes, [n]*number_of_nodes, 30, True, 10000, 10000, 10000, simulation_duration, PATH)

        print('Finished Simulations: ' + str(iteration_ansamble) + ' out of ' + str(18))
        iteration_ansamble = iteration_ansamble + 1

with open(PATH + "/RUNS/grid" + str(GRID_NUMBER) + "_configuration.txt", "w+") as text_file:
    text = 'GRID ' + str(GRID_NUMBER) + ' Configuration: ' + '\n'
    text = text + 'rho from ' + str(round(grid_rho[0], 2)) + ' to ' + str(round(grid_rho[-1], 2)) + ' with step 0.1' + '\n'
    text = text + 'queue number from ' + str(grid_n[0]) + ' to ' + str(grid_n[-1]) + ' with step 1' + '\n'
    text = text + 'grid duration: ' + str(round(time.time() - grid_start_time))
    text_file.write(text)
from Modules.Go import go
from Modules.Write_Simulation import writeSimulation

#rho = 1
number_of_nodes = 5
#while (rho <= 2):
#    for queue in range(1, 7):
#        print('GRID: rho = ' + str(rho) + ', queue = ' + str(queue))
#        arrival_rate = rho
#        array_of_departure_rates = [1]*number_of_nodes
#        array_of_queue_lengths = [queue]*number_of_nodes
#        finish_drop_window = 20
#        isdynamic = True
#        discrepancy = 0.05
#        overd2 = round(1/discrepancy**2)
#        #dynamic_window = number_of_nodes*(queue + 1)*overd2/4
#        dynamic_window = 5000
#        print(dynamic_window)
#        number_of_samples = 10000
#        dynamic_after_stationary_number_of_samples = 10000
#        finished, unstationary_data, node_state_dataframe, simulation_duration = go(arrival_rate, array_of_departure_rates, array_of_queue_lengths,
#                                                                                    finish_drop_window, isdynamic, discrepancy, dynamic_window,
#                                                                                    number_of_samples, dynamic_after_stationary_number_of_samples)
#        writeSimulation(finished, unstationary_data, node_state_dataframe, arrival_rate, array_of_departure_rates,
#                           array_of_queue_lengths, finish_drop_window, isdynamic, discrepancy, dynamic_window, number_of_samples,
#                           dynamic_after_stationary_number_of_samples, simulation_duration)
#    rho = rho + 0.2

for rho in range(0.2, 2, 0.2):
    arrival_rate = rho
    array_of_departure_rates = [1] * number_of_nodes
    array_of_queue_lengths = [4] * number_of_nodes
    finish_drop_window = 30
    isdynamic = False
    discrepancy = 0.05
    overd2 = round(1 / discrepancy ** 2)
    dynamic_window = number_of_nodes*(queue + 1)*overd2/4

    number_of_samples = 30000
    dynamic_after_stationary_number_of_samples = 10
    finished, unstationary_data, node_state_dataframe, simulation_duration = go(arrival_rate, array_of_departure_rates,
                                                                                array_of_queue_lengths,
                                                                                finish_drop_window, isdynamic, discrepancy,
                                                                                dynamic_window,
                                                                                number_of_samples,
                                                                                dynamic_after_stationary_number_of_samples)
    writeSimulation(finished, unstationary_data, node_state_dataframe, arrival_rate, array_of_departure_rates,
                    array_of_queue_lengths, finish_drop_window, isdynamic, discrepancy, dynamic_window, number_of_samples,
                    dynamic_after_stationary_number_of_samples, simulation_duration)
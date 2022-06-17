import numpy as np

def get_parameters_by_grid_number(grid_number):
    if grid_number == 1:
        grid_rho = np.arange(0.2, 0.8, 0.1)
        grid_n = range(1, 4, 1)
    elif grid_number == 2:
        grid_rho = np.arange(0.8, 1.4, 0.1)
        grid_n = range(1, 4, 1)
    elif grid_number == 3:
        grid_rho = np.arange(1.4, 2.0, 0.1)
        grid_n = range(1, 4, 1)
    elif grid_number == 4:
        grid_rho = np.arange(0.2, 0.8, 0.1)
        grid_n = range(4, 7, 1)
    elif grid_number == 5:
        grid_rho = np.arange(0.8, 1.4, 0.1)
        grid_n = range(4, 7, 1)
    elif grid_number == 6:
        grid_rho = np.arange(1.4, 2.0, 0.1)
        grid_n = range(4, 7, 1)
    elif grid_number == 7:
        grid_rho = np.arange(0.2, 0.8, 0.1)
        grid_n = range(7, 10, 1)
    elif grid_number == 8:
        grid_rho = np.arange(0.8, 1.4, 0.1)
        grid_n = range(7, 10, 1)
    elif grid_number == 9:
        grid_rho = np.arange(1.4, 2.0, 0.1)
        grid_n = range(7, 10, 1)
    else:
        print('WRONG GRID NUMBER!')
        return False, False

    return grid_rho, grid_n

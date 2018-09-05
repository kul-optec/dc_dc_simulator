import numpy as np
import datetime
from math import *

# defining as global
state_variables = []
output = []
independent_sources = []
matrices = []
particular_solution = []
eigenvalues = []
coeffs = []
time = []

COUNTER = 5000

def simulate(beginning_state, system, controller, simulation_time, TIME_STEP_POINTS, file_name):
    print 
    print("Starting simulation ... ")
    start = datetime.datetime.now()
    global state_variables, output, independent_sources, time
    global matrices
	
    npy_file = open(file_name, 'wb')	
    
    state = beginning_state
    independent_sources = np.array(system.get_source_values())
    
    time = np.array([0 for dummy in range(COUNTER)], dtype=float)
    state_variables = np.array([[0 for dummy in range(COUNTER)] for dummy in range(system.get_number_state_variables())], dtype=float)
    output = np.array([[0 for dummy in range(COUNTER)] for dummy in range(system.get_number_outputs())], dtype=float)

    step = controller.get_period() / TIME_STEP_POINTS
    
    counter = 0
    time[counter] = 0 # setting start time t0 = 0
    state_variables[:,0] = system.get_initial_values() # initial value
	# beginning:
    get_state_parameters(state, counter)
    output[:,0] = np.matmul(matrices[2],state_variables[:,counter]) + np.matmul(matrices[3],independent_sources)
    controller.take_output(output[:,0])
    controller.calculate_current_duty_ratio()

    if controller.get_duty_ratio() == 0:
        state = state.change_state_controller(controller.get_switches())
        print(time[counter], str(state))
        get_state_parameters(state)

	# solve ODEs for the first value
    counter += 1
    time[counter] = time[counter-1] + step
    solve_step(time[counter], counter)
    
    
    while(time[counter] <= simulation_time):
        counter += 1
        time[counter] = time[counter-1] + step
        solve_step(time[counter], counter)
        
		# empty matrices for faster calculation, writing in file	
        if (counter >= COUNTER - 1):
            if (time[0] > 0):
                np.save(npy_file, np.row_stack((time[1:counter],state_variables[:,1:counter])))
            else:
                np.save(npy_file, np.row_stack((time[0:counter],state_variables[:,0:counter])))
            state_variables[:,0] = state_variables[:,counter]
            time[0] = time[counter]
            counter = 0
            print("Part of data stored. Elpased " + str(datetime.datetime.now() - start))

		# checking for the state change
        if (counter > 0):
            help_state = state.change_state_internally(state_variables[:,counter-1:counter+1])
        else:
            help_state = state.change_state_internally(state_variables[:,counter-2:COUNTER])
            
        if help_state != None:
            counter -= 1
            new_time = state.new_time(help_state, time[counter], state_variables[:,counter], independent_sources)
            while new_time > 0:
                counter += 1
                time[counter] = new_time
                solve_step(time[counter], counter)                
                new_time = state.new_time(help_state, time[counter], state_variables[:,counter], independent_sources)
                
                if (counter >= COUNTER - 1):
                    if (time[0] > 0):
                        np.save(npy_file, np.row_stack((time[1:counter],state_variables[:,1:counter])))
                    else:
                        np.save(npy_file, np.row_stack((time[0:counter],state_variables[:,0:counter])))
                    state_variables[:,0] = state_variables[:,counter]
                    time[0] = time[counter]
                    counter = 0
                    print("Part of data stored. Elpased " + str(datetime.datetime.now() - start))
                
            state = help_state
            get_state_parameters(state, counter)
        elif controller.check_change(time[counter], step):	
            time_change = controller.change_time(time[counter])
            if (round(time[counter], 9) != round(time_change, 9)):
                counter += 1
                time[counter] = time_change
                solve_step(time[counter], counter)
                
            if controller.is_period(time[counter], step):
                controller.calculate_period(output[:,counter])
                if controller.get_duty_ratio() != 0:
                    state = beginning_state
                else:
                    state = beginning_state.change_state_controller(controller.get_switches())
            else:
                state = state.change_state_controller(controller.get_switches())

            get_state_parameters(state, counter)
			
		# empty matrices for faster calculation, writing in file	
        if (counter >= COUNTER - 1):
            if (time[0] > 0):
                np.save(npy_file, np.row_stack((time[1:counter],state_variables[:,1:counter])))
            else:
                np.save(npy_file, np.row_stack((time[0:counter],state_variables[:,0:counter])))
            state_variables[:,0] = state_variables[:,counter]
            time[0] = time[counter]
            counter = 0
            print("Part of data stored. Elpased " + str(datetime.datetime.now() - start))
	
    end = datetime.datetime.now()
    
    print("Simulation ended. Execution time is: %s" % (end - start))
    print
    print("Saving data in files state_variables.npy...")
    	
    if counter > 0:
        if (time[0] > 0):
            np.save(npy_file, np.row_stack((time[1:counter],state_variables[:,1:counter])))
        else:
            np.save(npy_file, np.row_stack((time[0:counter],state_variables[:,0:counter])))
		
    npy_file.close()
    
    print("Data saved.")
    print
    print("To plot data run program plot_diagrams.py.")
    	
    #controller.printing()


# gets particular solution
def get_particular_solution(last_value, matrix_A, matrix_B):
    global independent_sources
    
#    if np.linalg.det(matrix_A)  == 0:
#        pass
    particular_solution =-np.matmul(np.matmul(np.linalg.pinv(matrix_A), matrix_B), independent_sources)
    return particular_solution

def get_homogeneous_solution_coeffs(time, last_value, matrix_A, matrix_B):
    """
    get coefficients for homogeneous solution
    """
    global independent_sources
    
    number_eigvals = len(eigenvalues)
    size_A = len(matrix_A)
    M = np.array([[0 for dummy in range(size_A * number_eigvals)] for dummy in range(size_A * number_eigvals)],dtype=complex)
    x = np.array([0 for dummy in range(size_A * number_eigvals)],dtype=complex)
    for dummy_i in range(number_eigvals):
        for dummy_j in range(0, len(eigenvalues)):
            M[dummy_i * size_A : (dummy_i + 1) * size_A, dummy_j*size_A:(dummy_j+1)*size_A] = \
            np.eye(size_A) * eigenvalues[dummy_j]**dummy_i * np.exp(eigenvalues[dummy_j] * time)

    x[:size_A] = last_value - particular_solution
    for dummy in range(1, number_eigvals):
        x[dummy*size_A:(dummy+1)*size_A] = np.matmul(np.linalg.matrix_power(matrix_A, dummy), last_value) + \
            np.matmul(np.linalg.matrix_power(matrix_A, dummy - 1), np.matmul(matrix_B,independent_sources))

#    x = -np.matmul(np.linalg.pinv(M), x) 
    x = np.linalg.tensorsolve(M, x)                  
    return x

def solve_step(time, counter):
    """
    gets solution of state variables and output at specific time
    """
    global state_variables, output, independent_sources, eigenvalues
    num_eig = len(eigenvalues)
    size_A = len(particular_solution)
    M = np.array([[0 for dummy in range(num_eig*size_A)] for dummy in range(size_A)],dtype=complex)
    for dummy in range(num_eig):
        M[:,dummy*size_A:(dummy+1)*size_A] = np.eye(size_A) * np.exp(eigenvalues[dummy] * time)

    solution = (np.matmul(M,coeffs) + particular_solution) 
    
    state_variables[:,counter] = solution.real
    output[:,counter] = np.matmul(matrices[2],solution.real) + np.matmul(matrices[3],independent_sources)


# gets state matrices
def get_state_parameters(state, counter):
	global eigenvalues, particular_solution, coeffs, matrices
	matrices = state.get_matrices()
	eigenvalues = state.get_eigenvalues()
	particular_solution = get_particular_solution(state_variables[:,counter], matrices[0], matrices[1])
	coeffs = get_homogeneous_solution_coeffs(time[counter], state_variables[:,counter], matrices[0], matrices[1])


	

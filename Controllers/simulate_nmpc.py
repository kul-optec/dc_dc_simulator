from .nmpc_codegen.src_python import *
from .nmpc_codegen.src_python import tools
from .nmpc_codegen.src_python import models
from .nmpc_codegen.src_python import controller
from .nmpc_codegen.src_python import Cfunctions
from .nmpc_codegen.src_python.controller import constraints
from .nmpc_codegen.src_python.models.dc_dc import *

from pylab import *
from math import *
import sympy
import numpy as np
import datetime
import casadi as cd

dictionary = {0 : '', 3 : '\mbox{m}', 6 : '\mu', 9 : '\mbox{n}', 12 : '\mbox{p}'}


# defining as global
state_variables = []
output = []
independent_sources = []
matrices = []

time = []

def simulate(model, simulation_time, number_steps, duty_ratio, frequency, file_name, log_file_name):
    num_subsystems = model.get_state_number()
    
    A = []
    b = []
    list_dcm = []
    
    state = model.get_beginning_state()
    states = []
    
    while not (state in states):
        states.append(state)
        A.append(state.get_matrices_cd_index(1))
        b.append(state.get_matrices_cd_index(2))
        for dcm in state.get_dcm():
            if not (dcm in list_dcm):
                list_dcm.append([dcm, len(A)-1]) 
        
        states_new = state.get_next_states()
        if all(len(state_new.get_dcm()) == 0 for state_new in states_new):
            state = states_new[0]
        else:
            i = 0
            while(len(states_new[i].get_dcm()) == 0):
                i += 1
            state = states_new[i]
            
                
    num_states = A[0].size1()
    num_inputs = len(A) - 1
    
    # Q and R matrixes 
    Q = np.diag([1. for i in range(num_states)])
    R = np.diag([0.1 for dummy in range(num_inputs)])
    Q_terminal = Q #np.array([[2.0767,0.9497], [0.9497,1.8396]])
    R_terminal = np.diag([0 for dummy in range(num_inputs)])
    
    mpc_controller = prepare_model(A, b, num_subsystems, num_states, frequency, num_inputs+1, Q, R, Q_terminal, R_terminal)

    mpc_controller.horizon = 2                  # NMPC parameter
    mpc_controller.integrator_casadi = False    # optional  feature that can generate the integrating used  in the cost function
    mpc_controller.panoc_max_steps = 250        # the maximum amount of iterations the PANOC algorithm is allowed to do.
    mpc_controller.min_residual = -3
    
    # adding the constraints on state variables
    for dcm in list_dcm:
        mpc_controller.add_constraint(constraints.State_variable_constraint(dcm[0][1], dcm[0][2], dcm[1]))

    # generate the dynamic code
    mpc_controller.generate_code()
      
    # simulate everything
    initial_state = np.array([0 for i in range(num_states)])
    reference_state = model.steady_state(duty_ratio, 'CCM')
    reference_input = np.array(duty_ratio)
    delta = model.delta_steady_state(duty_ratio, 1/frequency, reference_state) 
    
    weights = [10. for dummy in range(len(list_dcm))]

    state_history, log_history = simulate_mpc(mpc_controller, initial_state, number_steps, \
                                 reference_state-delta, reference_input, weights, simulation_time)

    npy_file = open(file_name, 'wb')	
    np.save(npy_file, state_history)
    npy_file.close()
    
    log_file = open(log_file_name, 'w')
    for i in range(0,np.shape(log_history)[1]):
        file_string = str(log_history[0,i]) + "," + str(log_history[1,i]) + "," + str(log_history[2,i]) + "," + str(log_history[3,i]) + "\n"
        log_file.write(file_string)
    log_file.close()

    plot_log(state_history, log_history, file_name, log_file_name)
    
def prepare_model(A, b, number_subsystems, number_of_states, frequency, \
                  number_of_steps, Q, R, Q_terminal = None, R_terminal = None):
    # generate static files
    controller_output_location =  "./constructed_controller/" + str(datetime.datetime.now().date()) + "_" \
        + str(datetime.datetime.now().hour) + "-" + str(datetime.datetime.now().minute)
    tools.Bootstrapper.bootstrap(controller_output_location, simulation_tools = True)

#    # get example model
    (system_equations, number_of_inputs) = get_model(A, b, number_subsystems)
    integrator = "RK44"  # select a Runga-Kutta  integrator (FE is forward euler)
    constraint_input = Cfunctions.IndicatorBoxFunction([0 for dummy in range(number_of_inputs)], [1 for dummy in range(number_of_inputs)])  # input needs stay within these borders, 0 < dTs < Ts
    model = models.Model_continious(system_equations, constraint_input, number_of_states, \
                                    number_of_inputs, frequency, number_of_steps, integrator)
#
#    # define the control
    stage_cost = controller.Stage_cost_QR(model, Q, R)
    if(Q_terminal is None):
        mpc_controller = controller.Nmpc_panoc(controller_output_location, model, stage_cost)
    else:
        terminal_cost = controller.Stage_cost_QR(model, Q_terminal, R_terminal)
        mpc_controller = controller.Nmpc_panoc(controller_output_location, model, stage_cost, terminal_cost)

    return mpc_controller

def simulate_mpc(mpc_controller, initial_state, number_steps_period, reference_state, reference_input, weights, simulation_time):
    # -- simulate controller --
    number_of_steps = math.ceil(simulation_time / mpc_controller.model.period)
    # setup a simulator to test
    sim = tools.Simulator(mpc_controller.location)
    for i in range(0,len(weights)):
        sim.set_weight_constraint(i, weights[i])


    state = initial_state
    state_history = np.zeros((mpc_controller.model.number_of_states + 1, \
                              number_of_steps * number_steps_period + 1))
    size = number_steps_period // (mpc_controller.model.number_of_inputs + 1)
    time = 0
    
    state_history[0,0] = time
    state_history[1:len(state)+1,0] = state
    
    log_history = np.zeros((4, number_of_steps))

    for i in range(0, number_of_steps):
        result_simulation = sim.simulate_nmpc(state, reference_state, reference_input)
        cost = sim.get_last_buffered_cost()
#        string = "[" + str(i+1) + "/" + str(number_of_steps) + "]: cost = " + str(cost) + ", optimal input = " + str(result_simulation.optimal_input)  \
#            + ", time = " + str(result_simulation.micro_seconds) + ", iterations = " + str(result_simulation.panoc_interations)
#        print(string)
        
        log_history[:,i] = [cost, result_simulation.optimal_input, result_simulation.micro_seconds, result_simulation.panoc_interations]
        
        sum_inp = 0
        for index in range(mpc_controller.model.number_of_inputs):
            inp = result_simulation.optimal_input[index]
            sum_inp += inp
            interval = inp * mpc_controller.model.period / size
            for j in range(1,size+1):
                time += interval
                state = mpc_controller.model.get_next_state_numpy(interval, state, result_simulation.optimal_input[:mpc_controller.model.number_of_inputs], index)
                state_history[:, i*number_steps_period + size * index + j] = \
                np.reshape(np.row_stack((time, state[:])), mpc_controller.model.number_of_states + 1)
            
        interval = (1 - sum_inp) * mpc_controller.model.period / size
        for j in range(1,size+1):
            time += interval
            state = mpc_controller.model.get_next_state_numpy(interval, state, result_simulation.optimal_input[:mpc_controller.model.number_of_inputs], index + 1)            
            state_history[:, i*number_steps_period + size * (index + 1) + j] = \
            np.reshape(np.row_stack((time, state[:])), mpc_controller.model.number_of_states + 1)
        

    print("Final state:") 
    print(state)

    return state_history, log_history

def plot_log(state_history, log_history, file_name, log_file_name):
    plot_data(file_name)
    
    
def plot_data(file_name): 
    npy_file = open(file_name, 'rb')
    m = load(npy_file)
    
    
    while npy_file.read(1):
        
    	try:
    		npy_file.seek(-1, 1)
    		m = column_stack((m,load(npy_file)))
    	except EOFError or IOError:
    		break
        
    npy_file.close()
    
    time_coeff = 10 ** (ceil(log10(1.0 / max(m[0])) / 3) * 3)
    time_min = float(min(m[0]))
    time_max = float(max(m[0]))
    
    close('all')
    
    rc('text', usetex = True)
    rc('text.latex', preamble = r'\usepackage{amsmath}, \usepackage{amsfonts}')
    rc('font', family='serif', weight='normal', style='normal')
    
    figure(1, figsize=(6, 2 * (m.shape[0] - 1)), dpi = 600)
    subplots_adjust(wspace = 0.2, hspace = 0.2)
    
    for i in range(1, m.shape[0]):
    	
        subplot(m.shape[0], 1, i)
        coeff =  10 ** (ceil(log10(1.0 / max(abs(m[i]))) / 3) * 3)
        plot(m[0], m[i], linewidth = 1)
        
        xlim(time_min, time_max)
        m_max = float(max(m[i]))
        m_min = float(min(m[i]))
        delta = 0.2 * float(max([abs(min(m[i])), abs(m_max)]))
        ylim(float(min(m[i]) - delta), float(max(m[i]) + delta))
        y_arange = arange(float(m_min * coeff), (float(m_max + (m_max - m_min) / 8)  * coeff), \
        			float(float(m_max - m_min) * coeff / 4))
        yticks(linspace(float(min(m[i])), float(max(m[i])), 5), ['{:.1f}'.format(value) for value in y_arange])
    
        if i == m.shape[0] - 1:
            t_max = float(max(m[0]))
            t_min = float(min(m[0]))
            time_arange = arange(float(t_min * time_coeff), float((t_max + (t_max - t_min) / 20)  * time_coeff), \
    			float(t_max - t_min) * time_coeff / 10)
            xticks(linspace(time_min, time_max, 11), ['{:.1f}'.format(t) for t in time_arange])
        else:
            t_max = float(max(m[0]))
            t_min = float(min(m[0]))
            xticks(linspace(time_min, time_max, 11), arange(t_min * time_coeff, float(t_max + (t_max - t_min) / 20  * time_coeff), \
    			float((t_max - t_min) * time_coeff / 10)), visible = False)
    	
    	
        if i <= m.shape[0] * 0.5:
            label = sympy.latex('$i_{L' + str(i) + '} \; [ ' + dictionary[log10(coeff)] + '\mbox{A}]$')
            ylabel('$%s$' %label)
            xticks()
        else:
            label = sympy.latex('$v_{C' + str(i - m.shape[0] // 2) + '} \; [' + dictionary[log10(coeff)] + '\mbox{V}]$')
            ylabel('$%s$' %label)
    		
    		
    xlabel(r'$t \; [' + dictionary[log10(time_coeff)] + '\mbox{s}]$')
    fig_name = file_name.split('.npy')[0]
    savefig(fig_name + '.pdf', bbox_inches='tight', dpi = 600) # saving plot in file

    



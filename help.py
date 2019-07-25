from State_model import *
from Controllers import *

file_name = './examples/state_variables.npy'
log_file_name = './examples/log.txt'

model = System()

# SYSTEM DESCRIPTION
model.create_element(Voltage_source(1, 1, 0, 10.0))
model.create_element(Switch(1, 3, 2, 0))
model.create_element(Switch(2, 3, 2, 3))
model.create_element(Inductor(1, 1, 2, 100e-6))
model.create_element(Capacitor(1, 3, 0, 20e-6))
model.create_element(Resistor(1, 3, 0, 4.0))
model.set_control(1, 'on_state')
model.set_control(2, 'off_state')
model.set_output([['node', 3]])
model.initialize()
model.initialise_output()
#controller = Controller_pid.Controller([1], [2],\
#   'pole_zero_matching', [[[2.829e-06,0.02847,61.51], [7.013e-06,1, 0], 14.28]], 50e3)

frequency = 50e3
duty_ratio = [0.3]
simulation_time = 1e-3
TIME_STEP_POINTS = 20

state_space_model = State_space_model(model)
state_space_model.form_states()
state_space_model.form_state_lists()
state_space_model.print_states()


# SIMULATION
#simulate_eig.simulate(state_space_model.get_beginning_state(), model, controller, simulation_time, TIME_STEP_POINTS, file_name)
simulate_nmpc.simulate(state_space_model, simulation_time, TIME_STEP_POINTS, duty_ratio, frequency, file_name, log_file_name)
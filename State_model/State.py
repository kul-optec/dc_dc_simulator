# STATE CLASS CONTAINING ALL INFORMATION ABOUT SUBCIRCUIT
# CONTAINS CORRESPONDING MATRICES A, B, C AND D, EIGENVALUES AND NUMBER OF EIGENVALUES
# CONTAINS LIST OF POSSIBILITIES IN WHICH THIS STATE OCCURS: CONTROL, DICM AND DCVM
# IF DICM OR DCVM, HAS DEFINED INDUCTORS/CAPACITORS WHICH ARE WORKING IN
# DISCONTINUOUS MODE WITH THE SIGN (HAS A LIST WITH NUMBERS PRESENTING INDEXES WITH SIGN
# INDEX INSIDE STATE VARIABLES AND SIGN OF CURRENT DIRECTION INSIDE CUTSET OR VOLTAGE DIRECTION INSIDE LOOP)

# example: il1 - il2 = 0 cause dicm, list that describes that is ['dicm', [1, -2]]

# CONTAINS INFORMATION ABOUT NEXT STATES AS POINTER
# FUNCTION FOR CHECKING IF THE STATE SHOULD BE CHANGED IS change_state

import numpy as np

class State:
    """
    constans all information for one operating state: system matrices, 
    control, possible transitions
    """
    def __init__(self, index, absolute_error = 1e-6):
        self.__index = index
        self.__control_list = []
        self.__next_state = []
        self.__controlled_switches = []
        
        self.__independent_sources = 0

        self.__active_control = None		# different than None for internal control
        self.__absolute_error = absolute_error
        
        self.__A = []
        self.__B = []
        self.__C = []
        self.__D = []
        self.__A_cd = []
        self.__B_cd = []
        self.__C_cd = []
        self.__D_cd = []
        
        np.seterr(all='ignore')

    def __str__(self):
        string = "State is " + bin(self.__index) + " controlled by "

        for control in self.__control_list:
            string += (str(control[0]) + " ")

        string += " next state "
        for state in self.__next_state:
            string += (bin(state.__index) + " ")

        return string	


	# adding information
    def add_control(self, control):
        self.__control_list.append(control)
		
    def add_off_control(self, control_list):
        for control in control_list:
            if control[0] == 'dcvm':
                self.__control_list.append(list(control))


    def add_controlled_switches(self, switches):
        self.__controlled_switches = switches

    def add_matrices(self, A, B, C, D):
        self.__A = A
        self.__B = B
        self.__C = C
        self.__D = D
    
    def add_matrices_cd(self, A, B, C, D):
        self.__A_cd = A
        self.__B_cd = B
        self.__C_cd = C
        self.__D_cd = D

    def add_next_state(self, state):
        self.__next_state.append(state)
        
    def add_independent_sources(self, sources):
        self.__independent_sources = sources

#############################################################################################################################################
	# getting information
    
    def get_index(self):
        return self.__index

    def get_matrices(self):
        return [self.__A, self.__B, self.__C, self.__D]
    
    def get_matrices_index(self, indicator):
        if (indicator == 1):
            return self.__A
        elif (indicator == 2):
            return self.__B * self.__independent_sources
        elif (indicator == 3):
            return self.__C
        else:
            return self.__D
    
    def get_matrices_cd(self):
        return [self.__A_cd, self.__B_cd, self.__C_cd, self.__D_cd]
    
    def get_matrices_cd_index(self, indicator):
        if (indicator == 1):
            return self.__A_cd
        elif (indicator == 2):
            return self.__B_cd
        elif (indicator == 3):
            return self.__C_cd
        else:
            return self.__D_cd

    def get_eigenvalues(self):
        return self.__eigenvalues
		
    def get_control(self):
        return self.__control_list

##############################################################################################################################################
    def get_dcm(self):
        """
        return control methods which cause DCM
        """
        control_list = []
        for control in self.__control_list:
            if (control[0] != 'control'):
                control_list.append(control)
        return control_list
    
    def get_next_states(self):
        """
        return all next states
        """
        return self.__next_state

##############################################################################################################################################
    def calculate_eigenvalues(self):
        """
        initial calculation of eigenvalues
        """
        self.__eigenvalues = []
        dictionary = np.linalg.eig(np.array(self.__A))
        indicator = True
        sum1 = 0
        for i in range(self.__A.shape[0]):
            if all(self.__A[i, j] == 0 for j in range(self.__A.shape[1])):
                indicator = all(self.__B[i,j] for j in range(self.__B.shape[1]))
                if (indicator):
                    sum1 += 1
                
        for val in dictionary[0]:
            if (val != 0):
                self.__eigenvalues.append(complex(val))
            elif (indicator) and (sum1 > 0):
                sum1 -= 1
                self.__eigenvalues.append(complex(val))


    def define_control_value(self, independent_sources):
        """
        definition of the controlling methods for the current state
        """
        result = 0
        for control in self.__control_list:

            if control[0] != 'control':
                for dummy in range(len(control[2])):
					# sum of values of independent sources of interest
                    for element in control[2][dummy]:
                        result += sign(element) * independent_source[abs(element) - 1]	

                    # make vector for multiplying with state variables
                    matrix = [[0 for dummy_2 in range(len(self.__A))]]
                    for element in control[1][dummy]:
                        matrix[0][abs(element) - 1] = np.sign(element)

                control[1] = matrix
                control[2] = result


    def change_state_internally(self, state_variables):
        """
        checking change, used during simulation frequently
        if there exists condition to change state, returns next state
        """
        for state in self.__next_state:
            if state.check_change(state_variables):
                self.__active_control = None
                return state
        return None

    def check_change(self, state_variables):
        """
        checks if internal switching occurs
        """
        for control in self.__control_list:
            if control[0] != 'control':
				# sum of values of state variables of interest in the previous and the current interval of time
                sum1 = np.matmul(control[1], state_variables[:,0])
                sum2 = np.matmul(control[1], state_variables[:,1])

                if (np.sign(sum1 - control[2]) != np.sign(sum2 - control[2])):
                    self.__active_control = control
                    return True	
        return False

	
    def change_state_controller(self, switches):
        """
        check wheather it the change has to be changed externally by controller
        """
        index = self.__index
        for dummy in range(len(switches)):		
            index = index ^ (2**(switches[dummy] - 1))

        for state in self.__next_state:
            if any(control[0] == 'control' for control in state.__control_list) \
            and all(~(state.__index ^ index) & 2**(switches[dummy] - 1) for dummy in range(len(switches))):
                state.__active_control = None
                self.__active_control = None
                return state
        return None

    def new_time(self, state, time, last_value, independent_sources):
        """
        checking for given precision and returns second order newton-raphson estimation of soft switching
        """
        sum1 = np.matmul(state.__active_control[1],last_value) - state.__active_control[2]
        if (abs(sum1) > self.__absolute_error):
            sum2 = np.matmul(state.__active_control[1], np.matmul(self.__A, last_value) + np.matmul(self.__B, independent_sources))
            sum3 = np.matmul(state.__active_control[1], np.matmul(self.__A**2, last_value) + np.matmul(self.__A, \
                             np.matmul(self.__B, independent_sources)))
            return time + 1.0 / (sum3 / 2 / sum2 - sum2 / sum1)
        else:
            return -1

	
	

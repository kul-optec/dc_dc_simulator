class Model:
    """ 
    A discrete model describing the system behavior
       - If your model is continuous use the Model_continuous class. 
    """
    def __init__(self, system_equations, input_constraint, number_of_states,\
                 number_of_inputs, frequency, number_of_steps):
        """
        Constructor Model
        Parameters
        ---------
        system_equations : The discrete system equations, expressed as Patlab functions in the form f(state,input).
        input_constraint : The input constraints, must be a nmpccodegen.Cfunctions.ProximalFunction object.
        step_number : The step number of points of the discrete system.
        number_of_states : The dimension of the state.
        number_of_inputs : The dimension of the input.
        period : The period of the switching system.
        Returns
        ------
        Nothing
        """
        self._system_equations = system_equations
        self._input_constraint = input_constraint
        self._step_number = number_of_steps
        self._number_of_states = number_of_states
        self._number_of_inputs = number_of_inputs
        self._period = 1/frequency
        

    def get_next_state(self, time, state, input, index):
        """ 
        Obtain the next state of the discrete system 
        Parameters
        ---------
        state -- the current state of the system
        input -- the current input of the system
        Returns
        ------
        Python array containing the next state
        """
        return self._system_equations(state, input, index)

    def generate_constraint(self,location):
        """
        Generate constraints in C code.
        Parameters
        ---------
        location: target location of code generator
        """
        self._input_constraint.generate_c_code(location + "/casadi/g.c")
        self._input_constraint.prox.generate_c_code(location + "/casadi/proxg.c")

    @property
    def system_equations(self):
        """
        Get or set the discrete system equations, expressed as Python functions in the form f(state,input).
        """
        return self._system_equations

    @property
    def step_number(self):
        return self._step_number
    @step_number.setter
    def step_number(self, value):
        self._step_number = value

    @property
    def number_of_states(self):
        """
        Get or set The dimension of the state.
        """
        return self._number_of_states
    @number_of_states.setter
    def numer_of_states(self, value):
        self._number_of_states = value

    @property
    def number_of_inputs(self):
        """
        Get or set The dimension of the input.
        """
        return self._number_of_inputs
    @number_of_inputs.setter
    def numer_of_inputs(self, value):
        self._number_of_inputs = value
        
    @property
    def period(self):
        """
        Get or set the period.
        """
        return self._period
    @period.setter
    def period(self, value):
        self._period = value

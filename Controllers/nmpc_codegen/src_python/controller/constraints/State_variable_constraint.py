# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 11:41:17 2018

@author: ANA
"""

from .Constraint import  Constraint
import casadi as cd

class State_variable_constraint(Constraint):
    def __init__(self, variable_indexes, value, state_index):
        """ 
        construct limitations on the state variables caused by internal 
        circuit switching
        """
        super(State_variable_constraint, self).__init__()

        self._indexes = cd.SX(variable_indexes)
        self._value = cd.SX(value)
        self._state_index = state_index
        
    def evaluate_state_cost(self, state, input, index):
        """ evaluate the function h(x) """
        if (self._state_index == index):
            value = Constraint.trim_and_square(cd.mtimes(self._indexes, state) - self._value) * input 
        else:
            value = 0

        return value

    @property
    def number_of_constraints(self):
        return self._number_of_constraints
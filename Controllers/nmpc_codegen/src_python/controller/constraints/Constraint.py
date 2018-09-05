import casadi as cd
import numpy as np

class Constraint:
    """ A interface that represents the minimum interface of an general constraint
        A constraint needs at least the following method:
        - evaluate_cost , evaluates the cost of the constraint """
    def __init__(self):
        return 
        
    def evaluate_cost(self, state, input, index):
        """ evaluate the function h(x) """
        cost = self.evaluate_state_cost(state, input, index)
        return cost
        
    @staticmethod
    def trim_and_square(x):
        return  cd.fmax(x,0)**2

    @property
    def model(self):
        return self._model
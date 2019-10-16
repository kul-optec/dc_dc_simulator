#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 09:58:52 2018

@author: alekic
"""

import numpy as np
import casadi as cd

class DC_DC:
    def __init__(self, A, b, Ad, bd, c, state_reference, input_reference, number_subsystems):
        self._number_subsystems = number_subsystems
        self._A = A
        self._b = b
        self._Ad = Ad
        self._bd = bd
        self._cd = c
        self._state_reference = state_reference
        self._input_reference = input_reference
               
    def system_equation(self, x, u, index):
        x_dot = cd.mtimes(self._A[int(index)], x) + self._b[int(index)]
        return x_dot
    
    def system_equations_period(self, x, u):
        x_dot = cd.mtimes(self._Ad, x - self._state_reference) + cd.mtimes(self._bd, u-self._input_reference) + self._cd
        return x_dot

          
def get_model(A, b, Ad, bd, c, state_reference, input_reference, number_subsystems):
    model = DC_DC(A, b, Ad, bd, c, state_reference, input_reference, number_subsystems)
    system_equations = lambda state, input, index: model.system_equation(state, input, index)
    system_equations_period = lambda state, input: model.system_equations_period(state, input)
    number_of_inputs = len(A) - 1  # it is always duty ratio

    return (system_equations, system_equations_period, number_of_inputs)
    
def main():
    initial_state = np.array([0., 0., 0.])
    A = cd.SX.sym('A',3,3)
    b = cd.SX.sym('b',3)
    input = np.array([1.])

    tm = DC_DC(A,b,1)
    test = tm.system_equation(initial_state, input, 1)

    print(test)

if __name__ == "__main__":
    main()
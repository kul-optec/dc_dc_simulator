#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 09:58:52 2018

@author: alekic
"""

import numpy as np
import casadi as cd

class DC_DC:
    def __init__(self, A, b, number_subsystems):
        self._number_subsystems = number_subsystems
        self._A = A
        self._b = b
               
    def system_equation(self, x, u, index):
        x_dot = cd.mtimes(self._A[int(index)], x) + self._b[int(index)]
        return x_dot

          
def get_model(A, b, number_subsystems):
    model = DC_DC(A, b, number_subsystems)
    system_equations = lambda state, input, index: model.system_equation(state, input, index)
    number_of_inputs = len(A) - 1  # it is always duty ratio

    return (system_equations, number_of_inputs)
    
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
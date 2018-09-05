import sys
from sympy import *
import casadi as cd


class Element:
    """
    definition of elements that can be found in the converter
    gives the form of the element construction
    """
    def __init__(self, index, node1, node2, value):
        self._node1 = node1
        self._node2 = node2
        self._value = value
        self._index = index

    def __str__(self):
        return str(self._symbol) + " " + str(self._node1) + " " + str(self._node2)
    
    def __lt__(self, element):
        return self._index < element._index

	# sets position in matrix formed as modified nodal analysis
    def set_position(self, position):	
        self._position = position

	#### getting different parameters
    def get_index(self):
        return self._index
	
    def get_value(self):
        return self._value

    def get_nodes(self):
        return list([self._node1, self._node2])

    def is_node(self, node):
        return (self._node1 == node) or (self._node2 == node)

    def get_other_node(self, index):
        if (self._node1 == index):
            return self._node2
        return self._node1

    def get_symbol(self):
        return self._symbol
    
    def get_cd_symbol(self):
        return self._cd_symbol
	
    def get_current_direction(self, node):
        if (node == self._node1):
            return 1
        else:
            return -1

    def get_voltage_direction(self, node):
        if (node == self._node2):
            return 1
        else:
            return -1

    def get_position(self):
        return self._position + self._index - 1

    #### write inside matrix MNA (Modified Nodal Analysis)
    def write_matrix_symbolic(self, matrix, number_equations, index):
        self._write_matrix(matrix, number_equations, index, self._symbol)

    def write_matrix_valued(self, matrix, number_equations, index):
        self._write_matrix(matrix, number_equations, index, self._value)
        
    def write_matrix_symbolic_cd(self, matrix, number_equation, index):
        self._write_matrix(matrix, number_equations, indel, self._symbol_cd)
		


		
					













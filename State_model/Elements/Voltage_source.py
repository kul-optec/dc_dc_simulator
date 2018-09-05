from .Element import *

class Voltage_source(Element):
    """
    	independent voltage source class
    	"""
    def __init__(self, index, node1, node2, value):
        self._cd_symbol = cd.SX.sym('V' + str(index))
        self._symbol = sympify('V' + str(index))
        Element.__init__(self, index, node1, node2, value)		

    def _write_matrix(self, A, number_equations, index, value):
        if (self._node1):
            A[self._position + self._node1 - 1, number_equations] += self._symbol
            A[self._position + self._node1 - 1, self._node1 - 1] = 1
            A[self._index - 1, self._position + self._node1 - 1] = 1
        if (self._node2):
            A[self._position + self._node2 - 1, number_equations] += -self._symbol
            A[self._position + self._node2 - 1, self._node2 - 1] = -1
            A[self._index - 1, self._position + self._node2 - 1] = -1
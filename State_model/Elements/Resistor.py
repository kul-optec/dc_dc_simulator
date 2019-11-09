from .Element import *

class Resistor(Element):
    """
    resistor class
    """
    def __init__(self, index, node1, node2, value):
        self._cd_symbol = cd.SX.sym('R' + str(index))
        self._symbol = sympify('R' + str(index))
        Element.__init__(self, index, node1, node2, value)

    def _write_matrix(self, A, number_equations, index, value):
        if (self._node1):
            A[self._node1 - 1, self._node1 - 1] += 1 / value
            if (self._node2):
                A[self._node1 - 1, self._node2 - 1] -= 1 / value
                A[self._node2 - 1, self._node2 - 1] += 1 / value	
                A[self._node2 - 1, self._node1 - 1] -= 1 / value 
        else:
            A[self._node2 - 1, self._node2 - 1] += 1 / value
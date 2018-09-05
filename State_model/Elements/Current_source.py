from .Element import *

class Current_source(Element):
    """
    independent current source class
    """
    def __init__(self, index, node1, node2, value):
        self._symbol = sympify('I' + str(index))
        self._cd_symbol = SX.sym('I' + str(index))
        Element.__init__(self, index, node1, node2, value)

    def _write_matrix(self, A, number_equations, index, value):
        if (self._node1):
            A[self._node1 - 1, number_equations] += -self._symbol
        if (self._node2):
            A[self._node2 - 1, number_equations] += self._symbol
from .Element import *

class Switch(Element):
    """
    switch class

    switch type: 1 - transistor, 2 - diode, 3 - current bidirectional, 4 - voltage bidirectional, 5 - four quadrant 
    """
    def __init__(self, index, type_sw, node1, node2, function1 = 0, function2 = 0):
        self._cd_symbol = cd.SX.sym('SW' + str(index))
        self._symbol = sympify('SW' + str(index))
        self._type = type_sw
        Element.__init__(self, index, node1, node2, 1)

    def _write_matrix(self, A, number_equations, index, value):
        if (2**(self._index - 1) & index):
            modified_index = self._index - 1
            if (self._node1):
                A[self._position + modified_index, self._node1 - 1] = 1
                A[self._node1 - 1, self._position + modified_index] = 1
            if (self._node2):
                A[self._position + modified_index, self._node2 - 1] = -1
                A[self._node2 - 1, self._position + modified_index] = -1
        else:
            A[self._position + self._index - 1, self._position + self._index - 1] = 1
            modified_index = self._index - 1 
            if (self._node1):
                A[self._node1 - 1, self._position + modified_index] = 1
            if (self._node2):
                A[self._node2 - 1, self._position + modified_index] = -1

    def type_start_conducting(self):
        return self._type in [2, 3, 5]

    def type_stop_conducting(self):
        return self._type in [1, 2, 4]

    def control_type(self):
        return self._type in [1, 3, 4, 5]
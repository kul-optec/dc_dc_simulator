from .Element import *

class Capacitor(Element):
    """
    capacitor class
    """
    def __init__(self, index, node1, node2, value, initial = 0):
        self.__dcvm = False
        self.__dcvm_symbol = 0
        self.__initial_value = initial
        
        self._cd_symbol = cd.SX.sym('C' + str(index))
        self._symbol = sympify('C' + str(index))
        Element.__init__(self, index, node1, node2, value)	

    def _write_matrix(self, A, number_equations, index, value):
        if not self.__dcvm:
            sym = sympify('vc' + str(self._index))
            A[self._position + self._index - 1, number_equations] = sym
		
            if (self._node1):
                A[self._node1 - 1, self._position + self._index - 1] = value
                A[self._position + self._index - 1, self._node1 - 1] = 1
            if (self._node2):
                A[self._node2 - 1, self._position + self._index - 1] = -value
                A[self._position + self._index - 1, self._node2 - 1] = -1

        else:
            if self.__dcvm_symbol == 0:
                A[self._position + self._index - 1, self._position + self._index - 1] = 1
            else:
                A[self._position + self._index - 1, number_equations] = self.__dcvm_symbol
                if (self._node1):
                    A[self._node1 - 1, self._position + self._index - 1] = value
                    A[self._position + self._index - 1, self._node1 - 1] = 1
                if (self._node2):
                    A[self._node2 - 1, self._position + self._index - 1] = -value
                    A[self._position + self._index - 1, self._node2 - 1] = -1

            self.__dcvm = False
            self.__dcvm_symbol = 0

    def set_dcvm(self, elements_list):
        self.__dcvm = True	
        if len(elements_list):
            for element in elements_list[1 : ]:
                self.__dcvm_symbol += SX.sym('vc' + str(abs(element))) * sign(element) * sign(elements_list[0])

    def get_initial_value(self):
        return self.__initial_value		
# SINGLETON: CLASS THAT CONTAINS ALL INFORMATION ABOUT ELEMENTS AND NODES 
# I.E. NUMBER OF NODES, INDUCTORS, CAPACITORS, ...
# USED FOR COLLECTING THESE INFORMATION AND GETTING THEM WHEN NECCESSARY

from .Elements import * 
from .Nodes import *
from .Output import *


class System:
    def __init__(self):
        self.__number_voltage_sources = 0
        self.__number_current_sources = 0
        self.__number_switches = 0
        self.__number_inductors = 0
        self.__number_capacitors = 0
        self.__number_resistors = 0
        self.__number_independent_sources = 0
        
        self.__state_variables = 0
        self.__independent_sources = 0
        
        self.__number_elements = 0
        self.__number_nodes = 0
        
        self.__total_number_equations = 0
        
        self.__elements = []
        self.__symbols_bank = []
        self.__nodes = []
        self.__switches = []
        		
        # saves pattern for switches control
        self.__controlled_switches = 0
        self.__controlled_switches_on_state = 0
        self.__controlled_switches_off_state = 0
        
        # initialization block
        self.__inductors = []
        self.__capacitors = []
        self.__initial_values = []
        self.__state_variables_symbols = []

        # sources
        self.__sources_symbols = []
        self.__independent_sources = []
        self.__sources_values = []


	
    #####################################################################################################################################
    # get information
    def get_number_switches(self):
        return self.__number_switches

    def get_number_inductors(self):
        return self.__number_inductors

    def get_number_capacitors(self):
        return self.__number_capacitors

    def get_number_voltage_sources(self):
        return self.__number_voltage_sources
	
    def get_number_current_sources(self):
        return self.__number_current_sources

    def get_number_resistors(self):
        return self.__number_resistors

    def get_number_equations(self):
        return self.__total_number_equations

    def get_inductors(self):
        return self.__inductors
    
    def get_capacitors(self):
        return self.__capacitors

	### switches information
    def get_on_state_switches(self):
        return self.__controlled_switches_on_state

    def get_off_state_switches(self):
        return self.__controlled_switches_off_state

    def get_controlled_switches(self):
        return self.__controlled_switches

    def get_switches(self):
        return self.__switches

    def get_switches_indexes(self):
        lst = []
        for switch in self.__switches:
            lst.append(switch.get_index())
        return lst

    def get_controlled_switches_indexes(self):
        lst = []
        for switch in self.__switches:
            if switch.control_type():
                lst.append(switch.get_index())
        return lst

    ### information about state variables
    def get_number_state_variables(self):
        return self.__state_variables

    def get_state_variables_position(self):
        return self.__number_nodes + self.__number_voltage_sources + self.__number_switches - 1

    def get_state_variables_symbols(self):
        return self.__state_variables_symbols

    def get_initial_values(self):
        return self.__initial_values
	
	### independent sources
    def get_number_independent_sources(self):
        return self.__number_independent_sources

    def get_source_symbols(self):
        return self.__sources_symbols

    def get_source_values(self):
        return self.__sources_values

    def get_independent_sources(self):
        return self.__independent_sources

	### output
    def get_number_outputs(self):
        return self.__output.get_number()

    def get_output_indexes(self):
        return self.__output.get_indexes()

    def set_output(self, output_list):
        """
        setting the output
        """
        self.__output = Output()
        self.__output_list = output_list


	### set control of the controllable switches
    def set_control(self, control_switches_state, state):
        if (state == 'on_state'):
            self.__controlled_switches_on_state = control_switches_state
        else:
            self.__controlled_switches_off_state = control_switches_state

        self.__controlled_switches = self.__controlled_switches | control_switches_state		# all controlled switches


	### adds all elements and writes them
    def create_element(self, constructor):
        element = constructor 
        self.add_element(element)
        self.add_symbol(element.get_symbol())

        self.__number_elements += 1
	
        for node in element.get_nodes():
            self.add_node(node, element)
	
    def add_element(self, element):
        self.__elements.append(element)
        self.__number_elements += 1

        if (element.__class__ == Voltage_source):
            self.__number_voltage_sources += 1
        elif (element.__class__ == Inductor):
            self.__number_inductors += 1
        elif (element.__class__ == Capacitor):
            self.__number_capacitors += 1
        elif (element.__class__ == Switch):
            self.__number_switches += 1
        elif (element.__class__ == Current_source):
            self.__number_current_sources += 1
        elif (element.__class__ == Resistor):
            self.__number_resistors += 1

    def get_elements(self):
        return self.__elements

    def get_number_elements(self):
        return self.__number_elements

    def write_elements(self):
        for element in self.__elements:
            print(str(element))

	### adds all of the symbols and writes them
    def write_symbols(self):
        print(self.__symbols_bank)

    def add_symbol(self, symb):
        self.__symbols_bank.append(symb)

	### adds all circuit nodes and writes them
    def write_nodes(self):
        for node in self.__nodes:
            print(str(node))

    def get_nodes(self):	
        return self.__nodes

    def get_number_nodes(self):
        return self.__number_nodes

    def add_node(self, node_index, element):
        """
        adds node if does not exist and in the other case just adds element to node
        """
        global number_nodes

        dummy = True
        for node in self.__nodes:
            dummy = dummy and (node.index() != node_index)
	
        if (dummy):
            self.__nodes.append(Node(node_index))
            self.__number_nodes += 1
		
            for i in range(len(self.__nodes) - 1):
                if (self.__nodes[i].index() > self.__nodes[i + 1].index()):
                    dummy = self.__nodes[i]
                    self.__nodes[i] = self.__nodes[i+1]
                    self.__nodes[i+1] = dummy
	
        for node in self.__nodes:
            if (node.index() == node_index):
                node.add_element(element)
                break

	
	### calculates equations and writes indexes inside elements
    def initialize(self):
        # state variables
        self.__state_variables = self.__number_inductors + self.__number_capacitors
        self.__inductors = [0 for dummy in range(self.__number_inductors)]
        self.__capacitors = [0 for dummy in range(self.__number_capacitors)]
        self.__initial_values = [0 for dummy in range(self.__state_variables)]
        self.__state_variables_symbols = [0 for dummy in range(self.__state_variables)]

        # sources
        self.__number_independent_sources = self.__number_voltage_sources + self.__number_current_sources
        self.__sources_symbols = [0 for dummy in range(self.__number_independent_sources)]
        self.__independent_sources = [0 for dummy in range(self.__number_independent_sources)]
        self.__sources_values = [0 for dummy in range(self.__number_independent_sources)] 

        self.__total_number_equations = self.__number_nodes + self.__number_inductors + self.__number_capacitors + self.__number_voltage_sources + self.__number_switches - 1

        # sets elements position and gets important symbols
        for element in self.__elements:
            if isinstance(element, Voltage_source):
                element.set_position(self.__number_nodes - 1)
                self.__sources_symbols[element.get_index() - 1] = (sympify('V' + str(element.get_index())))
                self.__sources_values[element.get_index() - 1] = element.get_value()
                self.__independent_sources[element.get_index() - 1] = element.get_value()
            elif isinstance(element, Inductor):
                element.set_position(self.__number_nodes + self.__number_voltage_sources + self.__number_switches - 1)
                self.__inductors[element.get_index() - 1] = element
                self.__state_variables_symbols[element.get_index() - 1] = (sympify('il' + str(element.get_index())))
                self.__initial_values[element.get_index() - 1] = element.get_initial_value()
            elif isinstance(element, Capacitor):
                element.set_position(self.__number_nodes + self.__number_inductors + self.__number_voltage_sources + self.__number_switches - 1)
                self.__state_variables_symbols[self.__number_inductors + element.get_index() - 1] = (sympify('vc' + str(element.get_index())))
                self.__initial_values[self.__number_inductors + element.get_index() - 1] = element.get_initial_value()
                self.__capacitors[element.get_index() - 1] = element
            elif isinstance(element, Switch):
                element.set_position(self.__number_nodes + self.__number_voltage_sources - 1)
                self.__switches.append(element)
            elif isinstance(element, Current_source):
                self.__sources_symbols[self.__number_voltage_sources + element.get_index() - 1] = (sympify('I' + str(element.get_index())))
                self.__sources_values[element.get_index() - 1] = element.get_value()
                self.__independent_sources[self.__number_voltage_sources + element.get_index() - 1] = element.get_value()

    def initialise_output(self):			
        """
        sets output indexes
        """
        for lst in self.__output_list:
            if (lst[0] == 'node'):
                self.__output.add_index(lst[1] - 1)
            elif (lst[0] == 'inductor'):
                self.__output.add_index(self.__number_nodes + self.__number_voltage_sources + lst[1] - 2 )
            elif (lst[0] == 'capacitor'):
                self.__output.add_index(self.__number_nodes + self.__number_voltage_sources + self.__number_inductors + lst[1] - 2 )
		
	### adds indicator about dicm inside inductor
    def set_dicm(self, index, list_elements):
        self.__inductors[index - 1].set_dicm(list_elements)
	
	### adds indicator about dcvm inside capacitor
    def set_dcvm(self, index, list_elements):
        self.__capacitors[index - 1].set_dcvm(list_elements)
        

        


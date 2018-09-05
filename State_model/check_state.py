# functions that check if the operating state is possible
# according to paper D. Maksimovic and S. Cuk, "A Unified Analysis of PWM Converters in Discontinuous Modes"
# by finding cutsets and loop with given criteria

from State_model.Elements import *

def is_dicm(index, dicm_nodes, dicm_cutsets):
	"""
	check if dicm occurs in some dicm cutset and if it does, returns that cutset
	"""
	dicm = False
	iv_fixed = False
	elements = []
	sources = []

	for cutset in dicm_cutsets:
		if all((2**(element.get_index() -  1) & ~index) for element in cutset if isinstance(element, Switch)):
			element_list = []
			source_list = []
			for element in cutset:
				if isinstance(element, Inductor):	
					for node in dicm_nodes[dicm_cutsets.index(cutset)]:
						if element.is_node(node.index()):
							sign = element.get_current_direction(node.index()) * element.get_index() 
							element_list.append(sign)
				elif isinstance(element, Current_source):
					for node in dicm_nodes[dicm_cutsets.index(cutset)]:
						if element.is_node(node.index()):
							sign = element.get_current_direction(node.index()) * element.get_index()
							source_list.append(element)

			elements.append(list(element_list))
			sources.append(list(source_list))
			dicm = True and any(isinstance(element, Switch) and element.type_stop_conducting() for element in cutset)
			iv_fixed = True
					
	return [dicm, iv_fixed, elements, sources]

# checks if this is the state when dcvm occurs or when capacitor voltage has fixed value
# returns if the state is dcvm and elements and sources affected with dcvm
def is_dcvm(index, dcvm_nodes, dcvm_loops):
	dcvm = False
	cv_fixed = False
	elements = []
	sources = []
	nodes = []
	
	for loop in dcvm_loops:
		if all((2**(element.get_index() - 1) & index) for element in loop if isinstance(element, Switch)): # check all switches in loop are on
			element_list = []
			source_list = []
			for element in loop:
				if isinstance(element, Capacitor):
					found = False	
					for node in dcvm_nodes[dcvm_loops.index(loop)]:
						if element.is_node(node.index()) and not found:
							sign = element.get_voltage_direction(node.index()) * element.get_index() 
							element_list.append(sign)
							found = True
				elif isinstance(element, Voltage_source):
					found = False	
					for node in dcvm_nodes[dcvm_loops.index(loop)]:
						if element.is_node(node.index()) and not found:
							sign = element.get_voltage_direction(node.index()) * element.get_index() 
							source_list.append(sign)
							found = True

			elements.append(list(element_list))
			sources.append(list(source_list))
			dcvm = True and any(element.type_start_conducting() for element in loop if isinstance(element, Switch))
			cv_fixed = True
					
	return [dcvm, cv_fixed, elements, sources]


# find cutset that can cause DICM, or loop that can cause DCVM
def find_dicm_cutsets(cutsets, nodes, dicm_nodes):
	"""
	finds cutsets that can potentially cause DICM
	"""
	new_cutsets = []
	
	for cutset in cutsets:
		dummy = True
		for element in cutset:
			dummy = dummy and (isinstance(element, Switch) or isinstance(element, Current_source) or isinstance(element, Inductor))
		if dummy:
			if (any(isinstance(element, Switch) for element in cutset) and any(isinstance(element, Inductor) for element in cutset)): 
				new_cutsets.append(list(cutset))
				dicm_nodes.append(nodes[cutsets.index(cutset)])

	return new_cutsets

def find_dcvm_loops(loops, nodes, dcvm_nodes):
	"""
	finds loops that can potentially cause DCVM
	"""
	new_loops = []

	for loop in loops:
		dummy = True
		for element in loop:
			dummy = dummy and (isinstance(element, Switch) or isinstance(element, Voltage_source) or isinstance(element, Capacitor))
		if dummy:
			if (any(isinstance(element, Switch) for element in loop) and any(isinstance(element, Capacitor) for element in loop)):
				loop.sort()
				if not loop in new_loops: 
					new_loops.append(list(loop))
					dcvm_nodes.append(list(nodes[loops.index(loop)]))

	return new_loops

# 1) eliminates states with unproper control
def check_control_scheme(controlled_switches, on_state, off_state, index):
	"""
	finds if a control scheme is satisfied
	"""
	index = index & controlled_switches
	return ((index == on_state) or (index == off_state) or (index == 0))

# 2a) functions for eliminating states with loops of closed switches and voltage sources
def find_voltage_loops(loops):
	"""
	finds if there are loops consisting only of switches and voltage sources
	that eliminates states when those swithes are on
	"""
	new_loops = []

	for loop in loops:
		dummy = True
		for element in loop:
			dummy = dummy and (isinstance(element, Switch) or isinstance(element, Voltage_source))
		if dummy:
			if (any(isinstance(element, Switch) for element in loop) and any(isinstance(element, Voltage_source) for element in loop)): 
				new_loops.append(list(loop))

	return new_loops

def check_voltage_loops(index, voltage_loops):
	"""
	finds if there are loops with on switches and only voltage sources
	"""
	exists = False
	for loop in voltage_loops:
		loop_index = True
		for element in loop:
			if (isinstance(element, Switch)):
				if not (2**(element.get_index() - 1) & index):
					loop_index = False

		exists = exists or loop_index
	return exists

# 2b) functions for eliminating states with cutsets of open switches and current sources
def find_current_cutsets(cutsets):
	"""
	finds cutsets consisting of switches and current sources, thus states when those
	switches are off are impossible
	"""
	new_cutsets = []

	for cutset in cutsets:
		dummy = True
		for element in cutset:
			dummy = dummy and (isinstance(element, Switch) or isinstance(element, Current_source))
		if dummy:
			if (any(isinstance(element, Switch) for element in cutset) and any(isinstance(element, Current_source) for element in cutset)): 
				new_cutsets.append(list(loop))

	return new_cutsets

def check_current_cutsets(index, current_cutsets):
	"""
	finds if there are cutsets with off switches and only current sources
	"""
	exists = False
	for loop in current_cutsets:
		cutset_index = True
		for element in cutset:
			if (isinstance(element, Switch)):
				if not (2**(element.get_index() - 1) & index):
					cutset_index = False

		exists = exists or cutset_index

	return exists

import inspect

# 3a) eliminates states in which some cutsets with same inductors have all open switches and some not
def check_cutset_consistency(index, cutsets):
	"""
	eliminates state in which cutsets consisting of the same inductors are different = some has all open
	switches and others not
	"""
	if not len(cutsets):
		return True

	for i in range(len(cutsets) - 1):	
		for j in range(i + 1, len(cutsets)):
			# checks whether all inductors inside cutsets are the same
			dummy = all((element in cutsets[j]) for element in cutsets[i] if isinstance(element, Inductor)) \
					and all((element in cutsets[i]) for element in cutsets[j] if isinstance(element, Inductor))
			
			if (dummy):
				if (all((2**(element.get_index() - 1) & (~index)) for element in cutsets[i] if isinstance(element, Switch))):
					dummy = all((2**(element.get_index() - 1) & (~index)) for element in cutsets[j] if isinstance(element, Switch))
				elif all((2**(element.get_index() - 1) & (~index)) for element in cutsets[j] if isinstance(element, Switch)):
					dummy = all((2**(element.get_index() - 1) & (~index)) for element in cutsets[i] if isinstance(element, Switch))	

				if not dummy:
					return dummy		
	
	return True

# 3b) eliminates states in which some loops with same capacitors have all closed switches and some not
def check_loop_consistency(index, loops):
	"""
	eliminates state in which loops consisting of the same capacitors are different = some has all closed
	switches and others not
	"""
	if not (len(loops)):
		return True

	for i in range(len(loops) - 1):	
		for j in range(i + 1, len(loops)):
			# checks whether all capacitors inside loops are the same
			dummy = all((element in loops[j]) for element in loops[i] if isinstance(element, Capacitor)) \
					and all((element in loops[i]) for element in loops[j] if isinstance(element, Capacitor))
			
			if (dummy):
				if (all((2**(element.get_index() - 1) & index) for element in loops[i] if isinstance(element, Switch))):
					dummy = all((2**(element.get_index() - 1) & index) for element in loops[j] if isinstance(element, Switch))
				elif all((2**(element.get_index() - 1) & index) for element in loops[j] if isinstance(element, Switch)):
					dummy = all((2**(element.get_index() - 1) & index) for element in loops[i] if isinstance(element, Switch))	

				if not dummy:
					return dummy		
	
	return True

# 4) eliminates not possible DICM and DCVM cases -- to be written

# 5a) checks if DICM can occur, if there are at least one switch that is not 
# current controllable = a diode, voltage bidirectional
def check_dicm_cutset(cutsets, index):
	"""
	checks if DICM can occur, if there are at least one switch that is not 
	current controllable = a diode, voltage bidirectional
	"""
	exists = True
	for cutset in cutsets:
		if all(2**(element.get_index() - 1) & ~index for element in cutset if isinstance(element, Switch)):
			exists = exists and any(element.type_stop_conducting() for element in cutset if isinstance(element, Switch))
	return exists

# 5b) checks if DCVM can occur, if there are at least one switch that is not 
# current controllable = a diode, voltage bidirectional
def check_dcvm_loop(loops, index):
	"""
	checks if DCVM can occur, if there are at least one switch that is not 
	current controllable = a diode, voltage bidirectional
	"""
	exists = True
	for loop in loops:
		if all(2**(element.get_index() - 1) & index for element in loop if isinstance(element, Switch)):
			exists = exists and any(element.type_start_conducting() for element in loop if isinstance(element, Switch))
		
		if (exists):	
			return exists
	return exists
				
# functons for forming collection all of the cutset elements
def form_cutsets(cutset_nodes):
	#cutset_nodes = form_cutset_nodes(nodes)

	cutset_collection = []

	for cutset in cutset_nodes:
		cutset_elements = []
		for node in cutset:
			for element in node.get_elements():
				if element_in_cutset(element.get_other_node(node.index()), cutset):
					cutset_elements.append(element)

		cutset_collection.append(list(cutset_elements))

	return cutset_collection
	
	
def form_cutset_nodes(nodes):
	"""
	forms all of the possible combinations of nodes inside cutset
	"""
	result = []

	for i in range(0, len(nodes)):
		result.append(list([nodes[i]]))	
		temp = []
		for sublist in result:
			if (i < (len(nodes) - 1)):
				newlist = list(sublist)
				newlist.append(nodes[i + 1])
				newlist.sort()
				temp.append(newlist)
		
		for sublist in temp:
			result.append(sublist)
			
	return result

def element_in_cutset(node_index, cutset):
	"""
	returns if the element is in the cutset
	"""
	dummy = False
	for node in cutset:
		dummy = dummy or (node.index() == node_index)
	
	return (not dummy)



# functions for forming all of the loops of elements

# class used for forming loop
class Tree:
	def __init__(self, element, node, root):
		self.__root = root
		self.__element = element
		self.__node = node
		self.__subelements = []

	def __str__(self):
		string = "root " + str(self.__root) + " element " + str(self.__element.get_symbol()) + " subelements " 
		for i in range(len(self.__subelements)):
			string += str(self.__subelements[i].get_symbol()) 
			string += ", "
		return string

	def add_subelement(self, element):
		self.__subelements.append(element)

	def get_root(self):
		return self.__root

	def get_element(self):
		return self.__element

	def get_node(self):
		return self.__node

def form_loops(nodes, node_collection):
	"""
	forms all loops for provided nodes with their elements, 
	returns them as a list of lists of elements
	"""
	loop_collection = []

	for node in nodes:
		find_loop(node, node, nodes, loop_collection, node_collection, None)

	return loop_collection



def find_loop(beginning_node, node, nodes, loop_collection, node_collection, tree):
	"""
	helper functon for loop forming, called recursively from beginning node a tree is built
	if continues with going through the nodes if the node index is bigger than the previous 
	and continues forming tree structure when it comes to beginning node again, reades the 
	loop and puts it inside collection
	"""
	collection = node.get_elements()
	for element in collection:
		other_node_index = element.get_other_node(node.index())
		new_tree = Tree(element, node, tree)
		if (other_node_index > node.index()):
			if (tree != None):
				tree.add_subelement(element)
			find_loop(beginning_node, nodes[other_node_index], nodes, loop_collection, node_collection, new_tree)

		elif (other_node_index == beginning_node.index()) and (element != tree.get_element()):
			if (tree != None):
				tree.add_subelement(element)
			current_tree = new_tree
			loop = []
			loop_nodes = []
			loop_nodes.append(beginning_node)
			cont = True

			while (cont):
				loop.append(current_tree.get_element())
				loop_nodes.append(current_tree.get_node())
				current_tree = current_tree.get_root()
				if (current_tree == None):
					
					cont = False
				#loop.sort()

			if not (loop in loop_collection):
				loop_collection.append(loop)
				node_collection.append(loop_nodes)

			
					
# find loops and cutsets of inductors and capacitors
def is_ClS(loops, index):
	dummy = True
	for loop in loops:
		dummy = True
		for element in loop:
			dummy = dummy and (isinstance(element, Capacitor) or isinstance(element, Voltage_source) or isinstance(element, Switch))
		if dummy:
			if (any(isinstance(element, Capacitor) for element in loop) and any(isinstance(element, Switch) for element in loop) \
				and all((element.get_index() & index) for element in loop if isinstance(element, Switch))): 
				return dummy
	return False	

def is_ClnS(loops, index):
	dummy = True
	for loop in loops:
		dummy = True
		for element in loop:
			dummy = dummy and (isinstance(element, Capacitor) or isinstance(element, Voltage_source) or isinstance(element, Switch))
		if dummy:
			if (any(isinstance(element, Capacitor) for element in loop) and any(isinstance(element, Switch) for element in loop) \
				and all((element.get_index() & ~index) for element in loop if isinstance(element, Switch))): 
				return dummy
	return False

def is_LlS(loops, index, capacitors):
	dummy = True
	for loop in loops:
		dummy = True
		for element in loop:
			dummy = dummy and (isinstance(element, Inductor) or isinstance(element, Capacitor) or isinstance(element, Voltage_source) or isinstance(element, Switch))
		if dummy:
			if (any(isinstance(element, Inductor) for element in loop) and any(isinstance(element, Switch) for element in loop) \
				and all((element.get_index() & index) for element in loop if isinstance(element, Switch))) \
				and all((element not in capacitors) for element in loop if isinstance(element, Capacitor)) \
				and sum(1 for element in loop if isinstance(element, Inductor)) == 1: 				
				return dummy

	return False	

def is_LlnS(loops, index, capacitors):
	dummy = True
	for loop in loops:
		dummy = True
		for element in loop:
			dummy = dummy and (isinstance(element, Inductor) or isinstance(element, Switch) or isinstance(element, Voltage_source) or isinstance(element, Capacitor))
		if dummy:
			if (any(isinstance(element, Inductor) for element in loop) and any(isinstance(element, Switch) for element in loop) \
				and all((element.get_index() & ~index) for element in loop if isinstance(element, Switch))) \
				and all((element not in  capacitors) for element in loop if isinstance(element, Capacitor)) \
				and sum(1 for element in loop if isinstance(element, Inductor)) == 1: 
				return dummy
	return False

def is_LcS(cutsets, index):
	dummy = True
	for cutset in cutsets:
		dummy = True
		for element in cutset:
			dummy = dummy and (isinstance(element, Inductor) or isinstance(element, Current_source) or isinstance(element, Switch))
		if dummy:
			if (any(isinstance(element, Inductor) for element in cutset) and any(isinstance(element, Switch) for element in cutset) \
				and all((element.get_index() & index) for element in cutset if isinstance(element, Switch))): 
				return dummy
	return False

def is_LcnS(cutsets, index):
	dummy = True
	for cutset in cutsets:
		dummy = True
		for element in cutset:
			dummy = dummy and (isinstance(element, Inductor) or isinstance(element, Current_source) or isinstance(element, Switch))
		if dummy:
			if (any(isinstance(element, Inductor) for element in cutset) and any(isinstance(element, Switch) for element in cutset) \
				and all((element.get_index() & ~index) for element in cutset if isinstance(element, Switch))): 
				return dummy
	return False

def is_CcS(cutsets, index, inductors):
	dummy = True
	for cutset in cutsets:
		dummy = True
		for element in cutset:
			dummy = dummy and (isinstance(element, Inductor) or isinstance(element, Capacitor) or isinstance(element, Current_source) or isinstance(element, Switch))
		if dummy:
			if (any(isinstance(element, Capacitor) for element in cutset) and any(isinstance(element, Switch) for element in cutset) \
				and all((element.get_index() & index) for element in cutset if isinstance(element, Switch))) \
				and all((element not in inductors) for element in cutset if isinstance(element, Inductor)) \
				and sum(1 for element in cutset if isinstance(element, Capacitor)) == 1: 	
				for element in cutset:
					print(str(element))			
				return dummy

	return False	

def is_CcnS(cutsets, index, inductors):
	dummy = True
	for cutset in cutsets:
		dummy = True
		for element in cutset:
			dummy = dummy and (isinstance(element, Capacitor) or isinstance(element, Switch) or isinstance(element, Current_source) or isinstance(element, Inductor))
		if dummy:
			if (any(isinstance(element, Capacitor) for element in cutset) and any(isinstance(element, Switch) for element in cutset) \
				and all((element.get_index() & ~index) for element in cutset if isinstance(element, Switch))) \
				and all((element not in inductors) for element in cutset if isinstance(element, Inductor)) \
				and sum(1 for element in cutset if isinstance(element, Capacitor)) == 1:
				return dummy
	return False

# checking which kind of quasi-resonant converter possibly is
def is_ZV(loops, cutsets, index):
	return is_ClS(loops, index) and is_LcnS(cutsets, index)

def is_ZC(loops, cutsets, index):
	return is_ClnS(loops, index) and is_LcS(cutsets, index)

def is_ZV_QSW(loops, capacitors, index):
	return is_ClS(loops, index) and is_ClnS(loops, index) and is_LlS(loops, index, capacitors) and is_LlnS(loops, index, capacitors)

def is_ZC_QSW(cutsets, inductors, index):
	return is_LcS(cutsets, index) and is_LcnS(cutsets, index) and is_CcS(cutsets, index, inductors) and is_CcnS(cutsets, index, inductors)

def is_Qn_PWM(loops, cutsets, capacitors, inductors, index):
	return is_LlnS(loops, index, capacitors) and is_CcS(cutsets, index, inductors)

def is_Qf_PWM(loops, cutsets, capacitors, inductors, index):
	return is_LlS(loops, index, capacitors) and is_CcnS(cutsets, index, inductors)

# getting dicm inductors and dcvm capacitors
def get_dicm_inductors(cutsets):
	"""
	returns inductors that can cause dicm
	"""
	inductors = []
	for cutset in cutsets:
		for element in cutset:
			if isinstance(element, Inductor) and not (element in inductors):
				inductors.append(element)

	return inductors

def get_dcvm_capacitors(loops):
	"""
	returns capacitors that can cause dcvm
	"""
	capacitors = []
	for loop in loops:
		for element in loop:
			if isinstance(element, Capacitor) and not (element in capacitors):
				capacitors.append(element)

	return capacitors
		
		
		


			
		
	

# class of nodes
class Node:
    def __init__(self, node):
        self.__index = node
        self.__elements = []
        self.__element_number = 0
        
    def index(self):
        return self.__index

    def __eq__(self, node):
        return self.__index == node.__index
    
    def __lt__(self, node):
        return True

    def __ne__(self, node):
        return self.__index != node.__index
    
    def __str__(self):
        return "node" + str(self.__index)

    def add_element(self, element):
        self.__elements.append(element)
        self.__element_number += 1

    def get_elements(self):
        return self.__elements
	
    def get_element_number(self):
        return self.__element_number



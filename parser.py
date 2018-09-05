# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 21:23:00 2018

@author: ANA

PARSER FOR POWER CONVERTER IN THE NETLIST
"""

from State_model.System import *

def parse_input_file(model, file):
    lines = file.readlines()
    
    for line in lines:
        line = line.split()
        
        if (line[0] == 'V'):
            model.create_element(Voltage_source(int(line[1]), int(line[2]), int(line[3]), float(line[4])))
        elif (line[0] == 'SW'):
            model.create_element(Switch(int(line[1]), int(line[2]), int(line[3]), int(line[4])))
        elif (line[0] == 'L'):
            model.create_element(Inductor(int(line[1]), int(line[2]), int(line[3]), float(line[4])))
        elif (line[0] == 'C'):
            model.create_element(Capacitor(int(line[1]), int(line[2]), int(line[3]), float(line[4])))
        elif (line[0] == 'R'):
            model.create_element(Resistor(int(line[1]), int(line[2]), int(line[3]), float(line[4])))
        elif (line[0] == 'I'):
            model.create_element(Current_source(int(line[1]), int(line[2]), int(line[3]), float(line[4])))
        
    model.initialize()



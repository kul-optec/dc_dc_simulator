#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:53:20 2018

@author: alekic
"""

import os
from datetime import datetime
import time
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ast import literal_eval

from State_model import *
from Controllers import *
from parser import *

model = System()
controller = None
state_space_model = None

DIGITS = ['1','2','3','4','5','6','7','8','9']
OUTPUT_VARIABLES = ['node', 'inductor', 'capacitor']
MIN_D = 0
MAX_D = 1
MIN_F = 0
MAX_F = 1e9
SIMULATION_TIME = 10e-3
TIME_STEP_POINTS = 100

OUTPUT_FILE_NAME = './examples/state_variables.npy'

from diagrams import *

class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(300, 300, 850, 650)
        self.setWindowTitle("NMPC for power converters")
        self.setWindowIcon(QIcon('pythonlogo.png'))


        openFile = QAction("&Open File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.file_open)

        saveFile = QAction("&Save File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.file_save)

        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:white;font-weight:bold;}")
        self.statusBar.showMessage("Choose open and save file and controlling method.")
        self.setStatusBar(self.statusBar)

        mainMenu = self.menuBar()
        
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
       
        # variables
        self.open_file = None
        self.save_file = OUTPUT_FILE_NAME
        
        # control parameters
        self.on_switches = 0
        self.on_switches_list = list()
        self.off_switches = 0
        self.off_switches_list = list()
        self.output = []
        
        
        self.control_method = None
        self.discretization_method = None
        self.duty_ratio = 0
        self.controller_coeffs = None
        self.frequency = 0
        self.sim_time = SIMULATION_TIME
        self.time_step_points = TIME_STEP_POINTS
        
        
        self.diagram = Diagrams()
        
        self.home()

    def home(self):
        btn = QPushButton("Quit", self)
        btn.clicked.connect(self.close_application)
        btn.resize(btn.minimumSizeHint())
        btn.move(50,550)  
        
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("CHOOSE CONTROL METHOD")
        self.comboBox.addItem("Constant frequency and duty ratio")
        self.comboBox.addItem("PID controller")
        self.comboBox.addItem("Nonlinear Model Predictive Controller")
        self.comboBox.move(50, 50)
        self.comboBox.resize(300, 30)
        self.comboBox.activated[str].connect(self.control_choice)
        
        self.on_switches_box = QComboBox(self)
        self.on_switches_box.addItem("Select switches controlled with driver output")
        self.on_switches_box.move(50, 100)
        self.on_switches_box.resize(500, 30)
        self.on_switches_box.activated[str].connect(self.btnclicked_on_switches)
        self.on_switches_box.setEnabled(False)
        
        self.off_switches_box = QComboBox(self)
        self.off_switches_box.addItem("Select switches controlled with inverted driver output")
        self.off_switches_box.move(50, 150)
        self.off_switches_box.resize(500, 30)
        self.off_switches_box.activated[str].connect(self.btnclicked_off_switches)
        self.off_switches_box.setEnabled(False)
        
        self.output_box = QComboBox(self)
        self.output_box.addItem("Converter's output")
        self.output_box.move(50, 200)
        self.output_box.resize(500, 30)
        self.output_box.activated[str].connect(self.btnclicked_output)
        self.output_box.setEnabled(False)
        
        self.discretization_method_box = QComboBox(self)
        self.discretization_method_box.move(50, 350)
        self.discretization_method_box.resize(300, 30)
        self.discretization_method_box.addItem("CHOOSE DISCRETIZATION METHOD")
        self.discretization_method_box.addItem('pole_zero_matching')
        self.discretization_method_box.addItem('bilinear')
        self.discretization_method_box.activated[str].connect(self.btnclicked_discretization_method)
        self.discretization_method_box.setVisible(False)
        self.discretization_method_box.setEnabled(False)
        
        # frequency line
        self.frequency_label = QLabel('Add frequency', self)
        self.frequency_label.move(50,260)
        self.frequency_label.resize(300, 20)
        self.frequency_line = QLineEdit(self)
        self.frequency_line.move(50, 280)
        self.frequency_line.resize(300, 30)
        self.frequency_line.editingFinished.connect(self.get_frequency)
        self.frequency_line.setEnabled(False)
        
        # duty ratio line
        self.label = QLabel('Add duty ratio as a value between 0 and 1', self)
        self.label.move(50,330)
        self.label.resize(300, 20)
        self.label.setVisible(False)
        self.duty_ratio_line = QLineEdit(self)
        self.duty_ratio_line.move(50, 350)
        self.duty_ratio_line.resize(300, 30)
        self.duty_ratio_line.editingFinished.connect(self.get_duty_ratio)
        self.duty_ratio_line.setVisible(False)
        self.duty_ratio_line.setEnabled(False)
        
        self.button_controller = QPushButton('Add controller coefficients', self)
        self.button_controller.clicked.connect(self.open_controller_dir)
        self.button_controller.move(400,350)
        self.button_controller.resize(300, 30)
        self.button_controller.setVisible(False)
        self.button_controller.setEnabled(False)
        
        self.label_sim_time = QLabel('Add simulation time', self)
        self.label_sim_time.move(50,400)
        self.label_sim_time.resize(150, 20)
        self.sim_time_line = QLineEdit(self)
        self.sim_time_line.move(50, 420)
        self.sim_time_line.resize(150, 30)
        self.sim_time_line.editingFinished.connect(self.get_sim_time)
        self.sim_time_line.setEnabled(False)
        
        
        self.label_time_steps = QLabel('Add number time steps per period', self)
        self.label_time_steps.move(300,400)
        self.label_time_steps.resize(250, 20)
        self.time_steps_line = QLineEdit(self)
        self.time_steps_line.move(300, 420)
        self.time_steps_line.resize(150, 30)
        self.time_steps_line.editingFinished.connect(self.get_time_steps)
        self.time_steps_line.setEnabled(False)
        
        
        self.btn_simulate = QPushButton("SIMULATE", self)
        self.btn_simulate.clicked.connect(self.simulate)
        self.btn_simulate.resize(btn.minimumSizeHint())
        self.btn_simulate.move(50,480) 
        self.btn_simulate.setEnabled(False)
        
        self.btn_plot = QPushButton("PLOT", self)
        self.btn_plot.clicked.connect(self.plot)
        self.btn_plot.resize(btn.minimumSizeHint())
        self.btn_plot.move(300,480) 
        self.btn_plot.setEnabled(False)
        

        self.show()
              

    def file_open(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        self.open_file = open(name[0],'r')
        text = self.open_file.read()
         
        choice = QMessageBox.question(self, 'Correct file' , "Is the loaded file correct?\n\n" + text,
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.statusBar.showMessage("Input file chosen. Parsing converter netlist.", 2000)
            self.open_file = open(name[0],'r')
            parse_input_file(model, self.open_file)
            if not self.comboBox.isEnabled():
                self.check_control()
        else:
            self.open_file = None
            

    def file_save(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        self.save_file = name[0]  + '.npy'


    def control_choice(self, text):
        QApplication.setStyle(QStyleFactory.create(text))
        choice = QMessageBox.question(self, 'Control method' , "Is the chosen control method: " + text + "?",
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.comboBox.setEnabled(False)
            self.statusBar.showMessage("Control method chosen.", 2000)
            self.control_method = text
            if (text == "Constant frequency and duty ratio") or (text == "Nonlinear Model Predictive Controller"):
                self.label.setVisible(True)
                self.duty_ratio_line.setVisible(True)
            else:
                self.button_controller.setVisible(True)
                self.discretization_method_box.setVisible(True)
            if self.open_file != None:
                self.check_control()
            else:
                self.statusBar.showMessage("Choose input netlist file in File -> Open file.", 2000)
        else:
            pass
    
    # functions for control formulation
    def check_control(self):
        list_switch = model.get_controlled_switches_indexes()
               
        for item in list_switch:
            self.on_switches_box.addItem('switch ' + str(item))   
        
        self.on_switches_box.setEnabled(True)
        
        inductors = model.get_inductors()
        for inductor in inductors:
            self.output_box.addItem('inductor ' + str(inductor.get_index()))
        capacitors = model.get_capacitors()
        for capacitor in capacitors:
            self.output_box.addItem('capacitor ' + str(capacitor.get_index()))
        nodes = model.get_nodes()
        for node in nodes:
            if node.index() > 0:
                self.output_box.addItem('node ' + str(node.index()))


    def btnclicked_on_switches(self, text):
        index = 1 << (int(text.split()[1])-1)
        if not (index & self.on_switches):
            QApplication.setStyle(QStyleFactory.create(text))
            choice = QMessageBox.question(self, 'Driver controlled on switch' , "Is the chosen " + text + " driver controlled?",
                                                QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.on_switches = self.on_switches | index
                self.on_switches_list.append(int(text.split()[1]))
                if bin(self.on_switches).count('1') < self.on_switches_box.count()-1:
                    choice = QMessageBox.question(self, 'Driver controlled on switch' , "Are swithces: " + str(self.on_switches) + " all switches controlled by "\
                                                   "driver's output?",
                                                    QMessageBox.Yes | QMessageBox.No)
                if (choice == QMessageBox.Yes):
                    model.set_control(self.on_switches, 'on_state')
                    self.on_switches_box.setEnabled(False)
                    list_switch = model.get_controlled_switches_indexes() 
                    for item in self.on_switches_list:
                        list_switch.remove(item)
                    
                    if len(list_switch) > 0:
                        for item in list_switch:
                            self.off_switches_box.addItem('switch ' + str(item)) 
                            self.off_switches_box.setEnabled(True)
                    else:
                        self.output_box.setEnabled(True)
                    
        return
    
    def btnclicked_off_switches(self, text):
        index = 1 << (int(text.split()[1])-1)
        if not (index & self.off_switches):
            QApplication.setStyle(QStyleFactory.create(text))
            choice = QMessageBox.question(self, 'Driver controlled off switch' , "Is the chosen " + text + " controlled with driver inverted output?",
                                                QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.off_switches = self.off_switches | index
                self.off_switches_list.append(int(text.split()[1]))
                if bin(self.off_switches).count('1') < self.off_switches_box.count()-1:
                    choice = QMessageBox.question(self, 'Driver controlled on switch' , "Are " + str(self.off_switches) + " all switches controlled by"\
                                                   "driver's output?", QMessageBox.Yes | QMessageBox.No)
                if (choice == QMessageBox.Yes):
                    model.set_control(self.off_switches, 'off_state')
                    self.off_switches_box.setEnabled(False)
                    self.output_box.setEnabled(True)              

    
    def btnclicked_output(self, text):
        line = text.split()
        line = list([line[0], int(line[1])])
        if not line in self.output:
            QApplication.setStyle(QStyleFactory.create(text))
            choice = QMessageBox.question(self, "Converter's output" , "Do you want to add " + text + " as converters output?",
                                                QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.output.append(line)
                
                if len(self.output) < self.output_box.count()-1:
                    choice = QMessageBox.question(self, "Converter's output" , "Are " + str(self.output) + " all converter's outputs?",                                               
                                                    QMessageBox.Yes | QMessageBox.No)
                if (choice == QMessageBox.Yes):
                    model.set_output(self.output)
                    model.initialise_output()
                    self.output_box.setEnabled(False)  
                    if self.control_method == "PID controller":
                        self.frequency_line.setEnabled(True)
                        self.button_controller.setEnabled(True)
                        self.discretization_method_box.setEnabled(True)
                    else:
                        self.duty_ratio_line.setEnabled(True)
                        self.frequency_line.setEnabled(True)
                        
                        
    def btnclicked_discretization_method(self, text):
        self.discretization_method = text
        self.discretization_method_box.setEnabled(False)
        self.statusBar.showMessage("Choose file with coefficients.", 3000)
        
    def get_duty_ratio(self):
      self.duty_ratio = float(self.duty_ratio_line.text())
      if (self.duty_ratio > MIN_D and self.duty_ratio < MAX_D):
          self.statusBar.showMessage("Entered duty ratio is valid and equal " + str(self.duty_ratio) + ".")
          self.duty_ratio_line.setEnabled(False)     
          if not (self.frequency_line.isEnabled()):
              self.time_steps_line.setEnabled(True)
              self.sim_time_line.setEnabled(True)
      else:
          self.statusBar.showMessage("Entered duty ratio is not valid.") 
          self.duty_ratio_line.clear()
          self.duty_ratio = 0
          
    def open_controller_dir(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        self.open_file = open(name[0],'r')
        self.controller_coeffs = literal_eval(self.open_file.read())
        self.button_controller.setEnabled(False)
        if not (self.frequency_line.isEnabled()):
              self.time_steps_line.setEnabled(True)
              self.sim_time_line.setEnabled(True)
        
                    
    def get_frequency(self):
      self.frequency = float(self.frequency_line.text())
      if (self.frequency > MIN_F and self.frequency < MAX_F):
          self.statusBar.showMessage("Entered frequency is valid and equal " + str(self.frequency) + ".")
          self.frequency_line.setEnabled(False)         
          if ((self.control_method == "Constant frequency and duty ratio") or (self.control_method == "Nonlinear Model Predictive Controller") \
          and (not (self.duty_ratio_line.isEnabled()))):
              self.time_steps_line.setEnabled(True)
              self.sim_time_line.setEnabled(True)
          elif (self.control_method == "PID controller") and (not (self.button_controller.isEnabled() \
                                                              and self.discretization_method_box.isEnabled())):
              self.time_steps_line.setEnabled(True)
              self.sim_time_line.setEnabled(True)         
      else:
          self.statusBar.showMessage("Entered frequency is not valid.")
          self.frequency_line.clear()
          
    def get_sim_time(self):
      self.sim_time = float(self.sim_time_line.text())
      if (self.sim_time > 0):
          self.statusBar.showMessage("Entered simulation time is valid and equal " + str(self.sim_time) + ".")
          self.sim_time_line.setEnabled(False)  
          if not (self.time_steps_line.isEnabled()):
              self.btn_simulate.setVisible(True)
              self.btn_simulate.setEnabled(True) 
              self.btn_plot.setVisible(True)
      else:
          self.statusBar.showMessage("Entered duty ratio is not valid.") 
          self.sim_time_line.clear()
          self.sim_time = 0

    def get_time_steps(self):
      self.time_step_points = float(self.time_steps_line.text())
      if (self.time_step_points > 0):
          self.statusBar.showMessage("Entered number of time steps per one period is valid and equal " + str(self.time_step_points) + ".")
          self.time_steps_line.setEnabled(False)  
          if not (self.sim_time_line.isEnabled()):
              self.btn_simulate.setVisible(True)
              self.btn_simulate.setEnabled(True)   
              self.btn_plot.setVisible(True)
      else:
          self.statusBar.showMessage("Entered duty ratio is not valid.") 
          self.time_steps_line.clear()
          self.time_step_points = 0        
          
          

    def simulate(self):
        global state_space_model, controller, model
        self.statusBar.showMessage("Simulating...")
        if self.control_method == "Constant frequency and duty ratio": 
            controller = Controller_pid.Controller(self.on_switches_list, self.off_switches_list, 'None', self.duty_ratio, self.frequency)
        elif self.control_method == "PID controller":
            controller = Controller_pid.Controller(self.on_switches_list, self.off_switches_list, self.discretization_method,\
                                                    self.controller_coeffs, self.frequency)        
        else:
            pass
        
        state_space_model = State_space_model(model)
        state_space_model.form_states()
        state_space_model.form_state_lists()
        state_space_model.print_states()
        
        if (self.control_method == "Constant frequency and duty ratio") or (self.control_method == "PID controller"): 
            simulate_eig.simulate(state_space_model.get_beginning_state(), model, controller, \
                                                   self.sim_time, self.time_step_points, self.save_file)
        else:
            simulate_nmpc.simulate(state_space_model, self.sim_time, int(self.time_step_points), [self.duty_ratio], self.frequency, self.save_file)
        self.btn_simulate.setEnabled(False)
        self.btn_plot.setEnabled(True)
        self.statusBar.showMessage("Simulation finished.")
        
    def plot(self):
        self.statusBar.showMessage("Plotting...")
        self.diagram.show()
        self.diagram.plot(self.save_file)
        self.btn_plot.setEnabled(False)

            
       
    def close_application(self):
        choice = QMessageBox.question(self, 'Close application' , "Do you want to exit application?",
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.statusBar.showMessage("Closing application.", 1000)
            
            self.diagram.close()
            time.sleep(1)
            sys.exit()
        else:
            pass
        
  
def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())


run()





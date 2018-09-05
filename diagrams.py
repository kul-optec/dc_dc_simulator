from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from math import * 
from pylab import *
import sympy

# global
dictionary = {0 : '', 3 : '\mbox{m}', 6 : '\mu', 9 : '\mbox{n}', 12 : '\mbox{p}'}

class Diagrams(QWidget):
    def __init__(self, parent = None):
        super(Diagrams, self).__init__(parent)
        
        self.figure = None #Figure(figsize=(10, 8))
        self.subplots = []
        
        # it takes the `figure` instance as a parameter to __init__, set the layout
        self.layout = QVBoxLayout()
        
        self.setLayout(self.layout)
        self.setGeometry(50, 50, 1800, 1000)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.red)
        self.setPalette(p)
        self.setWindowTitle("Time diagrams")
               
    def plot(self, file_name):
        # reading input file
        npy_file = open(file_name, 'rb')
        m = load(npy_file)       
        while npy_file.read(1):
        	try:
        		npy_file.seek(-1, 1)
        		n = load(npy_file)
        		m = column_stack((m,n))
        	except EOFError or IOError:
        		break           
        npy_file.close()
        
        time_coeff = 10 ** (ceil(log10(1.0 / float(max(m[0]))) / 3) * 3)
        time_min = float(min(m[0]))
        time_max = float(max(m[0]))
        
        # plotting diagrams
        close('all')
        
        rc('text', usetex = True)
        rc('text.latex', preamble = r'\usepackage{amsmath}, \usepackage{amsfonts}')
        rc('font', family='serif', weight='normal', style='normal', size = 7)
        
        self.figure = Figure(figsize=(6, 2 * (m.shape[0] - 1)), dpi = 600)
        
        self.canvas = FigureCanvas(self.figure) # this is the Canvas Widget that displays the `figure`
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        
        subplots_adjust(wspace = 0.2, hspace = 0.2)
        
        for i in range(1, m.shape[0]):
        	
            self.subplots.append(self.figure.add_subplot(m.shape[0], 1, i))
            
            m_max = float(max(m[i]))
            m_min = float(min(m[i]))
            
            coeff =  10 ** (ceil(log10(1.0 / max(abs(m_min), abs(m_max))) / 3) * 3)
            
            self.subplots[i-1].plot(m[0], m[i], linewidth = 1)
            self.subplots[i-1].set_xlim(time_min, time_max)
            
            delta = 0.2 * float(max([abs(min(m[i])), abs(m_max)]))
            self.subplots[i-1].set_ylim(float(min(m[i]) - delta), float(max(m[i]) + delta))
            y_arange = arange(float(m_min * coeff), (float(m_max + (m_max - m_min) / 8)  * coeff), \
            			float(float(m_max - m_min) * coeff / 4))
            self.subplots[i-1].set_yticks(linspace(float(min(m[i])), float(max(m[i])), 5), ['{:.1f}'.format(value) for value in y_arange])
        
            t_max = float(max(m[0]))
            t_min = float(min(m[0]))
            if i == m.shape[0] - 1:
                time_arange = arange(float(t_min * time_coeff), float((t_max + (t_max - t_min) / 20)  * time_coeff), \
        			float(t_max - t_min) * time_coeff / 10)
                self.subplots[i-1].set_xticks(linspace(time_min, time_max, 11))
                self.subplots[i-1].set_xticklabels(['{:.1f}'.format(t) for t in time_arange])
            else:
                self.subplots[i-1].set_xticks(linspace(time_min, time_max, 11))
                self.subplots[i-1].set_xticklabels([])
        	
        	
            if i <= m.shape[0] * 0.5:
                label = sympy.latex('$i_{L' + str(i) + '} \; [ ' + dictionary[log10(coeff)] + '\mbox{A}]$')
                self.subplots[i-1].set_ylabel('$%s$' %label)
            else:
                label = sympy.latex('$v_{C' + str(i - m.shape[0] // 2) + '} \; [' + dictionary[log10(coeff)] + '\mbox{V}]$')
                self.subplots[i-1].set_ylabel('$%s$' %label)
        		
        		
        self.subplots[i-1].set_xlabel(r'$t \; [' + dictionary[log10(time_coeff)] + '\mbox{s}]$')
        fig_name = file_name.split('.npy')[0]
        self.figure.savefig(fig_name + '.pdf', bbox_inches='tight', dpi = 600) # saving plot in file


        self.canvas.draw()

        
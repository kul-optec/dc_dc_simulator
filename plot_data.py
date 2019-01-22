from pylab import *
from math import *
import sympy

from cycler import cycler

dictionary = {0 : '', 3 : '\mbox{m}', 6 : '\mu', 9 : '\mbox{n}', 12 : '\mbox{p}'}

def plot_data(file_names, horizons): 
    subplots = []
    fig = 0
    index = 0
    for file_name in file_names:
        npy_file = open(file_name, 'rb')
        m = load(npy_file)
        
        
        while npy_file.read(1):
            
        	try:
        		npy_file.seek(-1, 1)
        		m = column_stack((m,load(npy_file)))
        	except EOFError or IOError:
        		break
            
        npy_file.close()
        
        if file_name == file_names[0]:
            close('all')
            
            rc('text', usetex = True)
            rc('text.latex', preamble = r'\usepackage{amsmath}, \usepackage{amsfonts}')
            rc('font', family='serif', weight='normal', style='normal')
            
            fig = figure(1, figsize=(6, 2 * (m.shape[0] - 1)), dpi = 600)
            subplots_adjust(wspace = 0.2, hspace = 0.2)
            rc('axes', prop_cycle=(cycler('color', list('rbgk')) +
                           cycler('linestyle', ['-', '-.', '--', ':'])))
            
            time_coeff = 10 ** (ceil(log10(1.0 / max(m[0])) / 3) * 3)
            time_min = float(min(m[0]))
            time_max = float(max(m[0]))
            
                 
            
            for i in range(1, m.shape[0]):
                subplots.append(fig.add_subplot(m.shape[0], 1, i)) 
          
                if i == m.shape[0] - 1:
                    
                    t_max = float(max(m[0]))
                    t_min = float(min(m[0]))
                    time_arange = arange(float(t_min * time_coeff), float((t_max + (t_max - t_min) / 20)  * time_coeff), \
            			float(t_max - t_min) * time_coeff / 10)
                    subplots[i-1].set_xticks(linspace(time_min, time_max, 11))
                    subplots[i-1].set_xticklabels(['{:.1f}'.format(t) for t in time_arange])
                else:
                    t_max = float(max(m[0]))
                    t_min = float(min(m[0]))
                    subplots[i-1].set_xticks(linspace(time_min, time_max, 11))
                    subplots[i-1].set_xticklabels([])
                
                subplots[i-1].set_xlim(time_min, time_max)
                coeff =  10 ** (ceil(log10(1.0 / max(abs(m[i]))) / 3) * 3)
                m_max = float(max(m[i]))
                m_min = float(min(m[i]))
                delta = 0.2 * float(max([abs(min(m[i])), abs(m_max)]))
                subplots[i-1].set_ylim(float(min(m[i]) - delta), float(max(m[i]) + delta))
                y_arange = arange(float(m_min * coeff), (float(m_max + (m_max - m_min) / 8)  * coeff), \
            			float(float(m_max - m_min) * coeff / 4))
                subplots[i-1].set_yticks(linspace(float(min(m[i])), float(max(m[i])), 5), ['{:.1f}'.format(value) for value in y_arange])
                if i <= m.shape[0] * 0.5:
                    label = sympy.latex('$i_{L' + str(i) + '} \; [ ' + dictionary[log10(coeff)] + '\mbox{A}]$')
                    subplots[i-1].set_ylabel('$%s$' %label)
                    subplots[i-1].set_xticks([])
                else:
                    label = sympy.latex('$v_{C' + str(i - m.shape[0] // 2) + '} \; [' + dictionary[log10(coeff)] + '\mbox{V}]$')
                    subplots[i-1].set_ylabel('$%s$' %label)
        
        for i in range(1, m.shape[0]):
        	
#            subplot(m.shape[0], 1, i)
            lab = sympy.latex('$N =' + str(horizons[index]) + '$')
            
            subplots[i-1].plot(m[0], m[i], label = lab)
            
            
        index += 1
        

    		
    subplots[0].legend(loc="lower left", bbox_to_anchor=(0, 1.02, 1, 0.2),
          ncol=3, fancybox=True, shadow=True) 
    xlabel(r'$t \; [' + dictionary[log10(time_coeff)] + '\mbox{s}]$')
    savefig('state_variables.pdf', bbox_inches='tight', dpi = 600)

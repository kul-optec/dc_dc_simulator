# CLASS CONTROLLER
# 

from math import *
from scipy import poly1d


class Controller:
    def __init__(self, on_state_switches, off_state_switches, discretization_method,\
                 coefficients, frequency, relative_precision = 0):
        self.__on_state_switches = on_state_switches
        self.__off_state_switches = off_state_switches
        self.__switches = []

        for switch in on_state_switches:
            self.__switches.append(switch)

        for switch in off_state_switches:
            self.__switches.append(switch)	
		
        self.__frequency = frequency
        self.__period = 1.0 / frequency
		
        # for error calculation
        self.__error_leading_param = []
        if discretization_method != 'None':
            self.__error_list = [[] for dummy in range(len(coefficients))]
        else:
            self.__error_list = []
        self.__error_coeffs = []
        self.__reference_values = []

        # for duty ratio calculation
        self.__duty_ratio = []
        self.__duty_ratio_coeffs = []
        self.__result = []
		
        if discretization_method == 'None':
            self.__duty_ratio = [coefficients]
		
        else:
            for coefficient in coefficients:
                self.__reference_values.append(coefficient[2])
                self.calculate_coeffs(discretization_method, coefficient[0], coefficient[1])

		
    def calculate_coeffs(self, discretization_method, nominator, denominator): #calculate coeffs -- used only once inside initialization
        """
        calculates coefficients of the transfer function given as continuous for difference equation
        can be calculated as bilinear or pole-zero matched
        returns two lists of coefficients - first for duty ratio and second for error
        """
        c_tf_poly_nom = poly1d(nominator) # continuous tf nominator list coefficients to poly1d class
        c_tf_poly_denom = poly1d(denominator) # continuous tf denominator list coefficients to poly1d class

        c_zeros = c_tf_poly_nom.r        # cont. zeros found
        c_poles = c_tf_poly_denom.r      # cont. poles found

        d_zeros = []    # discrete zeros init list
        d_poles = []    # discrete poles init list

        if discretization_method == 'pole_zero_matching' :
            # discrete zeros calculation:
            if (c_tf_poly_nom.order == 0):
                d_zeros.append(-1)
            else:
                for i in range(len(c_zeros)):
                    d_zeros.append(exp(self.__period * c_zeros[i]))

            # discrete poles calculation:
            for i in range(len(c_poles)):
                d_poles.append(exp(self.__period * c_poles[i]))

        elif discretization_method == 'bilinear' :
            for i in range(len(c_zeros)):
                d_zeros.append(0)

            # discrete poles calculation:
            for i in range(len(c_poles)):
                d_poles.append(0)

		# Form discrete transfer function
        d_tf_poly_nom = poly1d(d_zeros,'True')    # construct poly from its roots:
        d_tf_poly_denom = poly1d(d_poles,'True')    # construct poly from its roots:
        self.__error_leading_param.append(d_tf_poly_nom.order - d_tf_poly_denom.order)

        # match gain:
        K = abs(d_tf_poly_denom(exp(0.01 * self.__period))) * abs(c_tf_poly_nom(0.01j)) \
				/(abs(d_tf_poly_nom(exp(0.01 * self.__period))) * abs((c_tf_poly_denom(0.01j))))
        d_tf_poly_nom = d_tf_poly_nom * K

        # extract coefficients from previous two poly instances

        # d coefficients
        # d[i] = k1*d[i-1] + k2*d[i-2]+ ... + kn*d[i-n]
        # duty_ratio_coef = [k1,k2, ... kn]
        duty_ratio_coef = []
        for i in range(d_tf_poly_denom.order):
            duty_ratio_coef.append(-d_tf_poly_denom[d_tf_poly_denom.order-1-i]/d_tf_poly_denom[d_tf_poly_denom.order])
        self.__duty_ratio_coeffs.append(duty_ratio_coef)

        # error coefficients:
        # d[i] = ke_1*e[i+m-n]+ke_2*e[i+m-n-1]+ ... 
        coeffs = []
        for i in range(d_tf_poly_nom.order+1):
            coeffs.append( d_tf_poly_nom[d_tf_poly_nom.order-i]/d_tf_poly_denom[d_tf_poly_denom.order] )
        self.__error_coeffs.append(coeffs)
		
	##################################################################################################################
	##### to get general information
    def get_switches(self):
        return self.__switches
		
    def get_period(self):
        return self.__period

	##################################################################################################################
	
    def check_change(self, time, step): # for now easy check for duty ratio
        """
        check if the state is to change initiated by controller
        checks weather the condition for turning off the switch is satisfied
        """
        if ((time - floor(time / self.__period) * self.__period) <= (self.__duty_ratio[-1] * self.__period) \
        and (time - floor(time / self.__period) * self.__period + step) > (self.__duty_ratio[-1] * self.__period)) or \
        (((time - floor(time / self.__period) * self.__period) <= self.__period) \
         and ((time - floor(time / self.__period) * self.__period + step) > self.__period)):
            return True
        return False

    def is_period(self, time, step):
        return  round(time, 9) == round(round(time * self.__frequency, 0) / self.__frequency, 9)
	
    def change_time(self, time):
        """
        returns switching time
        """
        if (time - floor(time / self.__period) * self.__period) <= (self.__duty_ratio[-1] * self.__period):
            return self.__duty_ratio[-1] * self.__period + floor(time / self.__period) * self.__period
        else:	
            return ceil(time / self.__period) * self.__period

	#################################################################################################################

    def get_duty_ratio(self):
        """
        returns last duty ratio
        """
        return self.__duty_ratio[-1]

    def calculate_period(self, output):
        """
        calculates duty ratio for the next switching interval
        """
        self.__current_output = output
        self.calculate_current_duty_ratio()

    def calculate_current_duty_ratio(self):
        for dummy in range(len(self.__error_list)):
            self.__error_list[dummy].append(-self.__current_output[dummy] + self.__reference_values[dummy])
		
        result = 0
        
        for dummy_i in range(len(self.__error_list)):
#            print(self.__error_coeffs[dummy_i], self.__error_list[dummy_i], self.__error_leading_param[dummy_i])
#            print(len(self.__error_coeffs[dummy_i]))
            for dummy_j in range(min(len(self.__error_coeffs[dummy_i]), len(self.__error_list[dummy_i]) - self.__error_leading_param[dummy_i])):
                result += self.__error_list[dummy_i][-1 - self.__error_leading_param[dummy_i] - dummy_j] \
                        * self.__error_coeffs[dummy_i][dummy_j]

        for item in self.__duty_ratio_coeffs:
            for dummy in range(min(len(item), len(self.__duty_ratio))):
                result += self.__result[-1 - dummy] * item[dummy]
		
        self.__result.append(result)
        if result > 1 :
            result = 1
        elif result < 0 :
            result = 0
				
        if not len(self.__error_list):
            self.__duty_ratio.append(self.__duty_ratio[-1])
        else:
            self.__duty_ratio.append(result)
	
    def take_output(self, output):
        self.__current_output = output


    def printing(self):
        """
        printing in file 
        """
        f = open('coeffs.txt','w')
        for dummy in range(len(self.__error_list)):
            f.write('leading index / duty ratio coeffs / error coeffs ' + \
                    str(self.__error_leading_param[dummy]) + " " + str(self.__duty_ratio_coeffs[dummy]) \
                    + " " + str(self.__error_coeffs[dummy]) + "\n\n")
            f.write("error: " + str(self.__error_list[dummy]) + "\n\n")
		
        f.write("duty ratio: " + str(self.__duty_ratio) + "\n\n")
        f.write("result calculation -- previous duty ratio limit: " + str(self.__result))	
        f.close() # you can omit it, in most cases as the destructor will call if
		


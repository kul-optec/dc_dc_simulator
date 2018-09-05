## DC-DC converter's simulator
Simulator offers GUI for the transient simulation of PWM DC-DC converters. Simulation can be done in open loop,
with PID controller applied or with control using nonlinear model predictive control (NMPC) concepts. 

Usage of the simulator and its design are described in the [User manual](https://kul-forbes.github.io/dc_dc_simulator/Tutorial.pdf).

## Install instructions
Program is written in Python 3.6 programming language using CASADI [1](https://github.com/casadi/casadi/wiki) package. For MPC simulator uses [NMPC-codegen](https://kul-forbes.github.io/nmpc-codegen/), which is integrated inside this simulator. 

For the usage of the simulator, it is necessary to 
have installed:
- Casadi version >= 3.2
- Gcc GNU compiler, Clang LLVM compiler, Intel C compiler or the Microsoft C Compiler
- cmake -H. -Bbuild -DCMAKE_C_COMPILER=clang creates a build system with clang compiler and Cmake

More informtion about installation can be found on the page [Install](https://kul-forbes.github.io/nmpc-codegen/install/Python_install.html).

## Published papers 
1) A. Lekić, 2017. Simulation of PWM DC-DC converters using eigenvalues and eigenvectors. Journal of Electrical Engineering, 68(1), pp.13-22.
2) A. Lekić, 2014, Automated DC-DC converters symbolic state-space model generation by the use of free software, In Proceedings of the 22nd Telecommunications Forum Telfor (TELFOR), 2014, pp. 995-998.





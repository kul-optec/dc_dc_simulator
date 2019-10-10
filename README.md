## DC-DC converter's simulator
Simulator offers GUI for the transient simulation of PWM DC-DC converters. Simulation can be done in open loop,
with PID controller applied or with control using nonlinear model predictive control (NMPC) concepts. 

Usage of the simulator and its design are described in the [User manual](https://github.com/kul-forbes/dc_dc_simulator/blob/master/Tutorial.pdf).

## Install instructions
Program is written in Python 3.6 programming language using CASADI [1](https://github.com/casadi/casadi/wiki) package. For MPC simulator uses [NMPC-codegen](https://kul-forbes.github.io/nmpc-codegen/), which is integrated inside this simulator. 

For the usage of the simulator, it is necessary to 
have installed:
- Casadi version >= 3.2 and < 3.5
- Gcc GNU compiler 

Windows users might use MSYS2: https://www.msys2.org/ and install the necessary using following commands.

Open msys2.exe and type: `pacman -Syu` to update MSYS2

Close the window and open it again and type: 
```
						 pacman -Sy pacman		(to update the package database)
						 pacman -S mingw-w64-x86_64-toolchain		(for a toolchain)
						 pacman -S make		(to install make)
```
						 
Add folders `<MSYS2 root>/mingw64/bin` and `<MSYS2 root>/usr/bin` to path.

Linux users have this installed.		 			

- Cmake: https://cmake.org/

More informtion about installation can be found on the page [Install](https://kul-forbes.github.io/nmpc-codegen/install/Python_install.html).

## Published papers 
1) A. Lekić, 2017. Simulation of PWM DC-DC converters using eigenvalues and eigenvectors. Journal of Electrical Engineering, 68(1), pp.13-22.
2) A. Lekić, 2014, Automated DC-DC converters symbolic state-space model generation by the use of free software, In Proceedings of the 22nd Telecommunications Forum Telfor (TELFOR), 2014, pp. 995-998.





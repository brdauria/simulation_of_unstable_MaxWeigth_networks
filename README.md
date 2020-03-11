# Simulation algorithms for "Stability and Instability of the MaxWeight Policy"

This repository contains the code used to generate some figures contained in the publication  
[M. Bramson, B. D'Auria and N. Walton (2020)](https://arxiv.org/abs/1909.10825), _Stability and Instability of the MaxWeight Policy_.


## Setup

After cloning the repository, install a python virtual environment

- On macOS and Linux:
```python3 -m venv env```

- On Windows:
```py -m venv env```

Activate it
- On macOS and Linux:
```source env/bin/activate```
- On Windows:
```.\env\Scripts\activate```

Install the dependencies  
```pip -r requirements.txt```

## Usage
To run the scripts, execute one of the following commands
- ```python Rybko-Stolyar_network.py``` (To make Figures 2 and 3),
- ```python multiclass_network.py``` (To make Figure 7),
- ```python variablespeed_singleclass_network.py``` (To make Figure 8).

To get help, execute the command with the option ```--help```.  
This option lists all the available parameters that can be passed to the script via the command line.  
 
For example:
```{python}
> python Rybko-Stolyar_network.py --help

Usage: Rybko-Stolyar_network.py [OPTIONS]

Options:
  --a FLOAT                       Mean arrival rate
  --nu INTEGER                    Mean service rate.
  --J INTEGER                     J+1 is the number of queues of each
                                  component.
  --init-A0 INTEGER               Queue length at queue A0.
  --init-Aj INTEGER               Queue length at queue Aj.
  --init-B0 INTEGER               Queue length at queue B0.
  --init-Bj INTEGER               Queue length at queue Bj.
  --runtime INTEGER               Discrete time simulation length.
  --save-to-file / --no-save-to-file
                                  Enable saving pictures to files.  [default:
                                  True]
  --output-dir TEXT               Set the output directory for pictures.
  --seed INTEGER                  Seed used to generate random quantities.
  --av INTEGER                    Windows parameter to compute moving
                                  averages.
  --version TEXT                  Suffix to append to the output files.
                                  Example: "v1"
  --cut / --no-cut                Visualize the cut region.  [default: True]
  --cut-level INTEGER             Denote a which level to start the cut.
  --cache / --no-cache            Read the simulation data form a file.
                                  [default: True]
  --cache-dir TEXT                Set the cache directory for simulations.
  --record / --no-record          Record simulation data and pictures to
                                  files.  [default: True]
  --debug / --no-debug            Enable debugging behaviour.  [default:
                                  False]
  --show-progress / --no-show-progress
                                  Show percentage of simulation completed.
                                  [default: True]
  --help                          Show this message and exit.
```

## Example of outputs
When the Python scripts are called with the ```--save-to-file``` option enabled, 
they will save in the ```--output-dir``` the output pictures in ```.pdf``` and ```.jpeg``` formats.

In the following the pictures that are obtained by calling the scripts with the default parameters are shown.
These same pictures were used in the publication  
[M. Bramson, B. D'Auria and N. Walton (2020)](https://arxiv.org/abs/1909.10825), _Stability and Instability of the MaxWeight Policy_.

- ```Rybko-Stolyar_network.py```  
Figure 2:  
<img src="https://github.com/brdauria/simulation_of_unstable_MaxWeigth_networks/raw/master/output/simulation_J30_a0p58_nu6_r500000_seed8086.jpeg" width="400">  
Figure 3:  
<img src="https://github.com/brdauria/simulation_of_unstable_MaxWeigth_networks/raw/master/output/cut-simulation_J30_a0p58_nu6_r500000_seed8086.jpeg" width="400">    

- ```multiclass_network.py```  
Figure 7:  
<img src="https://github.com/brdauria/simulation_of_unstable_MaxWeigth_networks/raw/master/output/simulation_K20_a1_eps0p1791_r50000_seed8086.jpeg" width="400">    

- ```variablespeed_singleclass_network.py```  
Figure 8:  
<img src="https://github.com/brdauria/simulation_of_unstable_MaxWeigth_networks/raw/master/output/simulation_m20_a1_eps0p1791_r50000_seed8086.jpeg" width="400">    

## License
  
The MIT License

Copyright (c) 2020 Maury Bramson, Bernardo D'Auria, Neil Walton.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Acknowledgments
The research of _M. Bramson_ was partially supported by **NSF grant DMS-1203201**.  
The research of _B. D’Auria_ was partially supported by the **Spanish Ministry of Economy and Competitiveness
Grant MTM2017-85618-P** (via FEDER funds). Part of this research was done while he was a visiting professor
at the NYUAD (Abu Dhabi, United Arab Emirates).
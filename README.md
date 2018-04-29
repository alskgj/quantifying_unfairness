Quantifying Unfairness
===

This is a platform to run experiments on YouTube and Vimeo in parallel. 
To run an experiment write an experiment script, examples are available in the experiments folder. 
Since this project makes heavy use of TC, it only works on Linux. 



## Installation
- Install python 3.6 or higher
- Clone this repository
- Change the NETWORK_INTERFACE flag in config.py to your network interface (run ifconfig to find the name)
- Install all dependencies in the requirements.txt file:
```
pip install -r requirements.txt
```
or, if you are not using a virtual environment: 
```
python3.6 -m pip install -r requirements.txt
``` 
If you have problems with the cairosvg installation you may need to install additional tools, try:
```
sudo apt install cairo python3-dev libffi-dev
```
If you are not using a debian based distribution, names may vary. 
For further information about installing cairosvg consult: http://cairosvg.org/documentation/#installation

- Traffic shaping requires root so you either need to allow running sudo without a password prompt:
```
sudo visudo
```
and then add the line
```
yourusername ALL=(ALL) NOPASSWD: ALL
```
or run the whole script as root.


## Documentation

Documentation is available in the docs folder.

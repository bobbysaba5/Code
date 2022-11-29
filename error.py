import matplotlib.pyplot as plt
from metpy.plots import Hodograph
from metpy.units import units
import numpy
import pickle

path = '/Users/bobbysaba/Documents/Thesis'

# open data files
with open(path + '/storm_vad.pickle', 'rb') as fh:
    storm_vad = pickle.load(fh) 

with open(path + '/sonde.pickle', 'rb') as fh:
    sonde_data = pickle.load(fh) 
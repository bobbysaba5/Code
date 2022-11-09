import os.path
import numpy as np
import pickle
import datetime as dt
import pandas as pd

data = os.listdir('/Users/bobbysaba/Documents/Thesis/Radiosonde')
path = '/Users/bobbysaba/Documents/Thesis/Radiosonde/'

file = pd.read_csv(path + '20170509_210308.csv')
file_2 = pd.read_csv(path + '20190518_195919.csv')
file_3 = pd.read_csv(path + '20220524_193821.csv')

    
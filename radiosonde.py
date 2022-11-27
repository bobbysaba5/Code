import os.path
import numpy as np
import pickle
import datetime as dt
import pandas as pd

data = os.listdir('/Users/bobbysaba/Documents/Thesis/Radiosonde')
sonde_path = '/Users/bobbysaba/Documents/Thesis/Radiosonde/'
path = '/Users/bobbysaba/Documents/Thesis/'

sonde_data = {}

for file in data:
    date = file[0:8]
    if date not in sonde_data:
        sonde_data[date] = {}
    time = file[9:15]
    sonde = pd.read_csv(sonde_path + file)
    if len(sonde.columns) == 38:
        sonde = pd.read_csv(sonde_path + file, header = 2)
        sonde['Date-Time'] = sonde['Date-Time'].str[12:-1]
        if time not in sonde_data[date]:
            sonde_data[date][time] = {'time': sonde['Date-Time'], 'wdir': sonde['Filtered Wind Dir'], 'wspd': sonde['Filtered Wind Spd (m/s)'],
                             'height': sonde['Filtered Altitude (m)'], 'u': sonde['GPS Velocity East (m/s)'], 'v': sonde['GPS Velocity North (m/s)'],
                             'w': sonde['GPS Velocity Up (m/s)']}
    if len(sonde.columns) == 9:
        if time not in sonde_data[date]:
            sonde_data[date][time] = {'time': sonde['time(s)'], 'height': sonde['zagl(m)'], 'u': sonde['u(m/s)'], 'v': sonde['v(m/s)']}
            
# save radiosonde data 
with open('/Users/bobbysaba/Documents/Thesis/sonde.pickle', "wb") as output_file:
    pickle.dump(sonde_data, output_file)

# open storm vad and stare dicts
with open(path + 'sonde.pickle', 'rb') as fh:
    sonde_data = pickle.load(fh) 
    
with open(path + 'storm_vad.pickle', 'rb') as fh:
    storm_vad = pickle.load(fh) 
    
# convert datetime to str_time
for date in storm_vad:
    for storm in storm_vad[date]:
        storm_vad[date][storm]['str_time'] = [time.strftime('%H%M%S') for time in storm_vad[date][storm]['time']]
        

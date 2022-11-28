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
            sonde_data[date][time] = {'time': np.array(sonde['Date-Time']), 'wdir': np.array(sonde['Filtered Wind Dir']), 
                                      'wspd': np.array(sonde['Filtered Wind Spd (m/s)']),
                                      'height': np.array(sonde['Filtered Altitude (m)']),
                                      'w': np.array(sonde['GPS Velocity Up (m/s)']),'hour_first': time}
    if len(sonde.columns) == 9:
        if time not in sonde_data[date]:
            sonde_data[date][time] = {'time': np.array(sonde['time(s)']), 'height': np.array(sonde['zagl(m)']), 
                                      'u': np.array(sonde['u(m/s)']), 'v': np.array(sonde['v(m/s)']), 'hour_first': time}

del sonde_data['20170610']['010243'] # only upper air?
            
# fix height agl
for date in sonde_data:
    for time in sonde_data[date]:
        if 'w' in sonde_data[date][time]:
            sonde_data[date][time]['height'] = sonde_data[date][time]['height'] - sonde_data[date][time]['height'][0]
      
# trim data above 2km
for date in sonde_data:
    for time in sonde_data[date]:
        too_high = np.where(sonde_data[date][time]['height'] > 2000)[0]
        for v in sonde_data[date][time]:
            if v == 'hour_first':
                continue
            sonde_data[date][time][v] = np.delete(sonde_data[date][time][v], too_high)

# convert hour_start
for date in sonde_data:
    for time in sonde_data[date]:
        t = sonde_data[date][time]['hour_first']
        h = int(t[0:2])
        m = int(t[2:4])/60
        s = float(t[4:])/3600
        sonde_data[date][time]['hour_first'] = h + m + s

# calculate hour_last
for date in sonde_data:
    for time in sonde_data[date]:
        t = sonde_data[date][time]['time'][-1]
        try:
            if ':' in t:
                h = int(t[0:2])
                m = int(t[3:5])/60
                s = float(t[6:])/3600
                sonde_data[date][time]['hour_last'] = h + m + s
                continue
        except:
            s = float(t)/3600
            sonde_data[date][time]['hour_last'] = sonde_data[date][time]['hour_first'] + s
        
# save radiosonde data 
with open('/Users/bobbysaba/Documents/Thesis/sonde.pickle', "wb") as output_file:
    pickle.dump(sonde_data, output_file)
    

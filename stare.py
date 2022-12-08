import netCDF4 as nc
import os.path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pickle
import datetime as dt

untouched_data = ['rows', 'cols', 'height', 'no_data', 'covariance_matrix', 'lats']
data = os.listdir('/Users/bobbysaba/Documents/Thesis/STARE')
stare_path = '/Users/bobbysaba/Documents/Thesis/STARE'
path = '/Users/bobbysaba/Documents/Thesis'

stare = {}

# convert nc files to dictionary
for file in data:
    scan_info = file.split('.')
    date = scan_info[0]
    file = nc.Dataset(stare_path + '/' + file)
    time_list = []
    year = int(scan_info[0][0:4])
    month = int(scan_info[0][4:6]) 
    if date not in stare:
        stare[date] = {}
    for v in file.variables.keys():
        if v == 'base_time':
            continue
        stare[date][v] = file[v][:]
        if v == 'hour':
            for h in stare[date][v]:
                day = int(scan_info[0][6:])
                if h > 24:
                    h -= 24
                    day += 1
                hours = int(h)
                minutes = int((h*60) % 60)
                seconds = int((h*3600) % 60)
                try:
                    time_list.append(dt.datetime(year, month, day, hours, minutes, seconds))
                except:
                    day = 1
                    month += 1
                    time_list.append(dt.datetime(year, month, day, hours, minutes, seconds))
        if v == 'height' and year == 2019:
            stare[date]['height'] = stare[date]['height'] / 1000
        if v == 'velocity':
            stare[date]['w'] = stare[date]['velocity']
    stare[date]['time'] = np.array(time_list)
    try:
        del stare[date]['epochtime']
    except:
        continue
    
# delete lowest 3 values
for date in stare:
    stare[date]['height'] = np.delete(stare[date]['height'], [0,1,2])
    for v in stare[date]:
        if v in untouched_data:
            continue
        try:
            stare[date][v] = np.delete(stare[date][v], [0,1,2], 1)
        except:
            continue
        
#chop off data above 2km
for date in stare:
    too_high = np.where(stare[date]['height'] > 2)[0]
    stare[date]['height'] = np.delete(stare[date]['height'], too_high)
    for v in stare[date]:
        if np.ndim(stare[date][v]) == 2:
            stare[date][v] = np.delete(stare[date][v], too_high, 1)

# clean up bad data points             
for date in stare:
    for v in stare[date]:
        if np.ndim(stare[date][v]) == 2:
            if v != 'intensity':
                stare[date][v][stare[date]['intensity'] < 1.01] = np.nan

# find unique lats and get rid of -999 and nan                
for date in stare:
    stare[date]['lats'] = np.unique(stare[date]['lat'])
    if str(stare[date]['lats'][-1]) == 'nan':
        stare[date]['lats'] = np.delete(stare[date]['lats'], -1)
    if stare[date]['lats'][0] == -999:
        stare[date]['lats'] = np.delete(stare[date]['lats'], 0)
        
# save data
with open(path + '/stare.pickle', "wb") as output_file:
    pickle.dump(stare, output_file)
        
# create indexes for the start of new storm
storm_stare = {}
for date in stare:
    lat_list = stare[date]['lat'].tolist()
    storm_index = []
    if date not in storm_stare:
        storm_stare[date] = {}
    for storm in range(1,len(stare[date]['lats']) + 1):
        storm_stare[date][storm] = {}
    for lat in stare[date]['lats']:
        storm_index.append(lat_list.index(lat))
    storm_index.sort()
    storm_index[0] = 0
    storm_stare[date]['indexes'] = storm_index

# insert storm data
for date in storm_stare:
    indexes = storm_stare[date]['indexes']
    for n in storm_stare[date]:
        if type(n) == int:
            if n == 1 and len(indexes) == 1:
                storm_stare[date][1] = stare[date]
            if n == 1 and len(indexes) > 1:
                for v in stare[date]:
                    if np.ndim(stare[date][v]) == 2:
                        storm_stare[date][n][v] = stare[date][v][0:indexes[n]]
                    if np.ndim(stare[date][v]) == 1:
                        storm_stare[date][n][v] = stare[date][v]
                    if v == 'time' or 'hour':
                        storm_stare[date][n][v] = stare[date][v][0:indexes[n]]
            if len(indexes) == n:
                for v in stare[date]:
                    if np.ndim(stare[date][v]) == 2:
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:]
                    if np.ndim(stare[date][v]) == 1:
                        storm_stare[date][n][v] = stare[date][v]
                    if v == 'time' or 'hour':
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:]
            if len(indexes) > n:
                for v in stare[date]:
                    if np.ndim(stare[date][v]) == 2:
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:indexes[n]]
                    if np.ndim(stare[date][v]) == 1:
                        storm_stare[date][n][v] = stare[date][v]
                    if v == 'time' or 'hour':
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:indexes[n]]
                        
for date in storm_stare:
    del storm_stare[date]['indexes']
    
# delete scans with no data
for date in storm_stare:
    for storm in storm_stare[date]:
        while np.nansum(storm_stare[date][storm]['w'][0]) == 0.0:
            for v in storm_stare[date][storm]:
                if v in untouched_data:
                    continue
                storm_stare[date][storm][v] = np.delete(storm_stare[date][storm][v], 0, 0)
        while np.nansum(storm_stare[date][storm]['w'][-1]) == 0.0:
            for v in storm_stare[date][storm]:
                if v in untouched_data:
                    continue
                storm_stare[date][storm][v] = np.delete(storm_stare[date][storm][v], -1, 0)

with open(path + '/storm_stare.pickle', "wb") as output_file:
    pickle.dump(storm_stare, output_file)        

import netCDF4 as nc
import os.path
import matplotlib.pyplot as plt
import numpy as np
import pickle

data = os.listdir('/Users/bobbysaba/Documents/Thesis/VAD')
vad_path = '/Users/bobbysaba/Documents/Thesis/VAD'
path = '/Users/bobbysaba/Documents/Thesis'

vad = {}

# convert nc files to dictionary
for file in data:
    scan_info = file.split('.')
    date = scan_info[0]
    file = nc.Dataset(vad_path + '/' + file)
    time_list = []
    year = scan_info[0][0:4]
    if date not in vad:
        vad[date] = {}
    for v in file.variables.keys():
        vad[date][v] = file[v][:]
        if v == 'hour':
            for h in vad[date][v]:
                hours = int(h)
                minutes = (h*60) % 60
                seconds = (h*3600) % 60
                time_list.append('%2d:%02d:%2d' % (hours,minutes,seconds))
        if v == 'height' and year == '2019':
            vad[date]['height'] = vad[date]['height']/1000
        if v == 'windspeed':
            vad[date]['wspd'] = vad[date]['windspeed']
            del vad[date]['windspeed']
        if v == 'winddir':
            vad[date]['wdir'] = vad[date]['winddir']
            del vad[date]['winddir']
    vad[date]['time'] = time_list
    del vad[date]['hour']
    try:
        del vad[date]['epochtime']       
    except:
        continue

data = os.listdir('/Users/bobbysaba/Documents/Thesis/STARE')
stare_path = '/Users/bobbysaba/Documents/Thesis/STARE'

stare = {}

# convert nc files to dictionary
for file in data:
    scan_info = file.split('.')
    date = scan_info[0]
    file = nc.Dataset(stare_path + '/' + file)
    time_list = []
    year = scan_info[0][0:4]
    if date not in stare:
        stare[date] = {}
    for v in file.variables.keys():
        stare[date][v] = file[v][:]
        if v == 'hour':
            for h in stare[date][v]:
                hours = int(h)
                minutes = (h*60) % 60
                seconds = (h*3600) % 60
                time_list.append('%2d:%02d:%2d' % (hours,minutes,seconds))
        if v == 'height' and year == '2019':
            stare[date]['height'] = stare[date]['height']/1000
        if v == 'velocity':
            stare[date]['w'] = stare[date]['velocity']

    stare[date]['time'] = time_list 
    del stare[date]['hour']
    try:
        del stare[date]['epochtime']
    except:
        continue
           
#chop off data above 3km
for date in vad:
    h = np.where(vad[date]['height'] >= 3)[0][0]
    vad[date]['height'] = np.delete(vad[date]['height'], np.s_[h:])
    for v in vad[date]:
        if np.ndim(vad[date][v]) == 2:
            vad[date][v] = np.delete(vad[date][v], np.s_[h:], axis = 1)
            
for date in stare:
    h = np.where(stare[date]['height'] >= 3)[0][0]
    stare[date]['height'] = np.delete(stare[date]['height'], np.s_[h:])
    for v in stare[date]:
        if np.ndim(stare[date][v]) == 2:
            stare[date][v] = np.delete(stare[date][v], np.s_[h:], axis = 1)          

# get rid of all nan columns
for date in vad:
    for v in vad[date]:
        if v == 'base_time' or len(vad[date][v]) != len(vad[date]['wspd']) or np.ndim(vad[date][v]) > 2:
            continue
        no_data = np.where(np.isnan(vad[date]['wspd']).all(axis =  1))[0]
        initial = vad[date][v]
        if v == 'time':
            new_time = []
            for i in range(0, len(initial)):
                if i not in no_data:
                    new_time.append(initial[i])
            vad[date][v] = new_time
            continue
        new = np.ones(np.shape(initial))
        column = 0
        for i in range(0, len(initial)):
            if i not in no_data:
                new[column] = initial[i]
                column += 1
        vad[date][v] = new
            
for date in stare:
    for v in stare[date]:
        if v == 'base_time' or len(stare[date][v]) != len(stare[date]['w']) or np.ndim(stare[date][v]) > 2:
            continue
        no_data = np.where(np.isnan(stare[date]['w']).all(axis =  1))[0]
        initial = stare[date][v]
        if v == 'time':
            new_time = []
            for i in range(0, len(initial)):
                if i not in no_data:
                    new_time.append(initial[i])
            stare[date][v] = new_time
            continue
        new = np.ones(np.shape(initial))
        column = 0
        for i in range(0, len(initial)):
            if i not in no_data:
                new[column] = initial[i]
                column += 1
        stare[date][v] = new

# find unique lats and get rid of -999 and nan
for date in vad:
    vad[date]['lats'] = np.unique(vad[date]['lat']).tolist()

for date in stare:
    stare[date]['lats'] = np.unique(stare[date]['lat']).tolist()
    
for date in stare:
    if str(stare[date]['lats'][-1]) == 'nan':
        del stare[date]['lats'][-1]
    if stare[date]['lats'][0] == -999:
        del stare[date]['lats'][0]

for date in vad:
    if str(vad[date]['lats'][-1]) == 'nan':
        del vad[date]['lats'][-1]
    if vad[date]['lats'][0] == -999:
        del vad[date]['lats'][0]  

# clean up bad data points        
for date in stare:
    for v in stare[date]:
        if np.ndim(stare[date][v]) == 2:
            if v != 'intensity':
                stare[date][v][stare[date]['intensity'] < 1.01] = np.nan
    
for date in vad:
    for v in vad[date]:
        if np.ndim(vad[date][v]) == 2:
            if v != 'intensity':
                vad[date][v][vad[date]['intensity'] < 1.01] = np.nan

# save data as pickle file    
with open(path + '/vad.pickle', "wb") as output_file:
    pickle.dump(vad, output_file)
    
with open(path + '/stare.pickle', "wb") as output_file:
    pickle.dump(stare, output_file)

# open dict files 
with open(path + '/vad.pickle', 'rb') as fh:
    vad = pickle.load(fh)
       
with open(path + '/stare.pickle', 'rb') as fh:
    stare = pickle.load(fh)

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
    
storm_vad = {}
for date in vad:
    lat_list = vad[date]['lat'].tolist()
    storm_index = []
    if date not in storm_vad:
        storm_vad[date] = {}
    for storm in range(1,len(vad[date]['lats']) + 1):
        storm_vad[date][storm] = {}
    for lat in vad[date]['lats']:
        storm_index.append(lat_list.index(lat))
    storm_index.sort()
    storm_index[0] = 0
    storm_vad[date]['indexes'] = storm_index

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
                    if v == 'time':
                        storm_stare[date][n][v] = stare[date][v][0:indexes[n]]
            if len(indexes) == n:
                for v in stare[date]:
                    if np.ndim(stare[date][v]) == 2:
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:]
                    if np.ndim(stare[date][v]) == 1:
                        storm_stare[date][n][v] = stare[date][v]
                    if v == 'time':
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:]
            if len(indexes) > n:
                for v in stare[date]:
                    if np.ndim(stare[date][v]) == 2:
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:indexes[n]]
                    if np.ndim(stare[date][v]) == 1:
                        storm_stare[date][n][v] = stare[date][v]
                    if v == 'time':
                        storm_stare[date][n][v] = stare[date][v][indexes[n-1]:indexes[n]]
                        
for date in storm_vad:
    indexes = storm_vad[date]['indexes']
    for n in storm_vad[date]:
        if type(n) == int:
            if n == 1 and len(indexes) == 1:
                storm_vad[date][1] = vad[date]
            if n == 1 and len(indexes) > 1:
                for v in vad[date]:
                    if np.ndim(vad[date][v]) == 2:
                        storm_vad[date][n][v] = vad[date][v][0:indexes[n]]
                    if np.ndim(vad[date][v]) == 1:
                        storm_vad[date][n][v] = vad[date][v]
                    if v == 'time':
                        storm_vad[date][n][v] = vad[date][v][0:indexes[n]]
            if len(indexes) == n:
                for v in vad[date]:
                    if np.ndim(vad[date][v]) == 2:
                        storm_vad[date][n][v] = vad[date][v][indexes[n-1]:]
                    if np.ndim(vad[date][v]) == 1:
                        storm_vad[date][n][v] = vad[date][v]
                    if v == 'time':
                        storm_vad[date][n][v] = vad[date][v][indexes[n-1]:]
            if len(indexes) > n:
                for v in vad[date]:
                    if np.ndim(vad[date][v]) == 2:
                        storm_vad[date][n][v] = vad[date][v][indexes[n-1]:indexes[n]]
                    if np.ndim(vad[date][v]) == 1:
                        storm_vad[date][n][v] = vad[date][v]
                    if v == 'time':
                        storm_vad[date][n][v] = vad[date][v][indexes[n-1]:indexes[n]]

for date in storm_stare:
    del storm_stare[date]['indexes']
    
for date in storm_vad:
    del storm_vad[date]['indexes']

# save storm_data as pickle file    
with open(path + '/storm_vad.pickle', "wb") as output_file:
    pickle.dump(storm_vad, output_file)
    
with open(path + '/storm_stare.pickle', "wb") as output_file:
    pickle.dump(storm_stare, output_file)

# open storm_data files 
with open(path + '/storm_vad.pickle', 'rb') as fh:
    storm_vad = pickle.load(fh)
       
with open(path + '/storm_stare.pickle', 'rb') as fh:
    storm_stare = pickle.load(fh)

for date in storm_vad:
    for storm in storm_vad[date]:
        if type(storm) == int:
            figure, (ax1,ax2) = plt.subplots(2, 1, sharex = True)
            x = storm_vad[date][storm]['time']
            y = storm_vad[date][storm]['height']
            z = np.transpose(storm_vad[date][storm]['wspd'])
            z_2 = np.transpose(storm_vad[date][storm]['wdir'])
            speed = ax1.contourf(x, y, z)
            dir = ax2.contourf(x, y, z_2)
            plt.xlabel('time (UTC)')
            figure.text(0.04, 0.5, 'height above lidar (km)', va = 'center', rotation = 'vertical')
            plt.suptitle('Storm ' + str(storm) + ' Wind Speed/Direction on ' + date)
            plt.colorbar(speed, ax=ax1, label = 'wind speed', ticks = [0,2,4,6,8,10])
            plt.colorbar(dir, ax=ax2, label = 'wind direction', ticks = [0,60,120,180,240,300,360])






















    
    
    
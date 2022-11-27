import netCDF4 as nc
import os.path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pickle
import datetime as dt

data = os.listdir('/Users/bobbysaba/Documents/Thesis/VAD')
vad_path = '/Users/bobbysaba/Documents/Thesis/VAD'
path = '/Users/bobbysaba/Documents/Thesis'

untouched_data = ['rows', 'cols', 'height', 'no_data', 'covariance_matrix', 'lats']

vad = {}

# convert nc files to dictionary
for file in data:
    scan_info = file.split('.')
    date = scan_info[0]
    file = nc.Dataset(vad_path + '/' + file)
    time_list = []
    year = int(scan_info[0][0:4])
    month = int(scan_info[0][4:6])    
    if date not in vad:
        vad[date] = {}
    for v in file.variables.keys():
        if v == 'base_time':
            continue
        vad[date][v] = file[v][:]
        if v == 'hour':
            for h in vad[date][v]:
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
            vad[date]['height'] = vad[date]['height'] / 1000
        if v == 'windspeed' or v == 'wspd':
            vad[date][v][vad[date][v] > 35] = np.nan
            vad[date]['wspd'] = vad[date][v]
            if v == 'windspeed':
                del vad[date]['windspeed']
        if v == 'winddir':
            vad[date]['wdir'] = vad[date]['winddir']
            del vad[date]['winddir']
        if v == 'w':
            vad[date][v][vad[date][v] > 10] = np.nan
            vad[date][v][vad[date][v] < -10] = np.nan
    vad[date]['time'] = np.array(time_list)
    try:
        del vad[date]['epochtime']       
    except:
        continue

# get rid of dates with no or all bad data
del vad['20220526']

data = os.listdir('/Users/bobbysaba/Documents/Thesis/STARE')
stare_path = '/Users/bobbysaba/Documents/Thesis/STARE'

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
    del stare[date]['hour']
    try:
        del stare[date]['epochtime']
    except:
        continue

# delete lowest 3 values
for date in vad:
    vad[date]['height'] = np.delete(vad[date]['height'], [0,1,2])
    for v in vad[date]:
        if v in untouched_data:
            continue
        try:
            vad[date][v] = np.delete(vad[date][v], [0,1,2], 1)
        except:
            continue
        
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
for date in vad:
    too_high = np.where(vad[date]['height'] > 2)[0]
    vad[date]['height'] = np.delete(vad[date]['height'], too_high)
    for v in vad[date]:
        if np.ndim(vad[date][v]) == 2:
            vad[date][v] = np.delete(vad[date][v], too_high, 1)
            
for date in stare:
    too_high = np.where(stare[date]['height'] > 2)[0]
    stare[date]['height'] = np.delete(stare[date]['height'], too_high)
    for v in stare[date]:
        if np.ndim(stare[date][v]) == 2:
            stare[date][v] = np.delete(stare[date][v], too_high, 1)    

# clean up bad data points 
for date in vad:
    for v in vad[date]:
        if np.ndim(vad[date][v]) == 2:
            if v != 'intensity':
                vad[date][v][vad[date]['intensity'] < 1.01] = np.nan
                
for date in stare:
    for v in stare[date]:
        if np.ndim(stare[date][v]) == 2:
            if v != 'intensity':
                stare[date][v][stare[date]['intensity'] < 1.01] = np.nan
                
for date in vad:
    vad[date]['wdir'][vad[date]['wspd'] == np.nan] = np.nan

# find unique lats and get rid of -999 and nan
for date in vad:
    vad[date]['lats'] = np.unique(vad[date]['lat'])
    if str(vad[date]['lats'][-1]) == 'nan':
        vad[date]['lats'] = np.delete(vad[date]['lats'], -1)
    if vad[date]['lats'][0] == -999:
        vad[date]['lats'] = np.delete(vad[date]['lats'], 0) 
    
for date in stare:
    stare[date]['lats'] = np.unique(stare[date]['lat'])
    if str(stare[date]['lats'][-1]) == 'nan':
        stare[date]['lats'] = np.delete(stare[date]['lats'], -1)
    if stare[date]['lats'][0] == -999:
        stare[date]['lats'] = np.delete(stare[date]['lats'], 0)
        
# fix lat error in 20220531 data
for scan in range(0, 6):
    vad['20220531']['lat'][scan] = 36.9386

# save vad and stare data    
with open(path + '/vad.pickle', "wb") as output_file:
    pickle.dump(vad, output_file)
    
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
    
# handle repositioning on 20220523
for storm in range(2, 6):
    for v in storm_vad['20220523'][1]:
        if v in untouched_data:
            continue
        if np.ndim(storm_vad['20220523'][1][v]) == 2:
            storm_vad['20220523'][1][v] = np.append(storm_vad['20220523'][1][v], storm_vad['20220523'][storm][v], axis = 0)
        if np.ndim(storm_vad['20220523'][1][v]) == 1:
            storm_vad['20220523'][1][v] = np.append(storm_vad['20220523'][1][v], storm_vad['20220523'][storm][v])
    del storm_vad['20220523'][storm]

# handle repositioning on 20220524    
for v in storm_vad['20220524'][7]:
    if v in untouched_data:
        continue
    if np.ndim(storm_vad['20220524'][7][v]) == 2:
        storm_vad['20220524'][7][v] = np.append(storm_vad['20220524'][7][v], storm_vad['20220524'][8][v], axis = 0)
    if np.ndim(storm_vad['20220524'][7][v]) == 1:
        storm_vad['20220524'][7][v] = np.append(storm_vad['20220524'][7][v], storm_vad['20220524'][8][v])
        
del storm_vad['20220524'][8]

# handle repositioning on 20220531
for v in storm_vad['20220531'][2]:
    if v in untouched_data:
        continue
    if np.ndim(storm_vad['20220531'][2][v]) == 2:
        storm_vad['20220531'][2][v] = np.append(storm_vad['20220531'][2][v], storm_vad['20220531'][3][v], axis = 0)
    if np.ndim(storm_vad['20220531'][2][v]) == 1:
        storm_vad['20220531'][2][v] = np.append(storm_vad['20220531'][2][v], storm_vad['20220531'][3][v])
        
del storm_vad['20220531'][3]

# handle repositioning on 20220612
for storm in range(5, 8):
    for v in storm_vad['20220612'][4]:
        if v in untouched_data:
            continue
        if np.ndim(storm_vad['20220612'][4][v]) == 2:
            storm_vad['20220612'][4][v] = np.append(storm_vad['20220612'][4][v], storm_vad['20220612'][storm][v], axis = 0)
        if np.ndim(storm_vad['20220612'][4][v]) == 1:
            storm_vad['20220612'][4][v] = np.append(storm_vad['20220612'][4][v], storm_vad['20220612'][storm][v])
    del storm_vad['20220612'][storm]

# handle repositioning on 20190520
for v in storm_vad['20190520'][1]:
    if v in untouched_data:
        continue
    if np.ndim(storm_vad['20190520'][1][v]) == 2:
        storm_vad['20190520'][1][v] = np.append(storm_vad['20190520'][1][v], storm_vad['20190520'][2][v], axis = 0)
    if np.ndim(storm_vad['20190520'][1][v]) == 1:
        storm_vad['20190520'][1][v] = np.append(storm_vad['20190520'][1][v], storm_vad['20190520'][2][v])

storm_vad['20190520'][2] = storm_vad['20190520'][3]
del storm_vad['20190520'][3]

# handle repositioning on 20190527
for storm in range(4, 6):
    for v in storm_vad['20190527'][3]:
        if v in untouched_data:
            continue
        if np.ndim(storm_vad['20190527'][3][v]) == 2:
            storm_vad['20190527'][3][v] = np.append(storm_vad['20190527'][3][v], storm_vad['20190527'][storm][v], axis = 0)
        if np.ndim(storm_vad['20190527'][3][v]) == 1:
            storm_vad['20190527'][3][v] = np.append(storm_vad['20190527'][3][v], storm_vad['20190527'][storm][v])
    del storm_vad['20190527'][storm]
    
# handle repositioning on 20190608
for storm in range(3, 5):
    for v in storm_vad['20190608'][2]:
        if v in untouched_data:
            continue
        if np.ndim(storm_vad['20190608'][2][v]) == 2:
            storm_vad['20190608'][2][v] = np.append(storm_vad['20190608'][2][v], storm_vad['20190608'][storm][v], axis = 0)
        if np.ndim(storm_vad['20190527'][3][v]) == 1:
            storm_vad['20190608'][2][v] = np.append(storm_vad['20190608'][2][v], storm_vad['20190608'][storm][v])
    del storm_vad['20190608'][storm]

# handle new storm in same position on 20190523
storm_vad['20190523'][3] = {}
third_storm = np.arange(43, len(storm_vad['20190523'][2]['time']), 1)

for v in storm_vad['20190523'][2]:
    if v == 'height':
        storm_vad['20190523'][3][v] = storm_vad['20190523'][2][v]
        continue
    if v in untouched_data:
        continue
    if v == 'time':
        storm_vad['20190523'][3][v] = storm_vad['20190523'][2][v][43:]
        storm_vad['20190523'][2][v] = np.delete(storm_vad['20190523'][2][v], third_storm, 0)
        continue
    if np.ndim(storm_vad['20190523'][2][v]) == 2:
        storm_vad['20190523'][3][v] = storm_vad['20190523'][2][v][43:]
        storm_vad['20190523'][2][v] = np.delete(storm_vad['20190523'][2][v], third_storm, 0)
    if np.ndim(storm_vad['20190523'][2][v]) == 1:
        storm_vad['20190523'][3][v] = storm_vad['20190523'][2][v]
        storm_vad['20190523'][2][v] = np.delete(storm_vad['20190523'][2][v], third_storm, 0)

# delete scans with no data               
for date in storm_vad:
    for storm in storm_vad[date]:
        while np.nansum(storm_vad[date][storm]['wspd'][0]) == 0.0:
            for v in storm_vad[date][storm]:
                if v in untouched_data:
                    continue
                storm_vad[date][storm][v] = np.delete(storm_vad[date][storm][v], 0, 0)
        while np.nansum(storm_vad[date][storm]['wspd'][-1]) == 0.0:
            for v in storm_vad[date][storm]:
                if v in untouched_data:
                    continue
                storm_vad[date][storm][v] = np.delete(storm_vad[date][storm][v], -1, 0)
        
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

# calculate bulk shear
for date in storm_vad:
    index_75 = np.where(vad[date]['height'] >= 0.075)[0][0]
    index_250 = np.where(vad[date]['height'] >= 0.25)[0][0]
    index_500 = np.where(vad[date]['height'] >= 0.5)[0][0]
    index_1000 = np.where(vad[date]['height'] > 1)[0][0]
    for storm in storm_vad[date]:
        storm_vad[date][storm]['75-250_shr'] = np.ones(np.shape(storm_vad[date][storm]['time']))
        storm_vad[date][storm]['75-500_shr'] = np.ones(np.shape(storm_vad[date][storm]['time']))
        storm_vad[date][storm]['75-1000_shr'] = np.ones(np.shape(storm_vad[date][storm]['time']))
        for scan in range(0, len(storm_vad[date][storm]['time'])):
            u_comp_250 = storm_vad[date][storm]['u'][scan][index_250] - storm_vad[date][storm]['u'][scan][index_75]
            u_comp_500 = storm_vad[date][storm]['u'][scan][index_500] - storm_vad[date][storm]['u'][scan][index_75]
            u_comp_1000 = storm_vad[date][storm]['u'][scan][index_1000] - storm_vad[date][storm]['u'][scan][index_75]
            v_comp_250 = storm_vad[date][storm]['v'][scan][index_250] - storm_vad[date][storm]['v'][scan][index_75]
            v_comp_500 = storm_vad[date][storm]['v'][scan][index_500] - storm_vad[date][storm]['v'][scan][index_75]
            v_comp_1000 = storm_vad[date][storm]['v'][scan][index_1000] - storm_vad[date][storm]['v'][scan][index_75]
            mag_250 = ((u_comp_250 ** 2) + (v_comp_250 ** 2)) ** 0.5
            mag_500 = ((u_comp_500 ** 2) + (v_comp_500 ** 2)) ** 0.5
            mag_1000 = ((u_comp_1000 ** 2) + (v_comp_1000 ** 2)) ** 0.5
            storm_vad[date][storm]['75-250_shr'][scan] = mag_250
            storm_vad[date][storm]['75-500_shr'][scan] = mag_500
            storm_vad[date][storm]['75-1000_shr'][scan] = mag_1000

poster_storms = {'20220523': [1], '20220524': [7], '20220531': [1, 2], '20220610': [1, 2], '20220611': [1], '20220612': [4], 
                 '20190525': [1, 2], '20190523': [1, 2, 3], '20190517': [1], '20190526': [1], '20190520': [1], 
                 '20190527': [2, 3], '20190528': [1], '20190608': [2], '20190611': [1]}

for date in poster_storms:
    real_storm = 1
    for storm in poster_storms[date]:
        figure, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, constrained_layout = True, sharex = True)
        # set plotting variables 
        x = storm_vad[date][storm]['time']
        y = storm_vad[date][storm]['height']
        z = np.transpose(storm_vad[date][storm]['wspd'])
        z_2 = np.transpose(storm_vad[date][storm]['wdir'])
        z_3 = np.transpose(storm_vad[date][storm]['w'])
        z_4 = storm_vad[date][storm]['75-250_shr']
        z_5 = storm_vad[date][storm]['75-500_shr']
        z_6 = storm_vad[date][storm]['75-1000_shr']
        # wind speed
        speed = ax1.contourf(x, y, z, cmap = 'rainbow', levels = np.arange(0, 25.001), extend = 'max')
        ax1.text(x[0], 1.5, 'horiz. wind speed (m/s)', fontsize = 9)
        plt.colorbar(speed, ax = ax1, ticks = [0, 5, 10, 15, 20, 25])
        ax1.set_ylabel('height (km)', fontsize = 9)
        ax1.set_yticks([0.5, 1.0, 1.5, 2.0], fontsize = 9)
        # wind dir
        dir = ax2.contourf(x, y, z_2, cmap = 'tab20c', levels = np.arange(0, 361, 20))
        plt.colorbar(dir, ax = ax2, ticks = [0, 120, 240, 360])
        ax2.text(x[0], 1.5, 'horiz. wind dir. (˚)', fontsize = 9)
        ax2.set_ylabel('height (km)', fontsize = 9)
        ax2.set_yticks([0.5, 1.0, 1.5, 2.0], fontsize = 9)
        # vertical wind speed
        vert = ax3.contourf(x,y,z_3, cmap = 'seismic', levels = np.arange(-6, 6.0001, 0.1), extend = 'both')
        plt.colorbar(vert, ax = ax3, ticks = [-6, -3, 0, 3, 6])
        ax3.text(x[0], 1.5, 'vert. wind speed (m/s)', fontsize = 9)
        ax3.set_ylabel('height (km)', fontsize = 9)
        ax3.set_yticks([0.5, 1.0, 1.5, 2.0], fontsize = 9)
        # bulk shear
        ax4.plot(x, z_4, color = 'green', label = '250m', linewidth = 0.8)
        ax4.plot(x, z_5, color = 'blue', label = '500m', linewidth = 0.8)
        ax4.plot(x, z_6, color = 'red', label = '1000m', linewidth = 0.8)
        ax4.set_ylabel('shear (m/s)', fontsize = 9)
        ax4.legend(loc = 'upper left', ncol = 3, prop = {'size':9})
        ax4.set(ylim = (0, 25))
        # plot shared x label
        plt.xlabel('time (UTC)')
        myFmt = mdates.DateFormatter('%H:%M')
        plt.gca().xaxis.set_major_formatter(myFmt)
        # general formatting
        plt.suptitle(date + ' Storm ' + str(real_storm))
        figure.align_ylabels()
        plt.savefig('/Users/bobbysaba/Documents/Thesis/Poster_Figs/' + date + ' Storm ' + str(real_storm) + '.png', dpi = 400)
        real_storm += 1

# save storm vad and stare data 
with open(path + '/storm_vad.pickle', "wb") as output_file:
    pickle.dump(storm_vad, output_file)
    
with open(path + '/storm_stare.pickle', "wb") as output_file:
    pickle.dump(storm_stare, output_file)

# open storm vad and stare dicts
with open(path + '/storm_vad.pickle', 'rb') as fh:
    storm_vad = pickle.load(fh) 

with open(path + '/storm_stare.pickle', 'rb') as fh:
    storm_stare = pickle.load(fh) 

# work in and merge 2017 LIDAR data



    
    
    
import datetime as dt
import netCDF4 as nc
import numpy as np
import os.path

data = os.listdir('/Users/bobbysaba/Documents/Thesis/DL_data_2017')
path = '/Users/bobbysaba/Documents/Thesis/DL_data_2017/'

untouched_data = ['rows', 'cols', 'height', 'no_data', 'covariance_matrix', 'lats']

data_2017 = {}
for file in data:
    scan_info = file.split('.')
    date = scan_info[0]
    file = nc.Dataset(path + file)
    year = int(scan_info[0][0:4])
    month = int(scan_info[0][4:6])  
    time_list = []
    if date not in data_2017:
        data_2017[date] = {}
        for v in file.variables.keys():
            if v == 'base_time':
                continue
            if v == 'alt':
                continue
            if v == 'lat':
                continue
            if v == 'lon':
                continue
            if v == 'time_offset':
                continue
            if v == 'maxht':
                continue
            data_2017[date][v] = file[v][:]
            if v == 'hour':
                for h in data_2017[date][v]:
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
        data_2017[date]['time'] = np.array(time_list)
    if date in data_2017:
        for v in data_2017[date]:
            if v == 'hour':
                for h in data_2017[date][v]:
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
            data_2017[date]['time'] = np.array(time_list)
            if v =='time':
                continue
            if np.ndim(file[v]) == 2:
                data_2017[date][v] = np.append(data_2017[date][v], file[v][:], axis = 0)
            if np.ndim(file[v]) == 1:
                data_2017[date][v] = np.append(data_2017[date][v], file[v][:])

# delete scans closest to the ground and trim data above 2km
for date in data_2017:
    data_2017[date]['height'] = np.delete(data_2017[date]['height'], [0,1,2])
    for v in data_2017[date]:
        if v in untouched_data:
            continue
        try:
            data_2017[date][v] = np.delete(data_2017[date][v], [0,1,2], 1)
        except:
            continue

for date in data_2017:
    too_high = np.where(data_2017[date]['height'] > 2)[0]
    data_2017[date]['height'] = np.delete(data_2017[date]['height'], too_high)
    for v in data_2017[date]:
        if np.ndim(data_2017[date][v]) == 2:
            data_2017[date][v] = np.delete(data_2017[date][v], too_high, 1)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
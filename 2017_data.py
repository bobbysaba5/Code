import datetime as dt
import netCDF4 as nc
import numpy as np
import os.path
import pickle

data = os.listdir('/Users/bobbysaba/Documents/Thesis/DL_data_2017')
path = '/Users/bobbysaba/Documents/Thesis/DL_data_2017/'

untouched_data = ['rows', 'cols', 'height', 'no_data', 'covariance_matrix', 'lats']
unused_data = ['base_time', 'alt', 'lat', 'lon', 'time_offset', 'maxht']

data_2017 = {}
for file in data:
    scan_info = file.split('.')
    date = scan_info[0]
    file = nc.Dataset(path + file)
    year = int(scan_info[0][0:4])
    month = int(scan_info[0][4:6])  
    time_list = []
    if date in data_2017:
        storm = len(data_2017[date]) + 1
        data_2017[date][storm] = {}
        for v in file.variables.keys():
            if v in unused_data:
                continue
            data_2017[date][storm][v] = file[v][:]
            if v == 'hour':
                for h in data_2017[date][storm][v]:
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
            data_2017[date][storm]['time'] = np.array(time_list)
    if date not in data_2017:
        data_2017[date] = {}
        data_2017[date][1] = {}
        for v in file.variables.keys():
            if v in unused_data:
                continue
            data_2017[date][1][v] = file[v][:]
            if v == 'hour':
                for h in data_2017[date][1][v]:
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
        data_2017[date][1]['time'] = np.array(time_list)


# delete scans closest to the ground and trim data above 2km
for date in data_2017:
    for storm in data_2017[date]:
        data_2017[date][storm]['height'] = np.delete(data_2017[date][storm]['height'], [0,1,2])
        for v in data_2017[date][storm]:
            if v in untouched_data:
                continue
            try:
                data_2017[date][storm][v] = np.delete(data_2017[date][storm][v], [0,1,2], 1)
            except:
                continue
        too_high = np.where(data_2017[date][storm]['height'] > 2)[0]
        data_2017[date][storm]['height'] = np.delete(data_2017[date][storm]['height'], too_high)
        for v in data_2017[date][storm]:
            if np.ndim(data_2017[date][storm][v]) == 2:
                data_2017[date][storm][v] = np.delete(data_2017[date][storm][v], too_high, 1)
    
# save data 
with open('/Users/bobbysaba/Documents/Thesis/lidar_2017.pickle', "wb") as output_file:
    pickle.dump(data_2017, output_file)        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
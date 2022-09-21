import netCDF4 as nc
import os.path
import matplotlib.pyplot as plt
import numpy as np
import pickle
import datetime

data = os.listdir('/Users/bobbysaba/Documents/Thesis/Data')
path = '/Users/bobbysaba/Documents/Thesis/Data'
format = '%H:%M:%S'
'''
lidar = {}

# convert nc files to dictionary
for file in data:
    if file[-2:] == 'nc':
        scan_info = file.split('.')
        date = file[25:33]
        file = nc.Dataset(path + '/' + file)
        st = scan_info[4]
        time_list = []
        if st not in lidar:
            lidar[st] = {}
        if date not in lidar[st]:
            lidar[st][date] = {}    
        for v in file.variables.keys():
            if v not in lidar[st][date]:
                lidar[st][date][v] = file[v][:]
            if v == 'epochtime':
                for h in lidar[st][date][v]:
                    time = datetime.datetime.fromtimestamp(h)
                    time = time.strftime(format)
                    time_list.append(time)
        lidar[st][date]['time'] = time_list

# convert masked arrays to arrays with -999 and find storms per file   
for st in lidar:
    for date in lidar[st]:
        for v in lidar[st][date]:
            if v == 'lat':
                lidar[st][date][v][np.isnan(lidar[st][date][v])] = -999
                lidar[st][date][v] = lidar[st][date][v].tolist()
        storm_lats = np.unique(lidar[st][date]['lat']).tolist()
        if -999 in storm_lats:
            storm_lats.remove(-999)
        lidar[st][date]['lats'] = storm_lats
    
# save lidar as pickle file    
with open(path + '/lidar.pickle', "wb") as output_file:
    pickle.dump(lidar, output_file)
'''
# open lidar dict file    
with open(path + '/lidar.pickle', 'rb') as fh:
    lidar = pickle.load(fh)

storm_data = {}

# create dictionary for data by storm
for st in lidar:
    if st not in storm_data:
        storm_data[st] = {}
    for date in lidar[st]:
        if date not in storm_data[st]:
            storm_data[st][date] = {}
        for n in range(1,len(lidar[st][date]['lats']) + 1):
            if n not in storm_data[st][date]:
                storm_data[st][date][n] = {}
        for v in lidar[st][date]:
            if v not in storm_data[st][date][n]:
                storm_data[st][date][n][v] = {}
           

# insert data
for st in storm_data:
    for date in storm_data[st]:
        indexes = []
        for lats in lidar[st][date]['lats']:
            index = lidar[st][date]['lat'].index(lats)
            indexes.append(index)
        indexes.sort()
        for n in storm_data[st][date]:
            if n == 1 and len(storm_data[st][date]) == 1:
                storm_data[st][date][1] = lidar[st][date]
            if n == 1 and len(storm_data[st][date]) > 1:
                for v in lidar[st][date]:
                    storm_data[st][date][n][v] = lidar[st][date][v][0:indexes[n]]
            if len(storm_data[st][date]) == n:
                for v in lidar[st][date]:
                    storm_data[st][date][n][v] = lidar[st][date][v][indexes[n-1]:]
            if len(storm_data[st][date]) > n:
                for v in lidar[st][date]:
                    storm_data[st][date][n][v] = lidar[st][date][v][indexes[n-1]:indexes[n]]
                  
# re-open lidar dict file becasue I had some weird probelm with the height array from STARE 20190614 disappearing
with open(path + '/lidar.pickle', 'rb') as fh:
    lidar = pickle.load(fh)

for date in storm_data['VAD']:
    for n in storm_data['VAD'][date]:
        storm_data['VAD'][date][n]['height'] = lidar['VAD'][date]['height']
for date in storm_data['STARE']:
    for n in storm_data['STARE'][date]:
        storm_data['STARE'][date][n]['height'] = lidar['STARE'][date]['height']
                
for st in storm_data:
    for date in storm_data[st]:
        for n in storm_data[st][date]:
            for v in storm_data[st][date][n]:
                storm_data[st][date][n][v] = np.array(storm_data[st][date][n][v])
 
# save storm date as pickle file    
with open(path + '/storm_data.pickle', "wb") as output_file:
    pickle.dump(storm_data, output_file)

# open storm_data dict file    
with open(path + '/storm_data.pickle', 'rb') as fh:
    storm_data = pickle.load(fh)               

for date in storm_data['VAD']:
    for n in storm_data['VAD'][date]:
        figure, (ax1, ax2, ax3) = plt.subplots(3,1, sharex = 'all')
        x = storm_data['VAD'][date][n]['time']
        y = storm_data['VAD'][date][n]['height']/1000
        z = np.transpose(storm_data['VAD'][date][n]['windspeed'])
        z_2 = np.transpose(storm_data['VAD'][date][n]['winddir'])
        z_3 = np.transpose(storm_data['VAD'][date][n]['w'])
        w = ax1.contourf(x,y,z_3)
        speed = ax2.contourf(x,y,z)
        direction = ax3.contourf(x,y,z_2)      
        plt.xlabel('time (UTC)')
        figure.text(0.04, 0.5, 'height above lidar (km)', va = 'center', rotation = 'vertical')
        plt.suptitle('Storm ' + str(n) + ' Data on ' + date)
        plt.colorbar(speed, ax=ax2, label = 'wind speed')
        plt.colorbar(direction, ax=ax3, label = 'wind direction', ticks = [0,60,120,180,240,300,360])
        plt.colorbar(w, ax=ax1, label = 'vertical velocity')
        plt.xticks(x[::2], rotation = 45)
        plt.savefig('/Users/bobbysaba/Documents/Thesis/Figures/' + date + '/VAD/storm_' + str(n) + '.png', dpi = 400)
'''    
for date in storm_data['STARE']:
    for n in storm_data['STARE'][date]:
        figure = plt.figure()
        x = storm_data['STARE'][date][n]['time']
        y = storm_data['STARE'][date][n]['height']/1000
        z = np.transpose(storm_data['STARE'][date][n]['w'])
        w = plt.contourf(x,y,z)
        plt.xlabel('time (UTC)')
        plt.ylabel('height above lidar (km)')        
        plt.title('Storm ' + str(n) + ' Data on ' + date)
        plt.colorbar(w, label = 'vertical velocity (m/s)')
        plt.tick_params(axis = 'x' , which = 'both', top = False, bottom = False, labelbottom = False)
'''  

            
              
                
###### VAD: 20190523 and 20190527
###### STARE: 20190614, 20190602, and 20190608
                
                
                
                
                
                
            
            
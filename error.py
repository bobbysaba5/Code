import matplotlib.pyplot as plt
import metpy
from metpy.plots import Hodograph
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
import pickle

path = '/Users/bobbysaba/Documents/Thesis'

no_lidar = ['20170510', '20220605', '20220513', '20220607', '20220517', '20190515', '20190507', '20170509', '20220606', '20190516',
            '20220604', '20220615', '20190501', '20220608', '20190601']
#%%
# open data files
with open(path + '/storm_vad.pickle', 'rb') as fh:
    storm_vad = pickle.load(fh) 

with open(path + '/sonde.pickle', 'rb') as fh:
    sonde_data = pickle.load(fh) 
  
# alter the lidar data to match the date/time formatting as sonde data
storm_vad['20190609'] = {}
storm_vad['20190609'][1] = {}
storm_vad['20190609'][1] = storm_vad['20190608'][2]
storm_vad['20190609'][1]['hour'] = storm_vad['20190609'][1]['hour'] - 24
del storm_vad['20190608'][2]

storm_vad['20190614'] = {}
storm_vad['20190614'][1] = {}
storm_vad['20190614'][1] = storm_vad['20190613'][1]
storm_vad['20190614'][1]['hour'] = storm_vad['20190614'][1]['hour'] - 24
del storm_vad['20190613'][1]

storm_vad['20190612'] = {}
storm_vad['20190612'][1] = {}
storm_vad['20190612'][1] = storm_vad['20190611'][1]
storm_vad['20190612'][1]['hour'] = storm_vad['20190612'][1]['hour'] - 24
del storm_vad['20190611'][1]

storm_vad['20190519'] = {}
storm_vad['20190519'][1] = {}
storm_vad['20190519'][1] = storm_vad['20190518'][2]
storm_vad['20190519'][1]['hour'] = storm_vad['20190519'][1]['hour'] - 24
del storm_vad['20190518'][2]

storm_vad['20190603'] = {}
storm_vad['20190603'][1] = {}
storm_vad['20190603'][1] = storm_vad['20190602'][3]
storm_vad['20190603'][1]['hour'] = storm_vad['20190603'][1]['hour'] - 24
del storm_vad['20190602'][3]

# delete days of sonde data where there is no lidar data
for date in no_lidar:
    del sonde_data[date]
#%%    
sonde_lidar = {}
    
for date in sonde_data:
    if date not in storm_vad:
        print(date)
        continue
    if date not in sonde_lidar:
        sonde_lidar[date] = {}
    launch = 1
    for time in sonde_data[date]:
        if launch not in sonde_lidar[date]:
            sonde_lidar[date][launch] = {}
        sonde_lidar[date][launch]['sonde_height'] = sonde_data[date][time]['height']
        sonde_lidar[date][launch]['sonde_u'] = sonde_data[date][time]['u']
        sonde_lidar[date][launch]['sonde_v'] = sonde_data[date][time]['v']
        start = sonde_data[date][time]['hour_first']
        end = sonde_data[date][time]['hour_last']
        for storm in storm_vad[date]:
            times = storm_vad[date][storm]['hour']
            if len(np.where(np.logical_and(times >= start, times <= end))[0]) > 0:
                sonde_lidar[date][launch]['lidar_height'] = storm_vad[date][storm]['height']
                scans = np.where(np.logical_and(times >= start, times <= end))[0]
                sonde_lidar[date][launch]['lidar_scans'] = scans
                lidar_u = np.ones((len(scans), len(storm_vad[date][storm]['u'][0])))
                lidar_v = np.ones((len(scans), len(storm_vad[date][storm]['v'][0])))
                lidar_u[0] = storm_vad[date][storm]['u'][scans[0]]
                lidar_v[0] = storm_vad[date][storm]['v'][scans[0]]
                if len(scans) > 1:
                    for i in range(1, len(scans)):
                        lidar_u[i] = storm_vad[date][storm]['u'][scans[i]]
                        lidar_v[i] = storm_vad[date][storm]['v'][scans[i]]
                sonde_lidar[date][launch]['lidar_u'] = np.nanmean(lidar_u, axis = 0)
                sonde_lidar[date][launch]['lidar_v'] = np.nanmean(lidar_v, axis = 0)
                sonde_lidar[date][launch]['lidar_u_scans'] = lidar_u
                sonde_lidar[date][launch]['lidar_v_scans'] = lidar_v
                continue        
        launch += 1

# handle sonde launches with no lidar data
no_lidar_2 = {'date': [], 'launch': []}

for date in sonde_lidar:
    for launch in sonde_lidar[date]:
        if 'lidar_u' not in sonde_lidar[date][launch]:
            no_lidar_2['date'].append(date)
            no_lidar_2['launch'].append(launch)
            
for i in range(0, len(no_lidar_2['date'])):
    del sonde_lidar[no_lidar_2['date'][i]][no_lidar_2['launch'][i]]
#%%
# plot hodographs
for date in sonde_lidar:
    for launch in sonde_lidar[date]:
        fig = plt.figure(figsize = (6, 6))
        ax = fig.add_subplot(1, 1, 1)
        u = sonde_lidar[date][launch]['lidar_u'] * units('m/s')
        v = sonde_lidar[date][launch]['lidar_v'] * units('m/s')
        height = sonde_lidar[date][launch]['lidar_height'] * units('m')
        h = Hodograph(ax, component_range = 30)
        h.plot(u, v, linewidth = 2, color = 'blue')  
        u = sonde_lidar[date][launch]['sonde_u'] * units('m/s')
        v = sonde_lidar[date][launch]['sonde_v'] * units('m/s')
        height = sonde_lidar[date][launch]['sonde_height'] * units('m')
        h.plot(u, v, linewidth = 2, color = 'red') 
        h.add_grid(increment = 5)
        ax.set_title(str(date) + ' ' + str(launch))
        
rms = {'2017': storm_vad['20170522'][1]['rms'], 
       '2019': storm_vad['20190528'][1]['rms'],
       '2022': storm_vad['20220529'][1]['rms']}
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
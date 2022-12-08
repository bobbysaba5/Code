import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pickle

path = '/Users/bobbysaba/Documents/Thesis'

# open storm vad and stare dicts
with open(path + '/storm_vad.pickle', 'rb') as fh:
    storm_vad = pickle.load(fh) 

with open(path + '/storm_stare.pickle', 'rb') as fh:
    storm_stare = pickle.load(fh) 
    
poster_storms = {'20220523': [1], '20220524': [7], '20220531': [1, 2], '20220610': [1, 2], '20220611': [1], '20220612': [4], 
                 '20190525': [1, 2], '20190523': [1, 2, 3], '20190517': [1], '20190526': [1], '20190520': [1], 
                 '20190527': [2, 3], '20190528': [1], '20190609': [1], '20190611': [1]}

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
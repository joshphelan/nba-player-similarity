# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 18:00:35 2023

Similar NBA Player Preprocessing

@author: Josh Phelan
"""

import pickle 
import numpy as np
from preprocess import preprocess

start = 1980
end = 2017
interval = 4

years = list(np.arange(start, end, interval))
years.append(2022)

for year in years:
    year = f'{year}'
    dist_dict = preprocess(year)
    
    # Save distance dictionary as pickle file
    with open('data/dist_dict_'+ year +'.pkl', 'wb') as f:
        pickle.dump(dist_dict, f)

# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:25:48 2023

Combine All Years Data

@author: Josh Phelan
"""

import pandas as pd
import numpy as np
from preprocess import preprocess
import pickle

start = 1980
end = 2017
interval = 4

years = list(np.arange(start, end, interval))
years.append(2022)

all_stats = pd.DataFrame()

for year in years:
    year = f'{year}'
    
    stats = pd.read_csv('data/NBA ' + year +' Combined Stats.csv',index_col=('ID'))
    stats.index = stats.index + year
    stats['Player'] = stats['Player'] + ' ('+ year+')'
    
    all_stats = pd.concat([all_stats,stats], axis = 0)
    
# Confirm no duplicates
all_stats.index.duplicated().any()

# Save final dataframe of combined stats
all_stats.to_csv('data/NBA All Years Combined Stats.csv')


# Dictionary of all years
dist_dict_all = preprocess('All Years')

# Save distance dictionary as pickle file
with open('data/dist_dict_all.pkl', 'wb') as f:
    pickle.dump(dist_dict_all, f)

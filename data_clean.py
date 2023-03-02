# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 17:19:52 2023

NBA Stats Data Cleansing

@author: Josh Phelan
"""

import numpy as np
from clean import clean

start = 1980
end = 2017
interval = 4

years = list(np.arange(start, end, interval))
years.append(2022)

for year in years:
    year = f'{year}'
    stats = clean(year)
    
    # Save final dataframe of combined stats
    stats.to_csv('data/NBA ' + year +' Combined Stats.csv')

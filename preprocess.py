# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:25:11 2023

Data Preprocessing Function

@author: josh
"""


import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import euclidean

def preprocess(year):

    stats = pd.read_csv('data/NBA ' + year +' Combined Stats.csv',index_col=('ID'))
    
    stats_num = stats.drop(['Player','Pos','Tm'],axis=1)
        
    # Normalize data based on standard scaler so all columns are considered evenly
    scaler = StandardScaler()
    
    scaler.fit(stats_num)
    
    scaled_data = scaler.transform(stats_num)
    
    # Creating dictionary of distance scores for each player in dataset
    dist_dict = {}
    for j in range(len(stats)):    
        # similar to player j by euclidean distance with scaled data
        sim_j = pd.DataFrame(columns=['Distance'])
        k = stats.index[j]
        for i in range(len(scaled_data)):
            # set index of sim_j to player that is being measured against
            q = stats.index[i]
            if i != j:
                sim_j.loc[q] = euclidean(scaled_data[j], scaled_data[i])
            else:
                continue
        dist_dict[k] = sim_j

    return dist_dict
    
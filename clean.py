# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:20:41 2023

Data Cleaning Function

@author: josh
"""


import pandas as pd

def clean(year):
    year = f'{year}'
    
    # Read Per Game and Advanced player stats from 2022 season
    # Tables gathered from basketballreference.com
    per_game = pd.read_csv('raw_data/NBA ' + year +' Per Game.csv')
    advanced = pd.read_csv('raw_data/NBA ' + year +' Advanced.csv')
    
    # Rename Basketball Reference Key as ID
    per_game.rename(columns={'Player-additional':'ID'}, inplace=True)
    advanced.rename(columns={'Player-additional':'ID'}, inplace=True)
    
    # Drop duplicates to only keep the total stats for traded players
    per_game.drop_duplicates(subset='ID',keep='first', inplace=True)
    advanced.drop_duplicates(subset='ID',keep='first', inplace=True)
    
    # Only keeping players with more than 30 games played for more reliable data
    per_game = per_game[per_game['G'] > 30]
    
    # Look at columns with null values
    advanced.isnull().sum()
    
    # Drop columns with all null values
    advanced.drop(['Unnamed: 19','Unnamed: 24'], axis=1, inplace=True)
    
    # Drop duplicates columns from advanced, including MP which is expressed as total minutes in this table
    advanced.drop(['Rk','Player','Age','Pos','Tm','G','MP'], axis=1, inplace=True)
    
    # Remove Rk column from per_game
    per_game.drop(['Rk'], axis=1, inplace=True)
    
    # Check null values for per_game
    per_game.isnull().sum()
    
    # Players with null values for 3P% did not attempt a single three point shot all season
    # Replace these null values with 0
    # Same for players with 0 free throw attempts
    per_game['3P%'] = per_game['3P%'].fillna(0)
    per_game['FT%'] = per_game['3P%'].fillna(0)
    
    # No more null values
    per_game.isnull().sum()
    
    # Merge dataframes together
    stats = pd.merge(per_game, advanced, how = "inner", on= "ID")
    
    # Clean player name so there are no asterisks
    stats['Player'] = stats['Player'].str.replace('*','', regex=True)
    
    # Drop Games Started because of incomplete data for 1980
    stats.drop('GS',axis=1,inplace=True)
    
    # Set index to player ID
    stats = stats.set_index('ID')
    
    return stats
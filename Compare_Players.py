# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:16:34 2023

Similar NBA Players App: Compare Players Page

@author: Josh Phelan
"""

import pandas as pd
import numpy as np
from random import sample
import pickle
import urllib.request
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import altair as alt
import PIL
import requests
from io import BytesIO
import streamlit as st

st.title('NBA Player Similarity')
with st.sidebar:
    col1, col2, col3 = st.columns([1,14,1])
    with col1:
        st.write("")
    with col2:
        st.image('raw_data/MJ.jpg',  use_column_width=True)
    with col3:
        st.write("")
        
    st.markdown(" ## NBA Player Similarity App")
    st.markdown("This app calculates the similarity score between NBA players from the 1980 to 2016 seasons at 4 year intervals, and the 2021-2022 season. Similarity is calculated based on Euclidean distance from standardized per game and advanced statistics. Data provided by [Basketball Reference](https://www.basketball-reference.com/).")
    st.sidebar.info("See the code on my [Github](https://github.com/joshphelan/nba-player-similarity).", icon="🔗")
    st.markdown('*Developed by Josh Phelan*')

st.header('Compare Two Players')

st.write('''This page calculates the similarity score between two selected players. 
         For players that played in multiple seasons, choose the specific season 
         for that player that you would like to compare to any other player
         over time. Choose random players for inspiration!''')

# function to return stats data for given year                  
@st.cache
def get_stats_data():
    stats = pd.read_csv('data/NBA All Years Combined Stats.csv',index_col=('ID'))
    return stats

# function to retrieve distance dictionary for given year
@st.cache(allow_output_mutation=True)
def get_dist_data():
    # load pickle file from url since I uploaded it to Github using Git Large File Storage
    dist_dict = pickle.load(urllib.request.urlopen("https://github.com/joshphelan/nba-player-similarity/blob/main/data/dist_dict_all.pkl?raw=true"))
    return dist_dict

# function that returns player id given player name
def get_id(player_name):
    name = player_name
    player_id = stats[stats['Player'] == name].index[0]
    return player_id

# function to show header for specific player
def name(player_name):
    return "Stats for " + player_name

# function to display similarity score
def score_display(score):
    return "Similarity Score: " + '{:.2%}'.format(score)

# function to calculate the max distance in the distance dictionary
def get_max_d():
    max_list = []
    for key in dist_dict:
        max_list.append(max(dist_dict[key]['Distance']))
    max_d = max(max_list)
    return max_d
    
# returns similarity score between two players
def get_similarity(player_1,player_2):
    d = dist_dict[player_1]['Distance'].loc[player_2]
    d_norm = d/max_d
    s = 1 - d_norm
    return s

# retrieves average similarity score from all players compared
def get_avg_s():
    def get_avg_d():
        avg_list = []
        for key in dist_dict:
            avg_list.append(dist_dict[key]['Distance'])
        avg_d = np.mean(avg_list)
        return avg_d
    avg_d = get_avg_d()
    avg_norm = avg_d/max_d
    avg_s = 1 - avg_norm
    return avg_s
    
    
stats = get_stats_data()
dist_dict = get_dist_data()
max_d = get_max_d()
avg_s = get_avg_s()

# select boxes to choose the two players to compare
player1 = st.selectbox("Choose player 1:", list(stats['Player']),key="player1_box")
player2 = st.selectbox("Choose player 2:", (list(stats['Player'])[::-1]),key="player2_box")
    
# initializing player1 and player 2 session state, if none
if "rand_player1" not in st.session_state or "rand_player2" not in st.session_state:
    st.session_state['rand_player1'] = stats.iloc[[0]]['Player']
    st.session_state['rand_player2'] = stats.iloc[[1]]['Player']

# function that updates players shown in select boxes with random players from stats data
def update_player():
    player1, player2 = get_random()
    st.session_state['rand_player1'] = player1
    st.session_state['rand_player2'] = player2

    st.session_state['player1_box'] = player1
    st.session_state['player2_box'] = player2

# randomly samples 2 players from the stats data
def get_random():
    return [i for i in sample(list(stats['Player']),2)]

# button to choose random players
st.button("Choose Random Players", on_click = update_player)


if player1 != player2:
    player1_id = get_id(player1)
    player2_id = get_id(player2)
    s = get_similarity(player1_id, player2_id)
    
    st.subheader("Similarity Score")
    # delta shows difference between similarity score and average score amongst all players
    st.metric("Similarity Score", '{:.2%}'.format(s), delta='{:.2%}'.format(s-avg_s),label_visibility="collapsed")
    
    # list of stats to potentially display from multiselect box
    no_player = [col for col in stats.columns if col != 'Player']
    all_stats = st.multiselect("Select stats to compare:",no_player,['Tm','PTS','TRB','AST'])
    
    # create dataframe for player1
    st.subheader(name(player1))
    stats_player1 = stats.loc[[player1_id]]
        
    # Display similar players with pictures in AgGrid
    render_image = JsCode('''
                          
        function renderImage(params) {
        // Create a new image element
        var img = new Image();
    
        // Set the src property to the value of the cell (should be a URL pointing to an image)
        img.src = params.value;
    
        // Set the width and height of the image to 50 pixels
        img.width = 25;
        img.height = 35;
    
        // Return the image element
        return img;
        }
    '''
    )
    
    # function to return contents from url
    def read_file_from_url(url):
        return requests.get(url).content
    
    # create list of the headshot for inputted player from basketball reference
    pics = []
    for idx in stats_player1.index:
        idx = idx[:-4]
        try:
            file_bytes = read_file_from_url(
                "https://www.basketball-reference.com/images/players/"+idx+".jpg"
                )
            image = PIL.Image.open(BytesIO(file_bytes))    
            
            pics.append("https://www.basketball-reference.com/images/players/"+idx+".jpg")
        except PIL.UnidentifiedImageError:
            pics.append("https://upload.wikimedia.org/wikipedia/en/thumb/0/03/National_Basketball_Association_logo.svg/105px-National_Basketball_Association_logo.svg.png")
    
    # insert headshot to stats_player dataframe
    stats_player1.insert(0,"Pic",pics)
    
    
    # build GridOptions object for AgGrid table
    options_builder = GridOptionsBuilder.from_dataframe(stats_player1[list("Pic".split(" "))+list("Player".split(" "))+all_stats])
    options_builder.configure_column('Pic', cellRenderer = render_image,width =50, header_name= "")
    options_builder.configure_column('Player', width=165)
    options_builder.configure_default_column(width=103)
    grid_options = options_builder.build()
    
    # display AgGrid table for player 1
    AgGrid(stats_player1[list("Pic".split(" "))+list("Player".split(" "))+all_stats], 
            gridOptions = grid_options,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False,
            height=125, theme='material')
    
    # create dataframe for player1
    st.subheader(name(player2))
    stats_player2 = stats.loc[[player2_id]]

        
    # create list of the headshots for most similar players from basketball reference
    pics = []
    for idx in stats_player2.index:
        idx = idx[:-4]
        try:
            file_bytes = read_file_from_url(
                "https://www.basketball-reference.com/images/players/"+idx+".jpg"
                )
            image = PIL.Image.open(BytesIO(file_bytes))    
            
            pics.append("https://www.basketball-reference.com/images/players/"+idx+".jpg")
        except PIL.UnidentifiedImageError:
            pics.append("https://upload.wikimedia.org/wikipedia/en/thumb/0/03/National_Basketball_Association_logo.svg/105px-National_Basketball_Association_logo.svg.png")
    
    # insert headshots to players dataframe
    stats_player2.insert(0,"Pic",pics)

    # build GridOptions object for AgGrid table
    options_builder = GridOptionsBuilder.from_dataframe(stats_player2[list("Pic".split(" "))+list("Player".split(" "))+all_stats])
    options_builder.configure_column('Pic', cellRenderer = render_image,width =50, header_name= "")
    options_builder.configure_column('Player', width=165)
    options_builder.configure_default_column(width=103)
    grid_options = options_builder.build()
    
    # display AgGrid table for player 2
    AgGrid(stats_player2[list("Pic".split(" "))+list("Player".split(" "))+all_stats], 
            gridOptions = grid_options,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False,
            height=125, theme='material')

    
    # function to return comparison table between two players
    @st.cache
    def get_comp_table():
        comp = pd.concat([stats.loc[player1_id],stats.loc[player2_id]],axis=1).transpose()
        return comp
    
    
    comp = get_comp_table()
    comp_percent = pd.DataFrame()
    comp_percent.index=comp.index
    comp_percent['Player'] = comp['Player']
    
    # list of percent of total stats between the 2 players
    for i in all_stats:
        if i not in ['Tm','Pos']:
            percent_list = []
            for row in comp.index:
                percent_list.append(comp[i][row]/sum(comp[i]))
            col_name = i
            comp_percent[col_name] = percent_list
    
    # melting comp_percent and comp dataframes so each stat name and stat value are row items
    comp_percent = comp_percent.reset_index()
    comp_percent = comp_percent.melt(id_vars=['index','Player'],var_name='Stat',value_name='Value').set_index('index')    
    comp = comp.reset_index()
    comp = comp.drop(['Pos','Tm'],axis=1)
    comp = comp.melt(id_vars=['index','Player'],var_name='Stat',value_name='Actual').set_index('index')
    comp_percent.rename(columns = {'0':'Value'},inplace=True)
    
    # merging comp_percent and comp on comp_percent so the actual stat values are included in comp_percent
    comp_percent = comp_percent.merge(comp,how='left')
    
    # horizontal stacked bar chart to show relative proportion of selected stats between selected players
    bar = alt.Chart(comp_percent).mark_bar().encode(
        x=alt.X('Value:Q',axis=alt.Axis(labels=False,title="Comparison")),
        y=alt.Y('Stat:N', sort='-x'),
        color = alt.Color('Player:N',sort='-y'),
        tooltip=[
            alt.Tooltip('Player', title="Player"),
            alt.Tooltip('Actual:Q', title="Actual"),
            alt.Tooltip('Value:Q', title="% of Total", format='.0%'),
        ]
        ).properties(
            title={
                "text":"Player Comparison",
                "subtitle" : "A direct comparison between the two players for each stat selected above.",
                "subtitleColor": "gray"
                }
        )
    # line for mean of percent of total values        
    rule = alt.Chart(comp_percent).mark_rule(color='steelblue').encode(
        x='mean(Value):Q'
        )
    
    fig = (bar + rule)
    st.altair_chart(fig, use_container_width=True)
    
else:
    st.error("Please select 2 different players.")
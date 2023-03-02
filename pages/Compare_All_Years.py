# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:16:34 2023

Compare All Years Page

@author: Josh Phelan
"""

import pandas as pd
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
    

st.header('Most Similar Players Across All Years')


st.write('''This page calculates the 5 most similar NBA players from all seasons 
          to the player inputted below. For players that played in multiple seasons, choose
         the specific season for that player that you would like to compare to any other player
         over time. Choose a random player for inspiration!''')

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

# function to return the top 5 most similar players given a player id
def similar_players(player_id):
    top5 = []
    dist = list(dist_dict[player_id].sort_values(by='Distance').to_dict(orient = 'index').keys())
    # Exclude the same player from another season from results
    dist = [key for key in dist if key[:-4] != player_id[:-4]]
    short_dist = [i[:-4] for i in dist]
    # Keep only each player's most similar season and remove all others
    dist = [key for n, key in list(enumerate(dist)) if key[:-4] not in short_dist[:n]]
    top5 = dist[:5]
    players = stats.loc[top5]
    return players

# function to calculate the max distance in the distance dictionary
def get_max_d():
    max_list = []
    for key in dist_dict:
        max_list.append(max(dist_dict[key]['Distance']))
    max_d = max(max_list)
    return max_d

# returns list of similarity scores based on relative distance and max distance
def get_similarity(player_id, df):
    s_list = []
    for idx in df.index:
        d = dist_dict[player_id].loc[idx]['Distance']
        d_norm = d/max_d
        s = 1 - d_norm
        s_list.append(s)
    return s_list

# function that returns player id given player name
def get_id(player_name):
    name = player_name
    player_id = stats[stats['Player'] == name].index[0]
    return player_id

# function to show header for specific player
def name(player_name):
    return "Stats for " + player_name

stats = get_stats_data()
dist_dict = get_dist_data()
max_d = get_max_d()

# initializing player for session state, if none
if "rand_player" not in st.session_state:
    st.session_state['rand_player'] = stats.iloc[0]['Player']

# function that updates player shown in selectbox with random player from stats data
def update_player():
    st.session_state['rand_player'] = get_random()
    st.session_state['player_box'] = st.session_state['rand_player']

# selectbox to choose player
player = st.selectbox("Choose player:", list(stats['Player']),key="player_box")

# randomly samples a player from the stats data
def get_random():
    return sample(list(stats['Player']),1)[0]

# button to choose a random player
st.button("Choose a Random Player", on_click = update_player)
    
# getting player id for inputted player
player_id = get_id(player)
# list of stats to potentially display from multiselect box
no_player = [col for col in stats.columns if col != 'Player']
all_stats = st.multiselect("Select stats to compare:",no_player,['Tm','PTS','TRB','AST'])
# create dataframe for inputted player
st.subheader(name(player))
stats_player = stats.loc[[player_id]]

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
for idx in stats_player.index:
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
stats_player.insert(0,"Pic",pics)

# build GridOptions object for AgGrid table
options_builder = GridOptionsBuilder.from_dataframe(stats_player[list("Pic".split(" "))+list("Player".split(" "))+all_stats])
options_builder.configure_column('Pic', cellRenderer = render_image,width =50, header_name= "")
options_builder.configure_column('Player', width=165)
options_builder.configure_default_column(width=103)
grid_options = options_builder.build()

# display AgGrid table for inputted player
AgGrid(stats_player[list("Pic".split(" "))+list("Player".split(" "))+all_stats], 
        gridOptions = grid_options,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        height=125, theme='material')


# retrieve 5 most similar players to inputted player
players = similar_players(player_id)
st.subheader('Most Similar Players')
# insert similarity score
players.insert(1,"Similarity",get_similarity(player_id,players))
players['Similarity'] = players['Similarity'].apply(lambda x: '{:.2%}'.format(float(x)))


# create list of the headshots for most similar players from basketball reference
pics = []
for idx in players.index:
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
players.insert(0,"Pic",pics)



# set session state for selected row id to the most similar player
if "sid" not in st.session_state:
    st.session_state['sid'] = 0
    
# build GridOptions object for AgGrid table
options_builder = GridOptionsBuilder.from_dataframe(players[list("Pic".split(" "))+list("Player".split(" "))+all_stats+list("Similarity".split(" "))])
options_builder.configure_column('Pic', cellRenderer = render_image,width =50, header_name= "")
options_builder.configure_column('Player', width=165)
options_builder.configure_column('Similarity', width=119)
options_builder.configure_default_column(width=103)
# set pre selected row to session state of sid
options_builder.configure_selection(selection_mode="single" ,pre_selected_rows=[st.session_state.sid])
grid_options = options_builder.build()

# display AgGrid table for most similar players
grid = AgGrid(players[list("Pic".split(" "))+list("Player".split(" "))+all_stats+list("Similarity".split(" "))], 
        gridOptions = grid_options,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        theme='material')

# function to return comparison table between inputted player and selected player
@st.cache
def get_comp_table(sel_row):
    comp_id = get_id(sel_row[0]["Player"])
    comp = pd.concat([stats.loc[player_id],stats.loc[comp_id]],axis=1).transpose()
    return comp

sel_row = grid["selected_rows"]
    
if sel_row:    
    comp = get_comp_table(sel_row)
    comp_percent = pd.DataFrame()
    comp_percent.index=comp.index
    comp_percent['Player'] = comp['Player']
    
    # list of percent of total stats between the 2 compared players
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
                "subtitle" : "From the table above, select the row of the player you would like to compare directly.",
                "subtitleColor": "gray"
                }
        )
    # line for mean of percent of total values        
    rule = alt.Chart(comp_percent).mark_rule(color='steelblue').encode(
        x='mean(Value):Q'
        )
    
    fig = (bar + rule)
    st.altair_chart(fig, use_container_width=True)




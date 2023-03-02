# NBA Player Similarity

Application Link: https://nba-player-similarity.streamlit.app

<p align="left">
<img src="https://github.com/joshphelan/nba-player-similarity/blob/main/raw_data/MJ.jpg?raw=true" width="250" />
</p>

I created a web application using Streamlit that allows a user to compare the similarity between NBA players. Similarity is measured by the Euclidean distance between the per game and advanced statistics of each player. The statistics are standardized based on a normal distribution. Player data includes players from the 1980 to 2016 seasons at 4 year intervals, and the 2021-2022 season.

The preprocess function in `preprocess.py` calculates the Euclidean distance between each player and every other player in the given dataset. Datasets for each year and all years combined were created using the `clean.py` function.

The application contains three pages that demonstrate similarity in different ways. The first page allows a user to compare two players to find their similarity score and compare their statistics. The other two pages allow a user to find the 5 most similar players to an inputted player within that season and amongst all seasons and compare their statistics.

On all pages, statistics are compared via interactive tables and a horizontal bar chart. The statistics for comparison are chosen by the user, and the tables and bar chart automatically update. There is also a “Choose Random Player” button that lets a user explore a randomly generated player from the dataset.

#!/usr/bin/env python
# coding: utf-8

# # NBA DPOY Shares
# 
# ### Anish Shourie
# 
# Script that calculates the cumulative number of shares of the Defensive Player of the Year (DPOY) award vote that a player has earned throughout his career. *dpoy_shares* is defined as the following:
# 
# $$\sum_{x}\dfrac{\text{number of points received in DPOY voting in year x}}{\text{maximum number of points in year x (all the first place votes)}}$$

# In[1]:


from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
import pandas as pd
import numpy as np
from datetime import datetime

# Getting the helper functions from the NBA_bball_ref_help.py file
import os, sys
currentdir = os.path.dirname(os.path.realpath('dpoy_shares.ipynb'))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

# see Python module in NBA directory
import NBA_bball_ref_help as bb


# In[6]:


"""
This cell will output a dictionary of player names and codes (together in a tuple)
The code is just the basketball reference URL subdirectory
For example, for Kobe Bryant it would be /players/b/bryanko01.html
The player name and code tuple is the key, and the dpoy_share is the value
"""

current_year = datetime.today().year

# DPOY first awarded in 1982-1983 season
years = list(range(1983,current_year+1))
dpoy_shares = {}
    
# scraping the table (commented out on the basketball-reference.com)    
def get_table(comments: list, s: str):
    
    for comment in comments:
        comment1 = BeautifulSoup(str(comment), 'lxml')
        table = comment1.find(id = s)
        if table:
            break
    
    return table


for year in years:

    url = "https://www.basketball-reference.com/awards/awards_{}.html".format(year)
    html = urlopen(url)
    soup = BeautifulSoup(html)
    comments = soup.find_all(string=lambda text:isinstance(text,Comment))

    table = get_table(comments, "dpoy")
    
    headers = [th.getText() for th in table.find_all('tr')[1].findAll('th')]
    headers = headers[1:]
    rows = table.find_all('tr')[1:]
    voting = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
    voting = pd.DataFrame(voting, columns = headers)
    voting = voting.dropna()

    players = []
    
    # finding table data
    tags = table.find_all('td')

    # finding "players" data tags to get unique identifier
    for tag in tags:
        for t in tag.find_all('a'):
            if 'players' in t.get('href'): # if 'players' in URL
                players.append(t.get('href'))

    i = 0
    for index, row in voting.iterrows():

        share = float(row['Pts Won']) / float(row['Pts Max'])
        tup = (players[i], row['Player'])
        
        # updating dictionary with dpoy_shares from the year in the loop
        try:
            dpoy_shares[tup] += share
        except:
            dpoy_shares[tup] = share
        
        # iterating through players list (rows in DataFrame are just the players in the list)
        i+=1


# In[7]:


"""
Run this cell if you just want the DPOY output
"""

dpoy_simple = pd.DataFrame(list(dpoy_shares.items()),columns = ['Code/Name','DPOY_shares'])
dpoy_simple = dpoy_simple.set_index('Code/Name')
dpoy_simple = dpoy_simple.sort_values(by='DPOY_shares', ascending=False)
dpoy_simple.head(5)


# In[3]:


"""
Creating full output
"""

cols = ['Player', 'Seasons', 'Games', 'Minutes', 'DWS',         'Seasons_>50', 'Seasons_>75', 'Seasons_DPOY', 'Seasons_>50_DPOY', 'Seasons_>75_DPOY',       'DPOY_awards','DPOY_shares']
output = pd.DataFrame(columns = cols)
output


# In[4]:


"""
Reading in spreadsheet with basketball-reference data about DPOY winners
"""

dpoy_winners = pd.read_excel('dpoy_winners.xlsx', index_col='code')
dpoy_winners.head(5)


# In[5]:


"""
This cell gets other statistics about the players
to output in a DataFrame
"""

base_url = 'https://www.basketball-reference.com'


for p in dpoy_shares.keys():
    
    url = base_url+p[0]

    html = urlopen(url)
    soup = BeautifulSoup(html)
    table = soup.find(id='div_advanced')

    headers = [th.getText() for th in table.find_all('tr')[0].findAll('th')]
    rows = table.find_all('tr')[1:]
    stats = [[tc.getText() for tc in rows[i].findAll(['th','td'])]for i in range(len(rows))]
    stats = pd.DataFrame(stats, columns = headers)

    stats = stats.replace(r'^\s*$', np.nan, regex=True)
    stats = stats.dropna(subset=['Age'])
    stats = stats.dropna(axis=1, how='all')

    stats['G'] = pd.to_numeric(stats['G'])
    stats['MP'] = pd.to_numeric(stats['MP'])
    stats['DWS'] = pd.to_numeric(stats['DWS'])
    
    stats = stats.drop_duplicates(subset='Season', keep='first')

    seasons = len(stats)
    games = sum(stats['G'])
    minutes = sum(stats['MP'])
    dws = sum(stats['DWS'])

    pct_50 = 0
    pct_50_dpoy = 0
    pct_75 = 0
    pct_75_dpoy = 0
    num_dpoy = 0

    for index, row in stats.iterrows():

        year = bb.get_season_int(season = row['Season'])

        if year >= 1983:
            num_dpoy += 1
        
        teams = bb.team_totals(year, row['Lg'])
        
        if row['Tm'] == 'TOT':
            tm_games = int(max(teams['G']))
        else:
            team = bb.team_codes(row['Tm'])
            tm_games = int(teams.loc[team,'G'])

        if row['G'] >= 0.75 * tm_games:
            pct_75 += 1
            
        if row['G'] >= 0.5 * tm_games:
            pct_50 += 1

        if row['G'] >= 0.75 * tm_games and year >= 1983:
            pct_75_dpoy += 1
            
        if row['G'] >= 0.5 * tm_games and year >= 1983:
            pct_50_dpoy += 1

    output.loc[p[0], 'Player'] = p[1]
    output.loc[p[0], 'Seasons'] = seasons
    output.loc[p[0], 'Games'] = games
    output.loc[p[0], 'Minutes'] = minutes
    output.loc[p[0], 'DWS'] = dws
    output.loc[p[0], 'Seasons_DPOY'] = num_dpoy
    output.loc[p[0], 'Seasons_>50'] = pct_50
    output.loc[p[0], 'Seasons_>75'] = pct_75
    output.loc[p[0], 'Seasons_>50_DPOY'] = pct_50_dpoy
    output.loc[p[0], 'Seasons_>75_DPOY'] = pct_75_dpoy
    output.loc[p[0], 'Seasons_>75_DPOY'] = pct_75_dpoy
    try:
        output.loc[p[0], 'DPOY_awards'] = dpoy_winners.loc[p[0], 'num']
    except:
        output.loc[p[0], 'DPOY_awards'] = 0
    output.loc[p[0], 'DPOY_shares'] = dpoy_shares[p]
    
    
output.head(5)


# In[6]:


output.to_csv("dpoy_shares.csv")


# In[ ]:





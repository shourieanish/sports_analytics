from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
import pandas as pd

"""
Getting the total stats for each team for a particular season
input: year (e.g. 1999 = 1998-99 NBA season)
output: DataFrame with team statistics for that season
"""
def team_totals(year: int = 1999, lg: str = 'NBA'):
    
    # checking input
    if not isinstance(year, int):
        raise ValueError("int required for year")

    if year > 1976 and lg != 'NBA':
    	raise ValueError("incorrect league code")
    
    teams_url = 'https://www.basketball-reference.com/leagues/{}_{}.html'.format(lg, year)

    # scraping
    html = urlopen(teams_url)
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find(id = 'div_totals-team')

    headers = [th.getText() for th in table.find_all('tr')[0].findAll('th')][1:]
    rows = table.find_all('tr')[1:]
    team_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
    team_stats = pd.DataFrame(team_stats, columns = headers)
    
    team_stats = team_stats[:-1]
    for index, row in team_stats.iterrows():
        if row['Team'][-1] == '*':
            team_stats.loc[index, 'Team'] = row['Team'][:-1]
            
    team_stats.set_index('Team', inplace=True)
    
    return team_stats


"""
Getting the integer form of an NBA season
input: String (e.g. "2015-16")
output: Integer (e.g 2016)
"""
def get_season_int(season: str) -> int:

	if isinstance(season, int):
		return season
	elif season.isnumeric():
		season_int = int(season)
	elif '-' in season:
		season = season.split('-')
		season_int = int(season[0])+1
	else:
		raise ValueError("Incorrect season format")

	return season_int


"""
Using a three letter code provided by
basketball-reference and matching it with the respective team
input: code (e.g. GSW)
output: String of team name (e.g. "Golden State Warriors")
"""
def team_codes(code: str) -> str:

	teams = {
	    "ATL" : "Atlanta Hawks",
	    "BOS" : "Boston Celtics",
	    "BRK" : "Brooklyn Nets",
	    "BUF" : "Buffalo Braves",
	    "CHA" : "Charlotte Bobcats",
	    "CHH" : "Charlotte Hornets",
	    "CHO" : "Charlotte Hornets",
	    "CHI" : "Chicago Bulls",
	    "CLE" : "Cleveland Cavaliers",
	    "DAL" : "Dallas Mavericks",
	    "DEN" : "Denver Nuggets",
	    "DET" : "Detroit Pistons",
	    "DNA" : "Denver Nuggets",
	    "DNN" : "Denver Nuggets",
	    "GSW" : "Golden State Warriors",
	    "HOU" : "Houston Rockets",
	    "IND" : "Indiana Pacers",
	    "KCK" : "Kansas City Kings",
	    "KEN" : "Kentucky Colonels",
	    "LAC" : "Los Angeles Clippers",
	    "LAL" : "Los Angeles Lakers",
	    "MEM" : "Memphis Grizzlies",
	    "MIA" : "Miami Heat",
	    "MIL" : "Milwaukee Bucks",
	    "NJN" : "New Jersey Nets",
	    "NOH" : "New Orleans Hornets",
	    "NOK" : "New Orleans/Oklahoma City Hornets",
	    "NOP" : "New Orleans Pelicans",
	    "NYA" : "New York Nets",
	    "NYK" : "New York Knicks",
	    "MIN" : "Minnesota Timberwolves",
	    "SEA" : "Seattle SuperSonics",
	    "OKC" : "Oklahoma City Thunder",
	    "ORL" : "Orlando Magic",
	    "PHI" : "Philadelphia 76ers",
	    "PHO" : "Phoenix Suns",
	    "POR" : "Portland Trail Blazers",
	    "SAC" : "Sacramento Kings",
	    "SAS" : "San Antonio Spurs",
	    "SDA" : "San Diego Conquistadors",
	    "SSL" : "Spirits of St. Louis",
	    "TOR" : "Toronto Raptors",
	    "UTA" : "Utah Jazz",
	    "UTS" : "Utah Stars",
	    "VAN" : "Vancouver Grizzlies",
	    "WAS" : "Washington Wizards",
	    "WSB" : "Washington Bullets"
	}

	return teams[code]
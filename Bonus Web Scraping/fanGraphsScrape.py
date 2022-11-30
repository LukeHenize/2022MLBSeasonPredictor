from bs4 import BeautifulSoup
#use selenium instead of requests when loading dynamic JS page content
from selenium import webdriver
import csv

#Scrape basic team stats from fangraphs.com
#use this dictionary to convert from full team names to abbreviated names
teams = ["LAA", "HOU", "OAK", "TOR", "ATL", "MIL", "STL", "CHC", "ARI", "LAD",
"SF", "CLE", "SEA", "MIA", "NYM", "WSH", "BAL", "SD", "PHI", "PIT", "TEX", "TB",
"BOS", "CIN", "COL", "KC", "DET", "MIN", "CHW", "NYY"]
fullNames = ["Angels", "Astros", "Athletics", "Blue Jays", "Braves", "Brewers", "Cardinals",
"Cubs", "DiamondBacks", "Dodgers", "Giants", "Guardians", "Mariners", "Marlins", "Mets",
"Nationals", "Orioles", "Padres", "Phillies", "Pirates", "Rangers", "Rays", "Red Sox",
"Reds", "Rockies", "Royals", "Tigers", "Twins", "White Sox", "Yankees"]

fullToAbbrv = {}
i = 0
while i < len(fullNames) :
    fullToAbbrv[fullNames[i]] = teams[i]
    i += 1

#sometimes will throw an error after selenium browser closes, but
#still gathers all data into .csv file.
try:
    driver = webdriver.Chrome()
    driver.get("https://www.fangraphs.com/standings/playoff-odds")
    source = driver.page_source

    #how we would get page source code if we were using requests instead
    #source = requests.get("https://www.fangraphs.com/standings/playoff-odds")
    #source.raise_for_status()

    #create and write header for csv file
    file = open("FanGraphs.csv", "w")
    writer = csv.writer(file)
    writer.writerow(["Team", "W", "L", "W%", "Strength of Schedule", "Make Playoffs"])

    #make the soup and start scraping
    soup = BeautifulSoup(source, "html5lib")
    divisionTags = soup.find_all("div", class_="scroll")
    for divisionTag in divisionTags :
        table = divisionTag.table.tbody
        #find each team (or row) in the table
        teamTags = table.find_all("tr", recursive=False)
        for teams in teamTags :
            #scrape the team stats we want
            fullName = teams.find("span", class_="fullName").string
            name = fullToAbbrv[fullName]
            wins = teams.contents[1].contents[0] #each <td> has text AND a <br>, so we call .contents twice
            losses = teams.contents[2].contents[0]
            winPercent = teams.contents[3].contents[0]
            strengthSched = teams.contents[8].contents[0]
            playoffOdds = teams.contents[12].contents[0]
            writer.writerow([name, wins, losses, winPercent, strengthSched, playoffOdds])
    #close webdriver and csv writer
    driver.close()
    file.close()
except Exception as e:
    print(e) 

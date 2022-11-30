#THIS FILE IS IDENTICAL TO THE JUPYTER NOTEBOOK FOR THIS PROJECT,
#BUT IN A .PY FILE SO IT CAN BE RUN A DIFFERENT WAY

#Objective: gather data from the 2022 MLB season so far
#and simulate the result of the remaining games for each team.

#To do this we will need access to basic team statistics like number 
#of wins, losses, and win percentage. In order to more accurately predict
#future games, the remaining season schedule for each team will also be accessed.
#The result of these games realistically depends on hundreds of factors, but 
#to keep this model relatively simple, we'll just use head-to-head score
#throughout the first half of the season to determine a team's probability 
#of winning a game against a given opponent.

from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import os
import random

#these are the team abbreviations we will use to refer to each team
teams = ["LAA", "HOU", "OAK", "TOR", "ATL", "MIL", "STL", "CHC", "ARI", "LAD",
"SF", "CLE", "SEA", "MIA", "NYM", "WSH", "BAL", "SD", "PHI", "PIT", "TEX", "TB",
"BOS", "CIN", "COL", "KC", "DET", "MIN", "CHW", "NYY"]


#we need to look at the remaining schedule of each team. To do this, we'll
#create a new csv file for each team to hold the schedule and head-to-head stats.
#We'll use a function to create these files and fill the schedule
#quickly for all thirty teams.

#but first, because a few of the abbreviations used by Baseball Reference
#are different from the ones we used above, we'll create a dictionary to convert the names.
bballRefNames = ["LAA", "HOU", "OAK", "TOR", "ATL", "MIL", "STL", "CHC", "ARI", "LAD",
"SFG", "CLE", "SEA", "MIA", "NYM", "WSN", "BAL", "SDP", "PHI", "PIT", "TEX", "TBR",
"BOS", "CIN", "COL", "KCR", "DET", "MIN", "CHW", "NYY"]
abbrvToRef = {}
refToAbbrv = {}
i = 0
while i < len(bballRefNames) :
    abbrvToRef[teams[i]] = bballRefNames[i]
    refToAbbrv[bballRefNames[i]] = teams[i]
    i += 1

def createScheduleCSV(teamName) :
    path = "schedules/" + teamName + ".csv"
    file = open(path, "w")
    writer = csv.writer(file)
    #write file header
    writer.writerow(["Date","Opponent", "Actual Result", "Predicted Result", "H2H Wins", "H2H Losses"])

    #get access to file
    schedFile = schedFileTemplate[ :41] + abbrvToRef[teamName] + schedFileTemplate[41: ]
    #use requests to get source code because the page content is not dynamic
    try :
        source = requests.get(schedFile)
        source.raise_for_status()
        soup = BeautifulSoup(source.text, "html.parser")
        #find schedule in page source code
        fullSched = soup.find("table", id="team_schedule").tbody
        games = fullSched.find_all("tr", recursive=False)
        tableDividers = fullSched.find_all("tr", class_="thead")
        #remove dividers from our schedule
        for divider in tableDividers :
            if divider in games :
                games.remove(divider)

        for game in games :

            #check date if after All-Star Break, don't fill in win/loss
            date = game.find("td", attrs={"data-stat":"date_game"})["csk"]

            opp = game.find("td", attrs={"data-stat":"opp_ID"}).string
            #if opp is SDP, WSN, SFG, TBR, or KCR then convert back
            opp = refToAbbrv[opp]

            resultCell = game.find("td", attrs={"data-stat":"win_loss_result"})
            if resultCell is not None : 
                result = resultCell.string
                #clear walk-off, we don't care
                if "-wo" in result :
                    result = result[0]
            else : #game hasn't been played yet and we will predict
                result = ""

            writer.writerow([date, opp, result])
        source.close()
    except Exception as e:
        print(e)
    file.close()

#Now we just call this function for each team (again, with the following abbreviations)
teams = ["LAA", "HOU", "OAK", "TOR", "ATL", "MIL", "STL", "CHC", "ARI", "LAD",
"SF", "CLE", "SEA", "MIA", "NYM", "WSH", "BAL", "SD", "PHI", "PIT", "TEX", "TB",
"BOS", "CIN", "COL", "KC", "DET", "MIN", "CHW", "NYY"]
#connect to the Baseball Reference page for each team using this link template.
schedFileTemplate = "https://www.baseball-reference.com/teams//2022-schedule-scores.shtml"
if not os.path.isdir("schedules") :
    os.mkdir("schedules")
for team in teams :
    createScheduleCSV(team)
    

#At this point, we haven't filled in the head-to-head win and loss columns for the
#teams, so we'll go back through the csv files and calculate those now with this function.
def createH2HScores(file) :
    schedule = pd.read_csv(file)
    h2hScores = pd.DataFrame(columns = ["Opponent","H2H Wins", "H2H Losses"])

    #fill our head-to-head dataframe with each opponent on the schedule
    for opp in schedule["Opponent"] :
        h2hScores.loc[len(h2hScores.index)] = [opp, 0, 0]

    #fill in wins/losses in this dataframe by looping back over the schedule.
    #we'll use this function to sum up cumulative h2h scores played before a certain game
    def findPrevH2HScores(gameNum, opp) :
        if gameNum == 0 : #special case for opening day
            return [0, 0]
        gameNum -= 1
        #go back in the schedule until we find last game played against opp
        while schedule.loc[gameNum, "Opponent"] != opp :
            gameNum -= 1
            if gameNum == -1 :
                #no previous games have been played on schedule
                return [0, 0]
        return [h2hScores.loc[gameNum, "H2H Wins"], h2hScores.loc[gameNum, "H2H Losses"]]

    for index, game in schedule.iterrows() :
        opp = game["Opponent"]
        prevH2H = findPrevH2HScores(index, opp)
        #if game hasn't been played, we just fill with prev score (don't increment W/L)
        if pd.isnull(game["Actual Result"]) :
            h2hScores.loc[index] = [opp, prevH2H[0], prevH2H[1]]
        #otherwise we can add either a W or L to h2hScores
        else :
            result = game["Actual Result"]
            if result == "W" :
                h2hScores.loc[index] = [opp, prevH2H[0] + 1, prevH2H[1]]
            elif result == "L" :
                h2hScores.loc[index] = [opp, prevH2H[0], prevH2H[1] + 1]

    #With the head-to-head scores finally calculated, we can add them back to
    #the teams' csv files. We'll need to combine the schedule and h2hScores 
    #dataframes as we cannot just edit the rows in the csv.
    schedule["H2H Wins"] = h2hScores["H2H Wins"]
    schedule["H2H Losses"] = h2hScores["H2H Losses"]
    #as stated at the start of the notebook, the predictions will be made on
    #head-to-head results, so we also need to calculate a win percentage
    #based on the h2h columns
    #1 win and 1 loss are added to account for games with 0 H2H wins/losses
    winChance = round((schedule["H2H Wins"] + 1) / (schedule["H2H Wins"] + schedule["H2H Losses"] + 2), 3)
    schedule["Win %"] = winChance

    #write h2hScores into the original csv file
    schedule.to_csv(file, index=False)

#After we've calculated a win % for each team for each game depending on their opponent, we're finally
#ready to begin predicting games. For each game that hasn't been played yet, we'll make a prediction
#using our calculated win percentage and a simple randomly generated number guess.
def predictSeason(file) :
    schedule = pd.read_csv(file)
    predictions = []
    #we don't need to predict any games that have already happened
    for index, game in schedule.iterrows() :
        if not pd.isnull(game["Actual Result"]) :
            predictions.append("-")
        elif pd.isnull(game["Predicted Result"]) : #check if we've already predicted this game from another file
            #predict game based on h2h win%
            winChance = game["Win %"]
            #generate a random number (0 -> 1.000) to simulate the game
            rand = random.randrange(0, 1000) / 1000.0
            #compare rand to winChance to see if game was won/lost
            if rand <= winChance :
                predictions.append("W")
            else :
                predictions.append("L")
    #add our predictions to the full schedule and rewrite csv one more time
    schedule["Predicted Result"] = predictions
    schedule.to_csv(file, index=False)

#At the very end of each team's csv file, we can calculate the season record, 
#and add the team's record to our dictionary.
def calcSeasonTeamStats(file, winCounts, team) :
    schedule = pd.read_csv(file)
    allResults = pd.concat([schedule["Actual Result"], schedule["Predicted Result"]])

    winCount = allResults.value_counts()["W"] 
    lossCount = allResults.value_counts()["L"]
    winChance = round((winCount / (winCount + lossCount)), 3)
    winCounts[team] = winCount
    #write(append) to csv
    handle = open(file, "a")
    writer = csv.writer(handle)
    writer.writerow(["Wins", "Losses", "Win %"])
    writer.writerow([winCount, lossCount, winChance])
    handle.close()

#get access to each team's csv file and generate 1) the head-to-head scores and
#win percentages, 2) predictions for each game yet to be played this season,
#3) season-long stats for each team, and 4) a complete standings file based on
#all our predictions

#create a dictionary to hold each team's win count
winCounts = {}
fileTemplate = "schedules/.csv"
for team in teams :
    file = fileTemplate[ :10] + team + fileTemplate[10: ]
    createH2HScores(file)
    predictSeason(file)
    calcSeasonTeamStats(file, winCounts, team)

#The "schedules" folder now holds a .csv file for each team 
#containing the team's schedule, actual results of games already 
#played, predicted results of games that have yet to be played, 
#and head to head scores against specific opponents. (Note that 
#the .csv files seem to display incorrectly when using the 
#default Jupyter csv viewer. Try using excel or some other 
#software).

#After calculating the season stats for each team, the winCounts 
#dictionary should hold the record for each team. We can now 
#create one last file to conveniently display division standings 
#across the league.

#We'll organize the teams into divisions by creating this dataframe
divisions = pd.DataFrame()
divisions["AL East"] = [["NYY", winCounts["NYY"]], ["BOS", winCounts["BOS"]], ["TB", winCounts["TB"]], ["TOR", winCounts["TOR"]], ["BAL", winCounts["BAL"]]]
divisions["AL Central"] = [["MIN", winCounts["MIN"]], ["CHW", winCounts["CHW"]], ["CLE", winCounts["CLE"]], ["KC", winCounts["KC"]], ["DET", winCounts["DET"]]]
divisions["AL West"] = [["LAA", winCounts["LAA"]], ["HOU", winCounts["HOU"]], ["TEX", winCounts["TEX"]], ["SEA", winCounts["SEA"]], ["OAK", winCounts["OAK"]]]
divisions["NL East"] = [["NYM", winCounts["NYM"]], ["ATL", winCounts["ATL"]], ["WSH", winCounts["WSH"]], ["PHI", winCounts["PHI"]], ["MIA", winCounts["MIA"]]]
divisions["NL Central"] = [["STL", winCounts["STL"]], ["MIL", winCounts["MIL"]], ["CHC", winCounts["CHC"]], ["CIN", winCounts["CIN"]], ["PIT", winCounts["PIT"]]]
divisions["NL West"] = [["SD", winCounts["SD"]], ["LAD", winCounts["LAD"]], ["SF", winCounts["SF"]], ["ARI", winCounts["ARI"]], ["COL", winCounts["COL"]]]
#sort each divisions according to number of wins
for division in divisions :
    sortedDiv = sorted(divisions[division], key = lambda x : x[1], reverse=True)
    divisions[division] = sortedDiv
#now create a standings file and write to it
standings = open("FinalStandings.csv", "w")
writer = csv.writer(standings)
writer.writerow(["MLB Predicted Standings"])
writer.writerow([""]) #print a space for formatting
winTotal = 0 #used for debugging
for division in divisions :
    writer.writerow([division + " Standings"])
    writer.writerow(["Team", "Wins", "Losses"])
    for team in divisions[division] :
        wins = winCounts[team[0]]
        losses = 162 - wins
        writer.writerow([team[0], wins, losses])

        winTotal += wins
writer.writerow(["Total Wins", "Total Games"])
writer.writerow([winTotal, (30 * 162) / 2])
standings.close()

#And with that, all 2022 regular season games have been predicted!
#See FinalStandings.csv for a convenient display of division 
#standings, the schedules folder for the results of each 
#individual game played by each team, or compare the results 
#generated here with the predictions on 
#[FanGraphs.com](https://www.fangraphs.com/standings/playoff-odds)
#(using a model I can only assume is significantly more complex).
#You can always run this code again and generate new (often 
#vastly different...) predictions!
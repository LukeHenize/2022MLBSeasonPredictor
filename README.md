# 2022MLBSeasonPredictor
A data science project that predicts the results of the remaining games of the 2022 MLB schedule using real statistics from games already played.

## Navigating This Project
The easiest way to check out my season predictor is through the Jupyter notebook (.ipynb file). It contains all of the code used in my predictor as well as my comments 
to explain what I am doing and why.

If you have Python (and a few necessary libraries) installed on your computer, you can download the predictor.py Python script and easily run the predictor yourself to generate 
new predictions. This project does have elements of randomness, so each time the Python script is run, new predictions are made. You can view the results of <i>every</i> 
game played throughout the season in the "schedules" folder or take a quicker look at the season-end division standings in the FinalStandings.csv file.

If you're uninterested in looking at code and just want to see what kind of predictions this project makes, I recommend you look through the "ASG PREDICTIONS" folder.
The files here were generated using this project and clearly show the results for every team's scheduled games (in the schedules folder) and the predicted division 
standings at the end of the year in the FinalStandings file, one of which can be opened in Excel to see playoff teams highlighted.

Finally, the "Bonus Web Scraping" folder is largely unrelated to the rest of my project. It contains a separate Python file that scrapes data from FanGraphs.com, a
site that publishes their own MLB predictions using a more advanced model. I would've liked to compare the results of my predictor to theirs, but time didn't allow. I've
left this folder in the repository in case anyone is interested anyways.

If you're reading this, thanks for checking out my project!

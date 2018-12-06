import pandas as pd
from pulp import *

def generate_nfl_lineup(QBs,RBs,WRs,TEs,DSTs,salary,salary_cap,points,players):
    ''' Computes the optimal lineup based on salaries and projected points.
    
    Args:
        infile: a pandas dataframe in the same format as the downloadable CSV file from DraftKings
        
    Returns:
        An array consisting of player IDs of players in the optimal DraftKings lineup
    '''
    
    # Define the problem
    prob = LpProblem('optimal_lineup', pulp.LpMaximize)
    
    # Variable to denote whether or not player is included in lineup
    include = LpVariable.dict('include', [player for player in players], lowBound=0, upBound=1, cat='Integer')
    
    # The objective is to maximize the number of projected points in the lineup
    prob += lpSum([include[player] * points[player] for player in players])

    # Positional constraints: 1 QB, >= 2 RBs, >= 3 WRs, >= 1 TEs, 1 DST, 9 players total
    prob += lpSum([include[player] * QBs[player] for player in players]) == 1
    prob += lpSum([include[player] * RBs[player] for player in players]) >= 2
    prob += lpSum([include[player] * WRs[player] for player in players]) >= 3
    prob += lpSum([include[player] * TEs[player] for player in players]) >= 1
    prob += lpSum([include[player] * DSTs[player] for player in players]) == 1
    prob += lpSum(include[player] for player in players) == 9
    
    # Salary constraints
    prob += lpSum([include[player] * salary[player] for player in players]) <= salary_cap
    
    status = prob.solve()
    
    # Print IDs of players in lineup
    lineup = []
    for player in players:
        if value(include[player]) == 1:
            lineup.append(player)
    
    return lineup

def main():
    infile = pd.read_csv("./data/DKSalaries_nfl.csv")
    salary_cap = 50000
    
    # Ensure formatting of columns is as expected
    assert len(infile.iloc[:,0].unique()) == 5, "There should be only five unique position types in dataset."
    
    # Initialize array of all player IDs
    players = []
    # Initialize position dictionaries
    QBs = {}
    RBs = {}
    WRs = {}
    TEs = {}
    DSTs = {}
    salary = {}
    points = {}
    
    # Add player ID as a key to the seven dictionaries initialized above
    # The five position dictionaries contain binary values:
    # if player is listed as respective position, dictionary value is 1, and 0 otherwise
    for i in range(len(infile)):
        players.append(infile.iloc[i,3]) # Append player ID to list
        salary[infile.iloc[i,3]] = infile.iloc[i,5]
        points[infile.iloc[i,3]] = infile.iloc[i,8]
        if infile.iloc[i,0] == 'QB':
            QBs[infile.iloc[i,3]] = 1
            RBs[infile.iloc[i,3]] = 0
            WRs[infile.iloc[i,3]] = 0
            TEs[infile.iloc[i,3]] = 0
            DSTs[infile.iloc[i,3]] = 0
        if infile.iloc[i,0] == 'RB':
            QBs[infile.iloc[i,3]] = 0
            RBs[infile.iloc[i,3]] = 1
            WRs[infile.iloc[i,3]] = 0
            TEs[infile.iloc[i,3]] = 0
            DSTs[infile.iloc[i,3]] = 0
        if infile.iloc[i,0] == 'WR':
            QBs[infile.iloc[i,3]] = 0
            RBs[infile.iloc[i,3]] = 0
            WRs[infile.iloc[i,3]] = 1
            TEs[infile.iloc[i,3]] = 0
            DSTs[infile.iloc[i,3]] = 0
        if infile.iloc[i,0] == 'TE':
            QBs[infile.iloc[i,3]] = 0
            RBs[infile.iloc[i,3]] = 0
            WRs[infile.iloc[i,3]] = 0
            TEs[infile.iloc[i,3]] = 1
            DSTs[infile.iloc[i,3]] = 0
        if infile.iloc[i,0] == 'DST':
            QBs[infile.iloc[i,3]] = 0
            RBs[infile.iloc[i,3]] = 0
            WRs[infile.iloc[i,3]] = 0
            TEs[infile.iloc[i,3]] = 0
            DSTs[infile.iloc[i,3]] = 1

    generate_nfl_lineup(QBs,RBs,WRs,TEs,DSTs,salary,salary_cap,points,players)
    
if __name__ == '__main__':
    main()
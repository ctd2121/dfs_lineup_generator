import pandas as pd
import pulp

def add_lineup_to_template(lineup, template, pos_P,pos_C1B,pos_2B,pos_3B,pos_SS,pos_OF):
    lineup_positions = {}
    for player in lineup:
        if pos_P[player] == 1:
            lineup_positions['P'] = player
        elif pos_C1B[player] == 1:
            if 'C/1B' not in lineup_positions:
                lineup_positions['C/1B'] = player
            else:
                lineup_positions['UTIL'] = player
        elif pos_2B[player] == 1:
            if '2B' not in lineup_positions:
                lineup_positions['2B'] = player
            else:
                lineup_positions['UTIL'] = player
        elif pos_3B[player] == 1:
            if '3B' not in lineup_positions:
                lineup_positions['3B'] = player
            else:
                lineup_positions['UTIL'] = player
        elif pos_SS[player] == 1:
            if 'SS' not in lineup_positions:
                lineup_positions['SS'] = player
            else:
                lineup_positions['UTIL'] = player
        elif pos_OF[player] == 1:
            if 'OF1' not in lineup_positions:
                lineup_positions['OF1'] = player
            else:
                if 'OF2' not in lineup_positions:
                    lineup_positions['OF2'] = player
                else:
                    if 'OF3' not in lineup_positions:
                        lineup_positions['OF3'] = player
                    else:
                        lineup_positions['UTIL'] = player

    template = template.append(lineup_positions, ignore_index=True)
    return template



def generate_fd_mlb_lineup(pos_P,pos_C1B,pos_2B,pos_3B,pos_SS,pos_OF,
                           salary,salary_cap,points,players,template):
    # Define the problem
    prob = pulp.LpProblem('optimal_lineup', pulp.LpMaximize)
    
    # Variable to denote whether or not player is included in lineup
    include = pulp.LpVariable.dict('include', [player for player in players], lowBound=0, upBound=1, cat='Integer')
    
    # The objective is to maximize the number of projected points in the lineup
    prob += pulp.lpSum([include[player] * points[player] for player in players])

    # Positional constraints: 1 P, >= 1 C1B,2B,3B,SS, >= 3 WRs, >= 1 TEs, 1 DST, 9 players total
    prob += pulp.lpSum([include[player] * pos_P[player] for player in players]) == 1
    prob += pulp.lpSum([include[player] * pos_C1B[player] for player in players]) >= 1
    prob += pulp.lpSum([include[player] * pos_2B[player] for player in players]) >= 1
    prob += pulp.lpSum([include[player] * pos_3B[player] for player in players]) >= 1
    prob += pulp.lpSum([include[player] * pos_SS[player] for player in players]) >= 1
    prob += pulp.lpSum([include[player] * pos_OF[player] for player in players]) >= 3
    prob += pulp.lpSum(include[player] for player in players) == 9
    
    # Salary constraints
    prob += pulp.lpSum([include[player] * salary[player] for player in players]) <= salary_cap
    
    status = prob.solve()
    
    # Create array that consists of IDs of players in lineup
    lineup = []
    for player in players:
        if pulp.value(include[player]) == 1:
            lineup.append(player)

    template = add_lineup_to_template(lineup, template,
                                      pos_P,pos_C1B,pos_2B,pos_3B,pos_SS,pos_OF)
    return template
    
def main():
    
    # INPUTS
    infile = pd.read_csv("./data/FanDuel-MLB.csv")
    salary_cap = 35000
        
    # Initialize array of all player IDs
    players = []
    # Initialize position dictionaries
    pos_P = {}
    pos_C1B = {}
    pos_2B = {}
    pos_3B = {}
    pos_SS = {}
    pos_OF = {}
    salary = {}
    points = {}
    
    # in FanDuel, catchers and first-basemen can be used interchangably
    infile.Position = infile.Position.replace('C', 'C1B')
    infile.Position = infile.Position.replace('1B', 'C1B')
    
    for i in range(len(infile)):
        players.append(infile.loc[i,'Id'])
        salary[infile.loc[i,'Id']] = infile.loc[i,'Salary']
        points[infile.loc[i,'Id']] = infile.loc[i,'FPPG']
        if infile.loc[i,'Position'] == 'P':
            pos_P[infile.loc[i,'Id']] = 1
            pos_C1B[infile.loc[i,'Id']] = 0
            pos_2B[infile.loc[i,'Id']] = 0
            pos_3B[infile.loc[i,'Id']] = 0
            pos_SS[infile.loc[i,'Id']] = 0
            pos_OF[infile.loc[i,'Id']] = 0
        elif infile.loc[i,'Position'] == 'C1B':
            pos_P[infile.loc[i,'Id']] = 0
            pos_C1B[infile.loc[i,'Id']] = 1
            pos_2B[infile.loc[i,'Id']] = 0
            pos_3B[infile.loc[i,'Id']] = 0
            pos_SS[infile.loc[i,'Id']] = 0
            pos_OF[infile.loc[i,'Id']] = 0
        elif infile.loc[i,'Position'] == '2B':
            pos_P[infile.loc[i,'Id']] = 0
            pos_C1B[infile.loc[i,'Id']] = 0
            pos_2B[infile.loc[i,'Id']] = 1
            pos_3B[infile.loc[i,'Id']] = 0
            pos_SS[infile.loc[i,'Id']] = 0
            pos_OF[infile.loc[i,'Id']] = 0
        elif infile.loc[i,'Position'] == '3B':
            pos_P[infile.loc[i,'Id']] = 0
            pos_C1B[infile.loc[i,'Id']] = 0
            pos_2B[infile.loc[i,'Id']] = 0
            pos_3B[infile.loc[i,'Id']] = 1
            pos_SS[infile.loc[i,'Id']] = 0
            pos_OF[infile.loc[i,'Id']] = 0
        elif infile.loc[i,'Position'] == 'SS':
            pos_P[infile.loc[i,'Id']] = 0
            pos_C1B[infile.loc[i,'Id']] = 0
            pos_2B[infile.loc[i,'Id']] = 0
            pos_3B[infile.loc[i,'Id']] = 0
            pos_SS[infile.loc[i,'Id']] = 1
            pos_OF[infile.loc[i,'Id']] = 0
        elif infile.loc[i,'Position'] == 'OF':
            pos_P[infile.loc[i,'Id']] = 0
            pos_C1B[infile.loc[i,'Id']] = 0
            pos_2B[infile.loc[i,'Id']] = 0
            pos_3B[infile.loc[i,'Id']] = 0
            pos_SS[infile.loc[i,'Id']] = 0
            pos_OF[infile.loc[i,'Id']] = 1

    # create template to be uploaded to FanDuel
    template = pd.DataFrame(columns = ['P', 'C/1B', '2B', '3B',
                                       'SS', 'OF1', 'OF2', 'OF3', 'UTIL'])

    template = generate_fd_mlb_lineup(pos_P,pos_C1B,pos_2B,pos_3B,pos_SS,pos_OF,
                           salary,salary_cap,points,players,template)
    return template
    
    
    
if __name__ == '__main__':
    template = main()
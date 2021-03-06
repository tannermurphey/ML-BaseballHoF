'''A collection of stats generating functions meant to clarify code in the notebooks.
Using the database in the '''

import numpy as np
import pandas as pd

players    = pd.read_csv('baseballdatabank-2022.2/core/People.csv') #basic player info, may want to trim down in future
batting    = pd.read_csv('baseballdatabank-2022.2/core/Batting.csv') # regular season batting
pitching   = pd.read_csv('baseballdatabank-2022.2/core/Pitching.csv')
FG_weights = pd.read_csv('FanGraphs-Leaderboard.csv')
postseason = pd.read_csv('baseballdatabank-2022.2/core/SeriesPost.csv')
awards     = pd.read_csv("baseballdatabank-2022.2/contrib/AwardsPlayers.csv")
allstar    = pd.read_csv("baseballdatabank-2022.2/core/AllstarFull.csv")
post_bat   = pd.read_csv('baseballdatabank-2022.2/core/BattingPost.csv')
post_pitch = pd.read_csv('baseballdatabank-2022.2/core/PitchingPost.csv')
halloffame = pd.read_csv('baseballdatabank-2022.2/contrib/HallOfFame.csv')
appearances= pd.read_csv('baseballdatabank-2022.2/core/Appearances.csv')

players_ids = set(players['playerID'].values)

batting = batting.replace('', 0, regex=True)
batting = batting.replace(np.NaN, 0, regex=True)

pitching = pitching.replace('', 0, regex=True)
pitching = pitching.replace(np.NaN, 0, regex=True)


def verify_player(playerID):
    '''Verifies that that player is in the database
    by checking their unique playerID against it.'''
    if playerID in players_ids:
        pass
    else:
        raise Exception(f"IDError: playerID {playerID} not found in database")

def verify_batter(playerID):
    '''Verifies that the playerID recorded at lease one AB at some point'''

    if playerID in batting['playerID'].values:
        pass
    else:
        raise Exception(f"IDError: playerID {playerID} not found among batters")

def verify_pitcher(playerID):
    '''Verifies that the playerID pitched at some point'''

    if playerID in pitching['playerID'].values:
        pass
    else:
        raise Exception(f"IDError: playerID {playerID} not found among pitchers")






def count_batting_stat(playerID, stat):
    '''Allows the searching of the total number of a stat a player has,
        (hits, walks, strikeouts, etc.).
        PARAMS: playerID: the playerID of the relevant player
                stat: the stat that we want to be tallied'''
    verify_player(playerID)
    verify_batter(playerID)

    if stat == "K": #adding this because I know I'll make this mistake in the future
        stat = "SO"

    return float(batting.loc[batting['playerID']==playerID, [stat]].sum().values)

def count_pitching_stat(playerID, stat):
    '''Allows the searching of the total number of a stat a player has,
        (strikeouts, wins, saves, etc.).
        PARAMS: playerID: the playerID of the relevant player
                stat: the stat that we want to be tallied'''
    verify_player(playerID)
    verify_pitcher(playerID)

    if stat == "K": #adding this because I know I'll make this mistake in the future
        stat = "SO"

    return float(pitching.loc[pitching['playerID']==playerID, [stat]].sum().values)


def get_FG_coeff(year, c):

    return float(FG_weights.loc[(FG_weights['Season']==year), [c]].values)

def count_appearances(playerID):
    '''Counts the appearances each player made at a position'''
    cols = ['G_p','G_c','G_1b','G_2b','G_3b','G_ss','G_of','G_dh','G_ph','G_pr']

    return appearances.loc[appearances['playerID']==playerID, cols].sum(axis=0)


###BASIC STATS
###These are the typical run-of-the-mill stats that don't require league
###comparisons. They include AVG,OBP, SLG, ERA, and WHIP. 


def AVG(playerID):
    '''Calculates the career batting average of the playerID.
    AVG = H/AB (hits per at-bat)
    PARAMS: playerID: the playerID of the relevant player.'''

    verify_player(playerID)
    verify_batter(playerID)

    hits = int(count_batting_stat(playerID, "H"))
    atbats = int(count_batting_stat(playerID, "AB"))


    return hits/atbats



def OBP(playerID):
    '''Calculates the career on-base percentage of the playerID
        OBP = (H+BB+HBP)/(AB+BB+SH+SF+HBP) (times reached base per plate appearence)
        PARAMS: playerID: the playerID of the relevant player.'''

    verify_player(playerID)
    verify_batter(playerID)


    # reached_base = batting.loc[batting['playerID']==playerID, ["H", "BB", "HBP"]].sum().sum()
    reached_base = sum([int(count_batting_stat(playerID, s)) for s in ["H", "BB", "HBP"]])
    # plate_appearance = batting.loc[batting['playerID']==playerID, ["AB", "BB", "SH", "HBP", "SF"]].sum().sum()
    plate_appearance = sum([int(count_batting_stat(playerID, s)) for s in ["AB", "BB", "SH", "HBP", "SF"]])

    return reached_base/plate_appearance


def SLG(playerID):
    '''Calculates the slugging percentage of the playerID
        SLG = (1B*1+2B*2+3B*3+HR*4)/AB (total bases on hits per at-bat
        PARAMS: playerID: the playerID of the relevant player.'''

    verify_player(playerID)
    verify_batter(playerID)


    hits     = int(count_batting_stat(playerID, "H"))

    doubles  = int(count_batting_stat(playerID, "2B"))
    triples  = int(count_batting_stat(playerID, "3B"))
    homeruns = int(count_batting_stat(playerID, "HR"))

    singles  = hits - doubles - triples - homeruns #since they're not directly logged here
    atbats   = int(count_batting_stat(playerID, "AB"))


    return (singles + 2*doubles + 3*triples + 4*homeruns)/atbats






def ERA(playerID):
    '''Calculates the Earned Run Average of the playerID
        ERA = (ER/IPOuts)*27 (Earned runs per 27 outs pitched)
        PARAMS: playerID: the playerID of the relevant player.'''

    verify_player(playerID)
    verify_pitcher(playerID)


    ER = int(count_pitching_stat(playerID, "ER"))
    IPouts = int(count_pitching_stat(playerID, "IPouts"))

    return 27*ER / IPouts


def WHIP(playerID):
    '''Calculates the WHIP of the playerID
        WHIP = 3*(BB+H)/IPouts (Walks + hits per inning pitched)
        PARAMS: playerID: the playerID of the relevant player.'''

    verify_player(playerID)
    verify_pitcher(playerID)

    WH = sum([int(count_pitching_stat(playerID, s)) for s in ["H", "BB"]])
    IPouts = int(count_pitching_stat(playerID, "IPouts"))

    return 3*WH/IPouts


### "Miscellanious Stats":
### These will be included in the basic stats due to their "easier to understand"
### nature. They're simply counting the awards won by the player in question (gold
### gloves, MVPs, etc.) and world series titles. However, they differ from the basic
### stats in that they have different requirements for setting up.

def award_count(playerID, award=None):
    '''Counts the awards the playerID has won. If award=None, all awards
    are counted. Otherwise the award specified will be counted
    PARAMS: playerID: ID of relevant player; award: specific award counted (default None)'''
    try:
        if award == None:
            return awards['playerID'].value_counts()[playerID]
        else:
            return awards.loc[awards['awardID']==award, ['playerID']].value_counts()[playerID]
    except:
        return 0
    
def allstar_count(playerID):
    '''Counts the number of all-star appearances by the playerID'''
    try:
        return allstar['playerID'].value_counts()[playerID]
    except:
        return 0



def WS_titles(playerID):
    '''Counts the number of World Series titles the playerID has'''

    try: 
        verify_batter(playerID)
    except:
        verify_pitcher(playerID)

    WS_count = 0

    date_start = players.loc[players['playerID']==playerID, ['debut']]
    year_start = int(np.array(date_start.values)[0][0][0:4])

    date_end = players.loc[players['playerID']==playerID, ['finalGame']]
    year_end = int(np.array(date_end.values)[0][0][0:4])

    for year in range(year_start, year_end+1):
        WS_winner = str(postseason.loc[(postseason['round']=='WS') & (postseason['yearID']==year), ['teamIDwinner']].values)

        if playerID in post_bat.loc[(post_bat['yearID']==year) & (post_bat['round'] == 'WS'), ['playerID']].values:
            player_team = str(post_bat.loc[(post_bat['yearID']==year) & (post_bat['playerID'] == playerID) & (post_bat['round'] == 'WS'), ['teamID']].values)
            if player_team == WS_winner:
                WS_count += 1

        # Gotta cover all bases (pun intended) in case a pitcher never batted in the WS
        elif playerID in post_pitch.loc[(post_pitch['yearID']==year) & (post_pitch['round'] == 'WS'), ['playerID']].values:
            player_team = str(post_pitch.loc[(post_pitch['yearID']==year) & (post_pitch['playerID'] == playerID) & (post_pitch['round'] == 'WS'), ['teamID']].values)
            if player_team == WS_winner:
                WS_count += 1

        else:
            continue
    
    return WS_count


def HoF_inductee(playerID):
    '''Checks whether player made it into the hall as a player. Managers
    would need a seperate category which at the moment is beyond the scope
    of the project'''
    inducted = playerID in halloffame.loc[(halloffame['inducted']=='Y') 
            & (halloffame['category']=='Player'), ['playerID']].values

    return int(inducted)


def count_seasons(playerID):
    '''Counts the number of different seasons a player played'''

    player_seasons = appearances.loc[appearances['playerID']==playerID, ['yearID']].values
    return len(set(player_seasons.astype(int).T[0]))


def last_season(playerID):
    '''returns the last year the player played in, part of the HoF requirements'''
    date_end = players.loc[players['playerID']==playerID, ['finalGame']]
    year_end = int(np.array(date_end.values)[0][0][0:4])
    return year_end

### Intermediate Stats:
### These stats are similar to the basic ones, but incorporate something
### else into the mix that pertains to the league as a whole. These stats
### include ERA+, OPS+, FIP, wOBA

def ERAplus(playerID):
    '''Calculates the career ERA+ of the playerID
        ERA+ = 100*ERA(league)/ERA(player)
        PARAMS: playerID: playerID of relevant player'''

    verify_player(playerID)
    verify_pitcher(playerID)

    ERA_p = ERA(playerID)
    ### This may be slightly off as it doesn't account for players starting/ending mid season
    ###Should be close enough approximation though

    ### Have to do some fun data type manipulation to get the correct years
    date_start = players.loc[players['playerID']==playerID, ['debut']]
    year_start = int(np.array(date_start.values)[0][0][0:4])

    date_end = players.loc[players['playerID']==playerID, ['finalGame']]
    year_end = int(np.array(date_end.values)[0][0][0:4])

    ra_l   = int(pitching.loc[(pitching['yearID']>=year_start) & (pitching['yearID']<=year_end), ['ER']].sum().values)
    outs_l = int(pitching.loc[(pitching['yearID']>=year_start) & (pitching['yearID']<=year_end), ['IPouts']].sum().values)


    ERA_l = 27*ra_l/outs_l

    return 100*ERA_l/ERA_p


def OPSplus(playerID):
    '''Calculates the career OPS+ of the playerID
        OPS+ = 100*OPS(player)/OPS(league)
        OPS = OBP + SLG (on-base plus slugging)
        PARAMS: playerID: playerID of relevant player'''

    verify_player(playerID)
    verify_batter(playerID)

    OBP_b = OBP(playerID)
    SLG_b = SLG(playerID)

    ### This may be slightly off as it doesn't account for players starting/ending mid season
    ###Should be close enough approximation though, assuming the player played multiple seasons

    ### Have to do some fun data type manipulation to get the correct years
    date_start = players.loc[players['playerID']==playerID, ['debut']]
    year_start = int(np.array(date_start.values)[0][0][0:4])

    date_end = players.loc[players['playerID']==playerID, ['finalGame']]
    year_end = int(np.array(date_end.values)[0][0][0:4])


    H_l   = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['H']].sum().values)
    BB_l  = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['BB']].sum().values)
    HBP_l = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['HBP']].sum().values)
    DBL_l = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['2B']].sum().values)
    TPL_l = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['3B']].sum().values)
    HR_l  = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['HR']].sum().values)
    AB_l  = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['AB']].sum().values)
    SH_l  = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['SH']].sum().values)
    SF_l  = int(batting.loc[(batting['yearID']>=year_start) & (batting['yearID']<=year_end), ['SF']].sum().values)
    SGL_l = H_l - DBL_l - TPL_l - HR_l

    RB_l = H_l + BB_l + HBP_l
    PA_l = AB_l + BB_l + HBP_l + SH_l + SF_l

    SLG_l = (SGL_l + 2*DBL_l + 3*TPL_l + 4*HR_l)/AB_l
    OBP_l = RB_l / PA_l   


    return 100*(OBP_b/OBP_l + SLG_b/SLG_l -1)




def wOBA(playerID):
    '''wOBA is the sum of unintentional BB, HBP, 1B, 2B, 3B, and HR
    individually weighted by type and year, all divided by
    (AB + uBB + SF + HBP)
    PARAMS: playerID'''

    verify_player(playerID)
    verify_batter(playerID)


    PA_tot = sum([count_batting_stat(playerID, s) for s in ['AB', 'BB', 'SF', 'HBP']]) \
                - count_batting_stat(playerID, 'IBB')

    years_played = batting.loc[batting['playerID']==playerID, ['yearID']].values.T[0]
    weighted_nums = 0

    # print(years_played)
    for yr in years_played:
        uBB = int(batting.loc[(batting['yearID']==yr) & (batting['playerID']==playerID), ['BB']].sum().values)
        HBP = int(batting.loc[(batting['yearID']==yr) & (batting['playerID']==playerID), ['HBP']].sum().values)
        dbl = int(batting.loc[(batting['yearID']==yr) & (batting['playerID']==playerID), ['2B']].sum().values)
        tpl = int(batting.loc[(batting['yearID']==yr) & (batting['playerID']==playerID), ['3B']].sum().values)
        HR  = int(batting.loc[(batting['yearID']==yr) & (batting['playerID']==playerID), ['HR']].sum().values)
        sgl = int(batting.loc[(batting['yearID']==yr) & (batting['playerID']==playerID), ['H']].sum().values) \
              - (dbl + tpl + HR)
        
        weighted_nums += uBB*get_FG_coeff(yr, 'wBB') + HBP*get_FG_coeff(yr, 'wHBP') + sgl*get_FG_coeff(yr, 'w1B')\
            + dbl*get_FG_coeff(yr, 'w2B') + tpl*get_FG_coeff(yr, 'w3B') + HR*get_FG_coeff(yr, 'wHR')




    return weighted_nums / PA_tot



def FIP(playerID):
    '''Calculates the career Fielding Independent Pitching of playerID
    FIP = (13*HR + 3*(BB+HBP)-2*SO + cFIP)/IPtot
    where cFIP = sum(CFIP(yr)*IP(yr))
    PARAMS : playerID'''

    verify_player(playerID)
    verify_pitcher(playerID)

    HR = count_pitching_stat(playerID, 'HR')
    BB_HBP = count_pitching_stat(playerID, 'BB') + count_pitching_stat(playerID, 'HBP')
    SO = count_pitching_stat(playerID, 'SO')
    IP_tot = count_pitching_stat(playerID, 'IPouts')/3

    years_played = batting.loc[batting['playerID']==playerID, ['yearID']].values.T[0]

    cFIP = 0
    for yr in years_played:
        c = get_FG_coeff(yr, 'cFIP')

        IPyr = float(pitching.loc[(pitching['playerID']==playerID) & (pitching['yearID']==yr), ['IPouts']].sum().values)/3

        cFIP += c*IPyr

    

    return (13*HR + 3*BB_HBP - 2*SO + cFIP)/IP_tot



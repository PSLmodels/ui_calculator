# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 15:09:28 2020

@author: probert2
"""

import pandas as pd
import numpy as np
import os


CUR_PATH = os.path.split(os.path.abspath(__file__))[0]

def get_file(f):
    # Returns as CSV in the data folder as a pandas DataFrame.
    return pd.read_csv(os.path.join(CUR_PATH, 'data', f))

#This CSV contains the parameters needed to calculate benefits amount
state_rules = get_file('state_thresholds.csv')

#This CSV contains the parameters needed to calculate eligibility
state_eligibility = get_file('state_eligibility.csv')

def calc_weekly_schedule(base_wage, rate, intercept, minimum, maximum):
    '''Finds weekly benefits from wages in a given period, a rate and intercept,
    a maximum benefit amount an a minimum benefit amount.
    '''
    
    no_truncation_benefits = (base_wage * rate) + intercept
    
    benefits = max(min(no_truncation_benefits, maximum), minimum)
    
    return benefits
    

def is_eligible(base_period, wba, state):
    
    '''
    Look up by state, and check eligibility from a list of quarterly earnings in the base period,
    and a potential weekly benefit amount if they are found to be eligible
    '''
    try:
        absolute_base, hqw, absolute_hqw, wba_thresh, num_quarters, outside_high_q, wba_outside_hq, absolute_2nd_high, wba_2hqw, abs_2hqw, hqw_2hqw  = state_eligibility.loc[state_eligibility['state'] == state].iloc[0][1:]
    except:
        print("""There was an error indexing the dataframe. 
              Check that your two character state code is is matched by a state code in state_eligibity.csv""")
        raise


    
    if sum(base_period) < absolute_base:
        return False
    if sum(base_period) < hqw*max(base_period):
        return False
    if max(base_period) < absolute_hqw:
        return False
    if sum(base_period) < wba_thresh*wba:
        return False
    if sum([quarter_wages > 0 for quarter_wages in base_period]) < num_quarters:
        return False
    if sum(base_period) - max(base_period) < outside_high_q:
        return False
    if np.sort(base_period)[-2] < absolute_2nd_high:
        return False
    if sum(np.sort(base_period)[-2:]) < wba_2hqw*wba:
        return False
    if sum(np.sort(base_period)[-2:]) < hqw_2hqw*max(base_period):
        return False
    if sum(np.sort(base_period)[-2:]) < abs_2hqw:
        return False
    
    return True
 
def find_base_wage(wage_concept, base_period):
    '''
    from the name of a wage concept and a list of earnings in the base period,
    calculate the total earnings that are used to calculate benefits in the state
    '''
    
    if wage_concept == "2hqw":
        base_wage = sum((np.sort(base_period))[-2:])
    elif wage_concept == "hqw":
        base_wage = max(base_period)
    elif wage_concept == "annual_wage":
        base_wage = sum(base_period)
    elif wage_concept == "2fqw":
        base_wage = sum(base_period[-2:])
    elif wage_concept == "ND":
        base_wage = sum((np.sort(base_period))[-2:]) + 0.5*np.sort(base_period)[-3]  
    else: 
        print("The wage concept " + str(wage_concept) + "from state_thresholds.csv is not defined")
        raise 
        
            
    return base_wage

def calc_weekly_state(earnings_hist, state):
    '''
    From quarterly earnings history in chronological order, and a two character state index
    calculate the weekly benefits.
    '''

    base_period = earnings_hist[-5:-1]
    
    
    try:
        wage_concept, rate, intercept,  minimum, maximum, inc_thresh = state_rules.loc[state_rules['state'] == state].iloc[0][1:7]
    except:
        print("""There was an error indexing the dataframe. 
              Check that your two character state code is is matched by a state code in state_thresholds.csv""")
        raise
    
    
    base_wage = find_base_wage(wage_concept, base_period)
    
    #check that the income is above the threshold for the given rules:
    if base_wage < inc_thresh:

        #Redefine the rules variables for the first entry such that the base wage is above the threshold
        wage_concept, rate, intercept,  minimum, maximum = state_rules.loc[state_rules['state'] == state].loc[base_wage >= state_rules['inc_thresh']].iloc[0][1:6]
        
        #find the basewage on the alternate concept
        base_wage = find_base_wage(wage_concept, base_period)


    wba = calc_weekly_schedule(base_wage, rate, intercept, minimum, maximum)

    if is_eligible(base_period, wba, state):
        return wba
    else:
        return 0


def calc_weekly_state_quarterly(q1, q2, q3, q4, states):
    '''
    This function is designed to be used with a dataframe. For lists q1,
    q2, q3, q4 which give earnings histories in order for any number of workers and
    a list of states with two character index of their state, it returns a list of 
    their weekly benefit amounts (returning 0 where the worker would be monetarily
    ineligible)
    '''
    try:
        len(q1)
    except:
       assert type(states) is str, "Check that you have one state per worker"  
       return calc_weekly_state([q1, q2, q3, q4, 0], states)
    try:
        assert (type(states) != str) & (len(states) > 0) & (len(states) == len(q1)), "Check that you have one state per worker"        
    except: 
        raise Exception('Check that you have one state per worker')

    earnings_history = [[q1[i], q2[i], q3[i], q4[i], 0] for i in range(len(q1))]
        
    return [calc_weekly_state(earnings_history[i], states[i]) for i in range(len(states))]
    

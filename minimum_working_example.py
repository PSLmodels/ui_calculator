# -*- coding: utf-8 -*-
"""
Created on Tue May 12 09:22:20 2020

@author: probert2
"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, 'source')

from ui_calculator import calc_weekly_state_quarterly

income_data = pd.read_csv("example_annual.csv")

income_data['weekly_earnings'] = income_data['wage']/income_data['weeks_worked']

def quarterly_earnings(annual_weeks, weekly_earnings, quarter_number):
    quarter_weeks = annual_weeks - 52 + 13 * quarter_number
    
    quarter_weeks = min(max(0, quarter_weeks), 13)
    
    return quarter_weeks*weekly_earnings

v_quarterly_earnings = np.vectorize(quarterly_earnings)

for i in range(4):
    income_data['q' + str(i + 1)] = v_quarterly_earnings(income_data['weeks_worked'], income_data['weekly_earnings'], i + 1)
    

income_data['benefits'] = calc_weekly_state_quarterly(
        income_data['q1'],                      
        income_data['q2'],
        income_data['q3'],
        income_data['q4'],
        income_data['state'],
        income_data['weeks_worked'])

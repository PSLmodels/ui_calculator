cd C:\Users\probert2\Documents\repo\covid_inc_sprt\issues\issue_9_repkit\
clear 
import delimited "example_annual.csv"

gen weekly_earnings = wage/weeks_worked

foreach quarter of num 1/4 {
	gen q`quarter'_weeks = weeks_worked - 52 + 13 * (`quarter') 
	
	gen q`quarter' = q`quarter'_weeks * weekly_earnings
	replace q`quarter' = 0 if q`quarter'_weeks < 0 
	replace q`quarter' = 13*weekly_earnings if q`quarter'_weeks > 13 
	
	drop q`quarter'_weeks
}

/* 
This code loads python and calls the UI calculator from python.
The strings, 'q1', 'q2', 'q3', 'q4' and 'state' should be modified
to reflect the names of the first quarter, second quarter etc variables
and the state of benefits variable. The state should be as a two digit code */


python
from sfi import Data

import pandas as pd
import sys
sys.path.insert(0, './source/')

from ui_calculator import calc_weekly_state_quarterly

benefits = calc_weekly_state_quarterly(
        Data.get('q1'),
        Data.get('q2'),
        Data.get('q3'),
        Data.get('q4'),
        Data.get('state'))
		
Data.addVarDouble('benefits')

Data.store('benefits', None, benefits)

end

su benefits

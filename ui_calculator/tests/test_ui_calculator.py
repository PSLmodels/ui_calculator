import pytest
import pandas as pd
import numpy as np
from ui_calculator import calc_weekly_state_quarterly
import os


CUR_PATH = os.path.split(os.path.abspath(__file__))[0]

def test_ui_calculator():
    # Load sample data with state, total wages, and total weeks over a year.
    income_data_path = os.path.join(CUR_PATH, '..', '..', 'example_annual.csv')
    income_data = pd.read_csv(income_data_path)
    # Preprocess
    # Calculate average weekly earnings.
    income_data['weekly_earnings'] = (
        income_data['wage'] / income_data['weeks_worked'])

    def quarterly_earnings(annual_weeks, weekly_earnings, quarter_number):
        """ Calculate quarterly earnings, assuming that annual_weeks represent
            weeks that occurred in reverse chronological order.
        """
        quarter_weeks = annual_weeks - 52 + 13 * quarter_number
        quarter_weeks = np.minimum(np.maximum(0, quarter_weeks), 13)  
        return quarter_weeks * weekly_earnings

    # Assign quarterly earnings for each quarter.
    for i in range(4):
        income_data['q' + str(i + 1)] = quarterly_earnings(
            income_data['weeks_worked'], income_data['weekly_earnings'], i + 1)

    # Calculate benefits with ui_calculator.
    income_data['benefits'] = calc_weekly_state_quarterly(
        income_data['q1'],                      
        income_data['q2'],
        income_data['q3'],
        income_data['q4'],
        income_data['state'],
        income_data['weeks_worked'])

    EXPECTED_BENEFITS = pd.Series([0, 240., 350.], name='benefits')
    pd.testing.assert_series_equal(income_data.benefits, EXPECTED_BENEFITS)

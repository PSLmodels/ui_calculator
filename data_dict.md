UI Calculator for Ganong, Noel and Vavra (2020): Data Dictionary
================
Peter Ganong, Pascal Noel, Peter Robertson and Joseph Vavra

## Computation of Weekly Benefit Amount (`state_thresholds.csv`)

Every state computes benefits using a `rate`, which is the ratio of
weekly benefits to a measure of prior earnings (`base_wage`). We
calculate:

`wba_formula = base_wage*rate + intercept`

This computation is subject to a maximum (`max`) and minimum (`min`)
benefit amount.

| Scenario                  | Weekly Benefit Amount |
| ------------------------- | --------------------- |
| `wba_formula` < `min`       | `min`                 |
| `min` < `wba_formula` < `max` | `wba_formula`         |
| `wba_formula` > `max`    | `max`                 |

The `wage_concept` records how the `base_wage` should be calculated and
has five possible
values:

| `wage_concept` | Value of `base_wage`                                                |
| -------------- | ------------------------------------------------------------------- |
| `annual_wage`  | annual wages                                                        |
| `hqw`          | wages in highest quarter                                            |
| `2hqw`         | wages in two highest quarters                                       |
| `2fqw`         | wages in last two quarters                                          |
| `ND`           | wages in two highest quarters + half wages in third highest quarter |

Finally, some states have different benefits schedules depending on
whether the income of an applicant is over a particular threshold. This
is captured by `inc_thresh`. The `inc_thresh` variable records the
minimum income as measured in the `wage_concept` for that row, such that
the rules in that row should be applied to calculate
benefits.

## Earnings/ Employment Needed in Base Period to Qualify (`state_eligibility.csv`)

We assume that the base period is the calendar year of 2018. We do this
because it matches what we observe in the CPS. This would correspond to
the standard base period for an applicant in April, May or June of 2019.
The DoL summary document for UI benefit rules says “Almost all
qualifying earnings are determined using a base period consisting of the
first four of the last five completed CQs. A few States use a different
base period. In the following states, more recent earnings may be used
in an alternative base period under certain conditions: AK, AR, CA, CO,
CT, DE, DC, GA, HI, ID, IL, IA, KS, ME, MD, MA, MI, MN, MT, NE, NV, NH,
NJ, NM, NY, NC, OH, OK, OR, PR, RI, SC, SD, UT, VT, VA, VI, WA, WV, and
WI.”

We include variables which enforce the following conditions. Most states
include only some of these conditions in their eligibility checks, so
the majority of values in `state_eligibility.csv` are
`0`.

| Variable            | Criterion                                                                                      |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| `absolute_base`     | minimum total earnings in the base period in dollars                                           |
| `hqw`               | minimum total earnings in the base period, expressed as a multiple of high quarter wages       |
| `absolute_hqw`      | minimum high quarter wage in dollars                                                           |
| `wba`               | minimum earnings in the base period, expressed as a multiple of worker’s weekly benefit amount |
| `num_quarters`      | minimum number of quarters with wages                                                          |
| `outside_high_q`    | minimum earnings outside high quarter in dollars                                               |
| `wba_outside_hq`    | minimum earnings outside high quarter, expressed as a multiple of the weekly benefit amount    |
| `absolute_2nd_high` | minimum earnings in 2nd highest quarter                                                        |
| `wba_2hqw`          | minimum earnings in two highest quarters as a multiple of the weekly benefit amount            |
| `abs_2hqw`          | minimum dollar amount in two highest quarters                                                  |
| `hqw_2hqw`          | minimum in two highest quarters as multiple of high quarter wages                              |

## State Specific Notes

Colorado, Iowa, Minnesota, Ohio and Wyoming all include statewide averages as part of their calculations. We use averages [from the BLS](https://www.bls.gov/oes/current/oessrcst.htm).

Colorado, Minnesota and New York have benefits schedules which change if the worker's income is in excess of a particular amount. We include the `inc_thresh` variable explained above to account for this. 

New Hampshire benefits are set to 1% of annual wages. This is the lower bound of the range of 1% - 1.1% in the Significant Provisions document. We could not readily find information on how the range between 1% and 1.1% is determined.

North Dakota has a `wage_concept` which is not common to any other states and is coded as `ND` and described in the `wage_concept` table above.

Alaska, Pennsylvania and Utah all have replacement rates which vary with income as a result of a fixed payment (or deduction) from the benefit. This is coded in the `intercept` column. 

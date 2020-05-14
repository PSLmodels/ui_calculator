library(reticulate)
library(tidyverse)

setwd("~/repo/ui_calculator/")

#point this to a conda environment that includes numpy and pandas. The YAML export of the environment
#we used is in the source folder.
use_condaenv() #You could also replace this with use_python()


source_python("source/ui_calculator.py")


#Example of weekly benefits calculated
income_data <- read.csv("example_annual.csv")

income_data <- income_data %>% mutate(weekly_earnings = wage/weeks_worked,
                   q1_earnings = weeks_worked - 39,
                   q2_earnings = weeks_worked - 26,
                   q3_earnings = weeks_worked - 13,
                   q4_earnings = weeks_worked) %>%
  mutate_at(vars(matches("q[1-4]_earnings" )), ~ case_when(.x > 13 ~ 13*weekly_earnings,
                                                           .x < 0 ~ 0,
                                                           TRUE ~ .x*weekly_earnings)) %>%
  mutate(benefits_amount = calc_weekly_state_quarterly(q1_earnings,
                                                       q2_earnings,
                                                       q3_earnings,
                                                       q4_earnings,
                                                       state) %>% map_dbl(1))
print(income_data)



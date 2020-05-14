library(reticulate)
library(quantreg)
library(tidyverse)
library(lubridate)
library(yaml)
library(rprojroot)
library("RColorBrewer")
matches <- dplyr::matches

setwd("~/repo/ui_calculator/")


#the benefits calculator is written in python.
#we call the calculator in R using the reticulate package
#the function we use is calc_weekly_state_quarterly()
#which takes 4 quarters of total earnings as the first four arguments
#and state as a 5th argument and returns a weekly benefit amount.
library(reticulate)
#point this to a conda environment that includes numpy and pandas. The YAML export of the environment
#we used is in the source folder.
use_condaenv() #You could also replace this with use_python()
source_python("source/ui_calculator.py")

palette <- RColorBrewer::brewer.pal(6, "Blues")


#### Read in data ####

fips_codes <- maps::state.fips %>%
  select(fips,
         state = abb) %>%
  select(STATEFIP = fips, state) %>%
  distinct() %>%
  bind_rows(tibble(state = c("HI", "AK"),
                   STATEFIP = c(15, 02))) %>%
  filter(state != "DC",
         state != "WV")


worker_citizen_instate <-
  read_csv("source/ASEC_2019.csv") %>%
  filter(INCWAGE < 99999998,
         INCWAGE > 0,
         CITIZEN != 5) %>%
  inner_join(fips_codes)

wages <- worker_citizen_instate %>%
  transmute(state,
            fips = STATEFIP,
            weight = ASECWT,
            wage = INCWAGE,
            employment_status = EMPSTAT,
            unemployment_duration = DURUNEMP,
            weeks_worked = WKSWORK1,
            usual_hours = UHRSWORKLY,
            unemp_reason = WHYUNEMP) %>%
  mutate(weekly_earnings = wage/weeks_worked,
         q1_earnings = weeks_worked - 39,
         q2_earnings = weeks_worked - 26,
         q3_earnings = weeks_worked - 13,
         q4_earnings = weeks_worked) %>%
  mutate_at(vars(matches("q[1-4]_earnings" )), ~ case_when(.x > 13 ~ 13*weekly_earnings,
                                                           .x < 0 ~ 0,
                                                           TRUE ~ .x*weekly_earnings)) %>%
  filter(wage >= (7.25 * usual_hours * weeks_worked))


rm(worker_citizen_instate)




#### Add weekly benefits to dataframe ####
#NB: this code is slow and should be expected to take 1-2 mins
wages <- wages %>%
  mutate(benefits_amount = calc_weekly_state_quarterly(q1_earnings,
                                                       q2_earnings,
                                                       q3_earnings,
                                                       q4_earnings,
                                                       state) %>% map_dbl(1))



### Benchmark Payments ####
fit_quantiles_state <- function(tau){
  wages %>%
    mutate(eligible = (employment_status == 21 & unemployment_duration <= 12 & unemp_reason %in% c(1, 2))) %>%
    filter( benefits_amount > 0) %>%
    rq(weekly_earnings ~  eligible + state, tau = tau, weights = weight, data = . ) %>%
    broom::augment(newdata = tibble(state = fips_codes$state,
                                    eligible = TRUE))
}

projected_earnings_dist <- map_dfr(c(seq(0.05, 0.95, 0.05), 0.99), fit_quantiles_state)

CPS_values <- projected_earnings_dist %>%
  rename(wage = .fitted, tau = .tau) %>%
  pivot_wider(names_from = tau, values_from = wage) %>%
  right_join(wages) %>%
  filter((employment_status == 21 & unemployment_duration <= 12 & unemp_reason %in% c(1, 2)) |
           employment_status == 10,
         benefits_amount > 0) %>%
  mutate_at(vars(contains(".")),
            ~ . < weekly_earnings) %>%
  filter(!`0.99`) %>%
  group_by_at(vars(contains("."))) %>%
  group_by(state, add = TRUE) %>%
  mutate(weight = weight/sum(weight)) %>%
  group_by(state) %>%
  summarise(aww = Hmisc::wtd.mean(wage/weeks_worked,
                                  weights = weight),
            awba  = Hmisc::wtd.mean(benefits_amount,
                                    weights = weight),
            rr1 = Hmisc::wtd.mean(benefits_amount/weekly_earnings,
                                  weights = weight),
            source = "CPS")

benchmarks <- read_csv("source/BAM_2018_benchmarks.csv") %>%
  mutate_at(c("wba", "earnings"), ~ str_remove_all(., "\\$|,") %>%
              as.numeric()) %>%
  transmute(aww = earnings,
            awba = wba,
            rr1 = rr1,
            state = State,
            source = "BAM")


benchmarks_for_plot <- benchmarks %>%
  bind_rows(CPS_values) %>%
  pivot_longer(cols = c("aww", "awba", "rr1"),
               names_to = "type",
               values_to = "amount") %>%
  pivot_wider(names_from = source,
              values_from = amount)


benchmarks_for_plot  %>%
  filter(type %in% c("awba", "aww")) %>%
  ggplot() +
  aes(BAM, CPS) +
  geom_text(aes(label = state)) +
  geom_abline() +
  geom_abline(slope = 0.85,
              colour = "red",
              alpha = 0.8) +
  geom_abline(slope = 1.15,
              colour = "red",
              alpha = 0.8) +
  labs(x = "Benchmarks from Department of Labor",
       y = "Our calculations from Current Population Survey") +
  facet_wrap(~type, labeller = labeller(type = c(aww = "Average weekly wage",
                                                 awba = "Average benefit amount")),
             scales = "free") +
  scale_x_continuous(labels = scales::dollar) +
  scale_y_continuous(labels = scales::dollar)




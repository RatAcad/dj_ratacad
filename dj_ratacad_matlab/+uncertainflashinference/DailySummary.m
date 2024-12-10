%{
# Summary statistics separately for each rat, each day and each period (day or night)
name : varchar(20)    # unique rat name
day: date             # date
isday : int           # day or night trial
---
trials : int          # number of trials
reward_rate : float   # proportion of rewarded trials (including omissions and early entries)
accuracy : float      # proportion of correct trials (only completed trials)
p_right : float       # proportion of right choices (only completed trials)
omission_rate : float # proportion of omitted responses
early_rate : float    # proportion of early responses
rt : float            # median response time (only completed trials)
it : float            # median trial initiation time (only completed trials)
%}
classdef DailySummary < dj.Manual
end
%{
# Detailed database with all statistics at each trial
name : varchar(20)                                                         # unique rat name
trial_datetime : datetime                                                  # unique timestamp of the trial
---
session_datetime : datetime                                                # timestamp of the session
trial : int                                                                # trial number w.r.t. experiment onset
isday : int                                                                # day or night trial
label : varchar(20)                                                        # experiment label
task : enum("count", "weigh")                                              # task version
stage: int                                                                 # stage number
trial_instage : int                                                        # trial number w.r.t. stage onset
rewardsize_left: int                                                       # size of the reward on left port  
rewardsize_right: int                                                      # size of the reward on right port
init_time : float                                                          # poke delay
flashes_left : varchar(50)                                                 # sequence of left flashes
flashes_right : varchar(50)                                                # sequence of right flashes
generative_side : enum("left", "right")                                    # generative category
correct_side : enum("left", "right")                                       # side of correct response
choice : enum("left", "right", "earlyleft", "earlyright", "omission")      # side of reported response
outcome : enum("correct", "error", "early", "omission")                    # trial outcome
rt: float                                                                  # response time
isuniform: int                                                             # whether the trial is a uniform, single LED brightness trial (only in last stage)
isopto: int                                                                # whether optogenetic manipulations were performed on that trial 
optoonset: float                                                           # onset of optogenetic manipulations
optodur: float                                                             # duration of optogenetic manipulations
ispaired: int                                                              # repeated trial from the past
pairedstrat: enum("none", "miniblock", "replay")                           # strategy for trial repetition
paired_inittime: datetime                                                  # trial timestamp of the repeated trial
isstaircase: int                                                           # trial informing the staircase titration procedure
staircase_dayval: tinyint unsigned                                         # brightness value of the day staircase
staircase_nightval: tinyint unsigned                                       # brightness value of the night staircase
tau: float                                                                 # value of tau parameter (number of bins)
alpha: float                                                               # value of alpha parameter (presence of empty bins)
sigma: float                                                               # value of sigma parameter (weak and incongruent flashes)
%}
classdef Trials < dj.Manual
end
%{
# Detailed database with all statistics at each trial
name : varchar(20)                                                         # unique rat name
trial_datetime : datetime                                                  # unique timestamp of the trial
---
run_datetime : datetime                                                    # timestamp of the run
session_datetime : datetime                                                # timestamp of the session
trial : int                                                                # trial number w.r.t. experiment onset
isday : int                                                                # day or night trial
label : varchar(20)                                                        # experiment label
task : enum("count", "weigh")                                              # task version
stage: int                                                                 # stage number
trial_instage : int                                                        # trial number w.r.t. stage onset
init_time : float                                                          # poke delay
flashes_left : varchar(50)                                                 # sequence of left flashes
flashes_right : varchar(50)                                                # sequence of right flashes
correct_side : enum("left", "right")                                       # side of correct response
choice : enum("left", "right", "earlyleft", "earlyright", "omission")      # side of reported response
outcome : enum("correct", "error", "early", "omission")                    # trial outcome
rt : float                                                                 # response time
ispaired : int                                                             # repeated trial from the past
pairedstrat : enum("none", "miniblock", "replay")                          # strategy for trial repetition
paired_inittime : datetime                                                 # trial timestamp of the repeated trial
isstaircase : int                                                          # trial informing the staircase titration procedure
staircase_dayval : tinyint unsigned                                        # brightness value of the day staircase
staircase_nightval : tinyint unsigned                                      # brightness value of the night staircase
tau : float                                                                # value of tau parameter (number of bins)
alpha : float                                                              # value of alpha parameter (presence of empty bins)
sigma : float                                                              # value of sigma parameter (weak and incongruent flashes)
%}
classdef Trials < dj.Manual
end
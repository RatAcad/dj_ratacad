%{
# Detailed database with all statistics at each trial
name : varchar(20)                                                                  # unique rat name
trial_inittime : datetime                                                           # unique timestamp of the trial
---
trial_starttime : datetime                                                          # start time of the trial (different than initiated)
session_starttime : datetime                                                        # timestamp of the session
trial : int                                                                         # trial number w.r.t. experiment onset
isday : int                                                                         # day or night trial
protocol: varchar(30)                                                               # protocol function
room: varchar(16)                                                                   # experimental room
position: varchar(5)                                                                # rack number and box position in the rack
experiment: varchar(100)                                                            # experiment label
commit_id: varchar(40)                                                              # GitHub commit ID
setting : varchar(20)                                                               # setting label
task : enum("count", "weigh")                                                       # task version
stage: int                                                                          # stage number
trial_instage : int                                                                 # trial number w.r.t. stage onset
rewardsize_left: int                                                                # size of the reward on left port  
rewardsize_right: int                                                               # size of the reward on right port
flashes_left : varchar(40)                                                          # sequence of left flashes
flashes_right : varchar(40)                                                         # sequence of right flashes
generative_side : enum("left", "right")                                             # generative category
correct_side : enum("left", "right")                                                # side of correct response
choice : enum("left", "right", "brokenfix", "earlyleft", "earlyright", "omission")  # side of reported response
outcome : enum("correct", "error", "brokenfix", "early", "omission")                # trial outcome
it : float                                                                          # poke delay
rt_side: float                                                                      # response time (side port entry)
rt_center: float                                                                    # response time (center port leaving)
isuniform: int                                                                      # whether the trial is a uniform, single LED brightness trial (only in last stage)
ispaired: int                                                                       # repeated trial from the past
paired_strat: enum("none", "miniblock", "replay")                                   # strategy for trial repetition
paired_reftime: datetime                                                            # trial timestamp of the repeated trial
trial_pairedtime : datetime                                                         # timestamp used to identify paired trials (see paired_reftime)
isstaircase: int                                                                    # trial informing the staircase titration procedure
staircase_dayval: tinyint unsigned                                                  # brightness value of the day staircase
staircase_nightval: tinyint unsigned                                                # brightness value of the night staircase
tau: float                                                                          # value of tau parameter (number of bins)
alpha: float                                                                        # value of alpha parameter (presence of empty bins)
beta: float                                                                         # value of beta parameter (proportion of unilateral/bilateral flashes)
sigma: float                                                                        # value of sigma parameter (weak and incongruent flashes)
isopto: int                                                                         # whether optogenetic manipulations were performed on that trial 
opto_onset: float                                                                   # onset of optogenetic manipulations
opto_dur: float                                                                     # duration of optogenetic manipulations
iseeg: int                                                                          # whether EEG recordings were performed
%}
classdef Trials < dj.Manual
end
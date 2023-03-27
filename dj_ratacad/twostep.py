"""
Schema for generic Bpod Data
"""

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import re

import datajoint as dj
from dj_ratacad import animal, bpod

schema = dj.schema("scott_twostep")


@schema
class TwoStepTrial(dj.Computed):
    definition = """
    # Gather TwoStep task specific data

    -> bpod.BpodTrialData
    task : enum("reward", "transition")                         # which task -- reward or transition revaluation
    stage : tinyint                                             # training stage
    ---
    free_choice=NULL : int                                      # whether rat given only one or both options on top row
    violation=NULL : int                                        # whether rat poked non active option
    choice=NULL : enum("left", "right")                         # which side on top row did rat choose
    outcome=NULL : enum("left", "right")                        # which side on bottom row turned on
    reward=NULL : enum("reward", "omission")                    # whether reward was administered or omitted
    correct_choice=NULL : int                                   # whether rat chose the option with highest probability of reward
    ---
    top_cue=NULL : enum("left", "right","both")                 # which top row side port light turned on 
    top_action=NULL : enum("left", "right")                     # which top row side port rat poked 
    bottom_cue=NULL : enum("left", "right")                     # which bottom row side port light turned on 
    bottom_action=NULL : enum("left", "right")                  # which bottom row side port rat poked
    ---
    transition_block=NULL : enum("congruent", "incongruent")    # which transition has higher probability
    con_transition_prob=NULL : float                            # probability of congruent outcome given choice
    incon_transition_prob=NULL : float                          # probability of incongruent outcome given choice
    reward_block=NULL : enum("left", "right")                   # which outcome port has higher reward probability
    left_reward_prob=NULL : float                               # probability of reward on left outcome port
    right_reward_prob=NULL : float                              # probability of reward on left outcome port
    transition_type=NULL : enum("common", "uncommon")           # whether outcome experienced was common or rare
    reward_type=NULL : enum("common", "uncommon")               # whether reward/omission was common or rare
    block_switch=NULL : int                                     # whether block changed this trial
    trial_in_block=NULL : int                                   # number of trials in block so far
    ---
    cr=NULL : int                                               # whether rewarded following a common transition
    ur=NULL : int                                               # whether rewarded following an uncommon transition
    co=NULL : int                                               # whether reward omitted following a common transition
    uo=NULL : int                                               # whether reward omitted following an uncommon transition
    ---
    top_init_time=NULL : float                                  # time stamp for top center poke trial initiation
    choice_time=NULL : float                                    # time stamp for entering choice port
    bottom_init_time=NULL : float                               # time stamp for light in bottom center poke
    outcome_poke_time=NULL : float                              # time stamp for entering outcome port
    ---
    stepone_rt=NULL : float                                     # duration of time between top side cue and poke response
    steptwo_rt=NULL : float                                     # duration of time between bottom side cue and poke response
    """

    @property
    def key_source(self):
        return bpod.BpodTrialData() & (bpod.BpodMetadata() & 'protocol="TwoStep"')

    def make(self, key):
        
        bpod_data = (bpod.BpodTrialData() & key).fetch(as_dict=True)[0]
        all_states = np.fromiter(bpod_data["states"].keys(), "U25")
        visited_states = [
            state for state in all_states if not np.isnan(bpod_data["states"][state][0])
        ]

        trial_data = key.copy()   
        
        # Task variant and training stage
        trial_data["task"] = (
            "reward" if bpod_data["trial_settings"]["Task"] == 1 else "transition"
        )
        trial_data["stage"] = bpod_data["trial_settings"]["Stage"]

        # Animal's choice and experienced outcome and reward        
        trial_data["free_choice"] = (
            bpod_data["additional_fields"]["FreeChoice"]
            if trial_data["stage"] >= 2
            else None
        )
        trial_data["violation"] = (
            bpod_data["additional_fields"]["Violation"]
            if trial_data["stage"] >= 3
            else None
        )

        if trial_data["stage"] >= 2:   
            trial_data["choice"] = (
                "left" 
                if (bpod_data["additional_fields"]["Choice"] == 1)
                else "right"
            )
        else:
            trial_data["choice"] = None

        if not np.isnan(bpod_data["states"]["OutcomeA"][0]):   
            trial_data["outcome"] = "left"
        elif not np.isnan(bpod_data["states"]["OutcomeB"][0]):
            trial_data["outcome"] = "right"   
        else:
            trial_data["outcome"] = None

        if trial_data["stage"] >= 3:
            if trial_data["violation"] == 0:
                trial_data["reward"] = (
                    "reward" 
                    if bpod_data["additional_fields"]["Reward"] == 1
                    else "omission"
                )
            else:
                trial_data["reward"] = None
        else:
            trial_data["reward"] = "reward"

        trial_data["correct_choice"] = (
            bpod_data["additional_fields"]["Correct"]
            if trial_data["stage"] >= 3
            else None
        )

        # Reward and transition probabilities
        if (trial_data["stage"] >= 2) and (bpod_data["additional_fields"]["TranBlock"] == 1):
            trial_data["transition_block"] = "congruent"
            trial_data["con_transition_prob"] = 1 - bpod_data["trial_settings"]["UncommonProbTransition"]  
            trial_data["incon_transition_prob"] = bpod_data["trial_settings"]["UncommonProbTransition"]  
        elif (trial_data["stage"] >= 2) and (bpod_data["additional_fields"]["TranBlock"] == 2):
            trial_data["transition_block"] = "incongruent"
            trial_data["con_transition_prob"] = bpod_data["trial_settings"]["UncommonProbTransition"]  
            trial_data["incon_transition_prob"] = 1 - bpod_data["trial_settings"]["UncommonProbTransition"] 
        else:
            trial_data["transition_block"] = None
            trial_data["con_transition_prob"] = None  
            trial_data["incon_transition_prob"] = None 

        if (trial_data["stage"] >= 3) and (bpod_data["additional_fields"]["RewBlock"] == 1):
            trial_data["reward_block"] = "left"
            trial_data["left_reward_prob"] = 1 - bpod_data["trial_settings"]["UncommonProbReward"]  
            trial_data["right_reward_prob"] = bpod_data["trial_settings"]["UncommonProbReward"]    
        elif (trial_data["stage"] >= 3) and (bpod_data["additional_fields"]["RewBlock"] == 2):
            trial_data["reward_block"] = "right"
            trial_data["left_reward_prob"] = bpod_data["trial_settings"]["UncommonProbReward"]   
            trial_data["right_reward_prob"] = 1 - bpod_data["trial_settings"]["UncommonProbReward"]  
        else:
            trial_data["reward_block"] = None
            trial_data["left_reward_prob"] = None  
            trial_data["right_reward_prob"] = None           

        # Common vs uncommon reward and transitions
        if trial_data["stage"] == 2:
            if trial_data["transition_block"] == "congruent":
                if trial_data["choice"] == trial_data["outcome"]:
                    trial_data["transition_type"] = "common"
                elif trial_data["choice"] != trial_data["outcome"]:
                    trial_data["transition_type"] = "uncommon"
            elif trial_data["transition_block"] == "incongruent":
                if trial_data["choice"] == trial_data["outcome"]:
                    trial_data["transition_type"] = "uncommon"
                elif trial_data["choice"] != trial_data["outcome"]:
                    trial_data["transition_type"] = "common"
            else:
                trial_data["transition_type"] = None
            trial_data["reward_type"] = None

        elif trial_data["stage"] >= 3:
            trial_data["transition_type"] = (
                "common"
                if bpod_data["additional_fields"]["TransitionType"] == 1
                else "uncommon"
            )    
            trial_data["reward_type"] = (
                "common"
                if bpod_data["additional_fields"]["RewardType"] == 1
                else "uncommon"
            ) 

        else: 
            trial_data["transition_type"] = None
            trial_data["reward_type"] = None

        # Indicate switch in reward/transition 
        trial_data["block_switch"] = (
            bpod_data["trial_settings"]["BlockSwitch"]
            if trial_data["stage"] >= 3
            else None
        )
        trial_data["trial_in_block"] = (
            bpod_data["trial_settings"]["BlockTrial"]
            if trial_data["stage"] >= 3
            else None
        )

        # Trial conditions 
        if trial_data["stage"] >= 3:
            trial_data["cr"] = (
                1 if (trial_data["transition_type"]=="common") and (trial_data["reward"]=="reward") else 0
            )
            trial_data["ur"] = (
                1 if (trial_data["transition_type"]=="uncommon") and (trial_data["reward"]=="reward") else 0
            )
            trial_data["co"] = (
                1 if (trial_data["transition_type"]=="common") and (trial_data["reward"]=="omission") else 0
            )
            trial_data["uo"] = (
                1 if (trial_data["transition_type"]=="uncommon") and (trial_data["reward"]=="omission") else 0
            )
        else:
            trial_data["cr"] = None
            trial_data["ur"] = None
            trial_data["co"] = None
            trial_data["uo"] = None

        # Bpod state timestamps
        if (trial_data["stage"] >= 2) and ("Step1" in bpod_data["states"]):
                trial_data["top_init_time"] = bpod_data["states"]["Step1"][1]
                trial_data["choice_time"] = bpod_data["states"]["Choice"][1]
        else:
            trial_data["top_init_time"] = None
            trial_data["choice_time"] = None

        if trial_data["stage"] >= 3:
            if trial_data["free_choice"] == 0 and trial_data["violation"] == 1:
                
                violate_time = bpod_data["states"]["Violation"][0]

                if ("PA1_Port1In" in bpod_data["events"]) and (
                    violate_time in np.atleast_1d(bpod_data["events"]["PA1_Port1In"])
                ):
                    trial_data["top_cue"]    = "right"
                    trial_data["top_action"] = "left"
                    trial_data["choice"]     = "left"
                elif ("PA1_Port3In" in bpod_data["events"]) and (
                    violate_time in np.atleast_1d(bpod_data["events"]["PA1_Port3In"])
                ): 
                    trial_data["top_cue"]    = "left"
                    trial_data["top_action"] = "right"
                    trial_data["choice"]     = "right"
                else:    
                    trial_data["top_cue"]    = None
                    trial_data["top_action"] = None

            elif trial_data["free_choice"] == 0 and trial_data["violation"] == 0:
                if not np.isnan(bpod_data["states"]["ChoiceA_OFF"][0]):

                    trial_data["top_cue"]    = "left"
                    trial_data["top_action"] = "left"
                elif not np.isnan(bpod_data["states"]["ChoiceB_OFF"][0]):

                    trial_data["top_cue"]    = "right"
                    trial_data["top_action"] = "right"
                else:    
                    trial_data["top_cue"]    = None
                    trial_data["top_action"] = None
            else:
                trial_data["top_cue"]   = "both"
                trial_data["top_action"] = trial_data["choice"]       
            
            if not np.isnan(bpod_data["states"]["OutcomeA"][0]):
                trial_data["bottom_init_time"]  = bpod_data["states"]["OutcomeA"][0] 
                trial_data["outcome_poke_time"] = bpod_data["states"]["OutcomeA"][1]
                trial_data["bottom_cue"] = "left"
                trial_data["bottom_action"] = (
                    "left"
                    if np.isnan(bpod_data["states"]["Violation"][0])
                    else "right"
                )
            elif not np.isnan(bpod_data["states"]["OutcomeB"][0]):
                trial_data["bottom_init_time"] = bpod_data["states"]["OutcomeB"][0]
                trial_data["outcome_poke_time"] = bpod_data["states"]["OutcomeB"][1]
                trial_data["bottom_cue"] = "right"
                trial_data["bottom_action"] = (
                    "right"
                    if np.isnan(bpod_data["states"]["Violation"][0])
                    else "left"
                )
            else:
                trial_data["bottom_init_time"] = None
                trial_data["outcome_poke_time"]  = None
                trial_data["bottom_cue"]   = None
                trial_data["bottom_action"]  = None
        
            trial_data["stepone_rt"] = bpod_data["states"]["Choice"][1] - bpod_data["states"]["Choice"][0]
            if not np.isnan(bpod_data["states"]["OutcomeA"][0]):
                trial_data["steptwo_rt"] = bpod_data["states"]["OutcomeA"][1] - bpod_data["states"]["OutcomeA"][0]
            elif not np.isnan(bpod_data["states"]["OutcomeB"][0]):
                trial_data["steptwo_rt"] = bpod_data["states"]["OutcomeB"][1] - bpod_data["states"]["OutcomeB"][0]
            else:
                trial_data["steptwo_rt"] = None

        else:
            trial_data["top_init_time"] = None
            trial_data["choice_time"] = None
            trial_data["bottom_init_time"] = None
            trial_data["outcome_poke_time"] = None
            trial_data["stepone_rt"] = None 
            trial_data["steptwo_rt"] = None

        self.insert1(trial_data)

        print(
            f"Added TwoStep Trial data for {trial_data['name']}, {trial_data['session_datetime']}, trial = {trial_data['trial']}"
        )

@schema
class DailySummary(dj.Manual):
    definition = """
    # Create daily summary

    -> animal.Animal
    summary_date : date             # date of summary
    ---
    trials : int                    # number of trials completed
    blocks : int                    # number of blocks completed
    leftward_choices : float        # fraction of choices toward left
    fraction_correct : float        # fraction of choices with highest probability of reward
    violation_rate : float          # fraction of trials animals chose inactive options
    training_stage : tinyint        # stage at end of day 
    """

    @property
    def key_source(self):

        return (
            animal.Animal() & (bpod.BpodMetadata - bpod.FileClosed()) & TwoStepTrial()
        ).fetch("KEY")

    def _make_tuples(self, key):

        summary_dates = (self & key).fetch("summary_date")
        latest_summary = (
            summary_dates[-1] if len(summary_dates) > 0 else datetime(2020, 7, 1)
        )
        latest_summary_str = (latest_summary + timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = datetime.today().strftime("%Y-%m-%d")

        trial_datetime, block_switch, choice, correct_choice, violation, stage = (
            TwoStepTrial()
            & key
            & f"trial_datetime>'{latest_summary_str}'"
            & f"trial_datetime<'{today_str}'"
        ).fetch("trial_datetime", "block_switch", "choice", "correct_choice", "violation", "stage")

        if len(trial_datetime) > 0:

            all_dates = [t.date() for t in trial_datetime]
            unique_dates = np.unique(all_dates)

            for d in unique_dates:

                these_trials = np.flatnonzero([a == d for a in all_dates])
                these_blocks = block_switch[these_trials]
                these_choices = choice[these_trials]
                these_correct = correct_choice[these_trials]
                these_violation = violation[these_trials]
                these_stages = stage[these_trials]

                summary_data = key.copy()
                summary_data["summary_date"] = d
                summary_data["trials"] = len(these_trials)
                summary_data["blocks"] = sum(
                    ((these_stages >= 3) & (these_blocks == 1))
                )
                summary_data["leftward_choices"] = sum(these_choices == "left") / len(these_trials)
                summary_data["fraction_correct"] = sum(
                    ((these_stages >= 3) 
                    & (these_correct == 1))
                ) / len(these_trials)
                summary_data["violation_rate"] = sum(
                    ((these_stages >= 3)
                    & (these_violation == 1))
                ) / len(these_trials)
                summary_data["training_stage"] = these_stages[-1]

                self.insert1(summary_data)

                print(
                    f"Added TwoStep Summary for {summary_data['name']}, {summary_data['summary_date']}"
                )

    def populate(self):

        for k in self.key_source:
            self._make_tuples(k)

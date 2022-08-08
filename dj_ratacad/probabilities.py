"""
Schema for generic Bpod Data
"""

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import re

import datajoint as dj
from dj_ratacad import animal, bpod

schema = dj.schema("scott_probabilities")


@schema
class ProbabilitiesTrial(dj.Computed):
    definition = """
    # Gather Probabilities task specific data

    -> bpod.BpodTrialData
    task : enum("Two_armed")                                    # which task -- the flash counting task or the free response flash rate task
    stage : tinyint                                             # training stage
    ---
    choice=NULL : enum("left", "right", "center", "omission")   # which side did mouse choose
    outcome=NULL : enum("rewarded", "nonrewarded", "omission")          # was decision correct (i.e. rewarded)
    correct_choice =NULL : int                                   # whether mice chose the option with highest probability of reward
    rt= NULL: float                                             # response time in s
    init_time= NULL : float                                    # time from the start of the trial to initiation
    majorprob_side : enum("left", "right", "center")            # the side with more probability of being rewarded
    prob_left : float                                           # the probability of a left flash
    prob_right : float                                          # the probability of a right flash
    bloc= NULL: int                                            # Number of bloc you are in
    bloc_length : int                                      # number of trials per bloc
    bloc_changing_prob : float                                  # probability of changing the bloc or side with more probability
    bloc_criteria : int                                    # number of repeated trials in the same side to change criteria, half of them rewarded
    min_bloc=NULL : int                                          # min number of trials to change bloc
    max_bloc=NULL : int                                          # max number of trials to change bloc
    enviroment=NULL : enum("None","normal", "poor", "rich")   # enviroment of the trial 
    previous_outcome=NULL : int                                # whether the previous trial was rewarded (1) or non-rewarded(0) or omission(2)
    previous_choice=NULL : enum("left", "right", "center")           # previous trial choice
    outcome_criteria : float                                    # criteria to change to block depending on outcome 1 change 0 no change
    choice_criteria : float                                     #criteria to change to block depending on outcome 1 left 3 no right        
    reward : int                                                # reward size (in uL)
    label=NULL : varchar(64)                                    # experiment label
    """

    @property
    def key_source(self):
        return bpod.BpodTrialData() & (bpod.BpodMetadata() & 'protocol="Probabilities"')

    def make(self, key):

        bpod_data = (bpod.BpodTrialData() & key).fetch(as_dict=True)[0]
        all_states = np.fromiter(bpod_data["states"].keys(), "U25")

        visited_states = [
            state
            for state in all_states
            if not np.isnan(bpod_data["states"][state][0]).all()
        ]
        trial_data = key.copy()
        #trial_data["task"] = (
        #    "probabilities" if bpod_data["trial_settings"]["Task"] == 1 else "rate"
        #)
        trial_data["task"] = 'Two_armed'
        trial_data["stage"] = bpod_data["trial_settings"]["Stage"]
        trial_data["stage"] = bpod_data["trial_settings"]["Reward"]
        trial_data["Bloc"] = bpod_data["trial_settings"]["Bloc"]
        trial_data["enviroment"] = ('normal' if bpod_data["trial_settings"]["Enviroment"] ==1 else 'poor' if \
                                    bpod_data["trial_settings"]["Enviroment"] ==2 else 'rich' if bpod_data["trial_settings"]["Enviroment"] ==3 else None)
        trial_data["bloc_length"] = bpod_data["trial_settings"]["TrialsBloc"]
        trial_data["bloc_changing_prob"] = bpod_data["trial_settings"]["BlocChanging"]
        trial_data["bloc_criteria"] = bpod_data["trial_settings"]["BlocChangingCriteria"]
        trial_data["min_bloc"] = bpod_data["trial_settings"]["MinBloc"]
        trial_data["max_bloc"] = bpod_data["trial_settings"]["MaxBloc"]
        trial_data["previous_outcome"] = bpod_data["trial_settings"]["PrevOutcome"]
        trial_data["previous_choice"] = bpod_data["trial_settings"]["PrevChoice"]
        trial_data["outcome_criteria"] = bpod_data["trial_settings"]["PrevOutcomeCrit"]
        trial_data["choice_criteria"] = bpod_data["trial_settings"]["PrevChoiceCrit"]
        if "Init" in visited_states:
            trial_data["init_time"] = bpod_data["states"]["Init"][1]
        elif "Lights" in visited_states:
            trial_data["init_time"] = bpod_data["states"]["Lights"][1]
        elif "Reward1" in visited_states:
            trial_data["init_time"] = bpod_data["states"]["Reward1"][0]
        elif "Reward3" in visited_states:
            trial_data["init_time"] = bpod_data["states"]["Reward3"][0]
        elif "Error" in visited_states:
            trial_data["init_time"] = bpod_data["states"]["Error"][0]
        else:
            trial_data["init_time"] = -100

        if "Consume1" in visited_states:
            correct_state = [vs for vs in visited_states if "Reward1" in vs][0]
            dec_time = bpod_data["states"][correct_state][0]
        elif "Consume3" in visited_states:
            correct_state = [vs for vs in visited_states if "Reward3" in vs][0]
            dec_time = bpod_data["states"][correct_state][0]
        elif "Error" in visited_states:
            dec_time = bpod_data["states"]["Error"][0]
        else:
            dec_time = None

        if ("Port1In" in bpod_data["events"]) and (
                dec_time in np.atleast_1d(bpod_data["events"]["Port1In"])
        ):
            trial_data["choice"] = "left"
        elif ("Port3In" in bpod_data["events"]) and (
                dec_time in np.atleast_1d(bpod_data["events"]["Port3In"])
        ):
            trial_data["choice"] = "right"
        elif ("Port2In" in bpod_data["events"]) and (
                dec_time in np.atleast_1d(bpod_data["events"]["Port2In"])
        ):
            trial_data["choice"] = "center"
        else:
            trial_data["choice"] = "omission"

        if bpod_data["trial_settings"]["RewardMaxPort"] == 1:
            trial_data["majorprob_side"] = "left"
        elif bpod_data["trial_settings"]["RewardMaxPort"] == 3:
            trial_data["majorprob_side"] = "right"
        elif bpod_data["trial_settings"]["RewardMaxPort"] == 2:
            trial_data["majorprob_side"] = "center"
        if bpod_data["trial_settings"]['Reward'] == 0 and bpod_data["trial_settings"]['Choice'] == 0 and dec_time == None:
            trial_data["outcome"] = "omission"
        elif bpod_data["trial_settings"]['Reward'] == 1:
                trial_data["outcome"] = "rewarded"
        else:
            trial_data["outcome"] = "non_rewarded"

        trial_data["rt"] = (
            dec_time - trial_data["init_time"] if dec_time is not None else None
        )
        if trial_data["majorprob_side"] == trial_data["choice"]:
            trial_data['correct_choice'] = 1
        else:
            trial_data['correct_choice'] = 0
        if trial_data["stage"] < 8:
            if trial_data["majorprob_side"] == "left":
                trial_data["prob_right"] = bpod_data["trial_settings"]["MaxLambdaLow"]
                trial_data["prob_left"] = bpod_data["trial_settings"]["MinLambdaHigh"]
            elif trial_data["majorprob_side"] == "right":
                trial_data["prob_left"] = bpod_data["trial_settings"]["MaxLambdaLow"]
                trial_data["prob_right"] = bpod_data["trial_settings"]["MinLambdaHigh"]
        else:
            if trial_data["majorprob_side"] == "left" and trial_data["eniroment"] == "normal":
                trial_data["prob_right"] = bpod_data["trial_settings"]["MinLambdaLow"]
                trial_data["prob_left"] = bpod_data["trial_settings"]["MaxLambdaHigh"]
            elif trial_data["majorprob_side"] == "right" and trial_data["eniroment"] == "normal":
                trial_data["prob_left"] = bpod_data["trial_settings"]["MinLambdaLow"]
                trial_data["prob_right"] = bpod_data["trial_settings"]["MaxLambdaHigh"]
            elif trial_data["majorprob_side"] == "left" and trial_data["eniroment"] == "poor":
                trial_data["prob_right"] = bpod_data["trial_settings"]["MinLambdaLow"]
                trial_data["prob_left"] = bpod_data["trial_settings"]["MinLambdaHigh"]
            elif trial_data["majorprob_side"] == "right" and trial_data["eniroment"] == "poor":
                trial_data["prob_left"] = bpod_data["trial_settings"]["MinLambdaLow"]
                trial_data["prob_right"] = bpod_data["trial_settings"]["MinLambdaHigh"]
            elif trial_data["majorprob_side"] == "left" and trial_data["eniroment"] == "rich":
                trial_data["prob_right"] = bpod_data["trial_settings"]["MaxLambdaLow"]
                trial_data["prob_left"] = bpod_data["trial_settings"]["MaxLambdaHigh"]
            elif trial_data["majorprob_side"] == "right" and trial_data["eniroment"] == "rich":
                trial_data["prob_left"] = bpod_data["trial_settings"]["MaxLambdaLow"]
                trial_data["prob_right"] = bpod_data["trial_settings"]["MaxLambdaHigh"]
            else:
                trial_data["prob_left"] = None
                trial_data["prob_right"] = None
        trial_data["label"] = (
            bpod_data["trial_settings"]["Label"][:24]
            if "Label" in bpod_data["trial_settings"]
            else None
        )

        self.insert1(trial_data)

        print(
            f"Added Probabilities Trial data for {trial_data['name']}, {trial_data['session_datetime']}, trial = {trial_data['trial']}"
        )


@schema
class DailySummary(dj.Manual):
    definition = """
    # Create daily summary

    -> animal.Animal
    summary_date : date             # date of summary
    ---
    trials : int                    # number of trials completed
    reward_rate : float             # percentage of rewarded trials (not counting omissions)
    p_right : float                 # percentage of trials mice chose right (not counting omissions)
    omission_rate : float           # percentage of incomplete trials
    training_stage : tinyint        # stage at end of day
    rt=NULL : float                      # reaction time
    """

    @property
    def key_source(self):

        return (
                animal.Animal() & (bpod.BpodMetadata - bpod.FileClosed()) & ProbabilitiesTrial()
        ).fetch("KEY")

    def _make_tuples(self, key):

        summary_dates = (self & key).fetch("summary_date")
        latest_summary = (
            summary_dates[-1] if len(summary_dates) > 0 else datetime(2020, 7, 1)
        )
        latest_summary_str = (latest_summary + timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = datetime.today().strftime("%Y-%m-%d")

        trial_datetime, outcome, choice, stage, training_criterion, reaction_time = (
                ProbabilitiesTrial()
                & key
                & f"trial_datetime>'{latest_summary_str}'"
                & f"trial_datetime<'{today_str}'"
        ).fetch("trial_datetime", "outcome", "choice", "stage", "training_criterion", "rt")

        if len(trial_datetime) > 0:

            all_dates = [t.date() for t in trial_datetime]
            unique_dates = np.unique(all_dates)

            for d in unique_dates:

                try:
                    these_trials = np.flatnonzero([a == d for a in all_dates])
                    these_outcomes = outcome[these_trials]
                    these_choices = choice[these_trials]
                    these_stages = stage[these_trials]
                    these_criterion = training_criterion[these_trials]

                    summary_data = key.copy()
                    summary_data["summary_date"] = d
                    summary_data["trials"] = len(these_trials)
                    summary_data["reward_rate"] = sum(
                        these_outcomes == "correct"
                    ) / sum(these_outcomes != "omission")
                    summary_data["p_right"] = sum(these_choices == "right") / sum(
                        these_outcomes != "omission"
                    )
                    summary_data["omission_rate"] = sum(
                        ((these_stages < 1) | (these_stages > 3))
                        & (these_outcomes == "omission")
                    ) / len(these_trials)
                    summary_data["training_stage"] = these_stages[-1]
                    these_rt = reaction_time[these_trials]
                    summary_data["rt"] = np.nanmean(these_rt)
                    self.insert1(summary_data)

                    print(
                        f"Added Probabilities Summary for {summary_data['name']}, {summary_data['summary_date']}"
                    )

                except:

                    print(f"Failed to create summary for {key['name']}, {d}")

    def populate(self):

        for k in self.key_source:
            self._make_tuples(k)
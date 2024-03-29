"""
Schema for generic Bpod Data
"""

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import re

import datajoint as dj
from dj_ratacad import animal, bpod

schema = dj.schema("scott_flashes")


@schema
class FlashesTrial(dj.Computed):
    definition = """
    # Gather Flashes task specific data

    -> bpod.BpodTrialData
    task : enum("count", "rate")                                # which task -- the flash counting task or the free response flash rate task
    stage : tinyint                                             # training stage
    ---
    choice=NULL : enum("left", "right", "center", "omission")   # which side did rat choose
    outcome=NULL : enum("correct", "error", "omission")         # was decision correct (i.e. rewarded)
    rt=NULL: float                                              # response time in s
    init_time=NULL : float                                      # time from the start of the trial to initiation
    correct_side : enum("left", "right", "center")              # correct side
    lambda_left : float                                         # the probability of a left flash
    lambda_right : float                                        # the probability of a right flash
    flash_bins : int                                            # number of flash bins
    flashes_left : varchar(100)                                 # flash sequence on the left side as a string (0 for no flash, 1 for flash)
    flashes_right : varchar(100)                                # flash sequence on the right side as a string (0 for no flash, 1 for flash)
    reward : int                                                # reward size (in uL)
    training_criterion : float                                  # training criterion variable
    label=NULL : varchar(64)                                    # experiment label
    """

    @property
    def key_source(self):
        return bpod.BpodTrialData() & (bpod.BpodMetadata() & 'protocol="Flashes"')

    def make(self, key):
        try:
            bpod_data = (bpod.BpodTrialData() & key).fetch(as_dict=True)[0]
        
            all_states = np.fromiter(bpod_data["states"].keys(), "U25")
    
            visited_states = [
                state
                for state in all_states
                if not np.isnan(bpod_data["states"][state][0]).all()
            ]
    
            trial_data = key.copy()
            trial_data["task"] = (
                "count" if bpod_data["trial_settings"]["Task"] == 1 else "rate"
            )
            trial_data["stage"] = bpod_data["trial_settings"]["Stage"]
            
            if "Init" in visited_states:
                trial_data["init_time"] = bpod_data["states"]["Init"][1]
            elif "DecisionCue" in visited_states:
                trial_data["init_time"] = bpod_data["states"]["DecisionCue"][1]
            elif "Correct" in visited_states:
                trial_data["init_time"] = bpod_data["states"]["Correct"][0]
            elif "Correct1" in visited_states:
                trial_data["init_time"] = bpod_data["states"]["Correct1"][0]
            elif "Error" in visited_states:
                trial_data["init_time"] = bpod_data["states"]["Error"][0]
            else:
                trial_data["init_time"] = -100
    
            if "Consume" in visited_states:
                correct_state = [vs for vs in visited_states if "Correct" in vs][0]
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
    
            if bpod_data["trial_settings"]["CorrectSide"] == 1:
                trial_data["correct_side"] = "left"
            elif bpod_data["trial_settings"]["CorrectSide"] == 3:
                trial_data["correct_side"] = "right"
            elif bpod_data["trial_settings"]["CorrectSide"] == 2:
                trial_data["correct_side"] = "center"
    
            if trial_data["choice"] == "omission":
                trial_data["outcome"] = "omission"
            elif trial_data["choice"] == trial_data["correct_side"]:
                trial_data["outcome"] = "correct"
            else:
                trial_data["outcome"] = "error"
    
            trial_data["rt"] = (
                dec_time - trial_data["init_time"] if dec_time is not None else None
            )
    
            bpod_data["trial_settings"]["TrialFlashRates"] = [
                -100 if np.isnan(x) else x
                for x in bpod_data["trial_settings"]["TrialFlashRates"]
            ]
    
            if (
                (trial_data["stage"] <= 0)
                or ((trial_data["task"] == "count") and (trial_data["stage"] > 4))
                or ((trial_data["task"] == "rate") and (trial_data["stage"] > 2))
            ):
                if trial_data["correct_side"] == "left":
                    trial_data["lambda_left"] = bpod_data["trial_settings"][
                        "TrialFlashRates"
                    ][0]
                    trial_data["lambda_right"] = bpod_data["trial_settings"][
                        "TrialFlashRates"
                    ][1]
                    trial_data["flashes_left"] = "".join(
                        bpod_data["trial_settings"]["TrialStimuli"][0].astype(str)
                    )
                    trial_data["flashes_right"] = "".join(
                        bpod_data["trial_settings"]["TrialStimuli"][1].astype(str)
                    )
                else:
                    trial_data["lambda_left"] = bpod_data["trial_settings"][
                        "TrialFlashRates"
                    ][1]
                    trial_data["lambda_right"] = bpod_data["trial_settings"][
                        "TrialFlashRates"
                    ][0]
                    trial_data["flashes_left"] = "".join(
                        bpod_data["trial_settings"]["TrialStimuli"][1].astype(str)
                    )
                    trial_data["flashes_right"] = "".join(
                        bpod_data["trial_settings"]["TrialStimuli"][0].astype(str)
                    )
            else:
                trial_data["lambda_left"] = 1 if trial_data["correct_side"] == "left" else 0
                trial_data["lambda_right"] = (
                    1 if trial_data["correct_side"] == "right" else 0
                )
                trial_data["flashes_left"] = ""
                trial_data["flashes_right"] = ""
    
            max_flashes = len(trial_data["flashes_left"])
    
            if max_flashes > 1:
                flash_states = all_states[
                    [bool(re.match(r"Flash", bdk)) for bdk in all_states]
                ]
    
                if "Flash0" in all_states:
                    flash_states = flash_states[1:]
    
                trial_data["flash_bins"] = np.flatnonzero(
                    ~np.isnan([bpod_data["states"][fs][0] for fs in flash_states])
                ).size
                trial_data["flashes_left"] = trial_data["flashes_left"][
                    0 : trial_data["flash_bins"]
                ]
                trial_data["flashes_right"] = trial_data["flashes_right"][
                    0 : trial_data["flash_bins"]
                ]
            else:
                trial_data["flash_bins"] = 0
            
            trial_data["reward"] = (
                bpod_data["trial_settings"]["Reward"][trial_data["flash_bins"] - 1]
                if type(bpod_data["trial_settings"]["Reward"]) == np.ndarray
                else bpod_data["trial_settings"]["Reward"]
            )
            trial_data["training_criterion"] = (
                bpod_data["additional_fields"]["TrainingCriterion"]
                if bpod_data["additional_fields"]["TrainingCriterion"] is not None
                else 0
            )
    
            trial_data["label"] = (
                bpod_data["trial_settings"]["Label"][:24]
                if "Label" in bpod_data["trial_settings"]
                else None
            )
    
            self.insert1(trial_data)
    
            print(
                f"Added Flashes Trial data for {trial_data['name']}, {trial_data['session_datetime']}, trial = {trial_data['trial']}"
            )
        except:
            print(key)
            print("failed to add")

@schema
class DailySummary(dj.Manual):
    definition = """
    # Create daily summary

    -> animal.Animal
    summary_date : date             # date of summary
    ---
    trials : int                    # number of trials completed
    reward_rate : float             # percentage of rewarded trials (not counting omissions)
    p_right : float                 # percentage of trials rat chose right (not counting omissions)
    omission_rate : float           # percentage of incomplete trials
    training_stage : tinyint        # stage at end of day
    training_criterion : float      # training criterion at end of day
    rt=NULL : float                      # reaction time
    """

    @property
    def key_source(self):

        return (
            animal.Animal() & (bpod.BpodMetadata - bpod.FileClosed()) & FlashesTrial()
        ).fetch("KEY")

    def _make_tuples(self, key):

        summary_dates = (self & key).fetch("summary_date")
        latest_summary = (
            summary_dates[-1] if len(summary_dates) > 0 else datetime(2020, 7, 1)
        )
        latest_summary_str = (latest_summary + timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = datetime.today().strftime("%Y-%m-%d")

        trial_datetime, outcome, choice, stage, training_criterion, reaction_time = (
            FlashesTrial()
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
                    summary_data["training_criterion"] = these_criterion[-1]
                    these_rt = reaction_time[these_trials]
                    summary_data["rt"] = np.nanmean(these_rt)
                    self.insert1(summary_data)

                    print(
                        f"Added Flashes Summary for {summary_data['name']}, {summary_data['summary_date']}"
                    )

                except:

                    print(f"Failed to create summary for {key['name']}, {d}")

    def populate(self):

        for k in self.key_source:
            self._make_tuples(k)

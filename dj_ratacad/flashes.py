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
    init_time : float                                           # time from the start of the trial to initiation
    correct_side : enum("left", "right", "center")              # correct side
    lambda_left : float                                         # the probability of a left flash
    lambda_right : float                                        # the probability of a right flash
    flash_bins : int                                            # number of flash bins
    flashes_left : varchar(100)                                 # flash sequence on the left side as a string (0 for no flash, 1 for flash)
    flashes_right : varchar(100)                                # flash sequence on the right side as a string (0 for no flash, 1 for flash)
    reward : int                                                # reward size (in uL)
    training_criterion : float                                  # training criterion variable
    label=NULL : varchar(24)                                    # experiment label
    """

    @property
    def key_source(self):
        return bpod.BpodTrialData() & (bpod.BpodMetadata() & 'protocol="Flashes"')

    def make(self, key):

        bpod_data = (bpod.BpodTrialData() & key).fetch(as_dict=True)[0]

        trial_data = key.copy()
        trial_data["task"] = (
            "count" if bpod_data["trial_settings"]["Task"] == 1 else "rate"
        )
        trial_data["stage"] = bpod_data["trial_settings"]["Stage"]

        trial_data["init_time"] = (
            bpod_data["states"]["Init"][1]
            if "Init" in bpod_data["states"]
            else bpod_data["states"]["DecisionCue"][1]
        )

        if (trial_data["stage"] > 1) and (
            not np.isnan(bpod_data["states"]["Correct"][0])
        ):
            dec_time = bpod_data["states"]["Correct"][0]
        elif (trial_data["stage"] > 1) and (
            ("Error" in bpod_data["states"].keys())
            and (not np.isnan(bpod_data["states"]["Error"][0]))
        ):
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

        if trial_data["correct_side"] == "left":
            trial_data["lambda_left"] = bpod_data["trial_settings"]["TrialFlashRates"][
                0
            ]
            trial_data["lambda_right"] = bpod_data["trial_settings"]["TrialFlashRates"][
                1
            ]
            trial_data["flashes_left"] = "".join(
                bpod_data["trial_settings"]["TrialStimuli"][0].astype(str)
            )
            trial_data["flashes_right"] = "".join(
                bpod_data["trial_settings"]["TrialStimuli"][1].astype(str)
            )
        else:
            trial_data["lambda_left"] = bpod_data["trial_settings"]["TrialFlashRates"][
                1
            ]
            trial_data["lambda_right"] = bpod_data["trial_settings"]["TrialFlashRates"][
                0
            ]
            trial_data["flashes_left"] = "".join(
                bpod_data["trial_settings"]["TrialStimuli"][1].astype(str)
            )
            trial_data["flashes_right"] = "".join(
                bpod_data["trial_settings"]["TrialStimuli"][0].astype(str)
            )

        max_flashes = len(trial_data["flashes_left"])
        if max_flashes > 1:
            all_states = np.fromiter(bpod_data["states"].keys(), "U25")
            flash_states = all_states[
                [bool(re.match(r"Flash", bdk)) for bdk in all_states]
            ]
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

        trial_data["reward"] = bpod_data["trial_settings"]["Reward"]
        trial_data["training_criterion"] = bpod_data["additional_fields"][
            "TrainingCriterion"
        ]
        trial_data["label"] = (
            bpod_data["trial_settings"]["Label"]
            if "Label" in bpod_data["trial_settings"]
            else None
        )

        self.insert1(trial_data)

        print(
            f"Added Flashes Trial data for {trial_data['name']}, {trial_data['session_datetime']}, trial = {trial_data['trial']}"
        )


@schema
class DailySummary(dj.Computed):
    definition = """
    # Create daily summary

    -> animal.Animal
    summary_date : date         # date of summary
    ---
    trials : int                # number of trials completed
    reward_rate : float         # percentage of rewarded trials
    omission_rate : float       # percentage of incomplete trials
    """

    CUTOFF_TIME = 28800

    @property
    def key_source(self):

        return animal.Animal() & (bpod.BpodMetadata() - bpod.FileClosed()) & FlashesTrial()

    def make(self, key):

        flashes_data = (FlashesTrial() & key).fetch(format="frame")


        ### get all data from the last day ###
        today = datetime.strftime(datetime.today(), "%Y-%m-%d")
        yesterday = datetime.strftime(datetime.today() - timedelta(days=1), "%Y-%m-%d")

        current_day = (
            FlashesTrial()
            & (
                bpod.BpodTrialData()
                & f"trial_date='{today}'"
                & f"trial_time<'08:00:00'"
            )
            & key
        ).fetch(as_dict=True)
        last_day = (
            FlashesTrial()
            & (
                bpod.BpodTrialData()
                & f"trial_date='{yesterday}'"
                & f"trial_time>'08:00:00'"
            )
            & key
        ).fetch(as_dict=True)
        last_24hr = last_day + current_day

        if len(last_24hr) > 0:
            n_trials = len(last_24hr)
            rewards = sum([t["outcome"] == "correct" for t in last_24hr])
            stage = last_24hr[-1]["stage"]
            training_criterion = last_24hr[-1]["training_criterion"]

            msg = (
                f"{key['name']}\n"
                f"trials = {n_trials}\n"
                f"rewards = {rewards}\n"
                f"stage = {stage}\n"
                f"training criterion = {training_criterion}"
            )

            summary = {"name": key["name"], "summary_date": today, "message": msg}

            self.insert1(summary)

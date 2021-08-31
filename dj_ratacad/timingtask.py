""" 
Schema for generic Bpod Data
"""

from os import stat_result
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import re

import datajoint as dj
from dj_ratacad import animal, bpod

schema = dj.schema("scott_timingtask")

@schema 
class TimingtaskTrial(dj.Computed):
    definition = """
    # Gather Timing task specific data
    
    -> bpod.BpodTrialData
    stage : tinyint                             # training stage
    ---
    press_time=NULL : float                     # timestamp of iniital lever press
    release_time=NULL : float                   # timestamp of lever release
    timeout : enum("y","n")                     # free sugar trial yes or no
    sample_time : float                         # sample time 
    estimate=NULL : enum("over","on","under")   # was estimation over/under/on time
    reward : enum("y","n")                      # was trial rewarded, not including timeouts
    reward_amount : int                         # reward size in uL


    """
    @property
    def key_source(self):
        return bpod.BpodTrialData() & (bpod.BpodMetadata() & 'protocol="TimingTask"')
    
    def make(self, key):
        bpod_data = (bpod.BpodTrialData() & key).fetch(as_dict=True)[0]
        all_states = np.fromiter(bpod_data["states"].keys(),"U25")

        visited_states = [
            state 
            for state in all_states 
            if not np.isnan(bpod_data["states"][state][0]).all()
        ]

        trial_data = key.copy()
        trial_data["stage"] = bpod_data["trial_settings"]["Stage"]
        trial_data["sample_time"] = bpod_data["trial_settings"]["SampleTime"]
        trial_data["reward_amount"] = bpod_data["trial_settings"]["Reward"]

        if not np.isnan(bpod_data["states"]["LPress"][0]):
            trial_data["timeout"] = "n"
            trial_data["press_time"] = bpod_data["states"]["LPress"][0]
            if np.isnan(bpod_data["states"]["Error"][0]):
                trial_data["reward"] = "y"
            else:
                trial_data["reward"] = "n"
            if not np.isnan(bpod_data["states"]["Holding"][0]):
                trial_data["release_time"] = bpod_data["states"]["Holding"][1]
            elif trial_data["stage"] == 1:
                trial_data["release_time"] = bpod_data["states"]["LPress"][1]
            else:
                if not np.nan(bpod_data["states"]["OverTime"][0]):
                    trial_data["release_time"] = bpod_data["states"]["OverTime"][1]
                    trial_data["estimate"] = "over"
                elif not np.nan(bpod_data["states"]["Ontime"][0]):
                    trial_data["release_time"] = bpod_data["states"]["OnTime"][1]
                    trial_data["estimate"] = "on"
                else:
                    trial_data["release_time"] = bpod_data["states"]["UnderTime"][1]
                    trial_data["estimate"] = "under"
                
        else:
            trial_data["timeout"] = "y"
            trial_data["reward"] = "n"
        
        self.insert1(trial_data)
        print(
            f"Added Timingtask Trial data for {trial_data['name']},{trial_data['session_datetime']}, {trial_data['trial']}"
        )



@schema
class DailySummary(dj.Manual):
    definition = """
    # Create daily summary
    
    -> animal.Animal
    summary_date : date                 # date of summary
    ---
    trials : int                        # number of trials completed
    timeouts : int                      # number of trials which time out & give free reward
    lever_presses : int                 # number of times lever is pressed
    reward : int                        # number of rewards not including timeouts
    training_stage : tinyint            # training stage 

    """

    @property
    def key_source(self):

        return(
            animal.Animal() & (bpod.BpodMetadata - bpod.FileClosed()) & TimingtaskTrial()
        ).fetch("KEY")

    def _make_tuples(self, key):

        summary_dates = (self & key).fetch("summary_date")
        latest_summary = (
            summary_dates[-1] if len(summary_dates) > 0 else datetime(2020,7,1)
        )
        latest_summary_str = (latest_summary + timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = datetime.today().strftime("%Y-%m-%d")

        trial_datetime, reward, timeouts, stage = (
            TimingtaskTrial()
            & key
            & f"trial_datetime>'{latest_summary_str}'"
            & f"trial_datetime<'{today_str}'"
        ).fetch("trial_datetime","reward","timeouts","stage")

        if len(trial_datetime) >  0:
            all_dates = [t.date() for t in trial_datetime]
            unique_dates = np.unique(all_dates)

            for d in unique_dates: 
                these_trials = np.flatnonzero([a == d for a in all_dates])
                these_rewards = reward[these_trials]
                these_stages = stage[these_trials]
                these_timeouts = timeouts[these_trials]

                summary_data = key.copy()
                summary_data["summary_date"] = d
                summary_data["trials"] = len(these_trials)
                summary_data["lever_presses"] = sum(these_timeouts == "n")
                summary_data["timeouts"] = sum(these_timeouts == "y")
                summary_data["reward"] = sum(these_rewards == "y")
                summary_data["training_stage"] = these_stages[-1]

                self.insert1(summary_data)
                print(f"Added Timingtask Summary for {summary_data['name']}, {summary_data['summary_date']}"
                )

    def populate(self):
        for k in self.key_source:
            self._make_tuples(k)            


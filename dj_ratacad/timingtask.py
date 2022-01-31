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
    reward : enum("y","n")                      # was trial rewarded
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
        
        if bpod_data["trial_settings"] == None:
            trial_data["stage"] = 1
            trial_data["sample_time"] = 0
            trial_data["reward_amount"] = 50
        else:
            trial_data["stage"] = bpod_data["trial_settings"]["Stage"]
            trial_data["sample_time"] = bpod_data["trial_settings"]["Sample"]
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
            elif trial_data["stage"] != 6 & trial_data["stage"] != 7:
                trial_data["release_time"] = bpod_data["states"]["LPress"][1]
                if trial_data["stage"] != 1:
                    trial_data["estimate"] = "under"
            else:
                if not np.isnan(bpod_data["states"]["OverTime"][0]):
                    trial_data["release_time"] = bpod_data["states"]["OverTime"][1]
                    trial_data["estimate"] = "over"
                elif not np.isnan(bpod_data["states"]["OnTime"][0]):
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
class TimingtaskTrialV2(dj.Computed):
    definition = """
    # Gather Timing task specific data
    
    -> bpod.BpodTrialData
    stage : tinyint                             # training stage
    ---
    reproduction_time : float                   # time reproduced (between cue light & second press)
    timeout : enum("y","n")                     # timeout error yes or no
    sample_time : float                         # sample time 
    itd_presses : int                           # how many times is lever pressed during ITD
    sample_presses: int                         # how many times lever is pressed during sample (before reproduction cue)
    reward_amount : float                       # reward size in uL
    reward_percent : float                      # percentage of max reward gained

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
        
        i = 1
        while ("Bin" + str(i)) in visited_states:
            lastBin = "Bin" + str(i)
            i+=1

        i -= 2


        trial_data["stage"] = bpod_data["trial_settings"]["Stage"]
        trial_data["sample_time"] = bpod_data["trial_settings"]["Sample"]

        j = 0
        count = 0
        if bpod_data["trial_settings"]["Stage"] != 1 and "Sample" in visited_states:
            sample_start =  bpod_data["states"]["Sample"][0]
            sample_end = bpod_data["states"]["Sample"][1]

            if "Port2In" not in bpod_data["events"]:
                print(key) # error check for missing Port2In event
            elif type(bpod_data["events"]["Port2In"]) is np.ndarray:
                while j < len(bpod_data["events"]["Port2In"]):
                    if bpod_data["events"]["Port2In"][j] > sample_start and bpod_data["events"]["Port2In"][j] < sample_end:
                        
                        count+=1 
                    j+=1

        trial_data["sample_presses"] = count

        if "Restart" in visited_states:
            trial_data["itd_presses"] = len(bpod_data["states"]["Restart"])
        else:
            trial_data["itd_presses"] = 0

        if "Error" in visited_states:
            trial_data["timeout"] = "y"
            trial_data["reproduction_time"] = 0
            trial_data["reward_amount"] = 0
            trial_data["reward_percent"] = 0
        else:
            trial_data["timeout"] = "n"
            if type(bpod_data["trial_settings"]["Reward"]) is np.ndarray:
                trial_data["reward_amount"] = bpod_data["trial_settings"]["Reward"][i]
            else: 
                trial_data["reward_amount"] = bpod_data["trial_settings"]["Reward"]

            if "MaxReward" not in bpod_data["trial_settings"]:
                MaxReward = 50
            else:
                MaxReward = bpod_data["trial_settings"]["MaxReward"]

            trial_data["reward_percent"] = trial_data["reward_amount"]/MaxReward

            if bpod_data["trial_settings"]["Stage"] != 1 and "Bin1" in visited_states:
                trial_data["reproduction_time"] = bpod_data["states"][lastBin][1] - bpod_data["states"]["Bin1"][0]
            else:
                trial_data["reproduction_time"] = 0
        
    
        
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
    trials : int                        # number of trials initiated
    training_stage : tinyint            # training stage 
    timeouts : int                      # number of trials that timed out
    earlypress_trials : int             # number of trials which have lever press during sample time
    avg_error : float                   # average percent error in reproductions
    maxreward_trials : int              # number of trials in which max reward was gained 
    
    """

    @property
    def key_source(self):

        return(
            animal.Animal() & bpod.BpodMetadata() & TimingtaskTrialV2()
        ).fetch("KEY")

    def _make_tuples(self, key):

        summary_dates = (self & key).fetch("summary_date")
        latest_summary = (
            summary_dates[-1] if len(summary_dates) > 0 else datetime(2020,7,1)
        )
        latest_summary_str = (latest_summary + timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = datetime.today().strftime("%Y-%m-%d")

        trial_datetime, stage, reproduction_time, sample_time, reward_percent, timeout, sample_presses = (
            TimingtaskTrialV2()
            & key
            & f"trial_datetime>'{latest_summary_str}'"
            & f"trial_datetime<'{today_str}'"
        ).fetch("trial_datetime","stage","reproduction_time","sample_time","reward_percent", "timeout","sample_presses")

        if len(trial_datetime) >  0:
            all_dates = [t.date() for t in trial_datetime]
            unique_dates = np.unique(all_dates)

            for d in unique_dates: 
                these_trials = np.flatnonzero([a == d for a in all_dates])
                these_reproductions = reproduction_time[these_trials]
                these_samples = sample_time[these_trials]
                these_stages = stage[these_trials]
                these_rewards = reward_percent[these_trials]
                these_timeouts = timeout[these_trials]
                these_presses = sample_presses[these_trials]

                summary_data = key.copy()
                summary_data["summary_date"] = d
                summary_data["trials"] = len(these_trials)
                summary_data["training_stage"] = these_stages[-1]
                summary_data["timeouts"] = sum(these_timeouts=='y')
            
                summary_data["earlypress_trials"] = sum(these_presses!=0)
                summary_data["avg_error"] = 0

                if summary_data["training_stage"] != 1:

                    x = 0
                    errors = []
                    while x < len(these_trials):
                        if these_stages[x] > 1:
                            error = abs(these_samples[x]-these_reproductions[x])
                            per = error/these_samples[x]
                            errors += [per]
                        x+=1

                    summary_data["avg_error"] = sum(errors)/len(errors) if len(errors) > 0 else 0   
                    

                summary_data["maxreward_trials"] = sum(these_rewards >= 0.99)
                
             
                # print(summary_data.keys)
                self.insert1(summary_data)
                print(f"Added Timingtask Summary for {summary_data['name']}, {summary_data['summary_date']}"
                )


    def populate(self):

        for k in self.key_source:
            self._make_tuples(k)            


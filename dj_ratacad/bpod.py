"""
Schema for generic Bpod Data
"""

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import traceback

import datajoint as dj
from dj_ratacad import rat
from dj_ratacad.utils import load_bpod_data, recarray_to_dict

schema = dj.schema("scott_bpod")


@schema
class BoxDesign(dj.Lookup):
    definition = """
    # Design of operant chamber

    design : varchar(20)      # name of design
    ---
    notes : varchar(280)    # brief description
    """

    contents = [
        ["3-port", "three nosepokes on one wall (left, center, right)"],
    ]


@schema
class Bpod(dj.Lookup):
    definition = """
    # Box ID in the Rat Academy

    bpod_id : varchar(20)    # unique box id
    -> BoxDesign
    ---
    serial : int             # serial number associated with Bpod device
    """

    contents = [
        ["RATACAD_1_1", "3-port", 6732980],
        ["RATACAD_1_2", "3-port", 5817960],
        ["RATACAD_1_3", "3-port", 6731020],
        ["RATACAD_1_4", "3-port", 6730020],
        ["RATACAD_1_5", "3-port", 6730280],
        ["RATACAD_1_6", "3-port", 6731860],
    ]


@schema
class Protocol(dj.Lookup):
    definition = """
    # List of tasks

    protocol : varchar(48)      # task name
    ---
    notes : varchar(280)        # brief description
    """

    contents = [
        ["Flashes", "Light flashes 2AFC task"],
    ]


@schema
class BpodMetadata(dj.Manual):
    definition = """
    # Metadata for each experiment

    -> rat.Rat
    session_datetime : timestamp            # date of experiment (associated with data file)
    ---
    -> Bpod                                 # box that experiment was conducted in
    -> Protocol                             # task
    file_path : varchar(256)                # path to the file on eng drive
    state_machine_version : varchar(20)     # StateMachineVersion from bpod data file 'Info'
    session_start_time_matlab : float       # SessionStartTime_MATLAB from bpod data file 'Info'
    settings_file = NULL : longblob         # SettingsFile from bpod data file 'Info'
    """

    DATA_DIR = Path.home() / "eng_research_scottlab" / "RATACAD_DATA"
    BPOD_LOOKUP_NAMES = ["Rhea", "Remy", "Ron", "Renee", "Robin", "Rachel"]

    def key_source(self):
        
        return (rat.Rat() - rat.Euthanized()).fetch("KEY")

    def _make_tuples(self, key):

        files_on_disk = list(BpodMetadata.DATA_DIR.glob(f"{key['name']}/*/Session Data/*.mat"))
        files_on_disk = [f.relative_to(BpodMetadata.DATA_DIR) for f in files_on_disk]
        files_on_dj = [Path(p) for p in (BpodMetadata() & key).fetch("file_path")]
        
        new_files = list(set(files_on_disk).difference(files_on_dj))
        protocols = Protocol.fetch("protocol")

        for nf in new_files:

            try:

                _, protocol, date, time = nf.stem.split("_")

                if protocol in protocols:

                    bpod_data = load_bpod_data(BpodMetadata.DATA_DIR / nf)
                    bpod_info = bpod_data["Info"]

                    sess_date = bpod_info["FileDate"] if "FileDate" in bpod_info else bpod_info["SessionDate"]
                    date = datetime.strftime(
                        datetime.strptime(sess_date, "%d-%b-%Y"),
                        "%Y-%m-%d",
                    )
                    time = bpod_info['FileStartTime_UTC'] if "FileStartTime_UTC" in bpod_info else bpod_info["SessionStartTime_UTC"]
                    bpod_id = bpod_info["BpodName"] if "BpodName" in bpod_info else f"RATACAD_1_{BpodMetadata.BPOD_LOOKUP_NAMES.index(key['name']) + 1}"

                    box_design = (Bpod() & f"bpod_id='{bpod_id}'").fetch("design")[0]

                    metadata = {
                        "name": key["name"],
                        "session_datetime": f"{date} {time}",
                        "bpod_id": bpod_id,
                        "design": box_design,
                        "protocol": protocol,
                        "file_path": str(nf),
                        "state_machine_version": bpod_info["StateMachineVersion"],
                        "session_start_time_matlab": bpod_info["SessionStartTime_MATLAB"],
                        "settings_file": bpod_info["SettingsFile"]
                        if "SettingsFile" in bpod_info
                        else None,
                    }

                    self.insert1(metadata)

                    print(f"Added Metadata for {key['name']}, {metadata['session_datetime']}")

            except Exception as e:

                print(f"Error adding file = {nf}:\n{e}")
                traceback.print_exc()

    def populate(self):

        for k in self.key_source():
            self._make_tuples(k)



@schema
class BpodTrialData(dj.Manual):
    definition = """
    # Bpod data

    -> BpodMetadata
    trial : int                                 # trial number
    trial_datetime : timestamp                  # date and time of trial
    ---
    trial_date : date                           # date of trial
    trial_time : time                           # time of trial
    states : longblob                           # States from RawEvents in Bpod data file, as dictionary
    events : longblob                           # Events from RawEvents in Bpod data file, as dictionary
    original_state_names_by_number : longblob   # OriginalStateNamesByNumber from RawData in Bpod data file, as numpy array
    original_state_data : longblob              # OriginalStateData from RawData in Bpod data file, as numpy array
    original_event_data : longblob              # OriginalEventData from RawData in Bpod data file, as numpy array
    original_state_timestamps : longblob        # OriginalStateTimestamps from RawData in Bpod data file, as numpy array
    original_event_timestamps : longblob        # OriginalEventTimestamps from RawData in Bpod data file, as numpy array
    state_machine_error_codes : longblob        # StateMachineErrorCodes from RawData in Bpod data file, as numpy array
    trial_start_timestamp : float               # TrialStartTimestamp from Bpod data file
    trial_end_timestamp : float                 # TrialEndTimestamp from Bpod data file
    data_timestamp=NULL : longblob              # DataTimestamp from Bpod data file
    trial_settings=NULL : longblob              # TrialSettings from Bpod data
    additional_fields=NULL : longblob           # Any additional fields in Bpod data file, as a dictionary
    """

    DEFAULT_FIELDS = [
        "Info",
        "nTrials",
        "RawEvents",
        "RawData",
        "TrialStartTimestamp",
        "TrialEndTimestamp",
        "DataTimestamp",
        "TrialSettings",
    ]

    def key_source(self):

        return (BpodMetadata() - FileClosed()).fetch("KEY")

    def _make_tuples(self, key):

        ### load data from bpod data file ###

        fp = (BpodMetadata() & key).fetch("file_path")[0]
        bpod_data = load_bpod_data(BpodMetadata.DATA_DIR / fp)

        ### check what's already been populated ###

        already_populated = (BpodTrialData() & key).fetch("trial")
        current_trial = 0 if len(already_populated) == 0 else max(already_populated)

        if bpod_data["nTrials"] - current_trial > 1:

            for t in range(current_trial, bpod_data["nTrials"]):

                trial_data = key.copy()
                trial_data["trial"] = t + 1

                time_elapsed = (
                    bpod_data["TrialStartTimestamp"][t]
                    - bpod_data["TrialStartTimestamp"][0]
                )
                trial_datetime = key["session_datetime"] + timedelta(seconds=time_elapsed)
                trial_data["trial_datetime"] = datetime.strftime(trial_datetime, "%Y-%m-%d %H:%M:%S")
                trial_data["trial_date"] = datetime.strftime(trial_datetime, "%Y-%m-%d")
                trial_data["trial_time"] = datetime.strftime(trial_datetime, "%H:%M:%S")

                raw_events = recarray_to_dict(bpod_data["RawEvents"]["Trial"][t])
                trial_data["states"] = raw_events["States"]
                trial_data["events"] = raw_events["Events"]

                trial_data["original_state_names_by_number"] = bpod_data["RawData"][
                    "OriginalStateNamesByNumber"
                ][t]
                trial_data["original_state_data"] = bpod_data["RawData"][
                    "OriginalStateData"
                ][t]
                trial_data["original_event_data"] = bpod_data["RawData"][
                    "OriginalEventData"
                ][t]
                trial_data["original_state_timestamps"] = bpod_data["RawData"][
                    "OriginalStateTimestamps"
                ][t]
                trial_data["original_event_timestamps"] = bpod_data["RawData"][
                    "OriginalEventTimestamps"
                ][t]
                trial_data["state_machine_error_codes"] = bpod_data["RawData"][
                    "StateMachineErrorCodes"
                ][t]

                trial_data["trial_start_timestamp"] = bpod_data["TrialStartTimestamp"][t]
                trial_data["trial_end_timestamp"] = bpod_data["TrialEndTimestamp"][t]

                if "DataTimestamp" in bpod_data:
                    trial_data["data_timestamp"] = bpod_data["DataTimestamp"][t]

                if "TrialSettings" in bpod_data:
                    trial_data["trial_settings"] = {}
                    for ts in bpod_data["TrialSettings"].keys():
                        trial_data["trial_settings"][ts] = bpod_data["TrialSettings"][ts][t]

                add_fields = [
                    k for k in bpod_data.keys() if k not in BpodTrialData.DEFAULT_FIELDS
                ]
                if len(add_fields) > 0:
                    trial_data["additional_fields"] = {}
                    for af in add_fields:
                        if type(bpod_data[af]) == np.ndarray:
                            # print(bpod_data[af].dtype)
                            trial_data["additional_fields"][af] = bpod_data[af][t]
                        else:
                            trial_data["additional_fields"][af] = bpod_data[af]

                self.insert1(trial_data)

            print(
                f"Added Trial data for {trial_data['name']}, {trial_data['session_datetime']}, trial = {trial_data['trial']}"
            )
    
    def populate(self):

        for k in self.key_source():
            self._make_tuples(k)


        




@schema
class FileClosed(dj.Manual):
    definition = """
    # Populated once the session is complete

    -> BpodMetadata
    """

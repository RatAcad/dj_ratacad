"""
Schema for generic Bpod Data
"""

import os
from pathlib import Path
import pathlib
from datetime import datetime, timedelta, date
import numpy as np
import traceback
import platform

import datajoint as dj
from dj_ratacad import animal
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
        ["Unknown", "unknown"],
        ["3-port", "three nosepokes on one wall (left, center, right)"],
        [
            "6-port",
            "six nosepokes on one wall (top: left, center, right; bottom: left, center, right)",
        ],
        ["lever-port", "one lever on the left and one nosepoke on the right"]
    ]


@schema
class Bpod(dj.Lookup):
    definition = """
    # Box ID in the Rat Academy

    bpod_id : varchar(20)    # unique box id
    -> BoxDesign
    mod_date : date          # date of last modification (YYYY-MM-DD)
    ---
    serial : int             # serial number associated with Bpod device
    """

    contents = [
        ["Unknown", "Unknown", "2020-07-01", 0],
        ["RATACAD_1_1", "3-port", "2021-01-21", 7156140],
        ["RATACAD_1_2", "3-port", "2021-01-21", 6734400],
        ["RATACAD_1_3", "3-port", "2021-01-21", 6732980],
        ["RATACAD_1_4", "3-port", "2021-01-21", 5817960],
        ["RATACAD_1_5", "3-port", "2021-01-21", 6731020],
        ["RATACAD_1_6", "3-port", "2021-01-21", 6730020],
        ["RATACAD_1_7", "3-port", "2021-01-21", 6730280],
        ["RATACAD_1_8", "3-port", "2021-01-21", 6731860],
        ["RATACAD_2_1", "3-port", "2021-01-21", 6730710],
        ["RATACAD_2_2", "3-port", "2021-01-21", 6730490],
        ["RATACAD_2_3", "3-port", "2021-01-21", 6731500],
        ["RATACAD_2_4", "3-port", "2021-01-21", 6730130],
        ["RATACAD_2_5", "3-port", "2021-01-21", 6730800],
        ["RATACAD_2_6", "3-port", "2021-01-21", 6729930],
        ["RATACAD_2_7", "3-port", "2021-01-21", 5736400],
        ["RATACAD_2_8", "3-port", "2021-01-21", 6732920],
        ["721G_1_1", "3-port", "2021-02-05", 6732940],
        ["721G_1_2", "3-port", "2021-02-05", 6733060],
        ["721G_1_3", "3-port", "2021-02-05", 6730220],
        ["721G_1_4", "3-port", "2021-02-05", 7152720],
        ["721G_1_5", "3-port", "2021-02-05", 7153510],
        ["721G_1_6", "3-port", "2021-02-05", 7156600],
        ["721G_1_7", "3-port", "2021-02-05", 6732930],
        ["721G_1_8", "3-port", "2021-02-05", 6730500],
        ["721G_1_9", "3-port", "2021-02-05", 6731870],
        ["721G_1_1", "6-port", "2021-03-20", 6732940],
        ["721G_1_2", "6-port", "2021-03-20", 6733060],
        ["721G_1_3", "6-port", "2021-03-20", 6730220],
        ["RATACAD_1_1", "3-port", "2021-07-28", 8529890],
        ["RATACAD_1_2", "3-port", "2021-07-28", 6732980],
        ["RATACAD_1_3", "3-port", "2021-07-28", 6730020],
        ["RATACAD_1_4", "3-port", "2021-07-28", 7156140],
        ["RATACAD_1_5", "3-port", "2021-07-28", 5817960],
        ["RATACAD_1_6", "3-port", "2021-07-28", 6731020],
        ["RATACAD_1_7", "3-port", "2021-07-28", 6734400],
        ["RATACAD_1_8", "3-port", "2021-07-28", 6730280],
        ["RATACAD_1_9", "3-port", "2021-07-28", 6731860],
        ["RATACAD_3_1", "6-port", "2021-07-29", 8529880],
        ["RATACAD_3_2", "6-port", "2021-07-29", 8528440],
        ["RATACAD_3_3", "6-port", "2021-07-29", 5736500],
        ["RATACAD_3_6", "lever-port", "2021-08-23", 8528710],
        ["RATACAD_3_7", "lever-port", "2021-08-23", 8410220],
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
        ["FlashCount", "Flash counting 2AFC task"],
        ["TwoStep", "Two Step planning task"],
        ["TimingTask", "Lever press interval timing task"]
    ]


@schema
class BpodMetadata(dj.Manual):
    definition = """
    # Metadata for each experiment

    -> animal.Animal
    session_datetime : timestamp            # date of experiment (associated with data file)
    ---
    -> Bpod                                 # box that experiment was conducted in
    -> Protocol                             # task
    file_path : varchar(256)                # path to the file on eng drive
    state_machine_version : varchar(20)     # StateMachineVersion from bpod data file 'Info'
    session_start_time_matlab : float       # SessionStartTime_MATLAB from bpod data file 'Info'
    settings_file = NULL : longblob         # SettingsFile from bpod data file 'Info'
    """

    DATA_DIR = Path(os.getenv("RATACAD_DATA_DIR", default=""))

    def key_source(self):

        return (animal.Animal() - animal.Euthanized()).fetch("KEY")

    def _make_tuples(self, key):

        files_on_disk = list(
            BpodMetadata.DATA_DIR.glob(f"{key['name']}/*/Session Data/*.mat")
        )

        files_on_disk = [f.relative_to(BpodMetadata.DATA_DIR) for f in files_on_disk]
        files_on_dj = [Path(p) for p in (BpodMetadata() & key).fetch("file_path")]

        new_files = list(set(files_on_disk).difference(files_on_dj))
        protocols = Protocol.fetch("protocol")

        for nf in new_files:

            try:

                _, protocol, _, _ = nf.stem.split("_")

                if protocol in protocols:

                    bpod_data = load_bpod_data(BpodMetadata.DATA_DIR / nf)

                    if bpod_data is not None:

                        bpod_info = bpod_data["Info"]

                        bpod_data["TrialStartTimestamp"] = (
                            [bpod_data["TrialStartTimestamp"]]
                            if type(bpod_data["TrialStartTimestamp"]) is float
                            else bpod_data["TrialStartTimestamp"]
                        )

                        bpod_data["TrialEndTimestamp"] = (
                            [bpod_data["TrialEndTimestamp"]]
                            if type(bpod_data["TrialEndTimestamp"]) is float
                            else bpod_data["TrialEndTimestamp"]
                        )

                        sess_date = (
                            bpod_info["FileDate"]
                            if "FileDate" in bpod_info
                            else bpod_info["SessionDate"]
                        )
                        sess_time = (
                            bpod_info["FileStartTime_UTC"]
                            if "FileStartTime_UTC" in bpod_info
                            else bpod_info["SessionStartTime_UTC"]
                        )
                        sess_datetime = datetime.strptime(
                            f"{sess_date} {sess_time}", "%d-%b-%Y %H:%M:%S"
                        )
                        time_offset = (
                            bpod_data["TrialEndTimestamp"][0]
                            - bpod_data["TrialStartTimestamp"][0]
                        )

                        sess_datetime_str = (
                            sess_datetime - timedelta(seconds=time_offset)
                        ).strftime("%Y-%m-%d %H:%M:%S")

                        bpod_id = (
                            bpod_info["BpodName"]
                            if "BpodName" in bpod_info
                            else "Unknown"
                        )

                        box_designs = (Bpod() & f"bpod_id='{bpod_id}'").fetch()
                        sess_date_dt = datetime.strptime(sess_date, "%d-%b-%Y")
                        recent_box_index = np.flatnonzero(
                            [
                                sess_date_dt.date() - bd["mod_date"] > timedelta(days=0)
                                for bd in box_designs
                            ]
                        )

                        if len(recent_box_index) > 0:
                            box_design = box_designs[recent_box_index[0]][1]
                            mod_date = box_designs[recent_box_index[0]][2]
                        else:
                            bpod_id = "Unknown"
                            box_design = "Unknown"
                            mod_date = "2020-07-01"

                        fp = (
                            pathlib.PureWindowsPath(nf).as_posix()
                            if platform.system() == "Windows"
                            else str(nf)
                        )

                        metadata = {
                            "name": key["name"],
                            "session_datetime": sess_datetime_str,
                            "bpod_id": bpod_id,
                            "design": box_design,
                            "mod_date": mod_date,
                            "protocol": protocol,
                            "file_path": fp,
                            "state_machine_version": bpod_info["StateMachineVersion"],
                            "session_start_time_matlab": bpod_info[
                                "SessionStartTime_MATLAB"
                            ],
                            "settings_file": bpod_info["SettingsFile"]
                            if "SettingsFile" in bpod_info
                            else None,
                        }

                        self.insert1(metadata)

                        print(
                            f"Added Metadata for {key['name']}, {metadata['session_datetime']}"
                        )

            except Exception as e:

                if type(e) is "TypeError":
                    print(f"Bpod Data file {nf.stem} is empty. Deleting file...")
                    (BpodMetadata.DATA_DIR / nf).unlink()
                else:
                    print(f"Bpod Data file {nf.stem} is corrupted, please manually check and delete file.")


    def populate(self):

        if BpodMetadata.DATA_DIR == Path(""):
            raise Exception(
                "The path to the Scott Lab ENG drive is not set. "
                "To populate new data, please set the environmental variable 'RATACAD_DATA_DIR' "
                "to the location of 'eng_research_scottlab/RATACAD_DATA'."
            )

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

        if bpod_data is not None:

            ### check what's already been populated ###

            already_populated = (BpodTrialData() & key).fetch("trial")
            current_trial = 0 if len(already_populated) == 0 else max(already_populated)

            if bpod_data["nTrials"] - current_trial > 0:

                if bpod_data["nTrials"] == 1:
                    bpod_data["TrialStartTimestamp"] = [
                        bpod_data["TrialStartTimestamp"]
                    ]
                    bpod_data["TrialEndTimestamp"] = [bpod_data["TrialEndTimestamp"]]
                    bpod_data["DataTimestamp"] = [bpod_data["DataTimestamp"]]
                    bpod_data["RawData"]["OriginalStateNamesByNumber"] = [
                        bpod_data["RawData"]["OriginalStateNamesByNumber"]
                    ]
                    bpod_data["RawData"]["OriginalStateData"] = [
                        bpod_data["RawData"]["OriginalStateData"]
                    ]
                    bpod_data["RawData"]["OriginalEventData"] = [
                        bpod_data["RawData"]["OriginalEventData"]
                    ]
                    bpod_data["RawData"]["OriginalStateTimestamps"] = [
                        bpod_data["RawData"]["OriginalStateTimestamps"]
                    ]
                    bpod_data["RawData"]["OriginalEventTimestamps"] = [
                        bpod_data["RawData"]["OriginalEventTimestamps"]
                    ]
                    bpod_data["RawData"]["StateMachineErrorCodes"] = [
                        bpod_data["RawData"]["StateMachineErrorCodes"]
                    ]

                for t in range(current_trial, bpod_data["nTrials"]):

                    trial_data = key.copy()
                    trial_data["trial"] = t + 1

                    time_elapsed = (
                        bpod_data["TrialStartTimestamp"][t]
                        - bpod_data["TrialStartTimestamp"][0]
                    )
                    trial_datetime = key["session_datetime"] + timedelta(
                        seconds=time_elapsed
                    )
                    trial_data["trial_datetime"] = datetime.strftime(
                        trial_datetime, "%Y-%m-%d %H:%M:%S"
                    )
                    trial_data["trial_date"] = datetime.strftime(
                        trial_datetime, "%Y-%m-%d"
                    )
                    trial_data["trial_time"] = datetime.strftime(
                        trial_datetime, "%H:%M:%S"
                    )

                    raw_events = (
                        recarray_to_dict(bpod_data["RawEvents"]["Trial"][t])
                        if bpod_data["nTrials"] > 1
                        else bpod_data["RawEvents"]["Trial"]
                    )
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

                    trial_data["trial_start_timestamp"] = bpod_data[
                        "TrialStartTimestamp"
                    ][t]
                    trial_data["trial_end_timestamp"] = bpod_data["TrialEndTimestamp"][
                        t
                    ]

                    if "DataTimestamp" in bpod_data:
                        trial_data["data_timestamp"] = bpod_data["DataTimestamp"][t]

                    if "TrialSettings" in bpod_data:
                        trial_data["trial_settings"] = {}
                        for ts in bpod_data["TrialSettings"].keys():
                            trial_data["trial_settings"][ts] = (
                                bpod_data["TrialSettings"][ts][t]
                                if bpod_data["nTrials"] > 1
                                else bpod_data["TrialSettings"][ts]
                            )

                    add_fields = [
                        k
                        for k in bpod_data.keys()
                        if k not in BpodTrialData.DEFAULT_FIELDS
                    ]

                    if len(add_fields) > 0:
                        trial_data["additional_fields"] = {}
                        for af in add_fields:
                            if type(bpod_data[af]) == np.ndarray:
                                trial_data["additional_fields"][af] = (
                                    bpod_data[af][t] if len(bpod_data[af]) > t else None
                                )
                            else:
                                trial_data["additional_fields"][af] = bpod_data[af]

                    self.insert1(trial_data)

                print(
                    f"Added Trial data for {trial_data['name']}, {trial_data['session_datetime']}, trial = {trial_data['trial']}"
                )

            else:

                last_trial_date = (BpodTrialData & key).fetch("trial_date")[-1]
                if date.today() - last_trial_date >= timedelta(days=3):
                    FileClosed.insert1(key)
                    print(
                        f"Closed Bpod File for {key['name']}, {key['session_datetime']}"
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

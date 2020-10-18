from datetime import datetime, timedelta
import numpy as np
from loguru import logger

from dj_ratacad import bpod
from dj_ratacad.utils import load_bpod_data, recarray_to_dict


def populate_trial_data():

    ### get list of open files ###

    open_files = (bpod.BpodMetadata() - bpod.FileClosed()).fetch("file_path")

    ### loop through files

    for of in open_files:

        ### load data from bpod data file ###

        bpod_data = load_bpod_data(bpod.BpodMetadata.DATA_DIR / of)

        ### check what's already been populated ###

        metadata = (bpod.BpodMetadata() & f"file_path='{of}'").fetch(as_dict=True)[0]
        already_populated = (bpod.BpodTrialData() & metadata).fetch("trial")
        current_trial = 0 if len(already_populated) == 0 else max(already_populated)

        if bpod_data["nTrials"] - current_trial > 1:

            for t in range(current_trial, bpod_data["nTrials"]):

                trial_data = {
                    "name": metadata["name"],
                    "session_datetime": metadata["session_datetime"],
                }
                trial_data["trial"] = t + 1

                time_elapsed = (
                    bpod_data["TrialStartTimestamp"][t]
                    - bpod_data["TrialStartTimestamp"][0]
                )
                trial_datetime = metadata["session_datetime"] + timedelta(
                    seconds=time_elapsed
                )
                trial_data["trial_date"] = datetime.strftime(trial_datetime, "%Y-%m-%d")
                trial_data["trial_time"] = datetime.strftime(trial_datetime, "%H-%M-%S")

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

                add_fields = [
                    k for k in bpod_data.keys() if k not in bpod.BpodTrialData.DEFAULT_FIELDS
                ]
                if len(add_fields) > 0:
                    trial_data["additional_fields"] = {}
                    for af in add_fields:
                        trial_data["additional_fields"][af] = (
                            bpod_data[af][t]
                            if type(bpod_data[af]) == np.ndarray
                            else bpod_data[af]
                        )

                bpod.BpodTrialData.insert1(trial_data)

            print(
                f"Added Trial data for {trial_data['name']}, {trial_data['session_datetime']}, trial = {trial_data['trial']}"
            )

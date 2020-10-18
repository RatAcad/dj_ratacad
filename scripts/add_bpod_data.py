""" setup """

from loguru import logger
import sys
import datajoint as dj

from pathlib import Path
import glob
from datetime import datetime

from dj_ratacad import rat, bpod, flashes
from dj_ratacad.utils import load_bpod_data, populate_trial_data


""" define constants """

LOG_FILE = Path.home() / "dj_ratacad.log"
DATA_DIR = Path.home() / "eng_research_scottlab" / "RATACAD_DATA"
BPOD_LOOKUP_NAMES = ["Rhea", "Remy", "Ron", "Renee", "Robin", "Rachel"]
PROTOCOLS_ON_DJ = bpod.Protocol.fetch("protocol")


""" configure logger """

log_format = "{time:YYYY:MM:DD HH:mm:ss} {level} -- line = {line} -- {message}"
logger.add(LOG_FILE, format=log_format)

class StreamToLogger:

    def __init__(self, level="INFO"):
        self._level = level

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass

sys.stdout = StreamToLogger()

""" configure datajoint """

dj.config["enable_python_native_blobs"] = True


""" loop through files, add new ones to datatjoint """

rats_on_study = (rat.Rat() - rat.Euthanized()).fetch("name")
files_on_dj = [Path(fp) for fp in bpod.BpodMetadata.fetch("file_path")]

for r in rats_on_study:

    files_on_disk = list(DATA_DIR.glob(f"{r}/*/Session Data/*.mat"))
    files_on_disk = [f.relative_to(DATA_DIR) for f in files_on_disk]
    new_files = list(set(files_on_disk).difference(files_on_dj))

    for nf in new_files:

        try:

            name, protocol, date, time = nf.stem.split("_")

            if protocol in PROTOCOLS_ON_DJ:

                bpod_data = load_bpod_data(DATA_DIR / nf)
                bpod_info = bpod_data["Info"]

                date = datetime.strftime(
                    datetime.strptime(bpod_info["SessionDate"], "%d-%b-%Y"),
                    "%Y-%m-%d",
                )
                time = bpod_info["SessionStartTime_UTC"]
                bpod_id = f"RATACAD_1_{BPOD_LOOKUP_NAMES.index(r) + 1}"

                box_design = (bpod.Bpod() & f"bpod_id='{bpod_id}'").fetch("design")[0]

                metadata = {
                    "name": r,
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

                bpod.BpodMetadata.insert1(metadata)

                logger.info(f"Added Metadata for {r}, {date} {time}")

        except Exception as e:

            logger.exception(f"Error adding file = {nf}:\n{e}")


""" populate trial data """

bpod.BpodTrialData.populate()
flashes.FlashesTrial.populate()
flashes.DailySummary.populate()

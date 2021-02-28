"""
dj-ratacad command line interface
"""

import click


@click.group()
def cli():
    pass


@cli.command()
def update():
    """ update database
    """

    from loguru import logger
    import sys
    from pathlib import Path
    from dj_ratacad import bpod, flashes

    """ configure logger """

    LOG_FILE = Path.home() / "dj_ratacad.log"
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

    """ populate metadata for new files """

    bpod.BpodMetadata.populate()

    """ populate trial data """

    bpod.BpodTrialData.populate()
    flashes.FlashesTrial.populate()
    flashes.DailySummary.populate()


@cli.command()
@click.argument("protocol")
@click.option("-d", "--date", type=str, help="date of summary to return")
def summary(protocol, date=None):
    """ print daily summary
    """

    import importlib
    from datetime import datetime, timedelta

    if date is None:
        date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    dj_schema = importlib.import_module(f"dj_ratacad.{protocol}")
    tbl = (dj_schema.DailySummary() & f"summary_date='{date}'").fetch(format="frame")
    tbl.reset_index(inplace=True)

    print(tbl)


@cli.command()
@click.argument("name")
@click.argument("weight", type=float)
@click.option("-d", "--date", type=str, help="date that animal was weighed")
@click.option("-b", "--baseline", is_flag=True)
def weight(name, weight, date=None, baseline=False):
    """ log animal weights to database
    """

    from dj_ratacad import animal
    from datetime import datetime

    weight_info = {'name' : name,
    'weight_date' : date if date is not None else datetime.today().date().strftime("%Y-%m-%d"),
    'weight' : weight,
    'baseline' : int(baseline)}

    if not baseline:
        baseline_weights = (animal.Weight() & f"name='{name}'" & 'baseline=1').fetch("weight")
        mean_baseline = sum([float(w) for w in baseline_weights]) / len(baseline_weights)
        weight_info.update({'percent_adlib' : weight / mean_baseline})

    animal.Weight.insert1(weight_info)


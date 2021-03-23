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
    from dj_ratacad import bpod, flashes, flashcount

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
    flashcount.FlashCountTrial.populate()
    flashcount.DailySummary.populate()

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
@click.argument("name", type=str)
@click.option("-w", "--weight", type=float, help="weight of animal")
@click.option("-d", "--date", type=str, help="date that animal was weighed")
@click.option("-b", "--baseline", is_flag=True)
@click.option("-r", "--remove", is_flag=True)
@click.option("-v", "--view", is_flag=True)
def weight(name, weight=None, date=None, baseline=False, remove=False, view=False):
    """ log animal weights to database
    """

    from dj_ratacad import animal
    from datetime import datetime

    if view:

        weight_df = (animal.Weight() & f"name='{name}'").fetch(format="frame")
        print(weight_df)

    elif weight is None:

        if not remove:

            raise Exception(
                "No action has been specified! "
                "Must specify weight (-w) to add a weight, remove (-r) to remove a weight, or view (-v) to view weights. "
                "Please only specify only one of weight, remove, or view."
            )

        else:

            (animal.Weight() & f"name='{name}'" & f"weight_date='{date}'").delete()
            print(f"Weight for {name} on {date} has been deleted.")

    else:

        if remove:

            raise Exception(
                "Both weight and remove were specified. "
                "Not sure if it was intended to add the weight to the database or "
                "remove the entry from the database. "
                "Please only specify one of weight or remove."
            )

        else:

            weight_info = {
                "name": name,
                "weight_date": date
                if date is not None
                else datetime.today().date().strftime("%Y-%m-%d"),
                "weight": weight,
                "baseline": int(baseline),
            }

            if not baseline:

                baseline_dates, baseline_weights = (
                    animal.Weight() & f"name='{name}'" & "baseline=1"
                ).fetch("weight_date", "weight")

                if datetime.strptime(date, "%Y-%m-%d").date() < baseline_dates[-1]:

                    raise Exception(
                        "Tried to enter a non-baseline weight that occurred before the baseline dates, "
                        "please double-check dates the specified date."
                    )

                mean_baseline = sum([float(w) for w in baseline_weights]) / len(
                    baseline_weights
                )
                weight_info.update({"percent_adlib": weight / mean_baseline})

            animal.Weight.insert1(weight_info)
            print(f"Weight for {name} on {date} = {weight} has been recorded.")


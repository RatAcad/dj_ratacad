# dj_ratacad: Datajoint for the Scott Lab Ratacademy

Python package for the Scott Lab Rat Academy datajoint pipeline. This package contains datajoint schema/table definitions, some utility functions, and command-line scripts.

## Requirements

- Python 3: Preferably using [Anaconda](https://www.anaconda.com/products/individual) or a virtual environment
- Personal account on the Scott Lab MySQL database (managed by IS&T). See instructions [here](dj_ratacad/docs/mysql.md).

## Getting Started

Once you have installed anaconda and you have a MySQL database account, please follow the instructions [here](dj_ratacad/docs/setup.md).

## Pushing Data From Rat Academy Control Computers

All data is currently pushed to the database from the daily training computer (RKC-SOM-LD-0003, 128.197.48.15). Instructions for setting up Rat Academy Control computers can be found on the [Scott Lab google drive](https://docs.google.com/document/d/1cAN6Vq61HbuDMiVo3U-vJHP5LDsBs5Y7RIQP8cbfAQg).

### Querying Data

For general information on querying data from python-datajoint databases, please see [datajoint's documentation](https://docs.datajoint.io/python/queries/Queries.html).

For detailed information about the Scott Lab datajoint pipeline, see [here](dj_ratacad/docs/query.md).

### Daily Summaries

Every task should have a `DailySummary` summary table, with a summary of rat performance that is populated daily. There is a command line interface to quickly access this table: `dj-ratacad summary task_name -d yyyy-mm-dd`.

Replace `task_name` with the name of the task (e.g. `flashes`). The default date is yesterday, so if you want the summary of yesterday's behavior for the flashes task: `dj-ratacad summary flashes`.

### Logging Weights

There is a command line interface to log rat weights.
- To enter a new weight: `dj-ratacad weight rat_name -d yyyy-mm-dd -w rat_weight`
- To remove a weight from the database: `dj-ratacad weight rat_name -d yyyy-mm-dd -r`
- To view all weights for a rat: `dj-ratacad weight rat_name -v`

Replace `rat_name` with the name of the rat and `yyyy-mm-dd` with the date the weight was recorded.

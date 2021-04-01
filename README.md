# dj_ratacad: Datajoint for the Scott Lab Ratacademy

Python package for the Scott Lab Rat Academy datajoint pipeline. This package contains datajoint schema/table definitions, some utility functions, and command-line scripts.

## Requirements

- Python 3: Preferably using [Anaconda](https://www.anaconda.com/products/individual) or a virtual environment
- Personal account on the Scott Lab MySQL database (managed by IS&T). See instructions [here](docs/mysql.md).

## Getting Started

Once you have installed anaconda and you have a MySQL database account, please follow the instructions [here](docs/setup.md).

## Pushing Data to datajoint From Rat Academy Control Computers

All data is currently pushed to the database everyday at 2 AM from the daily training computer (`RKC-SOM-LD-0003`, ip = `128.197.48.15`). If there are any issues with transferring data to datajoint, please refer to log files on this machine (located at `/home/ratacad1/dj_ratacad.log`). Instructions for setting up Rat Academy Control computers, including instructions for setting up this automated data transfer, can be found on the [Scott Lab google drive](https://docs.google.com/document/d/1cAN6Vq61HbuDMiVo3U-vJHP5LDsBs5Y7RIQP8cbfAQg).

## Using dj_ratacad

Documentation for using dj_ratacad can be found below:
- [Adding new animals](docs/animal.md)
- [Querying data](docs/query.md)
- [Checking daily summaries](docs/summary.md)
- [Logging animal weights](docs/weight.md)

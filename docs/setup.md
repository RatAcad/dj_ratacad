## Install RatAcad datajoint-python package and configure access to database

1. (Recommended) Set up a new conda environment and activate it:

```
conda create -n dj python=3.7
conda activate dj
```

2. Install the dj_ratacad package (will install all dependencies, including datajoint):

```
pip install git+https://github.com/RatAcad/dj_ratacad
```

3. Create your datajoint configuration. Please see datajoint documentation on [setting the datajoint config object](https://docs.datajoint.io/python/setup/01-Install-and-Connect.html). A few python lines like this should work: 

```
import datajoint as dj
dj.config['database.host'] = "buaws-aws-cf-rds-mysql-prod.cenrervr4svx.us-east-2.rds.amazonaws.com" #"buaw    s-aws-cf-rds-mysql-prod.cenrervr4svx.us-east-2.rds.amazonaws.com"
dj.config['database.user'] = "your_user_name"
dj.config.save_local()
```

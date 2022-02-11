## Install RatAcad datajoint-python package and configure access to database

1. (Recommended) Set up a new conda environment with python, then activate the environment:

```
conda create -n dj python
conda activate dj
```

2. Install the dj_ratacad package (this will install all dependencies, including datajoint):
- If you have ssh keys set up for your github account
  ```
  pip install git+ssh://git@github.com/RatAcad/dj_ratacad
  ```
- If you don't have ssh keys (i.e. you connect to github using just your username and password)
  ```
  pip install git+https://github.com/RatAcad/dj_ratacad
  ```

3. Create your datajoint configuration. Please see datajoint documentation on [setting the datajoint config object](https://docs.datajoint.io/python/setup/01-Install-and-Connect.html). A few python lines like this should work: 

```
import datajoint as dj
dj.config['database.host'] = "buaws-aws-cf-rds-mysql-prod.cenrervr4svx.us-east-2.rds.amazonaws.com"
dj.config['database.user'] = "your_user_name"
dj.config['database.password'] = "your_password"

# to save your credentials globally (recommended)
# (use these credentials from any working directory on your computer)
dj.config.save_global()

# to save your credentials locally
# (only use these credentials if you're in the present working directory)
dj.config.save_local()
```

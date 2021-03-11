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

3. Create your datajoint configuration. Please see datajoint documentation on [setting the datajoint config object](https://docs.datajoint.io/python/setup/01-Install-and-Connect.html).
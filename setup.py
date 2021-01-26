from setuptools import setup, find_packages

setup(
    name="dj_ratacad",
    version="0.0.0b0",
    packages=find_packages(),
    install_requires=[
        "datajoint",
        "datajoint_connection_hub",
        "numpy",
        "scipy",
        "mat73",
        "loguru",
        "click",
    ],
    entry_points={"console_scripts": ["dj-ratacad=dj_ratacad.cli:cli"]},
    author="Gary Kane",
    author_email="gakane@bu.edu",
    description="Datajoint pipeline for the Scott Lab Rat Academy",
)

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
        "loguru"
    ],
    scripts=['scripts/dj-ratacad'],
    author="Gary Kane",
    author_email="gakane@bu.edu",
    description="Datajoint pipeline for the Scott Lab Rat Academy",
)
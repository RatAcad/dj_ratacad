## Adding new animals

When you begin to test new animals, they must be manually added to the database. There are two tables that are important for tracking animal details:
- animal.Details: details for different strains of animals
- animal.Animal: details for specific animal


### animal.Details 

animal.Details only needs to be updated if a new strain of animal is being used. Current entries can be found in the table definition [here](../dj_ratacad/animal.py). They include these species, strain combinations:
- "Rat", "Long-Evans"
- "Rat", "Thy1-GCaMP"


### animal.Animal

Every animal needs to be entered in animal.Animal. The information needed to enter an animal in the database can be found in the animal.Animal table definition [here](../dj_ratacad/animal.py). This includes:
- name
- species and strain from animal.Details (see above)
- id: a unique identifier for the animal (e.g. eartag number)
- dob: date of birth
- pob: place of birth -- "BU" if bred in house, otherwise where it was purchased (e.g. "Charles River")
- sex: "M" or "F"

This information can be found on the [Scott Lab animal census sheet](https://docs.google.com/spreadsheets/d/188ymM6_04A6bwrk0CHPvVxHyYXW6LBybO3Pq-mzodso/edit#gid=976455736)

### Entering animals

##### NOTE: these instructions require that dj_ratacad is installed! On all Rat Academy control computers, dj_ratacad is installed in a conda environment called "dj". To install dj_ratacad, please see instructions on the [dj_ratacad home page](../).


To enter the animal, open a terminal, activate your datajoint conda/virtual environment, and open an ipython terminal. For example, in terminal:
```
conda activate dj
ipython
```

In ipython:
- import the animal schema from dj_ratacad
- create a dictionary containing the information for your new animal
- enter the new animal information into the animal.Animal table
For example:
```
from dj_ratacad import animal
my_new_animal = {
    'name' : 'MyRat',
    'species' : 'Rat',
    'strain' : 'Long-Evans',
    'id' : 12345,
    'dob' : '2021-04-01',
    'pob' : 'BU',
    'sex' : 'M',
    }
animal.Animal.insert1(my_new_animal)
```
To add multiple animals, create a dictionary for each animal, and run `animal.Animal.insert1` for each dictionary.
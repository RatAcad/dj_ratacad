"""
Schema for rat information
"""


import datajoint as dj


schema = dj.schema("scott_rat")


@schema
class Details(dj.Lookup):
    definition = """
    # Strain and source for each rat

    species         : varchar(24) # rat or mouse
    strain          : varchar(48) # nickname for strain
    ---
    source          : varchar(128) # where did it come from
    strain_full     : varchar(128) # full description of the strain
    stock           : varchar(48) # stock number for specific strain (if available, empty string if not)
    """

    contents = [
        ["Rat", "Long-Evans", "Charles River", "WT",  "006"],
        ["Rat", "Thy1-GCaMP", "RRRC", "LE-Tg(Thy1-GCaMP6f)7", "830"],
    ]


@schema
class Animal(dj.Manual):
    definition = """
    # Basic information about rats

    name : varchar(128)         # name of the animal (must be unique)
    ---
    -> Details
    id : int                    # animal identifier number
    dob : date                  # date of birth
    pob : varchar(24)           # place of birth (BU if bred in house, otherwise where it was purchased)
    sex : enum('M', 'F', 'U')   # sex of the rat (male, female, unknown)
    """


@schema
class Weight(dj.Manual):
    definition = """
    # Weights of rats

    -> Animal
    ---
    weight_time : datetime      # Date animal was weighed
    weight : decimal(5, 1)      # weight of the animal in grams (one decimal point)
    """


@schema
class EuthanasiaMethod(dj.Lookup):
    definition = """
    # Table of euthanasia methods
    
    method : varchar(48)        # method for euthanasia
    """
    contents = [
        ["Transcardial Perfusion"],
    ]


@schema
class Euthanized(dj.Manual):
    definition = """
    # Keep record of euthanized animals

    -> Animal
    ---
    date_euthanasia : date      # date rat was euthanized
    -> EuthanasiaMethod
    notes="" : varchar(280)     # any notes (e.g. reason for euthanizing)
    """
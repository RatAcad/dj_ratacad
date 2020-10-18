"""
Schema for rat information
"""


import datajoint as dj


schema = dj.schema("scott_rat")


@schema
class Strain(dj.Lookup):
    definition = """
    # Strain and source for each rat

    strain : varchar(48) # nickname for strain
    ---
    genotype : varchar(128) # full description of genotype
    source : varchar(128) # where did the rat come from
    stock : varchar(48) # stock number for specific strain (if available, empty string if not)
    """
    contents = [
        ["Long-Evans", "Long-Evans", "Charles River", "006"],
    ]


@schema
class Rat(dj.Manual):
    definition = """
    # Basic information about rats

    name : varchar(128)         # name of the rat (must be unique)
    ---
    id : int                    # rat identifier number
    dob : date # date of birth
    sex : enum('M', 'F', 'U')   # sex of the rat (male, female, unknown)
    -> Strain
    """


@schema
class Weight(dj.Manual):
    definition = """
    # Weights of rats

    -> Rat
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

    -> Rat
    ---
    date_euthanasia : date      # date rat was euthanized
    -> EuthanasiaMethod
    notes="" : varchar(280)     # any notes (e.g. reason for euthanizing)
    """
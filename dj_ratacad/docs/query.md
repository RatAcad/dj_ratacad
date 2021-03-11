This pipeline is designed around Bpod Trials (in the bpod.BpodTrialData table). All important information about an Bpod Trial is connected to the bpod.BpodTrialData table, including the rat, the box this rat was in and the box configuration, the protocol used, the time of the trial, etc. For more details, please see the [bpod schema definition](dj_ratacad/bpod.py), and the datajoint ERD diagram below. Further analyses that are specific to a particular task can be found in additional task-specific schema (e.g. see the [flashes task schema](dj_ratacad/flashes), which consolidates important information for each flashes task trial from the bpod.BpodTrialData table).

![ratacad_erd](images/dj_ratacad_erd.png)

#### Example Queries

To query all trial data from the flashes task as a list of dictionaries (a dictionary for each trial):

```
from dj_ratacad import flashes
flashes.FlashesTrial().fetch(as_dict=True)
```

To query only data from the rat "Ron": `(flashes.FlashesTrial() & 'name="Ron"').fetch(as_dict=True)`

To query only data from the final stage of training (stage 5):`(flashes.FlashesTrial() & 'stage=5').fetch(as_dict=True)`

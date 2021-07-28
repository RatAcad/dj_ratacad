## Adding/Modifying Bpod Testing Boxes

There are two places you may need to change the dj_ratacad pipeline in order to modify the configuration of existing boxes (e.g., change the nose poke panel) or to add new boxes.

### Box Design Table

First, check that the configuration of your box is entered into the [bpod.BoxDesign table](../dj_ratacad/bpod.py#L21). This table holds a list of the designs used in the rat academy (e.g., 3-port box or 6-port box). To enter a new design, please provide a short identifier (like "3-port" or "6-port"), and then a slightly longer description.

### Bpod Table

Next, add a new entry to the [bpod.Bpod table](../dj_ratacad/bpod.py#L42). If you are modifying an existing box, just put a new entry at the bottom as if you were adding a new one. For each new or modified box, please provide the box name (e.g. "RATACAD_1_1"), the description (exactly as it is in the Bpod.BoxDesign table), the date the entry is added, and the bpod serial number.

## Adding New Protocols

To add a new protocol to the dj_ratacad pipeline, please add an entry to the [bpod.Protocol table](../dj_ratacad/bpod.py#L96). Please provide the protocol name (exactly as it is in Bpod MATLAB/BpodAcademy), and a brief description of the task.
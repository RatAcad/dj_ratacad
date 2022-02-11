## Adding/Modifying Bpod Testing Boxes

There are two places you may need to change the dj_ratacad pipeline in order to modify the configuration of existing boxes (e.g., change the nose poke panel) or to add new boxes.

### Box Design Table

First, check that the configuration of your box is entered into the [bpod.BoxDesign table](../dj_ratacad/bpod.py#L21). This table holds a list of the designs used in the rat academy (e.g., 3-port box or 6-port box). To enter a new design, please provide a short identifier (like "3-port" or "6-port"), and then a slightly longer description.

### Bpod Table

Next, add a new entry to the [bpod.Bpod table](../dj_ratacad/bpod.py#L42). If you are modifying an existing box, just put a new entry at the bottom as if you were adding a new one. For each new or modified box, please provide the box name (e.g. "RATACAD_1_1"), the description (exactly as it is in the Bpod.BoxDesign table), the date the entry is added, and the bpod serial number.

## Adding New Protocols

To add a new protocol to the dj_ratacad pipeline, please add an entry to the [bpod.Protocol table](../dj_ratacad/bpod.py#L96). Please provide the protocol name (exactly as it is in Bpod MATLAB/BpodAcademy), and a brief description of the task.

To set up automated task-specific analysis for the new protocol, you will need to:
- Create a new database in the MySQL server that is managed by IS&T
  - Email ithelp@bu.edu (cc bgiven@bu.edu) asking to create a new database with the following info:
    - database url: buaws-aws-cf-rds-mysql-prod.cenrervr4svx.us-east-2.rds.amazonaws.com
    - database name: scott_<your_new_protocol> (e.g. "scott_flashes" or "scott_twostep")
    - the list of users who should get access to this database (give them bu net IDs like "gakane" instead of "Gary Kane"). specify which users need which permissions (read only access vs. read/write/delete access).
- Create a datajoint schema for your task. If you don't know what this means, please look at the [datajoint tutorials](https://tutorials.datajoint.io/beginner/building-first-pipeline/python/first-table.html) (read through full tutorial thoroughly!). Also refer to existing examples in the dj_ratacad pipeline ([Flashes Task schema](../dj_ratacad/flashes.py)).
  - **Important: please create a new git branch to edit dj_ratacad code**
  - Your schema should contain at least two tables:
    - your_task.YourTaskTrial (e.g. flashes.FlashesTrial): this table extracts task-relevant information for each trial. The purpose of this table is to perform all necessary pre-processing (any computations that you need to perform on all sessions) so the data in this table is ready for analysis!
    - your_task.DailySummary (e.g. flashes.DailySummary): this table extracts important summary statistics for each day of testing. The main purpose of this table is to provide a convenient way to check your data every day to confirm that the task went smoothly (i.e., that the boxes are functioning and animals are performing the task).
- Test your new table locally to make sure data is populating correctly. Again, refer to [datajoint tutorials](https://tutorials.datajoint.io/beginner/building-first-pipeline/python/computed-table.html) if you have any questions.
- Edit the [command line module](../dj_ratacad/cli.py#L56) so that your task data automatically populates every day:
  - Within the update() function, create a new populate function (e.g., populate_flashes), modeled after existing examples. If your task is called *newtask*:
    ```
    def populate_newtask():
        from dj_ratacad import newtask

        newtask.newtaskTrial.populate()
        newtask.DailySummary.populate()
    ```
  - Below the populate functions, start a [process to populate your task data](../dj_ratacad/cli.py#L80): `mp.Process(target=populate_newtask).start()`
- Finally, once you're sure that everything is working, merge your branch with the master. Once it's merged, it should integrated into the pipeline the next day :)



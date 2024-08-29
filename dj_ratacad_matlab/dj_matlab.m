% Routine to update DataJoint SQL database with network data

% Add toolboxes to the MATLAB path 
addpath('/home/ratacad1/ratacad/dj_ratacad/dj_ratacad_matlab');
addpath('/home/ratacad1/Documents/MATLAB/datajoint-matlab');
addpath('/home/ratacad1/MATLAB Add-Ons/Toolboxes/mym/distribution/mexa64');

% Define network location where data from rat academy is saved
ratacaddir = '/ad/eng/research/eng_research_scottlab/RATACAD_DATA';

% Run routine to update SQL database with behavioural data on network drive
dj_pushdatasets('UncertainFlashInference',    ratacaddir);
dj_pushdatasets('UncertainFlashInference_v2', ratacaddir);
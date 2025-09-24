% Routine to update DataJoint SQL database with network data

% Add toolboxes to the MATLAB path 
addpath('/home/ratacad1/Documents/MATLAB/dj_ratacad/dj_ratacad_matlab');
addpath('/home/ratacad1/Documents/MATLAB/datajoint-matlab');
addpath('/home/ratacad1/MATLAB Add-Ons/Toolboxes/mym/distribution/mexa64');

% Define network location where data from rat academy is saved
ratacaddir = '/ad/eng/research/eng_research_scottlab/RATACAD_DATA';

% Whether to drop existing tables
data2push = 'all'; % 'all' or 'missing'
protocolver = 'last'; % 'all' or 'last'

% Run routine to update SQL database with behavioural data on network drive
tic;
try
    if strcmpi(protocolver, 'all')        
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference'   , []                       , data2push);
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference_v2', 'UncertainFlashInference', data2push);
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference_v3', 'UncertainFlashInference', data2push);
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference_v4', 'UncertainFlashInference', data2push);
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference_v5', 'UncertainFlashInference', data2push);
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference_v6', 'UncertainFlashInference', data2push);
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference_v7', 'UncertainFlashInference', data2push);
    elseif strcmpi(protocolver, 'last')
        dj_pushdatasets(ratacaddir, 'UncertainFlashInference_v7', 'UncertainFlashInference', data2push);
    end
catch
    system(['/home/ratacad1/anaconda3/bin/curl -H "Tags: desktop_computer" ', ...
        '-d "Failed to publish new data on DataJoint" ntfy.sh/ratacademy']);
end
toc;
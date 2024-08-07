function DATA = dj_pushdatasets(protocolname, ratacaddir, duplmeth)
% The function publishes all available data from a given protocol to
% the SQL datajoint database.
% The following analysis functions must be available: 
% - "dj_[PROTOCOL NAME]_trialtable.m"
% - "dj_[PROTOCOL NAME]_summarytable.m"
% The following datajoint functions must be available:
% - "+[PROTOCOL NAME]/getSchema.m"
% - "+[PROTOCOL NAME]/Trials.m"
% - "+[PROTOCOL NAME]/DailySummary.m"
% - "+[PROTOCOL NAME]/StageSummary.m"
% 
% Maxime Maheu <maheu.mp@gmail.com> | 2024

% Define default path to data
if nargin < 2, ratacaddir = '/ad/eng/research/eng_research_scottlab/RATACAD_DATA'; end

% Determine how to deal with duplicates by default
if nargin < 3, duplmeth = 'REPLACE'; end

% Get analysis functions corresponding to the protocol
fun_trialtable   = eval(sprintf('@(d,n) dj_%s_trialtable(d,n)',   lower(protocolname)));
fun_summarytable = eval(sprintf('@(d,c) dj_%s_summarytable(d,c)', lower(protocolname)));

% Get datajoint functions corresponding to the protocol
trialfun = eval(sprintf('%s.Trials',       lower(protocolname)));
stagefun = eval(sprintf('%s.StageSummary', lower(protocolname)));
dailyfun = eval(sprintf('%s.DailySummary', lower(protocolname)));

% Initialize connection without TLS
fprintf('- Setting up datajoint connection... ');
reset = true;
use_tls = false;
dj.conn([], [], [], [], reset, use_tls);
fprintf('Done.\n');

% Retrieve data already populated on DataJoint
fprintf('- Getting data already on datajoint database... ');
query = uncertainflashinference.Trials;
keys = query.fetch;
availablerats  = {keys.name};
availabledates = cellfun(@(x) erase(x(1:10), '-'), {keys.trial_datetime}, 'uni', 0);
fprintf('Done.\n');

% Get rat list
fprintf('- Getting local rat list... ');
sublist = dir(ratacaddir);
sublist = sublist(~cellfun(@(x) x(1) == '.', {sublist.name}));
sublist = sublist(~contains({sublist.name}, 'Experimenter'));
Nr = numel(sublist);
fprintf('Done.');

% Loop over rats
DATA = cell(1,Nr);
for ir = 1:Nr
    fprintf('\n- Processing "%s"... ', sublist(ir).name);
    
    % Get session list on local data
    filelist = dir(fullfile(sublist(ir).folder, sublist(ir).name, protocolname, ...
        'Session Data', sprintf('*_%s_*.mat', protocolname)));
    parsed = cellfun(@(x) textscan(x, '%[^_]_%[^_]_%[^_]_%[^_.].%s'), {filelist.name}, 'uni', 0);
    datelist = cellfun(@(x) x{3}{1}, parsed, 'uni', 0);
    hourlist = cellfun(@(x) x{4}{1}, parsed, 'uni', 0);
    Nd = numel(filelist);
    
    % Determine whether data is available
    if Nd == 0
        fprintf('No data found.');
    else
        fprintf('Data found.');
        
        % Loop over files
        DATA{ir} = cell(1,Nd);
        for id = 1:Nd
            
            % Determine whether data is already available on DataJoint
            fprintf('\n     * Data from %s-%s... ', datelist{id}, hourlist{id});
            isavailable = any(strcmpi(availablerats,  sublist(ir).name) & ...
                              strcmpi(availabledates, datelist{id}));
            
            % Always overwrite data from the last two data files, which may
            % still be running
            if any(id == Nd-1:Nd), isavailable = false; end
            
            % If data is not yet available, publish it
            if isavailable
                fprintf('Data aleady available on DataJoint.');
            elseif ~isavailable
                
                % Load data
                fprintf('Loading data... ');
                load(fullfile(filelist(id).folder, filelist(id).name), 'SessionData');
                fprintf('Done. Building table... ');
                
                % Get trial table
                DATA{ir}{id} = fun_trialtable(SessionData, sublist(ir).name);
                
                % Send trial data table on the SQL database
                fprintf('Done. Sending table... ');
                insert(trialfun, DATA{ir}{id}, duplmeth);
                fprintf('Done.');
            end
        end
        
        % Combine data from different files
        DATA{ir} = [DATA{ir}{:}];
        
        % Create and send stage summary to SQL database
        fprintf('\n     * Sending summary stage table... ');
        stagetable = fun_summarytable(DATA{ir}, 'stage');
        insert(stagefun, stagetable, duplmeth);
        
        % Create and send daily summary to SQL database
        fprintf('Done.\n     * Sending summary day table... ');
        daytable = fun_summarytable(DATA{ir}, 'day');
        insert(dailyfun, daytable, duplmeth);
        fprintf('Done.');
    end
end
fprintf('\n');
end
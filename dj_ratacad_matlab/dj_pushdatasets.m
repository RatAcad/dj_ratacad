function dj_pushdatasets(ratacaddir, protocolname, djtable, data2push)
% The function publishes all available data from a given protocol to
% the SQL datajoint database.
% The following analysis functions must be available: 
% - "dj_[PROTOCOL NAME]_trialtable.m"
% - "dj_[PROTOCOL NAME]_summarytable.m"
% - "dj_[PROTOCOL NAME]_metadata.m" (optional)
% The following datajoint functions must be available:
% - "+[PROTOCOL NAME]/getSchema.m"
% - "+[PROTOCOL NAME]/Trials.m"
% - "+[PROTOCOL NAME]/DailySummary.m"
% - "+[PROTOCOL NAME]/StageSummary.m"
% 
% Maxime Maheu <maheu.mp@gmail.com> | 2024

% Define default path to data
if nargin < 1, ratacaddir = '/ad/eng/research/eng_research_scottlab/RATACAD_DATA'; end
if isempty(ratacaddir), ratacaddir = pwd; end

% Get analysis functions corresponding to the protocol
fun_trialtable   = eval(sprintf('@(d,n) dj_%s_trialtable(d,n)',   lower(protocolname)));
fun_summarytable = eval(sprintf('@(d,c) dj_%s_summarytable(d,c)', lower(protocolname)));

% Get datajoint functions corresponding to the protocol
if nargin < 3 || isempty(djtable), djtable = protocolname; end
trialfun = eval(sprintf('%s.Trials',       lower(djtable)));
stagefun = eval(sprintf('%s.StageSummary', lower(djtable)));
dailyfun = eval(sprintf('%s.DailySummary', lower(djtable)));

% Whether to push only missing sessions
if nargin < 4 || isempty(data2push), data2push = 'all'; end
duplmeth = 'REPLACE';

% Initialize connection without TLS
fprintf('- Setting up datajoint connection... ');
reset = true;
usetls = false;
dj.conn([], [], [], [], reset, usetls);
fprintf('Done.\n');

% Retrieve data already populated on DataJoint
if strcmpi(data2push, 'missing')
    fprintf('- Getting data already on datajoint database... ');
    query = eval(sprintf('%s.Trials', lower(djtable)));
    keys = query.fetch;
    availablerats  = unique({keys.name})';
    availabledates = unique(cellfun(@(x) erase(x(1:10), '-'), {keys.trial_inittime}, 'uni', 0))';
    fprintf('Done.\n');
elseif strcmpi(data2push, 'all')
    availablerats = {}; availabledates = {};
end

% Get rat list
fprintf('- Getting local rat list... ');
sublist = dir(ratacaddir);
sublist = sublist(~cellfun(@(x) x(1) == '.', {sublist.name}));
sublist = sublist(~contains({sublist.name}, 'Experimenter'));
sublist = sublist(~contains({sublist.name}, 'FakeSubject'));
Nr = numel(sublist);
fprintf('Done.\n');

% Get rat list
fprintf('- Loading meta-data... ');
metadatafun = sprintf('dj_%s_metadata', lower(djtable));
global explab badsegm injections;
if exist(metadatafun, 'file') == 2
    [explab, badsegm, injections] = eval(metadatafun);
end
fprintf('Done.');

% Loop over rats
for ir = 1:Nr
    ratname = sublist(ir).name;
    fprintf('\n- Processing "%s"... ', ratname);
    
    % Get session list on local data
    filelist = dir(fullfile(sublist(ir).folder, ratname, protocolname, ...
        'Session Data', sprintf('%s_*.mat', ratname)));
    datelist = cellfun(@(x) x(end-18:end-11), {filelist.name}, 'uni', 0);
    hourlist = cellfun(@(x) x(end-9:end-4),   {filelist.name}, 'uni', 0);
    [~,idx] = sortrows([datelist(:), hourlist(:)], 1:2);
    datelist = datelist(idx);
    hourlist = hourlist(idx);
    filelist = filelist(idx);
    Nd = numel(filelist);
    
    % Determine whether data is available
    if Nd == 0
        fprintf('No data found.');
    else
        fprintf('Data found.');
        
        % Loop over files
        for id = 1:Nd
            
            % Determine whether data is already available on DataJoint
            fprintf('\n\t* Data from %s-%s... ', datelist{id}, hourlist{id});
            isavailable = any(strcmpi(availablerats,  ratname) & ...
                          any(strcmpi(availabledates, datelist{id})));
            
            % Always overwrite data from today in case new trials were added
            if strcmpi(char(datetime('today',     'Format', 'yyyyMMdd')), datelist{id}), isavailable = false; end
            if strcmpi(char(datetime('yesterday', 'Format', 'yyyyMMdd')), datelist{id}), isavailable = false; end
            
            % If data is not yet available, publish it
            if isavailable
                fprintf('Data already available on DataJoint.');
            elseif ~isavailable
                
                % Determine whether there was an injection on that day
                injection = getinjectionlabel(ratname, datelist{id});
                
                % Load data
                fprintf('Loading data... ');
                try load(fullfile(filelist(id).folder, filelist(id).name), 'SessionData');
                catch, fprintf('Unable to load data. File likely corrupted! '); continue;
                end
                fprintf('Done. Building table... ');
                
                % Get trial table
                SessionData.ProtocolName = protocolname;
                SessionData.Injection = injection;
                DATA = fun_trialtable(SessionData, ratname);
                
                % Send trial data table on the SQL database
                fprintf('Done. Sending table... ');
                if ~isempty(fieldnames(DATA))
                    insert(trialfun, DATA, duplmeth);
                end
                fprintf('Done.');
            end
        end
        
        % Pull all data
        fprintf('\n\t* Pulling all data... ');
        DATA = struct2table(fetch(eval(sprintf('%s.Trials', lower(djtable))) & ...
            sprintf('name = "%s"', ratname) & ...
            sprintf('protocol = "%s"', protocolname), ...
            'isday', 'stage', 'outcome', 'choice', 'rt_side', 'it'));
        
        % Create and send stage summary to SQL database
        fprintf('Done.\n\t* Sending summary stage table... ');
        stagetable = fun_summarytable(DATA, 'stage');
        insert(stagefun, stagetable, duplmeth);
        
        % Create and send daily summary to SQL database
        fprintf('Done.\n\t* Sending summary day table... ');
        daytable = fun_summarytable(DATA, 'day');
        insert(dailyfun, daytable, duplmeth);
        fprintf('Done.');
    end
end
fprintf('\n');
end

% =========================================================================
% Subfunction to get injection label
function injectionlabel = getinjectionlabel(ratname, sessiontime)

% Loop over injection table
global injections;
for i = 1:numel(injections)
    
    % Determine whether there was an injection performed on that date for
    % that rat
    colid = find(strcmpi(injections{i}.Properties.VariableNames, ratname));
    rowid = find(strcmpi(injections{i}.Properties.RowNames,      sessiontime));
    if ~isempty(rowid) & ~isempty(colid), injectionlabel = injections{i}{rowid,colid}{1};
    
    % Otherwise, return a none label
    else, injectionlabel = 'None';
    end
end
end
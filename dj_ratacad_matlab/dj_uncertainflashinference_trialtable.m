function T = dj_uncertainflashinference_trialtable(bpodstruct, ratname)
% This function returns the trial table from a Bpod structure generated by
% the UncertainFlashInference protocol.
% 
% Maxime Maheu <maheu.mp@gmail.com> | 2024

% Define labels
tasklabels = {'count', 'weigh'};
portlabels = {'left', 'middle', 'right'};
pairlabels = {'none', 'miniblock', 'replay'};

% Labels for generative categories
gencat = [-1,1];
gencatlabels = {'left', 'right'};

% Specify the date-time format
dtformat = 'yyyy-MM-dd HH:mm:ss';
dtfun = @(x) char(datetime(x, 'Format', dtformat));

% Get onsets and offsets of bad segments and of experiments
global explab badsegm;
[badon, badoff]         = getonoff(badsegm, ratname);
[expon, expoff, ratidx] = getonoff(explab,  ratname);

% Loop over trials
Ntrials = bpodstruct.nTrials;
T = struct;
j = 1;
for i = 1:Ntrials
    
    % Get info corresponding to current trial
    protocol = bpodstruct.ProtocolName;
    settings = bpodstruct.TrialSettings(i);
    states   = bpodstruct.RawEvents.Trial{i}.States;
    events   = bpodstruct.RawEvents.Trial{i}.Events;
    
    % Determine experiment label of current trial
    idx = ratidx((settings.InitTimeTrial >= expon) & (settings.InitTimeTrial <= expoff));
    
    % Determine if the current trial belongs to a bad segment
    inbadseg = (settings.InitTimeTrial >= badon) & (settings.InitTimeTrial <= badoff);
    if ~any(inbadseg)
        
        % Get choice and timings
        [choice, outcome, timepoke] = getdecisionlabels(states);
        computingdelay = seconds(settings.InitTimeSMA - settings.InitTimeTrial);
        
        % Build table
        T(j).name               = ratname;
        T(j).trial_datetime     = dtfun(settings.InitTimeTrial);
        % -----------------------------------------------------------------
        T(j).session_datetime   = dtfun(settings.RunOnset);
        T(j).trial              = i;
        T(j).isday              = settings.IsDay;
        % -----------------------------------------------------------------
        T(j).protocol           = protocol;
        T(j).experiment         = getvalue(table2struct(explab(idx,:)), 'Experiment', 'None');
        % -----------------------------------------------------------------
        T(j).setting            = settings.Label;
        T(j).task               = tasklabels{settings.Design + 1};
        T(j).stage              = settings.Stage;
        T(j).trial_instage      = settings.StageTrials;
        % -----------------------------------------------------------------
        T(j).rewardsize_left    = settings.SizeReward(1);
        T(j).rewardsize_right   = settings.SizeReward(end);
        % -----------------------------------------------------------------
        T(j).init_time          = seconds(settings.InitTimeTrial - settings.InitTimeFixation);
        T(j).flashes_left       = strjoin(arrayfun(@num2str, settings.Trial(1,:), 'uni', 0), ' ');
        T(j).flashes_right      = strjoin(arrayfun(@num2str, settings.Trial(2,:), 'uni', 0), ' ');
        T(j).generative_side    = gencatlabels{settings.CatGen == gencat};
        T(j).correct_side       = portlabels{settings.SideCorrect};
        T(j).choice             = choice;
        T(j).outcome            = outcome;
        T(j).rt                 = max([timepoke + computingdelay, -1], [], 'OmitNaN');
        % -----------------------------------------------------------------
        T(j).isuniform          = getvalue(settings, 'UniformTrial');
        % -----------------------------------------------------------------
        T(j).isopto             = getvalue(settings, 'OptoTrial');
        T(j).optoonset          = getvalue(events, 'GlobalTimer1_Start');
        T(j).optodur            = T(j).isopto * max([T(j).rt, getvalue(settings, 'OptoMaxDuration')]);
        % -----------------------------------------------------------------
        T(j).iseeg              = getvalue(settings, 'EEGtrigs');
        % -----------------------------------------------------------------
        T(j).ispaired           = getvalue(settings, 'PairedTrial');
        T(j).pairedstrat        = pairlabels{settings.PairedStrategy + 1};
        T(j).paired_inittime    = dtfun(settings.PairedInitTime);
        % -----------------------------------------------------------------
        T(j).isstaircase        = getvalue(settings, 'StaircaseTrial');
        staircase               = getvalue(settings, 'StaircaseVal', {0, 0});
        T(j).staircase_nightval = staircase{1}(end);
        T(j).staircase_dayval   = staircase{2}(end);
        % -----------------------------------------------------------------
        T(j).tau                = getvalue(settings, 'Tau');
        T(j).alpha              = getvalue(settings, 'Alpha');
        T(j).beta               = getvalue(settings, 'Beta');
        T(j).sigma              = getvalue(settings, 'Sigma');
        j = j + 1;
    end
end
end

% =========================================================================
% Subfunction to get onset/offset
function [on, off, ratidx] = getonoff(metadatatable, ratname)

% Get rows corresponding to the rat
ratidx = find(strcmpi(metadatatable.Rat, ratname));

% Get beginning and enf of time windos
on  = metadatatable(ratidx,:).Beginning;
off = metadatatable(ratidx,:).End;

% Deal with missing fields
on (isempty(on ) | isnat(on )) = datetime('01-Jan-0000');
off(isempty(off) | isnat(off)) = datetime('31-Dec-9999');

% Fill time if missing
nodate = @(x) (hour(off) == 0) & (minute(off) == 0) & (second(off) == 0);
on (nodate(on )) = on (nodate(on )) + duration(00, 00, 01);
off(nodate(off)) = off(nodate(off)) + duration(23, 59, 59);

end

% =========================================================================
% Subfunction to get choice & outcome labels from Bpod trial structure
function [choice, outcome, timepoke] = getdecisionlabels(trialstruc)

% Define detection variable
ports   = [1 3];
correct = arrayfun(@(x) sprintf('Correct%i',    x), ports, 'uni', 0);
error   = arrayfun(@(x) sprintf('Error%i',      x), ports, 'uni', 0);
early   = arrayfun(@(x) sprintf('EarlyEnter%i', x), ports, 'uni', 0);
fun     = @(x,y) any(~isnan([x, y]));

% Get boolean categories
isleft       = fun(trialstruc.(correct{1}), trialstruc.(error{1}));
isright      = fun(trialstruc.(correct{2}), trialstruc.(error{2}));
isleftearly  = fun(trialstruc.(early{1}), []);
isrightearly = fun(trialstruc.(early{2}), []);
isearly      = isleftearly | isrightearly;
iscorrect    = fun(trialstruc.(correct{1}), trialstruc.(correct{2}));
isomitted    = all(cellfun(@(x) all(isnan(trialstruc.(x))), [correct, error, early]));

% Determine choice label
if isleft,       choice = 'left';       end
if isright,      choice = 'right';      end
if isleftearly,  choice = 'earlyleft';  end
if isrightearly, choice = 'earlyright'; end
if isomitted,    choice = 'omission';   end

% Determine outcome label
if  iscorrect, outcome = 'correct';  end
if ~iscorrect, outcome = 'error';    end
if  isearly,   outcome = 'early';    end
if  isomitted, outcome = 'omission'; end

% Get timing of decision poke
timepoke = cellfun(@(x) trialstruc.(x)(1), [correct, error, early]);
timepoke = timepoke(~isnan(timepoke));
end

% =========================================================================
% Subfunction to deal with missing field
function value = getvalue(trialstruc, fieldname, defaultvalue)

% In case of empty input
if isempty(trialstruc), trialstruc = struct; end

% By default, the default value is 0
if nargin < 3 || isempty(defaultvalue), defaultvalue = 0; end

% Return value it it exists
if isfield(trialstruc, fieldname), value = trialstruc.(fieldname);

% Otherwise return default value
else, value = defaultvalue;
end

end
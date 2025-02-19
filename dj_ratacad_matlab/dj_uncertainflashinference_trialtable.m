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
dtformat = 'yyyy-MM-dd HH:mm:ss.SSS';
dtfun = @(x) char(datetime(x, 'Format', dtformat));

% Specify which versions of the protocol have the central fixation enabled
global fixationver;
fixationver = {'v3', 'v4', 'v5', 'v6'};

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
    
    % First, determine if the current trial belongs to a bad segment, in
    % which case we simply ignore this trial
    if isempty(settings.InitTimeTrial), continue; end % file corrupted
    inbadseg = (settings.InitTimeTrial >= badon) & (settings.InitTimeTrial <= badoff);
    if any(inbadseg), continue; end
    
    % Determine experiment label of current trial
    idx = ratidx((settings.InitTimeTrial >= expon) & (settings.InitTimeTrial <= expoff));
    
    % Get choice and timings
    [choice, outcome, tsidepoke, rtside, rtcenter] = getdecisionlabels(states, events, protocol);
    
    % If trial field is missing, it means a single, maximally bright
    % flash was presented
    if ~isfield(settings, 'CatGen'), settings.CatGen = settings.CatInf; end
    if ~isfield(settings, 'Trial') || isempty(settings.Trial)
        settings.Trial = [0; 0];
        settings.Trial((settings.CatInf + 3) / 2) = settings.BrightnessMax;
    end
    
    % Get trial starting and initiation times
    [begtrl, begctr, it, prdtrl, isday] = getinittimes(settings, states, protocol);
    
    % Build table
    T(j).name               = ratname;
    T(j).trial_inittime     = dtfun(begctr);
    T(j).trial_starttime    = dtfun(begtrl);
    % ---------------------------------------------------------------------
    T(j).session_starttime  = dtfun(settings.RunOnset);
    T(j).trial              = i;
    T(j).isday              = isday;
    % ---------------------------------------------------------------------
    T(j).protocol           = protocol;
    T(j).room               = getvalue(table2struct(explab(idx,:)), 'Room', 'Unknown');
    T(j).position           = getvalue(table2struct(explab(idx,:)), 'Position', 'Unknown');
    T(j).experiment         = getvalue(table2struct(explab(idx,:)), 'Experiment', 'Unknown');
    T(j).commit_id          = getvalue(settings, 'CommitID', 'Unknown');
    % ---------------------------------------------------------------------
    T(j).setting            = settings.Label;
    T(j).task               = tasklabels{settings.Design + 1};
    T(j).stage              = settings.Stage;
    T(j).trial_instage      = settings.StageTrials;
    % ---------------------------------------------------------------------
    T(j).rewardsize_left    = settings.SizeReward(1);
    T(j).rewardsize_right   = settings.SizeReward(end);
    % ---------------------------------------------------------------------
    T(j).flashes_left       = strjoin(arrayfun(@num2str, settings.Trial(1,:), 'uni', 0), ' ');
    T(j).flashes_right      = strjoin(arrayfun(@num2str, settings.Trial(2,:), 'uni', 0), ' ');
    T(j).generative_side    = gencatlabels{settings.CatGen == gencat};
    T(j).correct_side       = portlabels{settings.SideCorrect};
    T(j).choice             = choice;
    T(j).outcome            = outcome;
    % ---------------------------------------------------------------------
    T(j).it                 = max([it,       -10], [], 'OmitNaN');
    T(j).rt_side            = max([rtside,   -10], [], 'OmitNaN');
    T(j).rt_center          = max([rtcenter, -10], [], 'OmitNaN');
    % ---------------------------------------------------------------------
    T(j).isuniform          = getvalue(settings, 'UniformTrial');
    % ---------------------------------------------------------------------
    T(j).ispaired           = getvalue(settings, 'PairedTrial');
    T(j).paired_strat       = pairlabels{settings.PairedStrategy + 1};
    T(j).paired_reftime     = dtfun(settings.PairedInitTime);
    T(j).trial_pairedtime   = dtfun(prdtrl);
    % ---------------------------------------------------------------------
    T(j).isstaircase        = getvalue(settings, 'StaircaseTrial');
    staircase               = getvalue(settings, 'StaircaseVal', {0, 0});
    T(j).staircase_nightval = staircase{1}(end);
    T(j).staircase_dayval   = staircase{2}(end);
    % ---------------------------------------------------------------------
    T(j).tau                = getvalue(settings, 'Tau');
    T(j).alpha              = getvalue(settings, 'Alpha');
    T(j).beta               = getvalue(settings, 'Beta');
    T(j).sigma              = getvalue(settings, 'Sigma');
    % ---------------------------------------------------------------------
    T(j).isopto             = getvalue(settings, 'OptoTrial');
    T(j).opto_onset         = T(j).isopto * min(getvalue(events, 'GlobalTimer1_Start'));
    T(j).opto_dur           = T(j).isopto * max([tsidepoke, getvalue(settings, 'OptoMaxDuration')], [], 'OmitNaN');
    % ---------------------------------------------------------------------
    T(j).iseeg              = getvalue(settings, 'EEGtrigs');
    j = j + 1;
end
end

% =========================================================================
% Subfunction to get onset/offset
function [on, off, ratidx] = getonoff(metadatatable, ratname)

% Get rows corresponding to the rat
ratidx = find(strcmpi(metadatatable.Rat, ratname));

% Get beginning and enf of time windows
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
function [choice, outcome, tsidepoke, rtside, rtcenter] = getdecisionlabels(states, events, protocol)

% Decisions
% ~~~~~~~~~

% Define detection variable
sideports  = [1 3];
centerport = 2;
correct    = arrayfun(@(x) sprintf('Correct%i',    x), sideports, 'uni', 0);
error      = arrayfun(@(x) sprintf('Error%i',      x), sideports, 'uni', 0);
early      = arrayfun(@(x) sprintf('EarlyEnter%i', x), sideports, 'uni', 0);
fun        = @(x,y) any(~isnan([x, y]));

% Get boolean categories
isleft    = fun(states.(correct{1}), states.(error{1}));
isright   = fun(states.(correct{2}), states.(error{2}));
iscorrect = fun(states.(correct{1}), states.(correct{2}));
global fixationver;
if contains(protocol, fixationver)
    isbrokenfix  = fun(states.('BrokenFixation'), []);
    isleftearly  = false;
    isrightearly = false;
    isearly      = false;
    possresp     = [correct, error];
    isomitted    = all(cellfun(@(x) all(isnan(states.(x))), [possresp, 'BrokenFixation']));
else % v1/v2 protocol
    isbrokenfix  = false;
    isleftearly  = fun(states.(early{1}), []);
    isrightearly = fun(states.(early{2}), []);
    isearly      = isleftearly | isrightearly;
    possresp     = [correct, error, early];
    isomitted    = all(cellfun(@(x) all(isnan(states.(x))), possresp));
end

% Determine choice label
if isleft,       choice = 'left';       end
if isright,      choice = 'right';      end
if isbrokenfix,  choice = 'brokenfix';  end
if isleftearly,  choice = 'earlyleft';  end
if isrightearly, choice = 'earlyright'; end
if isomitted,    choice = 'omission';   end

% Determine outcome label
if  iscorrect,   outcome = 'correct';   end
if ~iscorrect,   outcome = 'error';     end
if  isbrokenfix, outcome = 'brokenfix'; end
if  isearly,     outcome = 'early';     end
if  isomitted,   outcome = 'omission';  end

% Reaction times
% ~~~~~~~~~~~~~~

% Get timing of the side cue
f = fieldnames(states);
i = strcmpi(f, 'SideCue') | strcmpi(f, 'DecisionCue') | strcmpi(f, 'WaitForPoke');
tsidecue = cellfun(@(x) states.(x)(1), f(i));
tsidecue = tsidecue(~isnan(tsidecue));
if isempty(tsidecue), tsidecue = NaN; end 

% Get timing of decision poke
tsidepoke = cellfun(@(x) states.(x)(1), possresp);
tsidepoke = tsidepoke(~isnan(tsidepoke));
if isempty(tsidepoke), tsidepoke = NaN; end

% Compute reaction time as the different between 
rtside = tsidepoke - tsidecue;

% For the 3rd/4th versions of the protocol, we can measure RT as the timing
% at which the central port is left
cportname = sprintf('Port%iOut', centerport);
rtcenter = NaN;
if contains(protocol, fixationver)
    if isfield(events, cportname) && ...          % center poke out detected
       all(~isnan(states.FixationMaintenance(:))) % stage with fixation
        
        % Get last port out event between side port available and side poke
        to = events.(cportname);
        lastto = max(to(to >= tsidecue & to <= tsidepoke));
        
        % If empty that means center port was left before, which may indicate a
        % broken fixation immediately after side cue occurence
        if isempty(lastto), lastto = max(to(to <= tsidecue)); end
        
        % Now express relative to side cue onset as for the other reaction time
        rtcenter = lastto - tsidecue;
    end
end

end

% =========================================================================
function [begtrl, begctr, it, prdtrl, isday] = getinittimes(settings, states, protocol)

% In v3-6 of the protocol
global fixationver;
if contains(protocol, fixationver)
    
    % Get the trial start time (single state machine)
    begtrl = settings.InitTimeTrial;
    
    % Determine the duration of the initation cue state
    f = fieldnames(states);
    fi = contains(f, 'InitiationCue');
    if any(fi)
        f = f{fi};
        it = states.(f)(end);
    else, it = 0;
    end
    
    % The trial initiation time it the starting time plus the initiation
    % cue duration
    begctr = begtrl + seconds(it);
    
    % Paired trial time label corresponds to the trial start time
    prdtrl = begtrl;
    
% In v1 and v2 of the protocol, separate state machines are sent for the
% center poke waiting and trial presentation period
else
    
    % 1st state machine => center poke => 2nd state machine
    begtrl = settings.InitTimeFixation;
    begctr = settings.InitTimeTrial;
    
    % Difference between these two timestamps gives initiation times
    it = seconds(begctr - begtrl);
    
    % Paired trial time label corresponds to 2nd state machine
    prdtrl = begctr;
end

% If trial was scheduled during day/night but completed during night/day
% (respectively), we flag it appropriately for future rejection
dayon   = timeofday(datetime('07:30', 'InputFormat', 'HH:mm'));
nighton = timeofday(datetime('19:30', 'InputFormat', 'HH:mm'));
day2night_trans = timeofday(begtrl) < nighton && timeofday(begctr) > nighton;
night2day_trans = timeofday(begtrl) < dayon   && timeofday(begctr) > dayon;
if day2night_trans || night2day_trans, isday = -10;
else, isday = settings.IsDay;
end

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
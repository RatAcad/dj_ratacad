function T = dj_uncertainflashinference_summarytable(trialtable, cond)
% This function returns the summary table (day- or stage-specific) from the
% trial table generated by the dj_uncertainflashinference_trialtable
% function.
% 
% Maxime Maheu <maheu.mp@gmail.com> | 2024

% Turn into table for easier indexing
trialtable = struct2table(trialtable);

% Divide between two summary tables
switch cond
    
    % Split according to stages
    case 'stage'
        levels = num2cell(unique(trialtable.stage));
        idx = cellfun(@(x) trialtable.stage == x, levels, 'uni', 0);
        
    % Split according to days
    case 'day'
        
        % For nights, we put together late hour trials of day i with early
        % hour trials of day i+1 (instead of both early and late hours of day i)
        % N.B. in practice, morning night are labelled as belonging to yesterday
        dayStartTime  = hours(07) + minutes(30); % 7:30 AM
        dateTimeList  = datetime(trialtable.trial_datetime);
        baseDates     = dateshift(dateTimeList, 'start', 'day');
        timeOfDay     = timeofday(dateTimeList);
        adjustedDates = baseDates;
        adjustedDates(timeOfDay < dayStartTime) = adjustedDates(timeOfDay < dayStartTime) - days(1);
        
        % Get trial indices for each day after the transformation
        levels = arrayfun(@(x) char(datetime(x, 'Format', 'yyyy-MM-dd')), unique(adjustedDates), 'uni', 0);
        idx = cellfun(@(x) contains(trialtable.trial_datetime, x), levels, 'uni', 0);
end

% Loop over stages/days
N = numel(idx);
T = struct;
k = 1;
for i = 1:N
    for j = [1,0] % separately for day vs. night
        
        % Get trial indices
        trli = idx{i} & (trialtable.isday == j);
        cmpi = contains(trialtable.outcome, 'correct') | contains(trialtable.outcome, 'error');
        
        % Build table
        if sum(trli & cmpi) > 0
            T(k).name          = trialtable.name{1};
            T(k).(cond)        = levels{i};
            T(k).isday         = j;
            % -----------------------------------------------------------------
            T(k).trials        = sum(trli);
            T(k).reward_rate   = mean(contains(trialtable.outcome(trli), 'correct'));
            T(k).accuracy      = mean(contains(trialtable.outcome(trli & cmpi), 'correct')); % completed trials
            T(k).p_right       = mean(contains(trialtable.choice(trli & cmpi), 'right')); % completed trials
            T(k).omission_rate = mean(contains(trialtable.outcome(trli), 'omission'));
            T(k).early_rate    = mean(contains(trialtable.outcome(trli), 'early'));
            T(k).rt            = median(trialtable.rt(trli & cmpi)); % completed trials
            T(k).init          = median(trialtable.init_time(trli & cmpi)); % completed trials
            k = k + 1;
        end
    end
end
end
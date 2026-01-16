function varargout = dj_uncertainflashinference_metadata
% This function loads meta-data manually annoted by the experimenter
% specifying segments of bad data (e.g. due to box malfunction). The
% meta-data is manually added to a Google Sheets which this function reads.
% 
% Maxime Maheu <maheu.mp@gmail.com> | 2024

% Define properties of the meta-data sheet
code   = '2PACX-1vSvzAAvw_wZnhjZ3yNAYowx2yyWw4EBfgGtAP3ANvShjDQmTlWZVPxkDUS6UkGsvKK1TaMc0JB1XLfc';
tabid  = [0, 1782685558, 560237878, 1642303063];
format = {'dd-MMM-yyyy', 'dd-MMM-yyyy HH:mm', 'yyyyMMdd', 'yyyyMMdd'};

% Specify URL completion function
urlfun = @(i) sprintf('https://docs.google.com/spreadsheets/d/e/%s/pub?gid=%i&single=true&output=csv', ...
    code, tabid(i));

% Loop over first two tabs (labels)
varargout = cell(1,3);
for i = 1:2
    
    % Detect import options from the URL
    X = readgooglesheet(urlfun(i));
    
    % Convert to table
    T = cell2table(X(2:end,:));
    T.Properties.VariableNames = X(1,:);
    
    % Format
    T.Beginning = datetime(T.Beginning, 'Format', format{i});
    T.End = datetime(T.End, 'Format', format{i});
    varargout{i} = T;
end

% Loop over next two tabs (injections)
for i = 3:numel(tabid)
    
    % Detect import options from the URL
    T = readgooglesheet(urlfun(i));
    
    % Build date x rat injection table
    ratid = T(1,2:end);
    dates = T(8:end,1);
    dates = cellfun(@(x) [x, '/26'], dates, 'uni', 0);
    dates = cellfun(@(x) datetime(x, 'Format', 'eeee MM/dd/yy'), dates, 'uni', 0);
    dates = cellfun(@(x) char(x, format{i}), dates, 'uni', 0);
    injections = T(8:end,2:end);
    injections(cellfun(@isempty, injections)) = {'None'};
    varargout{i} = array2table(injections, 'VariableNames', ratid, 'RowNames', dates);
end
varargout{3} = varargout(3:end);

end

% =========================================================================
% Subfunction to read Google Sheet and return a formatted table
function T = readgooglesheet(url)

% Read data as text
T = urlread(url);

% Organise in rows and columns
T = textscan(T, '%s', 'Delimiter', '\n');
T = cellfun(@(x) textscan(x, '%s', 'Delimiter', ','), T{1}, 'uni', 0);
T = cellfun(@(x) x{1}, T, 'uni', 0);
numcells = cellfun(@numel, T);
maxcells = max(numcells);
T(numcells ~= maxcells) = cellfun(@(x) [x; {''}], T(numcells ~= maxcells), 'uni', 0);
T = [T{:}]';

end
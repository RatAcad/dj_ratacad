function varargout = dj_uncertainflashinference_metadata
% This function loads meta-data manually annoted by the experimenter
% specifying segments of bad data (e.g. due to box malfunction). The
% meta-data is manually added to a Google Sheets which this function reads.
% 
% Maxime Maheu <maheu.mp@gmail.com> | 2024

% Define properties of the meta-data sheet
code   = '2PACX-1vSvzAAvw_wZnhjZ3yNAYowx2yyWw4EBfgGtAP3ANvShjDQmTlWZVPxkDUS6UkGsvKK1TaMc0JB1XLfc';
tabid  = [0, 1782685558];
format = {'dd-MMM-yyyy', 'dd-MMM-yyyy HH:mm'};

% Loop over both tabs
varargout = cell(1,2);
for i = 1:2
    
    % Detect import options from the URL
    url = sprintf('https://docs.google.com/spreadsheets/d/e/%s/pub?gid=%i&single=true&output=csv', code, tabid(i));
    varargout{i} = readgooglesheet(url, format{i});
end

end

% =========================================================================
% Subfunction to read Google Sheet and return a formatted table
function T = readgooglesheet(url, dtformat)

% Read data as text
metadata = urlread(url);

% Organise in rows and columns
metadata = textscan(metadata, '%s', 'Delimiter', '\n');
metadata = cellfun(@(x) textscan(x, '%s', 'Delimiter', ','), metadata{1}, 'uni', 0);
metadata = cellfun(@(x) x{1}, metadata, 'uni', 0);
metadata = [metadata{:}]';

% Convert to table
T = cell2table(metadata(2:end,:));
T.Properties.VariableNames = metadata(1,:);

% Format
T.Beginning = datetime(T.Beginning, 'Format', dtformat);
T.End = datetime(T.End, 'Format', dtformat);

end
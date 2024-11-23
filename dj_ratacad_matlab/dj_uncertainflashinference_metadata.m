function varargout = dj_uncertainflashinference_metadata
% This function loads meta-data manually annoted by the experimenter
% specifying segments of bad data (e.g. due to box malfunction). The
% meta-data is manually added to a Google Sheets which this function reads.
% 
% Maxime Maheu <maheu.mp@gmail.com> | 2024

% Define properties of the meta-data sheet
code  = '2PACX-1vSvzAAvw_wZnhjZ3yNAYowx2yyWw4EBfgGtAP3ANvShjDQmTlWZVPxkDUS6UkGsvKK1TaMc0JB1XLfc';
tabid = [0, 1782685558];

% Loop over both tabs
varargout = cell(1,2);
for i = 1:2
    
    % Detect import options from the URL
    url = sprintf('https://docs.google.com/spreadsheets/d/e/%s/pub?gid=%i&single=true&output=csv', code, tabid(i));
    opts = detectImportOptions(url);
    
    % Customize import options
    opts.Delimiter = ',';
    opts.DataLines = [2, Inf];
    for j = 1:numel(opts.VariableNames), opts.VariableTypes{j} = 'string'; end
    datelab = {'Beginning', 'End'};
    for j = 1:numel(datelab)
        k = strcmpi(opts.VariableNames, datelab{j});
        opts.VariableTypes{k} = 'datetime';
        opts = setvaropts(opts, datelab{j}, 'InputFormat', 'dd-MMM-yyyy HH:mm');
    end
    
    % Import data
    varargout{i} = readtable(url, opts);
end
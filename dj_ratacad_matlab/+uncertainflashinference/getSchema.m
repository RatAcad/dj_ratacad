function obj = getSchema
persistent OBJ
if isempty(OBJ)
    OBJ = dj.Schema(dj.conn, 'uncertainflashinference', 'scott_uncertainflashinference');
end
obj = OBJ;
end
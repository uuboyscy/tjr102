local common = import 'common.libsonnet';
local table = import 'table.libsonnet';
local mode = 'insert';
local date_suffix = '_${EXECUTION_DATE}';

local table_name = std.extVar('table');
local tmp_table_name = 'tmp.' + table_name + date_suffix;

local normal_file_name = '/data/raw/' + table_name + '/${LOAD_TYPE}/' + table[table_name].filename + date_suffix + '.csv';
local ref_file_name = '/data/raw/' + table_name + '/${LOAD_TYPE}/' + table[table_name].filename + '.csv';
local ref_keyword = 'ref';
local filename_has_date = if std.objectHas(table[table_name], 'filename_has_date') && table[table_name].filename_has_date then true else false;
local filename_hasnt_date = if std.objectHas(table[table_name], 'filename_has_date') && !table[table_name].filename_has_date then true else false;

local has_mode = if std.objectHas(table[table_name], 'mode') then true else false;
local is_ref = if std.length(std.findSubstr(ref_keyword, table_name)) > 0 then true else has_mode && table[table_name].mode == 'ref';
local is_merge = has_mode && table[table_name].mode == 'merge';

local name_with_date = if filename_hasnt_date then false else (if (is_ref && !is_merge && !filename_has_date) then false else true);
local file_name = if !name_with_date then ref_file_name else normal_file_name;

local match_columns = if std.objectHas(table[table_name], 'match_columns') then table[table_name].match_columns else [];
local update_columns = if std.objectHas(table[table_name], 'update_columns') then table[table_name].update_columns else [];


local output_table = 'tmp.' + table_name + if !name_with_date then '' else date_suffix;
local staging_table = table_name + if !name_with_date then '' else date_suffix;

local delimiter = if std.objectHas(table[table_name], 'delimiter') then table[table_name].delimiter else ',';
local header = if std.objectHas(table[table_name], 'header') then table[table_name].header else false;
local null_as = if std.objectHas(table[table_name], 'null_as') then table[table_name].null_as else '';

{
  VERSION: common['VERSION'],
  DATABASE: common['DATABASE'],
  USER: common['USER'],
  HOST: common['HOST'],
  PORT: common['PORT'],
  GPLOAD: {
    INPUT: [
      {
        SOURCE: {
          LOCAL_HOSTNAME: common['LOCAL_HOSTNAME'],
          PORT: table[table_name].gpfdist_port,
          FILE: [
            file_name
          ],
        },
      },
      { FORMAT: 'CSV' },
      { DELIMITER: delimiter },
      { HEADER: header },
      { NULL_AS: null_as },
      { COLUMNS: table[table_name].schema },
    ],
    EXTERNAL: [{ SCHEMA: 'ext' }],
    OUTPUT: [{ TABLE: output_table }, { MODE: mode }, { MATCH_COLUMNS: match_columns }, { UPDATE_COLUMNS: update_columns },],
    PRELOAD: [{ REUSE_TABLES: true }, { STAGING_TABLE: staging_table }, { TRUNCATE: true },],
    SQL: [{
      // BEFORE: ''
      // AFTER: ''
    },]
  },
}

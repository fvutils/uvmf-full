from command_helper import *
import os
import sys

# Command to run Covercheck analysis
def generate_command(v=None):
  cc_cmd_str = ''
  if v['directives_file'] != '':
    cc_cmd_str = cc_cmd_str + 'do '+v['directives_file'] + ';'
  if os.path.isfile(v['build_dir']+os.path.sep+'modelsim.ini'):
    modelsim_ini_str = '-modelsimini '+v['build_dir']+'/modelsim.ini'
  else:
    modelsim_ini_str = ''
  if v['init_file']:
    init_cmd_str = '-init '+v['init_file']
  else:
    init_cmd_str = ''
  cc_cmd_str = cc_cmd_str + 'covercheck compile -work '+v['lib']+' '+modelsim_ini_str+' -d '+v['top']+' '+v['compile_extra']+';'
  if v['ucdb_filename']:
    if not os.path.exists(v['ucdb_filename']):
      logger.error("UCDB file \"{}\" for CoverCheck run does not exist".format(v['ucdb_filename']))
      sys.exit(1)
    cc_cmd_str = cc_cmd_str + 'covercheck load ucdb '+v['ucdb_filename']+';'
  cc_cmd_str = cc_cmd_str + 'covercheck verify -timeout '+v['timeout']+' '+init_cmd_str+' '+v['verify_extra']+';'
  cc_cmd_str = cc_cmd_str + 'covercheck generate exclude covercheck_exclude.do;'
  cc_cmd_str = cc_cmd_str + 'exit'
  return [ clean_whitespace('qverify -c -od covercheck_results -do \"{}\"'.format(cc_cmd_str))]

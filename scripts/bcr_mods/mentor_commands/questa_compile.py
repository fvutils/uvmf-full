from command_helper import *
import os

# Invoke compile operations for Questa. Verilog (vlog) first, then VHDL (vcom)
def generate_command(v=None):
  if 'using_qvip':
    mvc_switch = '-timescale 1ps/1ps'
  else:
    mvc_switch = ''
  cmds = []
  # Verilog/SV and C are compiled with vlog
  vlog_flist_str = filelists(val=v['filelists'],assoc='vlog')+" "+filelists(v['filelists'],assoc='c')
  # VHDL compiled with vcom
  vhdl_flist_str = filelists(val=v['filelists'],assoc='vhdl')
  arch_str = ''
  if v['use_64_bit']:
    arch_str = '-64'
  suppress_str = ''
  if v['suppress']:
    suppress_str = "-suppress "+v['suppress']
  modelsimini_str = ''
  if v['modelsimini']:
    modelsimini_str = '-modelsimini '+v['modelsimini']
  cmds = []
  if v['mappings'] != '':
    # Expect this to be sets of <logical_name>:<physical_name> pair strings separated by spaces
    for m in library_mappings(v['mappings']):
      cmds.append(clean_whitespace('vmap {} {} {}'.format(m[0],m[1],modelsimini_str)))
    modelsimini_str = ""  ## Clear this if a modelsim.ini file was pointed to along with vmap commands
  if vlog_flist_str != '':
    cmds.append(clean_whitespace("vlog {} {} {} {} {} {} {} -l {}".format(vlog_flist_str,arch_str,modelsimini_str,v['vlog_switches'],v['vlog_extra'],mvc_switch,suppress_str,v['vlog_log_filename'])))
  if vhdl_flist_str != '':
    cmds.append(clean_whitespace("vcom {} {} {} {} {} {} -l {}".format(vhdl_flist_str,arch_str,modelsimini_str,v['vcom_switches'],v['vcom_extra'],suppress_str,v['vlog_log_filename'])))
  return cmds



from command_helper import *

# Command to build the HDL side of a Veloce setup
# This will include the velanalyze commands and velcomp
def generate_command(v=None):
  cmds = []
  hdl_vhdl_flist_str = filelists(v['filelists'],assoc='vhdl',patt=r'.*hdl_vhdl.*')
  hdl_vlog_flist_str = filelists(v['filelists'],assoc='vlog',patt=r'.*hdl_vlog.*')
  hvl_vhdl_flist_str = filelists(v['filelists'],assoc='vhdl',patt=r'.*hvl_vhdl.*')
  hvl_vlog_flist_str = filelists(v['filelists'],assoc='vlog',patt=r'.*hvl_vlog.*')

  # HVL analysis
  # Special velanalyze -extract_hvl_info command to compile UVM package
  cmds.append(clean_whitespace("velanalyze -sv {} -extract_hvl_info +incdir+{} +define+QUESTA {}/uvm_pkg.sv {}".format(v['velanalyze_vlog_switches'],v['uvm_src_path'],v['uvm_src_path'],v['velanalyze_vlog_extra'])))
  # hvl_vlog.qf gets passed into velanalyze using -extract_hvl_info
  if hvl_vlog_flist_str:
    cmds.append(clean_whitespace("velanalyze -sv {} -extract_hvl_info +incdir+{} {} {}".format(v['velanalyze_vlog_switches'],v['uvm_src_path'],hvl_vlog_flist_str,v['velanalyze_vlog_extra'])))
  # hvl_vhdl.qf as well (if it exists)
  if hvl_vhdl_flist_str:
    cmds.append(clean_whitespace("velanalyze -hdl vhdl {} -extract_hvl_info +incdir+{} {} {}".format(v['velanalyze_vhdl_switches'],v['uvm_src_path'],hvl_vhdl_flist_str,v['velanalyze_vhdl_extra'])))

  # HDL analysis
  # hdl_vhdl.qf gets passed into velanalyze with VHDL setting
  if hdl_vhdl_flist_str:
    cmds.append(clean_whitespace("velanalyze -hdl vhdl {} {} {}".format(hdl_vhdl_flist_str,v['velanalyze_vhdl_switches'],v['velanalyze_vhdl_extra'])))
  # hdl_vlog.qf gets passed into velanalyze with Verilog setting
  if hdl_vlog_flist_str:
    cmds.append(clean_whitespace("velanalyze -sv {} {} {}".format(hdl_vlog_flist_str,v['velanalyze_vlog_switches'],v['velanalyze_vlog_extra'])))
  

  # Velcomp
  cmds.append(clean_whitespace("velcomp -top hdl_top {} {}".format(v['velcomp_switches'],v['velcomp_extra'])))

  return cmds

from command_helper import *
import os

# Invoke vsim 
def generate_command(v=None):
  if 'using_qvip' in v and v['using_qvip']:
    if 'QUESTA_MVC_HOME' not in os.environ:
      logger.error("using_qvip set True but $$QUESTA_MVC_HOME not set")
      sys.exit(1)
    mvc_switch = '-t 1ps -mvchome '+os.environ['QUESTA_MVC_HOME']
  else:
    mvc_switch = ''
  if 'error_limit' in v and (v['error_limit'] > 0):
    msglimit_str = '-msglimit error -msglimitcount '+str(v['error_limit'])
  else:
    msglimit_str = ''
  if 'code_coverage_enable' in v and v['code_coverage_enable']:
    coverage_run_str = '-coverage'
  else:
    coverage_run_str = ''
  if 'verbosity' in v and v['verbosity'] != '':
    verbosity_str = '+UVM_VERBOSOITY='+v['verbosity']
  else:
    verbosity_str = ''
  lib_str = ''
  if 'lib' in v and v['lib']:
    lib_str = '-lib '+v['lib']
  arch_str = ''
  if v['use_64_bit']:
    arch_str = '-64'
  if v['live']:
    mode_str = '-gui'
    run_cmd = 'run 0'
    debug_str = '-onfinish stop -classdebug'
    if not(v['use_vis'] or v['use_vis_uvm']):
      debug_str = debug_str + ' -uvmcontrol=all -msgmode both'
    ## For live sim, turn on transaction logging by default unless explicitly asked to have it off (set to False)
    if v['enable_trlog'] == '':
      v['enable_trlog'] = True
  else:
    mode_str = v['mode']
    run_cmd = 'run -all'
    debug_str = ''
  if v['use_vis'] or v['use_vis_uvm']:
    if v['vis_wave']:
      vis_wave_str = "-qwavedb="+v['vis_wave']
    elif v['use_vis_uvm']:
      vis_wave_str = "-qwavedb="+v['vis_wave_tb']
    else:
      vis_wave_str = "-qwavedb="+v['vis_wave_rtl']
    if v['enable_trlog']:
      vis_wave_str = vis_wave_str+"+transaction"
  else:
    vis_wave_str = ""
  if v['enable_trlog']:
    trlog_str = "+uvm_set_config_int=*,enable_transaction_viewing,1"
  else:
    trlog_str = ''
  if v['run_command']:
    run_command = v['run_command']
  elif v['live']:
    run_command = 'run 0'
    if v['use_vis_uvm'] or v['use_vis']:
      run_command = run_command+"; do viswave.do"
    else:
      run_command = run_command+"; do wave.do"
    quit_command = ''
  else:
    run_command = "run -a"
    if v['quit_command']:
      quit_command = v['quit_command']
    else:
      quit_command = 'quit'
  do_str = ''
  for i in [v['extra_pre_do'],v['pre_do'],v['extra_do'],run_command,v['post_do'],quit_command]:
    if i: 
      do_str = do_str + i + ';'
  full_do_str = ''
  if do_str:
    full_do_str = '-do \"'+do_str+'\"'
  suppress_str = ''
  if v['suppress']:
    suppress_str = "-suppress "+v['suppress']
  modelsimini_str = ''
  if v['modelsimini']:
    modelsimini_str = '-modelsimini '+v['modelsimini']
  return [clean_whitespace("vsim {} {} {} -l {} -solvefaildebug +UVM_NO_RELNOTES \
            -sv_seed {} {} {} {} +notimingchecks +UVM_TESTNAME={} {} {} {} {}  {} {} {} {} \
            -stats=perf {} {} -permit_unmatched_virtual_intf".format(
    arch_str,
    mode_str,
    v['tops'],
    v['log_filename'],
    str(v['seed']),
    msglimit_str,
    coverage_run_str,
    lib_str,
    v['test'],
    verbosity_str,
    v['extra'],
    v['switches'],
    mvc_switch,
    debug_str,
    vis_wave_str,
    trlog_str,
    full_do_str,
    suppress_str,
    modelsimini_str,
    ))]



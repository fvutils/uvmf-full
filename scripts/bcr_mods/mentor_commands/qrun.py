from command_helper import *
import os

# Command to run a simulation using qrun
def generate_command(v=None):
  if 'filelists' in v:
    ## This could return a simple string of "-f" switches or a dict of strings depending on what is passed into it.
    ## If a list is passed in it returns a simple string.
    ## If a dict is passed in then it means we have library associations that will need to be handled further down
    ## and the return value will also be a dict, one string for each desired library.
    ret = filelists(v['filelists'])
  else:
    ret = ''
  if isinstance(ret,str):
    filelist_str = ret
  else:
    filelist_str = ''
    for l in v['liborder']:
      filelist_str = filelist_str + ' -makelib ' + l + ' ' + ret[l] + ' -endlib ' + ' -L ' + l   ## Why do we need a -L here?
    if '__default__' in ret:
      filelist_str = filelist_str + ret['__default__']
  pdu_str = ''
  if 'pdu' in v and v['pdu']:
    for p in v['pdu'].split(' '):
      pdu_str = pdu_str + ' -makepdu ' + p.replace('.','_') + "_pdu" + ' ' + p + ' -end'  
  if 'using_qvip' in v and v['using_qvip']:
    if 'QUESTA_MVC_HOME' not in os.environ:
      logger.error("using_qvip set True but $$QUESTA_MVC_HOME not set")
      sys.exit(1)
    mvc_switch = '-t 1ps -timescale 1ps/1ps -mvchome '+os.environ['QUESTA_MVC_HOME']
  else:
    mvc_switch = ''
  if 'code_coverage_enable' in v and v['code_coverage_enable']:
    try: coverage_build_str = '+cover='+v['code_coverage_types']+'+'+v['code_coverage_target']
    except KeyError:
      logger.error("Unable to enable code coverage, types and/or target are undefined")
      sys.exit(1)
    coverage_run_str = '-coverage'
  else:
    coverage_run_str = ''
    coverage_build_str = ''
  arch_str = ''
  if 'use_64_bit' in v and v['use_64_bit']:
    arch_str = '-64'
  outdir_str = ''
  if 'outdir' in v and v['outdir'] != '':
    outdir_str = '-outdir '+v['outdir']
  if 'verbosity' in v and v['verbosity'] != '':
    verbosity_str = '+UVM_VERBOSOITY='+v['verbosity']
  else:
    verbosity_str = ''
  if 'build_only' in v and v['build_only']:
    v['do'] = ''
    coverage_run_str = ''
    flow_control = '-optimize'
  elif 'compile_only' in v and v['compile_only']:
    v['do'] = ''
    coverage_run_str = ''
    coverage_build_str = ''
    flow_control = '-compile'
  elif 'sim_only' in v and v['sim_only']:
    filelist_str = ''
    coverage_build_str = ''
    flow_control = '-simulate'
  else:
    flow_control = ''
  if 'error_limit' in v and (v['error_limit'] > 0):
    msglimit_str = '-msglimit error -msglimitcount '+str(v['error_limit'])
  else:
    msglimit_str = ''
  # Determine flow (-batch, -gui, -c)
  # If v['live'] then set to -gui. Otherwise use v['mode']
  if v['live']:
    mode_str = '-gui'
    # In live mode, only run through time 0
    run_cmd = 'run 0'
    # Other command-line stuff for live simulation
    debug_str = '-onfinish stop -classdebug'
    if not (v['use_vis'] or v['use_vis_uvm']):
      debug_str = debug_str + ' -uvmcontrol=all -msgmode both'
    ## For live sim, turn on transaction logging by default unless explicitly asked to have it off (set to False)
    if v['enable_trlog'] == '':
      v['enable_trlog'] = True
  else:
    mode_str = v['mode']
    # In batch mode, run simulation entirely
    run_cmd = 'run -all'
    debug_str = ''
  # Determine options to use for wave dumping & debug
  # Use v['use_vis'] and v['use_vis_uvm'] for this. If neither are set, then no -qwave, -debug, -designfile switches
  # Otherwise, set -debug and -designfile. Content of -qwavedb dependent on how those two v are set, plus v['vis_wave']
  # If 'vis_wave' is specified use it to populate -qwavedb option. Otherwise, pull from 'vis_wave_rtl' or 'vis_wave_tb' if 'use_vis' or 'use_vis_uvm' are 
  # specified, respectively.
  if v['use_vis'] or v['use_vis_uvm']:
    vis_args_str = "-visualizer -designfile "+v['vis_design_filename']
    if v['live']:
      vis_args_str = vis_args_str+" -debug,livesim"
    else:
      vis_args_str = vis_args_str+" -debug"
    if v['access']:
      vis_args_str = vis_args_str+" "+v['access']
    if v['vis_wave']:
      vis_wave_str = "-qwavedb="+v['vis_wave']
    elif v['use_vis_uvm']:
      vis_wave_str = "-qwavedb="+v['vis_wave_tb']
    else:
      vis_wave_str = "-qwavedb="+v['vis_wave_rtl']
    if v['enable_trlog']:
      vis_wave_str = vis_wave_str+"+transaction"
    if v['vis_wave_filename']:
      vis_wave_str = vis_wave_str+"+wavefile="+v['vis_wave_filename']
  else:
    vis_args_str = ""
    vis_wave_str = ""
  # Enable transaction logging if requested
  if v['enable_trlog']:
    trlog_str = "+uvm_set_config_int=*,enable_transaction_viewing,1"
  else:
    trlog_str = ''
  # Build up the dofile command set
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
    run_command = 'run -a'
    if v['quit_command']:
      quit_command = v['quit_command']
    else:
      quit_command = 'quit'
  do_str = ''
  for dv in [v['extra_pre_do'],v['pre_do'],v['extra_do'],run_command,v['post_do'],quit_command]:
    if dv: 
      do_str = do_str + dv + ';'
  full_do_str = ''
  if do_str:
    full_do_str = '-do \"'+do_str+'\"'
  lib_str = ''
  for l in v['lib'].split(' '):
    if l: 
      lib_str = lib_str + '-L '+l
  suppress_str = ''
  if v['suppress']:
    suppress_str = "-suppress "+v['suppress']
  modelsimini_str = ''
  if v['modelsimini']:
    modelsimini_str = '-modelsimini '+v['modelsimini']
  script_str = ''
  if 'gen_script' in v and v['gen_script']:
    script_str = '-script qrun_script'
  top_str = ''
  if 'tops' in v and v['tops']:
    for t in v['tops'].split(' '):
      top_str = top_str + ' -top '+t
  cmds = []
  if v['mappings'] != '':
    # Expect this to be sets of <logical_name>:<physical_name> pair strings separated by spaces
    for m in library_mappings(v['mappings']):
      cmds.append(clean_whitespace('vmap {} {} {}'.format(m[0],m[1],modelsimini_str)))
    modelsimini_str = ""  ## Clear this if a modelsim.ini file was pointed to along with vmap commands
  cmds.append(clean_whitespace('qrun {} {} {} {} -l {} {} {} -solvefaildebug +UVM_NO_RELNOTES \
            -sv_seed {} {} {} {} +notimingchecks +UVM_TESTNAME={} {} {} {} {} {} {} {} {} {} {} {} {}\
            -stats=perf {} {} -permit_unmatched_virtual_intf'.format(
    mode_str,
    arch_str,
    flow_control,
    outdir_str,
    v['log_filename'],
    filelist_str,
    pdu_str,
    str(v['seed']),
    msglimit_str,
    coverage_run_str,
    coverage_build_str,
    v['test'],
    verbosity_str,
    v['extra'],
    v['switches'],
    mvc_switch,
    debug_str,
    full_do_str,
    vis_args_str,
    vis_wave_str,
    trlog_str,
    lib_str,
    script_str,
    top_str,
    suppress_str,
    modelsimini_str,
    )) )

  return cmds

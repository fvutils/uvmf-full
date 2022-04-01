from command_helper import *
import os

# Invoke vopt
def generate_command(v=None):
  cmds = []
  if v['use_vis'] or v['use_vis_uvm']:
    vis_args_str = "-designfile "+v['vis_design_filename']
    if v['live']:
      vis_args_str = vis_args_str+" -debug,livesim"
    else:
      vis_args_str = vis_args_str+" -debug"
    if 'access' in v:
      vis_args_str = vis_args_str+" "+v['access']
  else:
    if v['live']:
      vis_args_str = "+acc"
    else:
      vis_args_str = ''
  lib_str = ''
  for l in v['lib'].split(' '):
    if l: 
      lib_str = lib_str + '-L '+l
  work_str = ''
  if 'work' in v:
    work_str = '-work '+v['work']
  arch_str = ''
  if v['use_64_bit']:
    arch_str = '-64'
  modelsimini_str = ''
  if v['modelsimini']:
    modelsimini_str = '-modelsimini '+v['modelsimini']
  suppress_str = ''
  if v['suppress']:
    suppress_str = "-suppress "+v['suppress']
  cmds.append(clean_whitespace("vopt {} {} {} -o {} {} {} {} {} {} -l {}".format(arch_str,v['tops'],work_str,v['out'],vis_args_str,v['extra'],modelsimini_str,suppress_str,lib_str,v['log_filename'])))
  return cmds



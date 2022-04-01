from command_helper import *
import os

# Invoke visualizer
def generate_command(v=None):
  if 'wavefile' in v:
    wavefile_str = "-wavefile "+v['wavefile']
  else:
    wavefile_str = ""
  if 'formatfile' in v:
    dofile_str = "-do "+v['formatfile']
  else:
    dofile_str = ""
  return [ clean_whitespace('vis -designfile {} {} {} {}'.format(
    v['designfile'],
    wavefile_str,
    dofile_str,
    v['extra'],
  )) ]

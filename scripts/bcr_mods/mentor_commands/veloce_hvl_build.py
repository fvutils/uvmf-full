from command_helper import *
import os
import importlib
import sys

# Command to build the HVL side of a Veloce setup
# This will include the Questa compile (vlog/vcom), the velhvl command, and the vopt command
def generate_command(v=None):
  cmds = []
  # Figure out the current package, we need to use others in same package to define sub-commands
  package_name = vars(sys.modules[__name__])['__package__']
  # Use the questa compile module to carry out the vlog/vcom commands
  questa_compile_module = importlib.import_module('.questa_compile',package_name)
  cmds = questa_compile_module.generate_command(v)
  cmds.append(clean_whitespace("velhvl {} {}".format(v['velhvl_switches'],v['velhvl_extra'])))
  # Use the vopt compile module to run vopt
  vopt_module = importlib.import_module('.vopt',package_name)
  v['extra'] = v['vopt_extra']
  cmds = cmds + vopt_module.generate_command(v)
  return cmds



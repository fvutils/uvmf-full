from command_helper import *
import os
import sys
import shutil
import glob

# Command to clean a simulation directory
def generate_command(v=None):
  globstr = '*~ *.ucdb vsim.dbg *.vstf *.log work *.mem *.transcript.txt certe_dump.xml \
     *.wlf transcript covhtmlreport VRMDATA design.bin *.so *.dll qwave.db *.dbg dpiheader.h visualizer*.ses \
     vrmhtmlreport veloce.med veloce.wave tbxbindings.h edsenv sv_connect.* \
     *.o *.so covercheck_results qrun.out *.qf *.vf infact_genfiles'
  if 'realclean' in v and v['realclean']:
    globstr = globstr + ' modelsim.ini'
  logger.info("Cleaning up working directory...")
  try:
    for gl in globstr.split(' '):
      for fp in glob.glob(gl):
        if os.path.isfile(fp): 
          os.remove(fp)
        else: 
          shutil.rmtree(fp)
  except:
    logger.error("Error detected during cleanup")
    sys.exit(1)
  return []



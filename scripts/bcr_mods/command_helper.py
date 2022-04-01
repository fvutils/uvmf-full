import logging
import pprint
import re

__all__ = ['logger','generate_command','vars_string','clean_whitespace','filelists','library_mappings']

logger = logging.getLogger("logger")
pprinter = pprint.PrettyPrinter(indent=2)

def generate_command(self,vars=None):
  logger.error("generate_command was left undefined")
  sys.exit(1)

def vars_string(vars=None):
  ret = ""
  for name,value in vars.items():
    ret = ret + "\n  {}:{}".format(name,value)
  return ret

def clean_whitespace(val):
  return re.sub(r"\s+"," ",val)

def filelists(val,assoc=None,patt=None):
  ret = {}
  if patt:
    r = re.compile(patt)
  else:
    r = None
  if isinstance(val,list):
    # File list input is a simple list. Means that no library associations are present
    d = {'__default__':val}
  elif isinstance(val,dict):
    # File list input is a dictionary. Means library associations are present. Will return a dictionary of strings
    # keyed off each library association instead of a simple string
    d = val
  else:
    logger.error("filelists input must be list or dict")
    sys.exit(1)
  for n,v in d.items():
    s = ''
    for e in v:
      # Check for a syntax association (vlog,vhdl,etc) and only include in output if 
      # no association was requested or the association matches the first entry in the tuple
      if not assoc or e[0]==assoc:
        # Second entry of the tuple is expected to be a string containing a space separated list of file paths
        # Split those into an actual list and iterate across each one
        for f in e[1].split(' '):
          # If a regex pattern wasn't provided or if there's a match, the entry can go into the output
          if not r or r.match(f):
            s = s + ' -f '+f
    ret[n] = s
  # Return type is based on input type.  If input was a simple list, return the one string that was placed in '_default_'
  # Otherwise, return a full dict of strings (one for each libassoc plus the default)
  if isinstance(val,list):
    return ret['__default__']
  else:
    return ret

def library_mappings(val):
  mapping_re = re.compile(r'(?P<logical>\S+):(?P<physical>\S+)')
  map_list = val.split(' ')
  map_tuples = []
  for m in map_list:
    s = mapping_re.search(m)
    if not s:
      logger.error("Invalid format for library mapping, \"{}\" must be in '<logical>:<physical>' format".format(m))
      sys.exit(1)
    map_tuples.append((s.group('logical'),s.group('physical')))
  return map_tuples



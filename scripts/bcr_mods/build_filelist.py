#! /usr/bin/env python

import sys
import os
import time
import re

sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/templates/python")
if sys.version_info[0] < 3:
  sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/templates/python/python2")

from uvmf_version import version
__version__ = version

try:
  import yaml
  from voluptuous import Required,Optional,Any,In,Schema,MultipleInvalid
  from voluptuous.humanize import humanize_error
  import argparse
  import logging
  import traceback
  import pprint
  from bcr_mods.common import *
  import platform
except ImportError as ie:
  print("ERROR:Missing library: %s" % str(ie))
  sys.exit(1)

class Node:
  def __init__(self, name, parent):
    self.name = name
    self.parent = parent
    self.children = []

  def __repr__(self):
    return 'Node '+repr(self.name)

  def dic(self):
    retval = {self:[]}
    for i in self.children:
      retval[self].append(i.dic())
    return retval

  def display(self):
    pass

  def has_children(self):
    return bool(self.children)

  def get_parent(self):
    return self.parent

  def printme(self,input="",level=0):
    val = "%s// %s %s\n" % (input, " "*level*3, self.name)
    for i in self.children:
      val = i.printme(val,level+1)
    return val

class Builder(object):

  def __init__(self):
    config_schema = {
      Optional('src'): [ str ],
      Optional('incdir'): [ str ],
      Optional('options'): list,
      Optional('needs'): [ str ],
    }
    self.schema = Schema(config_schema)
    self.clear()
    self.logger = logging.getLogger("logger")
    self.libassoc = None

  def clear(self):
    self.source_files = []
    self.incdirs = []
    self.options = []
    self.source_files_tuple = []
    self.incdirs_tuple = []
    self.options_tuple = []    
    self.parsing_stack = []
    self.top_node = None
    self.lib_data = {}

  def find_libassoc(self,fname):
    if not self.libassoc:
      return None
    for d in self.libassoc:
      for n,v in d.items():
        if not isinstance(v,(str,list)):
          self.logger.error("Library association entry for library \"{}\" is illegal (not string or list)".format(n))
          sys.exit(1)
        if isinstance(v,str) and v == fname:
          return n
        elif isinstance(v,list):
          for l in v:
            if l == fname:
              return n
    return None

  def validate(self,fname,data_structure):
    try:
      self.schema(data_structure)
    except MultipleInvalid as e:
      resp = humanize_error(data_structure, e).split('\n')
      self.logger.error("While validating config file \"{}\":\n{}".format(fname,pprint.pformat(resp, indent=2)))
      sys.exit(1)
    
  def read_file(self,fname,parent=None,lib_name=None):
    """ Read a provided configuration file in order to build up a file list and set of switches for the
    build. Can be called recursively if a given config file includes another config file. All paths are
    converted to absolute based on the location of the current config file
    """
    ## Resolve full path to file name
    full_fname = resolve_path(fname,os.getcwd())
    ## Check that file exists
    if not os.path.exists(full_fname):
      self.logger.error("Compile file \"{}\" does not exist".format(full_fname))
      sys.exit(1)
    ## Log the node and mark it as a child of the parent
    this_node = Node(full_fname,parent)
    if parent:
      parent.children.append(this_node)
    else:
      self.top_node = this_node
    ## Check for recursion
    if full_fname in self.parsing_stack:
      self.logger.fatal("Circular reference to config file \"{}\" detected. Stack:\n  {}".format(full_fname,'\n  '.join(map(str,self.parsing_stack))))
      sys.exit(1)
    try:
      fs = open(full_fname)
    except IOError:
      ## It is not an error if a compile file didn't exist. This is allowed for the overall flow convenience. Just silently skip.
      ##self.logger.error("Unable to open compile file \"{}\"".format(full_fname))
      ##sys.exit(1)
      return
    self.parsing_stack.append(full_fname)
    try:
      yaml_data = yaml.safe_load(fs)
    except yaml.scanner.ScannerError as e:
      self.logger.error("Error in file \"{}\": {}".format(full_fname,e))
      sys.exit(1)
    fs.close()
    ## Validate structure of config file we just loaded
    self.validate(full_fname,yaml_data)
    ## Capture directory name of config file
    dir_name = os.path.dirname(full_fname)
    if 'needs' in yaml_data:
      for n in yaml_data['needs']:
        norm_file = resolve_path(n, dir_name,fname)
        if not os.path.exists(norm_file):
          self.logger.error("Config file \"{}\" needed by \"{}\" cannot be found".format(norm_file, full_fname))
          sys.exit(1)
        lib = self.find_libassoc(os.path.basename(norm_file))
        if not lib and lib_name:
          lib = lib_name
        if lib:
          lib_debug_str = 'library '+lib+' '
          if lib not in self.lib_data:
            self.lib_data[lib] = {  
                                    'source_files':[],
                                    'incdirs':[],
                                    'options':[],
                                    'source_files_tuple':[],
                                    'incdirs_tuple':[],
                                    'options_tuple':[],
                                 }
        else:
          lib_debug_str = ''
        self.logger.debug("Jumping into {}config file \"{}\" from config file \"{}\"".format(lib_debug_str,norm_file, full_fname))
        self.read_file(norm_file,this_node,lib)
    if 'src' in yaml_data:
      for f in yaml_data['src']:
        ## Source file here could be just a file or it could include a switch (-f, for example) at the front. If so,
        ## extract that switch and save it for later
        m = re.match(r"(-\S+\s+)?(\S+)",f)
        switch = m.group(1)
        norm_file = resolve_path(m.group(2),dir_name,fname)
        if not os.path.exists(norm_file):
          self.logger.warning("File \"{}\" mentioned in config file \"{}\" may not exist".format(norm_file,full_fname))
        if lib_name:
          sf = self.lib_data[lib_name]['source_files']
          sft = self.lib_data[lib_name]['source_files_tuple']
        else:
          sf = self.source_files
          sft = self.source_files_tuple
        if norm_file not in sf:
          if switch:
            sft.append((full_fname,switch+norm_file))
          else:
            sft.append((full_fname,norm_file))
          sf.append(norm_file)
          self.logger.debug("Added source file \"{}\" listed in config file \"{}\"".format(norm_file,full_fname))
        else:
          self.logger.debug("Source file \"{}\" listed in config file \"{}\" already present, skipping".format(norm_file,full_fname))
    if 'options' in yaml_data:
      for s in yaml_data['options']:
        if lib_name:
          ot = self.lib_data[lib_name]['options_tuple']
          o = self.lib_data[lib_name]['options']
        else:
          ot = self.options_tuple
          o = self.options
        if s not in o:
          ot.append((full_fname,s))
          o.append(s)
          self.logger.debug("Added options \"{}\" listed in config file \"{}\"".format(s,full_fname))
        else:
          self.logger.debug("Options \"{}\" listed in config file \"{}\" already present, skipping".format(s,full_fname))
    if 'incdir' in yaml_data:
      for i in yaml_data['incdir']:
        norm_path = resolve_path(i,dir_name,fname)
        if not os.path.exists(norm_path):
          self.logger.warning("Include directory \"{}\" listed in config file \"{}\" may not exist".format(norm_path,full_fname))
        if lib_name:
          it = self.lib_data[lib_name]['incdirs_tuple']
          id = self.lib_data[lib_name]['incdirs']
        else:
          it = self.incdirs_tuple
          id = self.incdirs
        if norm_path not in id:
          it.append((full_fname,norm_path))
          id.append(norm_path)
          self.logger.debug("Added include directory \"{}\" listed in config file \"{}\"".format(norm_path,full_fname))
        else:
          self.logger.debug("Include directory \"{}\" from config file \"{}\" already present, skipping".format(norm_path,full_fname))
    self.parsing_stack.pop()

  def search_assoc(self,ext,fileassoc):
    for k,v in fileassoc.items():
      if ext in v:
        return k
    return None

  def create(self,qf_file_prefix,use_fileassoc=False,fileassoc={},incassoc={},nobuild=False):
    create_data = {}
    ret_data = {}
    if self.source_files_tuple or self.options_tuple or self.incdirs_tuple:
      create_data = {'__default__': { 'source_files_tuple':self.source_files_tuple,
                                      'source_files':self.source_files,
                                      'options_tuple':self.options_tuple,
                                      'options':self.options,
                                      'incdirs_tuple':self.incdirs_tuple,
                                      'incdirs':self.incdirs, } }
    for k,v in self.lib_data.items():
      create_data[k] = v
    for k,v in create_data.items():
      ret_data[k] = self.create_internal(qf_file_prefix=qf_file_prefix,data=v,libname=k,use_fileassoc=use_fileassoc,fileassoc=fileassoc,incassoc=incassoc,nobuild=nobuild)
    if (len(ret_data) == 1) and '__default__' in ret_data:
      return ret_data['__default__']
    else:
      return ret_data

  def create_internal(self,qf_file_prefix,data,libname,use_fileassoc=False,fileassoc={},incassoc={},nobuild=False):
    header = "// File generated by {} version {}\n\n".format(__name__,__version__)
    header = header + "// File tree:\n"
    header = header + self.top_node.printme() + "\n\n"
    files_written = []
    file_lists = {}
    if platform.system() == "Windows":
      is_windows = True
    else:
      is_windows = False
    ## Set up a default incassoc of "+incdir+"
    incassoc['__default__'] = "+incdir+"
    if use_fileassoc:
      # Need to parse through all source files and divide them up based on file extension associations.
      for f in data['source_files_tuple']:
        # Determine file extension of this file
        ext = os.path.splitext(f[1])[1]
        # Check to see if we can determine the file association. Error if not
        assoc = self.search_assoc(ext,fileassoc)
        if not assoc:
          self.logger.error("Unable to determine file association for file \"{}\" in compile file \"{}\", aborting".format(f[1],f[0]))
          sys.exit(1)
        # Place this file information into the appropriate file list
        if assoc not in file_lists:
          file_lists[assoc] = []
        self.logger.debug("Associated file \"{}\" with \"{}\"".format(f,assoc))
        file_lists[assoc].append(f)
    else:
      # No file association needed. Place all files into same list using "__default__" as the key
      file_lists['__default__'] = data['source_files_tuple']
    # Now that we have the file lists, need to produce the files. Each file_lists entry gets its own file list output
    # using the format 'qf_file_prefix + _ + file_lists_key + .qf'
    for k,v in file_lists.items():
      if k == '__default__':
        ext = ''
      else:
        ext = '_' + k
      if libname == '__default__':
        lib = ''
      else:
        lib = '_' + libname
      output = qf_file_prefix + ext + lib + '.qf'
      if not nobuild:
        try:
          ofh = open(output, 'w')
        except IOError:
          self.logger.error("Unable to create file list {0}".format(output))
          sys.exit(1)
      if k=='__default__':
        assoc = ''
      else:
        assoc = k
      files_written.append((assoc,output))
      if not nobuild:
        # Put the same header and file tree information at the top of all .qf files
        ofh.write(header)
        last_source = None
        ## Print out incdirs for this key
        if data['incdirs_tuple'] and k in incassoc:
          ofh.write("// ********** Include directories **********\n")
          for i in data['incdirs_tuple']:
            if (i[0] != last_source):
              ofh.write("\n// From {}\n".format(i[0]))
              last_source = i[0]
            if is_windows:
              ps = i[1].replace('\\','\\\\')
            else:
              ps = i[1]
            ofh.write("  "+incassoc[k]+ps+"\n")
          ofh.write("\n")
        last_source = None
        ## Print out files for this key
        ofh.write("// ********** Source files **********\n")
        for i in file_lists[k]:
          if (i[0] != last_source):
            ofh.write("\n// From {}\n".format(i[0]))
            last_source = i[0]
          if is_windows:
            ps = i[1].replace('\\','\\\\')
          else:
            ps = i[1]
          ofh.write("  "+ps+"\n")
        ofh.write("\n")
        last_source = None
        if data['options_tuple']:
          options = []
          for i in data['options_tuple']:
            # Options may be present as stand-alone list entries or as a list with element 0 a key and element 1 a value.
            # If its a stand-alone item they will be used across all file lists. Any tuple elements will only be applied
            # if element 0 matches the current key.
            src = i[0]
            val = i[1]
            if type(val) is list:
              key = val[0]
              val = val[1]
            else:
              key = None
            if (key == k) or (key == None):
              options.append((src,val))
          if len(options) > 0:
            last_source = None
            ofh.write("// ********** Options **********\n")
            for i in options:
              if (i[0] != last_source):
                ofh.write("\n// From {}\n".format(i[0]))
                last_source = i[0]
              ofh.write(  i[1]+"\n")
        ofh.close()
        self.logger.debug("Wrote file list {}".format(output))
    return files_written






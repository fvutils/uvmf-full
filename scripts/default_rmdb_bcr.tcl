package require fileutil
variable recursion_check
variable tcdict
variable builddict 
variable file_read
variable root_dir
variable debug
variable ini

## Variables controllable by user via ini file along with their defaults
#puts [format "DEFAULT code_coverage_enable : %s" $ini(code_coverage_enable)]

## The $builddict dictionary contains the following sub-structure:
##  { <testbench_name> }
##      - { buildcmd } : Extra command-line arguments to use during 'make build' command
##      - { runcmd } : Extra command-line arguments appended to vsim command for this testbench
##      - { builddir } : Directory where this testbench's .compile files live      
##  { <repeated for all testbenches> }

## $tcdict organization to allow for per-iteration extra-args
##  { <testbench_name> }
##     { <testcase_name> }
##        { Iteration# } : Incrementing from 0 to N
##          { seed } : Seed to use for this iteration
##          { extra_args } : Extra command-line arguments for this iteration

proc initTcl {rd {master_seed 0} {dbg 0}} {
  global file_read
  global root_dir
  global debug
  global ini
  set debug $dbg
  set file_read 0
  set root_dir $rd
  if {$master_seed=="random"} {
    puts "NOTE: Using random master seed"
    set ms [clock seconds]
  } else {
    puts "NOTE: Using fixed random seed"
    set ms $master_seed
  }
  set rv [expr {srand($ms)}]
  puts [format "NOTE: Master seed set to %d" $ms]
  vrmSetupDefaults
  vrmSetup
  if {$dbg==1} {
    puts [format "DEBUG: Initialization variable settings:"]
    dumpIniVars
  }
  return 0
}

## Default proc is empty - expectation is that user points to a separate
## file pointed to by $UVMF_VRM_INI env variable to override this proc
## and fill it with desired overrides to default behavior. That Tcl is 
## sourced early enough that other procs (to define non-standard LSF, for
## example) can be defined as well
proc vrmSetup {} {}

## These are default initialization variables 
proc vrmSetupDefaults {} {
  setIniVar code_coverage_enable 0 1
  setIniVar code_coverage_types "bsf" 1
  setIniVar code_coverage_target "/hdl_top/DUT." 1
  setIniVar code_coverage_map 0 1
  setIniVar extra_merge_options "" 1
  setIniVar extra_run_options "" 1
  setIniVar tplanfile "" 1
  setIniVar tplanoptions "-format Excel" 1
  setIniVar no_rerun 1 1
  setIniVar use_infact 0 1
  setIniVar use_vis 0 1
  setIniVar use_vinfo 0 1
  setIniVar dump_waves 0 1
  setIniVar dump_waves_on_rerun 0 1
  setIniVar vis_dump_options "+signal+report+memory=512" 1
  setIniVar exclusionfile "" 1
  setIniVar pre_run_dofile {""} 1
  setIniVar pre_vsim_dofile {""} 1
  setIniVar use_test_dofile 0 1
  setIniVar use_job_mgmt_run 0 1
  setIniVar use_job_mgmt_build 0 1
  setIniVar use_job_mgmt_covercheck 0 1
  setIniVar use_job_mgmt_exclusion 0 1
  setIniVar use_job_mgmt_report 0 1
  setIniVar gridtype "lsf" 1
# Use of older switches "-source" and "-htmldir" have been replaced with "-annotate" and "-output" respectively.
# May need to use this alternative set of switches if using an older release of Questa
#  setIniVar html_report_args "-details -source -testdetails -showexcluded -htmldir (%VRUNDIR%)/covhtmlreport" 1
  setIniVar html_report_args "-details -annotate -testdetails -showexcluded -output (%VRUNDIR%)/covhtmlreport" 1
  setIniVar gridcommand_run "bsub -J (%INSTANCE%) -oo (%TASKDIR%)/(%SCRIPT%).o%J -eo (%TASKDIR%)/(%SCRIPT%).e%J (%WRAPPER%)" 1
  setIniVar gridcommand_build "bsub -J (%INSTANCE%) -oo (%TASKDIR%)/(%SCRIPT%).o%J -eo (%TASKDIR%)/(%SCRIPT%).e%J (%WRAPPER%)" 1
  setIniVar gridcommand_covercheck "bsub -J (%INSTANCE%) -oo (%TASKDIR%)/(%SCRIPT%).o%J -eo (%TASKDIR%)/(%SCRIPT%).e%J (%WRAPPER%)" 1
  setIniVar gridcommand_exclusion "bsub -J (%INSTANCE%) -oo (%TASKDIR%)/(%SCRIPT%).o%J -eo (%TASKDIR%)/(%SCRIPT%).e%J (%WRAPPER%)" 1
  setIniVar gridcommand_report "bsub -J (%INSTANCE%) -oo (%TASKDIR%)/(%SCRIPT%).o%J -eo (%TASKDIR%)/(%SCRIPT%).e%J (%WRAPPER%)" 1
  setIniVar use_covercheck 0 1
  setIniVar top_du_name "top_du_name" 1
  setIniVar covercheck_build "covercheck_build" 1
  setIniVar extra_covercheck_options "" 1
  setIniVar covercheck_analyze_timeout "15m" 1
  setIniVar covercheck_init_file "" 1
  setIniVar covercheck_ucdb_file "(%DATADIR%)/tracker.ucdb" 1
  setIniVar timeout 3600 1
  setIniVar queue_timeout 60 1
  setIniVar build_timeout -1 1
  setIniVar build_queue_timeout -1 1
  setIniVar run_timeout -1 1
  setIniVar run_queue_timeout -1 1
  setIniVar exclusion_timeout -1 1
  setIniVar exclusion_queue_timeout -1 1
  setIniVar covercheck_timeout -1 1
  setIniVar covercheck_queue_timeout -1 1
  setIniVar report_timeout -1 1
  setIniVar report_queue_timeout -1 1
  setIniVar email_servers {} 1
  setIniVar email_recipients {} 1
  setIniVar email_sections "all" 1
  setIniVar email_subject {} 1
  setIniVar email_message {} 1
  setIniVar email_originator {} 1
  setIniVar usestderr 0 1
  setIniVar trendfile {} 1
  setIniVar trendoptions {} 1
  setIniVar triagefile {} 1
  setIniVar triageoptions {} 1
  setIniVar bcr_exec_cmd_linux "uvmf_bcr.py" 1
  setIniVar bcr_exec_cmd_windows "python $::env(UVMF_HOME)/scripts/uvmf_bcr.py" 1
  return 0
}

proc getTimeoutVal {globalTimeout timeout} {
  if { $timeout == -1 } { 
    return $globalTimeout 
  } else { 
    return $timeout
  }
}

proc getIniVar {varname} {
  global ini
  global debug
  set lv [string tolower $varname]
  if {[info exists ini($lv)]} {
    return $ini($lv)
  }
  if {[array size ini] > 0} {
    puts [format "ERROR : ini variable %s not found" $varname]
    puts [format "        Available ini variables: %s" [array names ini]]
    exit 88
  }
}

proc setIniVar {varname value {firsttime 0}} {
  global ini
  global debug
  if { $debug == 1 } {
    puts [format "DEBUG: ini variable \"%s\" getting set to \"%s\"" $varname $value]
  }
  set lv [string tolower $varname]
  if {$firsttime==0} {
    if {![info exists ini($lv)]} {
      puts [format "ERROR: ini variable \"%s\" unrecognized on set attempt. Following list are available:\n\t%s" $varname [array names ini]]
      exit 88
    }
  }
  set ini($lv) $value
}

proc dumpIniVars {} {
  global ini
  parray ini
}

## Returns a path to the inFact SDM .ini file if inFact is enabled.
## Returns "" if inFact is disabled
proc getInfactSdmIni {datadir} {
  if {[getIniVar use_infact]} {
	return [file join "+infact=$datadir" "infactsdm_info.ini"]
  } else {
    return ""
  }
}

## Top level test list parser invocation.  Sets up some globals and then
## fires off the internal reader (for purposes of nesting)
proc ReadTestlistFile {file_name invoc_dir {collapse 0} {debug 0} {init 0}} {
  global recursion_check
  global tcdict
  global file_read
  if {$file_read == 1} {
    return ""
  }
  set recursion_check ""
  set tcdict [dict create]
  set builddict [dict create]
  ReadTestlistFile_int $file_name $invoc_dir $collapse $debug
  if {$debug == 1} {
    print_tcdict
  }
  set file_read 1
  return ""
}

proc print_tcdict {} {
  global tcdict
  puts "DEBUG: tcdict contents:"
  dict for {top testnames} $tcdict {
    puts [format "Testbench : \"%s\"" $top]
    dict for {test iter} $testnames {
      puts [format "\t- Test : \"%s\"" $test]
      foreach i [dict keys $iter] {
        if {[dict get $iter $i extra_args] != ""} {
          set ea_str [format "- Extra Args : \"%s\"" [dict get $iter $i extra_args]]
        } else {
          set ea_str ""
        }
        puts [format "\t\t- %d - Seed : %s %s" $i [dict get $iter $i seed] $ea_str]
      }
    }
  }
}

proc print_builddict {} {
  global builddict
  puts "DEBUG: builddict contents:"
  if {![info exists builddict]} {
    puts "  builddict is EMPTY"
    return
  }
  dict for {buildname entry} $builddict {
    puts [format "  %s - %s" $buildname $entry]
  }
}

proc GetMapInfo { build_name key } {
  global builddict
  if {![dict exists $builddict $build_name]} {
    puts [format "ERROR getMapInfo - build %s invalid" $build_name]
    exit
  }
  if {![dict exists $builddict $build_name "mapinfo"]} {
    return ""
  }
  return [dict get $builddict $build_name "mapinfo" $key]
}
 
## Actual test list file reader.  See embedded comments for more detail
proc ReadTestlistFile_int {file_name invoc_dir collapse {debug 1} {init 0}} {
  global recursion_check
  global tcdict
  global builddict
  global root_dir
  set tops ""
  ## Elaborate "^" at beginning of $file_name and expand with $root_dir
  regsub -- {^\^} $file_name $root_dir file_name
  ## Derive full path for filename
  set file_name [file normalize $file_name]
  ## Recursion is checked for, i.e. if a test list includes itself
  if {[lsearch $recursion_check $file_name] >= 0} {
    puts [format "ERROR RECURSION : %s" $file_name]
    exit 88
  }
  if {$debug==1} {
    puts [format "DEBUG: Opening file \"%s\"" $file_name]
  }
  lappend recursion_check $file_name
  if {![file isfile $file_name]} {
    puts [format "ERROR INVALID FILE : %s" $file_name]
    exit 88
  }  
  set dir [file dirname $file_name]
  set tfile [open $file_name r]
  while {![eof $tfile]} {
    gets $tfile line
    ## Skip comment lines in testlist file - first column a # sign
    if {[string range $line 0 0] != "#"} {
      ## Skip whitespace
      if {[llength $line] != 0} {
        ##
        ## Process TB_INFO lines, which has information regarding how to
        ## build a particular testbench
        ##
        if {[string match "TB_INFO" [lindex $line 0]]} {
          if {[llength $line] != 4} {
            puts [format "ERROR TB_INFO ARGS : %s" $line]
            exit 88
          }
          dict set builddict [lindex $line 1] "buildcmd" [lindex $line 2]
          dict set builddict [lindex $line 1] "runcmd" [lindex $line 3]
          dict set builddict [lindex $line 1] "builddir" $dir
          if {$debug==1} {
            puts [format "DEBUG: Registering testbench %s" [lindex $line 1]]
            puts [format "DEBUG:   buildcmd: %s" [lindex $line 2]]
            puts [format "DEBUG:   runcmd: %s" [lindex $line 3]]
            puts [format "DEBUG:   builddir: %s" $dir]
          }
        } elseif {[string match "TB_LOCATION" [lindex $line 0]]} {
          ## Process TB_LOCATION lines which can override the default builddir entry for this bench.
          ## This allows some flexibility into where the test list lives vs. where the bench's ./sim directory
          ## exists, and should be specified when the test list exists outside of the ./sim directory
          if {[llength $line] != 3} {
            puts [format "ERROR TB_LOCATION ARGS : %s" $line]
            exit 88
          }
          if {![info exists builddict] || ![dict exists $builddict [lindex $line 1]]} {
            puts [format "ERROR TB_LOCATION - No TB_INFO entry for %s" [lindex $line 1]]
            print_builddict
            exit 88
          }
          dict set builddict [lindex $line 1] "builddir" [lindex $line 2]
          if {$debug==1} {
            puts [format "DEBUG: Setting builddir for %s as %s" [lindex $line 1] [lindex $line 2]]
          }
        ##
        ## Process TB_MAP lines, which must contain three arguments after the keyword
        ##   The three arguments should be the testbench name, followed by the source hierarchy, then the destination hierarchy
        ##
        } elseif {[string match "TB_MAP" [lindex $line 0]]} {
          if {[llength $line] != 4} {
            puts [format "ERROR TB_MAP ARGS : %s" $line]
          }
          if {![info exists builddict] || ![dict exists $builddict [lindex $line 1]]} {
            puts [format "ERROR TB_MAP - No TB_INFO entry for %s" [lindex $line 1]]
            print_builddict
            exit 88
          }
          set source_hier [split [string trim [lindex $line 2]] "/"]
          set dest_hier [split [string trim [lindex $line 3]] "/" ]
          dict set builddict [lindex $line 1] "mapinfo" "blockpath" [join [lrange $source_hier 0 end-1] "/"]
          dict set builddict [lindex $line 1] "mapinfo" "blockleaf" [lindex $source_hier end]
          dict set builddict [lindex $line 1] "mapinfo" "syspath" [join [lrange $dest_hier 0 end-1] "/"]
          dict set builddict [lindex $line 1] "mapinfo" "sysleaf" [lindex $dest_hier end]
        ##
        ## Process TB lines, which should contain a unique build label
        ##
        } elseif {[string match "TB" [lindex $line 0]]} {
          if {[llength $line] != 2} {
            puts [format "ERROR TB ARGS : %s" $line]
            exit 88
          }
          if {![info exists builddict] || ![dict exists $builddict [lindex $line 1]]} {
            puts [format "ERROR TB - No TB_INFO entry for %s" [lindex $line 1]]
            print_builddict
            exit 88
          }
          set tops [lindex $line 1]
          if {$debug == 1} {
            puts [format "DEBUG: Current top \"%s\"" $tops]
          }
        ##
        ## Process TEST lines, which will be stored according to the last TB seen
        ## Each TEST line contains a test name, a repeat count, and some number of
        ## seeds. Optional last item on a TEST line is a string of additional vsim 
        ## args to be used for just that test.
        ## If the test name contains DASHES those are converted to UNDERSCORES because
        ## the system uses dashes internally
        ##
        } elseif {[string match "TEST" [lindex $line 0]]} {
          if {[llength $tops] == 0} {
            puts [format "ERROR TEST NO TOP SPECIFIED : %s" $line]
            exit 88
          }
          if {[llength $line] == 1} {
            puts [format "ERROR TEST NOT ENOUGH ARGS : %s" $line]
            exit 88
          }
          ## Pull off final extra vsim args if possibly present
          if {[llength $line] > 2} {
            set extra_test_vsim_args [lindex $line end]
            if {![string is integer -strict $extra_test_vsim_args]} {
              ## Last item on the line wasn't a random seed, therefore it is vsim args
              ## Remove item from the list before further processing
              set line [lreplace $line end end]
              if {$debug == 1} {
                puts [format "DEBUG: Detected additional plusarg \"%s\" for test \"%s\"" $extra_test_vsim_args [lindex $line 1]]
              }
            } else {
              set extra_test_vsim_args ""
            }
          } else {
            set extra_test_vsim_args ""
          }
          ## Extract test name from line
          set tname [lindex $line 1]
          ## Convert dashes to underscores if found
          set tname [string map { - _ } $tname]
          ## Extract repeat count from line. If unspecified default to 1
          if {[llength $line] == 2} {
            set repcount 1
          } else {
            set repcount [lindex $line 2]
          }
          ## Extract seeds from line. May contain between 0 and $repcount seeds
          ## If any are unspecified default to internally generated random unless
          ## $collapse is specified in which we ignore the repeat count and fix 
          ## the seed to zero.
          set seedlist ""
          set iterlist ""
          if {$collapse == 0} {
            for {set repeat 0 } {$repeat < [expr $repcount]} {incr repeat } {
              if {[lindex $line [expr $repeat + 3]] == ""} {
                lappend seedlist "[expr {int(rand() * 10000000000000000) % 4294967296}]"
              } else {
                lappend seedlist [lindex $line [expr $repeat + 3]]
              }
              lappend iterlist $repeat
            }
          } else {
            lappend seedlist "0"
            lappend iterlist "0"
          }
          ## Now build up the $tcdict entries for this line
          if {![dict exists $tcdict $tops $tname]} {
            ## First time we've seen this test so create a new entry
            if {$debug == 1} {
              puts [format "DEBUG: Creating initial entry for test \"%s\"" $tname]
            } 
            set firstiter 0
          } else {
            ## Not the first time we've seen this test, figure out where to start
            ## appending more iterations
            set firstiter [llength [dict keys [dict get $tcdict $tops $tname]]]
            if {$debug == 1} {
              puts [format "DEBUG: Adding extra entries starting at %d for test \"%s\"" $firstiter $tname]
            }
          }
          foreach seed $seedlist {
            dict set tcdict $tops $tname $firstiter seed $seed
            dict set tcdict $tops $tname $firstiter extra_args $extra_test_vsim_args
            incr firstiter
          }
          if {$debug == 1} {
            puts [format "DEBUG: Added %d test \"%s\" for build \"%s\"" [llength $seedlist] $tname $tops]
          }
        ##
        ## Process INCLUDE lines, which is another file to parse.  
        ##
        } elseif {[string match "INCLUDE" [lindex $line 0]]} {
          if {$debug == 1} {
            puts [format "DEBUG: Including file %s" [lindex $line 1]]
          }
          ReadTestlistFile_int [lindex $line 1] $invoc_dir $collapse $debug
        }
        ## No check for invalid commands for potential forward-compatibility
      }
    }
  }
  set recursion_check [lrange $recursion_check 0 end-1]
  if {$debug==1} {
    puts [format "DEBUG: Finished with file \"%s\"" $file_name]
    print_builddict
  }
}

## Called by the runnables, returns a list of testbenches to
## build, produces the top-level of runnable hierarchy  
proc GetBuilds {args} {
  global tcdict
  return [dict keys $tcdict]
}
## Called by the runnables, returns the build command unique to
## this particular build.
proc GetBuildCmd {build} {
  global builddict
  return [dict get $builddict $build "buildcmd"]
}

## Called by the runnables, returns the run command for this particular build.
proc GetRunCmd {build} {
  global builddict
  return [dict get $builddict $build "runcmd"]
}

proc GetBuildDir {build} {
  global builddict
  return [dict get $builddict $build "builddir"]
}

## Returns extra arguments for a given test.  The full testname
## is expected to be passed in as per standard format 
## <benchname>-<tesname>-<iter>-<seed> so that'll need to be split
## out in order to extract info from the test case dictionary
proc GetExtraArgs {testname} {
  global tcdict
  set rv [split $testname -]
  return [dict get $tcdict [lindex $rv 0] [lindex $rv 1] [lindex $rv 2] "extra_args"]
}

## Called by the runnables, returns a list of tests to run for
## a specified build.  Format is expected to be as follows:
## <testbench_name>-<testcase_name>-<iteration>-<seed>
proc GetTestcases {build collapse} {
  global tcdict
  set ret ""
  dict for {test test_info} [dict get $tcdict $build] {
    foreach i [dict keys $test_info] {
      lappend ret [format "%s-%s-%s-%s" $build $test $i [dict get $test_info $i seed]]
    }
  }
  return $ret
}
proc FindMVCHome { Makefile_name } {
  set matchcnt [llength [fileutil::grep "mvchome" $Makefile_name]]
  return $matchcnt
}

## This will cause all UCDBs to be merged regardless of test status.  Default is to not merge in failing tests.
## If a test does not pass, strip all coverage information except for assertions but include it in the merge.  The
## intent is to ensure that test pass/fail information is maintained but bad tests do not contribute towards
## coverage
proc OkToMerge {userdata} {
  upvar $userdata data
  set passfail $data(passfail)
  set ucdbfile $data(ucdbfile)
  if { ![ string match "passed" $passfail ] } {
    exec vsim -c -viewcov $ucdbfile -do "coverage edit -keeponly -assert; coverage save $ucdbfile; quit"
  }
  return 1
}

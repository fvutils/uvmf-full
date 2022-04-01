#mvchome

MSEED ?= random
COLLAPSE ?= 0

run: clean
	vrun -rmdb $(UVMF_HOME)/scripts/default.rmdb -GCOLLAPSE=$(COLLAPSE) -j 2 -nolocalrerun $(EXTRA_RUN_ARGS) -clean -mseed $(MSEED) -html

clean:
	rm -rf vrmhtmlreport transcript VRMDATA *.log covhtmlreport *.ucdb

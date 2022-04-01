#mvchome
export AXI4_2X2_FABRIC_QVIP_DIR_NAME ?= ../../../../../../../../verification_ip/environment_packages/axi4_2x2_fabric_qvip_dir/uvmf

MSEED ?= random
COLLAPSE ?= 0

run: clean
	vrun -rmdb $(UVMF_HOME)/scripts/default.rmdb -GCOLLAPSE=$(COLLAPSE) -j 2 -nolocalrerun $(EXTRA_RUN_ARGS) -clean -mseed $(MSEED) -html

clean:
	rm -rf vrmhtmlreport transcript VRMDATA *.log covhtmlreport *.ucdb

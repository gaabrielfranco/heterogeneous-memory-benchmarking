#!/bin/bash

PYTHON=python3
SCRIPT=./plot_comparison_per_core.py

SCRIPT_ISOL=./plot_isolbench.py

SCRIPT_LAT=./plots_latency.py

$PYTHON $SCRIPT DRAM_distribution MIG_distribution 
$PYTHON $SCRIPT DRAM_MIG_distribution MIG_DRAM_distribution
$PYTHON $SCRIPT with_perfcnt/BRAM_nc_distribution with_perfcnt/OCM_nc_distribution
$PYTHON $SCRIPT with_perfcnt/BRAM_m_distribution with_perfcnt/OCM_m_distribution
$PYTHON $SCRIPT DRAM_all256_obsC4_interfC2_distribution DRAM_isol_distribution_2
$PYTHON $SCRIPT DRAM_isol_distribution_2 DRAM_jh_isol_distribution_2
$PYTHON $SCRIPT DRAM_jh_nczva_distribution DRAM_jh_isol_distribution_2

$PYTHON $SCRIPT_ISOL

$PYTHON $SCRIPT_LAT DRAM_l MIG_l
$PYTHON $SCRIPT_LAT DRAM_MIG_l MIG_DRAM_l 
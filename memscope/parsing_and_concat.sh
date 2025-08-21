#!/bin/bash

# Memscope results
for experiment in "DRAM_MIG_distribution" "DRAM_MIG_l" "DRAM_MIG_l_distribution" "DRAM_all256_obsC4_interfC2_distribution" "DRAM_distribution" "DRAM_isol_distribution_2" "DRAM_jh_isol_distribution_2" "DRAM_jh_nczva_distribution" "DRAM_l" "DRAM_l_distribution" "MIG_DRAM_distribution" "MIG_DRAM_l" "MIG_DRAM_l_distribution" "MIG_distribution" "MIG_l" "MIG_l_distribution" "with_perfcnt/BRAM_m_distribution" "with_perfcnt/BRAM_nc_distribution" "with_perfcnt/OCM_m_distribution" "with_perfcnt/OCM_nc_distribution"
do
    python3 parsing.py --base_folder $experiment
    python3 concatenate_csv.py --experiment_combine $experiment
done

# Isolbench results
python3 parsing_isolbench.py
python3 concatenate_csv_isolbench.py

import argparse
from copy import deepcopy
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib
import sys

# Folder that has the results
PARENT_FOLDER = "data/"

# Arguments
experiment_1 = sys.argv[1]
experiment_2 = sys.argv[2]

experiment_plot = PARENT_FOLDER + experiment_1
folders = glob.glob(f"{experiment_plot}/*_csv")

experiment_plot = PARENT_FOLDER + experiment_2
folders += glob.glob(f"{experiment_plot}/*_csv")

filename = experiment_1.removesuffix("_distribution") + "_" + experiment_2.removesuffix("_distribution")

try:
    filename = filename.replace("/", "_")
except:
    pass

# Constructing data
df_combined = None
for folder in folders:
    # Read CSV
    df = pd.read_csv(f"{folder}/combined_results.csv")

    operations_observed_read = ["r", "l", "s", "m"]
    plot_bandwidth_operations = ["r", "s", "w", "x"]

    # We assume a unique buffer size interference for each experiment
    assert df["Buffer size Interference"].nunique() == 1

    # Convert to KB instead of MB
    df["Buffer Size (Observed)"] = df["Buffer Size (Observed)"].apply(lambda x: eval(x) / 1024).astype(int)

    df.rename(columns={"Buffer Size (Observed)": "Buffer Size Observed (KB)"}, inplace=True)
    df["Interfering Cores"] = df["Active Cores"].astype(int)

    # Mapping operations
    ## s -> r
    ## x -> w
    df["Operation Observed"] = df["Operation Observed"].replace({"s": "r", "x": "w"})
    df["Operation Interference"] = df["Operation Interference"].replace({"s": "r", "x": "w"})

    if "with_perfcnt" in folder:
        df["Operation Observed"] = df["Operation Observed"].replace({"r": "s", "w": "x", "l": "m"})
        df["Operation Interference"] = df["Operation Interference"].replace({"r": "s", "w": "x", "l": "m"})

    # Getting the unique operation
    df["Operation"] = df.apply(lambda x: "(" + x["Operation Observed"] + "," + x["Operation Interference"] + ")", axis=1)

    df["Plot bandwidth"] = df["Operation Observed"].apply(lambda x: True if x in plot_bandwidth_operations else False)

    # Bandwidth (MB/s)
    # First: convert Diff (ns) to seconds
    df["Diff (s)"] = df["Diff (ns)"] / 1e9
    # Second: convert Bytes R (bytes) to MB
    df["MegaBytes R"] = df["Bytes R"] / (1024 * 1024)
    # Third: convert Bytes W (bytes) to MB
    df["MegaBytes W"] = df["Bytes W"] / (1024 * 1024)
    # Fourth: Compute bandwidth.
    # Cases: when it's a read operation, then it's MegaBytes R / Diff (s)
    # Cases: when it's a write operation, then it's MegaBytes W / Diff (s)

    df["Bandwidth (MB/s)"] = df.apply(lambda x: x["MegaBytes R"] / x["Diff (s)"] if x["Operation Observed"] in operations_observed_read else x["MegaBytes W"] / x["Diff (s)"], axis=1)

    # Bandwidth (GB/s)
    # First: convert Diff (ns) to seconds
    df["Diff (s)"] = df["Diff (ns)"] / 1e9
    # Second: convert Bytes R (bytes) to MB
    df["GigaBytes R"] = df["Bytes R"] / (1024 * 1024 * 1024)
    # Third: convert Bytes W (bytes) to MB
    df["GigaBytes W"] = df["Bytes W"] / (1024 * 1024 * 1024)
    # Fourth: Compute bandwidth.
    # Cases: when it's a read operation, then it's GigaBytes R / Diff (s)
    # Cases: when it's a write operation, then it's GigaBytes W / Diff (s)

    df["Bandwidth (GB/s)"] = df.apply(lambda x: x["GigaBytes R"] / x["Diff (s)"] if x["Operation Observed"] in operations_observed_read else x["GigaBytes W"] / x["Diff (s)"], axis=1)


    # Latency
    df["Latency (s)"] = df["Diff (s)"] / (df["Bytes R"] / 64) # Bytes R / 64 bytes 
    df["Latency (ns)"] = df["Diff (ns)"] / (df["Bytes R"] / 64) # Bytes R / 64 bytes 

    if "DRAM_all256_obsC4_interfC2_distribution" in folder:
        df["Memory Targets"] = "Obs: Private Part.; Int: Shared Part."
    elif "DRAM_jh_nczva_distribution" in folder:
        df["Memory Targets"] = "Nc write stream"
    elif "DRAM_jh_isol_distribution" in folder:
        df["Memory Targets"] = "Obs: Private Part.; Int: Shared Part."
    # Saving if it's DRAM or MIG or both
    elif filename == "DRAM_l_DRAM_m":
        # Special case where two memories are the same type
        if "DRAM_l" in folder:
            df["Memory Targets"] = "DRAM-l"
        else:
            df["Memory Targets"] = "DRAM-m"
    elif "DRAM_MIG" in folder:
        df["Memory Targets"] = "Obs: DRAM, Int: PL-DRAM"
    elif "MIG_DRAM" in folder:
        df["Memory Targets"] = "Obs: PL-DRAM, Int: DRAM"
    elif "DRAM" in folder and ("DRAM_all256_obsC4_interfC2_distribution" in folders[0] or "DRAM_jh_isol_distribution_2" in folders[0]):
        df["Memory Targets"] = "Obs + Int: Shared Cache"
    elif "DRAM" in folder:
        df["Memory Targets"] = "Obs + Int: DRAM"
    elif "MIG" in folder:
        df["Memory Targets"] = "Obs + Int: PL-DRAM"
    elif "BRAM" in folder:
        df["Memory Targets"] = "Obs + Int: BRAM"
    elif "OCM" in folder:
        df["Memory Targets"] = "Obs + Int: OCM" 
    else:
        raise Exception(f"{folder} do not contain DRAM, MIG, BRAM or OCM strings.")
    
    # Merging dataframes
    if df_combined is None:
        df_combined = deepcopy(df)
    else:
        df_combined = pd.concat([df_combined, df])
        df_combined.reset_index(inplace=True, drop=True)


if "with_perfcnt" in folder:
    df_combined = deepcopy(df_combined[~(df_combined["Operation"].isin(["(s,s)", "(s,x)", "(x,x)", "(x,y)"])) | ~(df_combined["Interfering Cores"] == 0)])
else:
    df_combined = deepcopy(df_combined[~(df_combined["Operation"].isin(["(r,r)", "(w,w)"])) | ~(df_combined["Interfering Cores"] == 0)])

if "with_perfcnt" in folder:
    df_combined = deepcopy(df_combined[~(df_combined["Operation"].isin(["(m,s)", "(m,y)"])) | ~(df_combined["Interfering Cores"] == 0)])
else:
    df_combined = deepcopy(df_combined[~(df_combined["Operation"].isin(["(m,w)"])) | ~(df_combined["Interfering Cores"] == 0)])

# Plot script
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.style.use("ggplot")
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["axes.edgecolor"] = "black"
plt.rc("font", size=5)

if df_combined["Plot bandwidth"].nunique() != 1:
    raise Exception("Combined data has different plot types: one part plot bandwidth and another one plot latency.")

if df_combined["Plot bandwidth"].unique()[0]:
    y_column = "Bandwidth (GB/s)"
else:
    y_column = "Latency (ns)"

if experiment_1 == "with_perfcnt/BRAM_nc_distribution" and experiment_2 == "with_perfcnt/OCM_nc_distribution":
    figsize = (7, 1.)
else:
    figsize = (3.5, 1.)

fig, axis = plt.subplots(1, 4, sharex=False, sharey=True, figsize=figsize, gridspec_kw={'width_ratios': [1, 2, 2, 2]})

for idx, interf_cores in enumerate(sorted(df_combined["Interfering Cores"].unique())):
    df_interf_cores = df_combined[df_combined["Interfering Cores"] == interf_cores]
    sns.boxplot(
        df_interf_cores, x="Operation", y=y_column,
        hue="Memory Targets", order=sorted(df_interf_cores["Operation"].unique()),
        hue_order=sorted(df_interf_cores["Memory Targets"].unique()), fill=False,
        dodge=False,
        widths=.5, linewidth=0.75,
        flierprops={"markersize": 2},
        ax=axis[idx],
        legend=True if idx == 0 else False
    )
    axis[idx].set_title(f"Interf. Cores = {interf_cores}", fontsize=5)
    axis[idx].set_xlabel(None)
    if idx != 0:
        axis[idx].set_ylabel(None)
    else:
        h, l = axis[idx].get_legend_handles_labels() # Extracting handles and labels
        ph = [plt.plot([],marker="", ls="")[0]] # Canvas
        handles = ph + h
        labels = ["Memory Targets:"] + l  # Merging labels
        axis[idx].legend(handles, labels, loc='center', bbox_to_anchor=(3.5, -0.3), ncol=3)


    axis[idx].grid(True, color = "black", alpha=0.5)

plt.ylim(0)

# Loop through each axis and set the box width for the first plot
for i, ax in enumerate(axis.flat):
    # We modify the box width for the first facet (column)
    if i == 0:  # First column
        for patch in ax.artists:
            patch.set_width(patch.get_width() * 2)  # Double the width of the boxes in the first column

# Iterate over the FacetGrid's axes and add vertical lines dynamically
for idx, ax in enumerate(axis.flat):  # Works for both single and multiple columns
    xticks = ax.get_xticks()  # Get the actual tick positions

    # Removing the "empty" operations for active core 0 only if it's plot bandwidth
    if idx == 0 and df_combined["Plot bandwidth"].unique()[0]:
        if "with_perfcnt" in folder:
            xticks = [0, 1]
            ax.set_xticks(xticks, labels=["(s,-)", "(x,-)"])
        else:
            xticks = [0, 1]
            ax.set_xticks(xticks, labels=["(r,-)", "(w,-)"])
    elif filename == "DRAM_jh_nczva_DRAM_jh_isol_distribution_2":
        ax.set_xticks([0, 1, 2, 3], labels=["(r,r)", "(r,w*)", "(w,r)", "(w,w*)"], fontsize=4.5)

    # Removing the "empty" operations for active core 0 only if it's plot latency
    if idx == 0 and not df_combined["Plot bandwidth"].unique()[0]:
        xticks = [0]
        ax.set_xticks(xticks, labels=["(m,-)"])
        
    # Compute midpoints between ticks
    midpoints = [(xticks[i] + xticks[i+1]) / 2 for i in range(len(xticks) - 1)]

    # Add vertical dashed lines at computed midpoints
    for mid in midpoints:
        ax.axvline(mid, linestyle='dashed', color='black', alpha=0.5)

# Creating the plots folder
plot_folder = "plots"
if not os.path.exists(plot_folder):
    os.mkdir(plot_folder)

plt.grid(True)
outfile = f"{plot_folder}/{filename}_boxplot.pdf"
print(f"Generating output file: {outfile}")
plt.savefig(outfile, bbox_inches="tight", pad_inches=0.01, dpi=800)
plt.close()
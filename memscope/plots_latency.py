from copy import deepcopy
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib
import sys

PARENT_FOLDER = "data/"

experiment_1 = sys.argv[1]
experiment_2 = sys.argv[2]

if experiment_1 == "DRAM_MIG_l":
    legend_pos = 1
else:
    legend_pos = 0

# Experiment 1 
experiment_plot = PARENT_FOLDER + f"{experiment_1}_distribution"
folders = glob.glob(f"{experiment_plot}/*_csv")

# Experiment 2
experiment_plot = PARENT_FOLDER + f"{experiment_2}_distribution"
folders += glob.glob(f"{experiment_plot}/*_csv")

filename = f"{experiment_1}_{experiment_2}"

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

    # Latency
    df["Latency (s)"] = df["Diff (s)"] / (df["Bytes R"] / 64) # Bytes R / 64 bytes 
    df["Latency (ns)"] = df["Diff (ns)"] / (df["Bytes R"] / 64) # Bytes R / 64 bytes 

    # Saving if it's DRAM or MIG or both
    if filename == "DRAM_l_DRAM_m":
        # Special case where two memories are the same type
        if "DRAM_l" in folder:
            df["Memory Targets"] = "DRAM-l"
        else:
            df["Memory Targets"] = "DRAM-m"
    elif "DRAM_MIG" in folder:
        df["Memory Targets"] = "Obs: DRAM, Int: PL-DRAM"
    elif "MIG_DRAM" in folder:
        df["Memory Targets"] = "Obs: PL-DRAM, Int: DRAM"
    elif "DRAM" in folder:
        df["Memory Targets"] = "Obs + Int: DRAM"
    elif "MIG" in folder:
        df["Memory Targets"] = "Obs + Int: PL-DRAM"
    elif "BRAM" in folder:
        df["Memory Targets"] = "BRAM"
    elif "OCM" in folder:
        df["Memory Targets"] = "OCM" 
    else:
        raise Exception(f"{folder} do not contain DRAM, MIG, BRAM or OCM strings.")
    
    # Merging dataframes
    if df_combined is None:
        df_combined = deepcopy(df)
    else:
        df_combined = pd.concat([df_combined, df])
        df_combined.reset_index(inplace=True, drop=True)

if df_combined["Plot bandwidth"].unique()[0]:
    raise Exception("We are plotting latency and the data says otherwise.")

# Removing operation "(l,r)" in Interfering Cores = 0
prev_n_rows = df_combined.shape[0]
df_combined = deepcopy(df_combined[(df_combined["Operation"] != "(l,w)") | (df_combined["Interfering Cores"] != 0)])
assert df_combined.shape[0] == prev_n_rows - 60 or df_combined.shape[0] == prev_n_rows - 30 # 2 * 30 execs or 30 execs

# Plot
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.style.use("ggplot")
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["axes.edgecolor"] = "black"
plt.rc("font", size=5)

fig, axes = plt.subplot_mosaic("ABCD;EEFF", figsize=(3.1, 3.), sharex=False, sharey=True, gridspec_kw={'height_ratios': [1.25, 1], 'hspace': 0.5})

axis = []
for axval in axes.values():
    axis.append(axval)

for idx, interf_cores in enumerate(sorted(df_combined["Interfering Cores"].unique())):
    df_interf_cores = deepcopy(df_combined[df_combined["Interfering Cores"] == interf_cores])
    if idx == 0:
        # For this case, we do not care about the second operation.
        # For this plot, we should have only 1 operation when Interf. Cores = 0
        assert df_interf_cores["Operation"].nunique() == 1

        # Keep only the first operation, add '-' in the second
        df_interf_cores["Operation"] = df_interf_cores["Operation"].apply(lambda x: f"{x.split(',')[0]},-)")
    sns.boxplot(
        df_interf_cores, x="Operation", y="Latency (ns)",
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
        axis[idx].legend(handles, labels, loc='center', bbox_to_anchor=(2, -0.25), ncol=3)

    axis[idx].grid(True, color = "grey", alpha=0.5)

plt.ylim(0)

# Loop through each axis and set the box width for the first plot
for i, ax in enumerate(axis):
    # We modify the box width for the first facet (column)
    if i == 0:  # First column
        for patch in ax.artists:
            patch.set_width(patch.get_width() * 2)  # Double the width of the boxes in the first column

# Iterate over the FacetGrid's axes and add vertical lines dynamically
for idx, ax in enumerate(axis):  # Works for both single and multiple columns
    if idx < 4:
        xticks = ax.get_xticks()  # Get the actual tick positions
        
        # Compute midpoints between ticks
        midpoints = [(xticks[i] + xticks[i+1]) / 2 for i in range(len(xticks) - 1)]

        # Add vertical dashed lines at computed midpoints
        for mid in midpoints:
            ax.axvline(mid, linestyle='dashed', color='black', alpha=0.5)


# Getting their individual data
if len(df_combined["Buffer size Interference"].unique()) != 1:
    raise Exception("We have more than a Buffer size Interference value in the experiments, which is an error.")

buffer_size_interf = df_combined["Buffer size Interference"].unique()[0]

# Experiment 1 
experiment_plot = PARENT_FOLDER + f"{experiment_1}"
folders = glob.glob(f"{experiment_plot}/*{buffer_size_interf}*_csv")

# Experiment 2
experiment_plot = PARENT_FOLDER + f"{experiment_2}"
folders += glob.glob(f"{experiment_plot}/*{buffer_size_interf}*_csv")

assert len(folders) == 2

# Constructing data
for idx, folder in enumerate(folders):
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

    # Latency
    df["Latency (s)"] = df["Diff (s)"] / (df["Bytes R"] / 64) # Bytes R / 64 bytes 
    df["Latency (ns)"] = df["Diff (ns)"] / (df["Bytes R"] / 64) # Bytes R / 64 bytes 

    # Saving if it's DRAM or MIG or both
    if filename == "DRAM_l_DRAM_m":
        # Special case where two memories are the same type
        if "DRAM_l" in folder:
            df["Memory Targets"] = "DRAM-l"
        else:
            df["Memory Targets"] = "DRAM-m"
    elif "DRAM_MIG" in folder:
        df["Memory Targets"] = "DRAM_PL-DRAM"
    elif "MIG_DRAM" in folder:
        df["Memory Targets"] = "PL-DRAM_DRAM"
    elif "DRAM" in folder:
        df["Memory Targets"] = "DRAM"
    elif "MIG" in folder:
        df["Memory Targets"] = "PL-DRAM"
    elif "BRAM" in folder:
        df["Memory Targets"] = "BRAM"
    elif "OCM" in folder:
        df["Memory Targets"] = "OCM" 
    else:
        raise Exception(f"{folder} do not contain DRAM, MIG, BRAM or OCM strings.")
        
    # Keeping only Active Cores in [0, 3]
    df = df[df["Active Cores"].isin([0, 3])]

    # Create Active Cores, Operation
    df["Active Cores, Operation"] = df["Active Cores"].astype(str) + ", " + df["Operation"]

    sns.pointplot(df, x="Buffer Size Observed (KB)", y="Latency (ns)",
                  hue="Active Cores, Operation", ax=axis[idx+4], errorbar=None,
                  dodge=True, markersize=1, linewidth=0.75, legend=True if idx == legend_pos
                  else False)
    axis[idx+4].tick_params(axis="x", rotation=45)

    if idx == legend_pos:
        axis[idx+4].legend(title=None, ncol=2)

    axis[idx+4].set_xlabel("Buffer Size Obs. (KB)", fontsize=5)
    axis[idx+4].set_title(df["Memory Targets"].unique()[0], size=5)

for i in range(6):
    axis[i].set(ylim=0)

# Creating the plots folder
plot_folder = "plots"
if not os.path.exists(plot_folder):
    os.mkdir(plot_folder)

outfile = f"{plot_folder}/{filename}_boxplot_lineplot.pdf"
print(f"Generating output file: {outfile}")
plt.savefig(outfile, bbox_inches="tight", pad_inches=0.01, dpi=800)
plt.close()

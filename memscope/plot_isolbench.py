import argparse
from copy import deepcopy
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib

####################################
# ISOLBENCH
experiment_plot = "isol_output"
distribution_experiment = True

PARENT_FOLDER = "data/"
experiment_plot = PARENT_FOLDER + experiment_plot

df_isolbench = pd.read_csv(f"{experiment_plot}/combined_results.csv")

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.style.use("ggplot")
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["axes.edgecolor"] = "black"
plt.rc("font", size=5)

# We assume a unique buffer size interference for each experiment
assert df_isolbench["Buffer size Interference"].nunique() == 1

operations_observed_read = ["r", "l", "s", "m"]
plot_bandwidth_operations = ["r", "s", "w", "x"]

# Distribution experiment
# Checking if there are 30 executions (from 1 to 30)
assert (np.array(sorted(df_isolbench["Execution"].unique())) == np.array(range(1, 31))).all()

# Getting the unique operation
df_isolbench["Operation"] = df_isolbench.apply(lambda x: "(" + x["Operation Observed"] + "," + x["Operation Interference"] + ")", axis=1)

df_isolbench["Interfering Cores"] = df_isolbench["Active Cores"].astype(int)

#df_isolbench["Memory Type"] = "ISOLBENCH"
df_isolbench["Memory Type"] = "Obs + Int: DRAM (IsolBench)"

df_isolbench["Bandwidth (GB/s)"] = df_isolbench["Bandwidth (MB/s)"] / 1024

# Making this modification for the plot x-axis be prettier
df_isolbench.loc[(df_isolbench["Interfering Cores"] == 0) & (df_isolbench["Operation"] == "(r,r)"), "Operation"] = "(r,w)"
####################################

####################################
# DRAM_isol_distribution
experiment_plot = PARENT_FOLDER + "DRAM_isol_distribution_2"
folders = glob.glob(f"{experiment_plot}/*_csv")

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
    df["Operation Observed"] = df["Operation Observed"].replace({"s": "r", "x": "w"},)
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

    df["Memory Type"] = "Obs + Int: DRAM (MemScope)"
    
    # Merging dataframes
    if df_combined is None:
        df_combined = deepcopy(df)
    else:
        df_combined = pd.concat([df_combined, df])
        df_combined.reset_index(inplace=True, drop=True)

# I don't know how general this will be
df_combined = deepcopy(df_combined[~(df_combined["Operation"].isin(["(r,r)", "(w,w)"])) | ~(df_combined["Interfering Cores"] == 0)])

# Concatenate dataframes
df = pd.concat([df_isolbench, df_combined]).reset_index(drop=True)

# Plot
fig, axis = plt.subplots(1, 4, sharex=False, sharey=True, figsize=(3.5, 1.), gridspec_kw={'width_ratios': [1, 2, 2, 2]})

for idx, interf_cores in enumerate(sorted(df["Interfering Cores"].unique())):
    df_interf_cores = df[df["Interfering Cores"] == interf_cores]
    sns.boxplot(
        df_interf_cores, x="Operation", y="Bandwidth (GB/s)",
        hue="Memory Type", order=sorted(df_interf_cores["Operation"].unique()),
        hue_order=sorted(df_interf_cores["Memory Type"].unique()), fill=False,
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
        labels = ["Memory Type:"] + l  # Merging labels
        axis[idx].legend(handles, labels, loc='center', bbox_to_anchor=(3.5, -0.3), ncol=3)


    axis[idx].grid(True, color = "grey", alpha=0.5)

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

outfile = f"{plot_folder}/ISOLBENCH_DRAM_isol_boxplot.pdf"
print(f"Generating output file: {outfile}")
plt.savefig(outfile, bbox_inches="tight", pad_inches=0.01, dpi=800)
plt.close()



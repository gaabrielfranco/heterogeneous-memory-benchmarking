import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import glob

folders = glob.glob("data/*")

df = pd.DataFrame()
for folder in folders:
    if "canny_fullhd" in folder:
        continue
    experiment_name = folder.split("/")[-1]
    files = sorted(glob.glob(f"{folder}/*.csv"))
    baseline_metric = pd.read_csv(f"{folder}/{experiment_name}_upool2.csv", header = None).T.values.reshape(-1)
    if "stitch_fullhd" in folder:
        baseline_metric = baseline_metric[:19]
    for file in files:
        x = pd.read_csv(file, header = None).T
        if "stitch_fullhd" in folder:
            x = x.iloc[:19]

        x = x.rename(columns={0: "metric"})
        x["benchmark"] = experiment_name
        x["benchmark_plot"] = experiment_name.replace("_", "\n")
        x["experiment"] = file.split("/")[2].split(".")[0].removeprefix(experiment_name)[1:]
        x["execution"] = range(len(x))
        x["metric"] /= baseline_metric


        df = pd.concat([
            df,
            x
        ]).reset_index(drop=True)

# Plot
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.style.use("ggplot")
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["axes.edgecolor"] = "black"
plt.rc("font", size=5)


main_plot_experiments = ["disparity_vga",
                            "mser_vga",
                            "sepia_vga",
                            "svm_cif",
                            "canny_vga",
                            "grayscale_vga",
                            "sobel_vga",
                            "sift_vga",
                            "tracking_fullhd",
                            "stitch_fullhd"]
#

EXPERIMENT_MAPPING = {
    'upool2_upool2': "Obs: upool2, Int: upool2",
    'upool2_upool3': "Obs: upool2, Int: upool3",
    'upool3_upool2': "Obs: upool3, Int: upool2",
    'upool3_upool3': "Obs: upool3, Int: upool3",
}

df["experiment"] = df["experiment"].replace(EXPERIMENT_MAPPING)

hue_order = sorted(df["experiment"].unique())

hue_order = hue_order[-2:] + hue_order[:-2] # just to start with upool2 and upool3

df_main = df[df.benchmark.isin(main_plot_experiments)]
df_appendix = df[~df.benchmark.isin(main_plot_experiments)]

fig, ax = plt.subplots(1, 1, figsize=(3.5, 1.5))
sns.barplot(df_main, y="metric", x="benchmark_plot", hue="experiment", hue_order=hue_order, errorbar="sd", ax=ax, err_kws={"linewidth": 1.5})

plt.xlabel(None)
plt.tight_layout()
plt.legend(title=None, ncol=2)
plt.ylabel("Slowdown " + r"($\times$)")
plt.savefig(f"plots/rt-bench_barplot.pdf", dpi=800)
print("Saved plots/rt-bench_barplot.pdf")
plt.close()

fig, ax = plt.subplots(1, 1, figsize=(3.5, 1.5))
sns.barplot(df_appendix, y="metric", x="benchmark_plot", hue="experiment", hue_order=hue_order, errorbar="sd", ax=ax, err_kws={"linewidth": 1.5})
plt.xlabel(None)
plt.tight_layout()
plt.ylim(0, 2)
plt.ylabel("Slowdown " + r"($\times$)")
plt.legend(title=None, ncol=2)
plt.savefig(f"plots/rt-bench_barplot_appendix.pdf", dpi=800)
print("Saved plots/rt-bench_barplot_appendix.pdf")
plt.close()



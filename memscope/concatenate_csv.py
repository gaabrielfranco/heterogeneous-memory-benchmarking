import argparse
import glob
import pandas as pd

# Argument is the folder to parse

parser = argparse.ArgumentParser(description="Parse to a CSV file.")
parser.add_argument("--experiment_combine", "-e", type=str, required=True, help="The experiment to combine")

args = parser.parse_args()
experiment_combine = args.experiment_combine

if "distribution" in experiment_combine:
    distribution_experiment = True
else:
    distribution_experiment = False

PARENT_FOLDER = "data/"

base_folder = f"{PARENT_FOLDER}{experiment_combine}"
folders = glob.glob(f"{base_folder}/*_csv")

for folder in folders:
    files = glob.glob(f"{folder}/*.csv")

    # Remove combined_results.csv if it exists
    try:
        files.remove(f"{folder}/combined_results.csv")
    except:
        pass

    df = None
    
    for file in files:
        attrs = file.split("/")[-1].split("_")
        df_file = pd.read_csv(file)
        if len(attrs) == 8:
            df_file["Cachable Observed"] = attrs[0]
            df_file["Operation Observed"] = attrs[1]
            df_file["Buffer size Observed"] = attrs[2]
            df_file["Pool Id Observed"] = attrs[3]
            df_file["Cachable Interference"] = attrs[4]
            df_file["Operation Interference"] = attrs[5]
            df_file["Buffer size Interference"] = attrs[6]
            df_file["Pool Id Interference"] = attrs[7].split(".")[0]
        elif len(attrs) == 9:
            df_file["Cachable Observed"] = attrs[0]
            df_file["Operation Observed"] = attrs[1]
            df_file["Buffer size Observed"] = attrs[2]
            df_file["Pool Id Observed"] = attrs[3]
            df_file["Cachable Interference"] = attrs[4]
            df_file["Operation Interference"] = attrs[5]
            df_file["Buffer size Interference"] = attrs[6]
            df_file["Pool Id Interference"] = attrs[7]
            df_file["Execution"] = attrs[8].split(".")[0]
        else:
            raise Exception(f"Filename {file} is not in the expected format.")
        
        if distribution_experiment and len(attrs) != 9:
            raise Exception(f"Distribution experiments have to have files with 9 arguments.")
        
        if not distribution_experiment and len(attrs) != 8:
            raise Exception(f"Non-Distribution experiments have to have files with 8 arguments.")


        if df is None:
            df = df_file
        else:
            df = pd.concat([df, df_file])

    df.reset_index(drop=True, inplace=True)
    print(f"Saving combined results to {folder}/combined_results.csv")
    df.to_csv(f"{folder}/combined_results.csv", index=False)
        
    




import argparse
import glob
from pprint import pprint
import pandas as pd

experiment_combine = "isol_output"

distribution_experiment = True

PARENT_FOLDER = "data/"

base_folder = f"{PARENT_FOLDER}{experiment_combine}"
folders = glob.glob(f"{base_folder}/*")

df = None

for folder in folders:
    exp_folders = glob.glob(f"{folder}/*_csv")
    for exp_folder in exp_folders:
        files = glob.glob(f"{exp_folder}/*.csv")    
    
        for file in files:
            attrs = file.split("/")[-1].split("_")
            if distribution_experiment and len(attrs) != 9:
                raise Exception(f"Distribution experiments have to have files with 9 arguments.")

            df_file = pd.read_csv(file)
            df_file["Cachable Observed"] = attrs[0]
            df_file["Operation Observed"] = attrs[1]
            df_file["Buffer size Observed"] = attrs[2]
            df_file["Pool Id Observed"] = attrs[3]
            df_file["Cachable Interference"] = attrs[4]
            df_file["Operation Interference"] = attrs[5]
            df_file["Buffer size Interference"] = attrs[6]
            df_file["Pool Id Interference"] = attrs[7]
            df_file["Execution"] = attrs[8].split(".")[0]
            

            if df is None:
                df = df_file
            else:
                df = pd.concat([df, df_file])

df.reset_index(drop=True, inplace=True)

assert len(df) == 420

print(f"Saving combined results to {base_folder}/combined_results.csv")
df.to_csv(f"{base_folder}/combined_results.csv", index=False)
        
    




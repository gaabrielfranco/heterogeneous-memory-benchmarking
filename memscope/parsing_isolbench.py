import re
import glob
import os
import argparse

base_folder = "isol_output"

## Appending the parent folder in the base folder
PARENT_FOLDER = "data/"

base_folder = PARENT_FOLDER + base_folder

# Getting all the experiments folders
active_cores_folders = glob.glob(f"{base_folder}/*")

for experiment_folders in active_cores_folders:
    # Assuming that everything that it's inside the folder is a experiment.
    exp_folders = glob.glob(f"{experiment_folders}/*")

    for folder in exp_folders:
        if "csv" in folder:
            continue

        files = glob.glob(f"{folder}/*")

        # If csv folder doesn't exist, create it
        if not os.path.exists(f"{folder}_csv/"):
            os.mkdir(f"{folder}_csv/")

        for experiment_file in files:
            print(f"Processing file {experiment_file}")

            # Opening the kernel file
            f = open(experiment_file, "r")

            # Creating the name of the csv file in the folder experiments_csv
            _, filename = os.path.split(experiment_file)
            csv_path = os.path.join(f"{folder}_csv/", f"{filename}.csv")

            # Creating the csv file to save the results
            csv_file = open(csv_path, "w")
            csv_file.writelines("Active Cores,Bandwidth (MB/s)\n")

            # Starting process the results after finding the line with RESULTS:
            bandwidth = None
            active_core = eval(experiment_folders.split("/")[-1][-1])
            assert active_core in [0, 1, 2, 3]

            for line in f.readlines():
                #if re.match(r"CPU0: B/W =.*", line):
                if re.match(r"Extra benchmark metric:.*", line):
                    bandwidth = eval(line.split(": ")[-1])
                    break

            if bandwidth is None:
                raise Exception(f"Error processing bandwidth in {experiment_file}")
            
            csv_file.writelines(f"{active_core},{bandwidth}\n")
            csv_file.close()


                

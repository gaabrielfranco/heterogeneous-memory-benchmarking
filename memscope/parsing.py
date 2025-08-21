import re
import glob
import os
import argparse

# Argument is the folder to parse

parser = argparse.ArgumentParser(description="Parse to a CSV file.")
parser.add_argument("--base_folder", "-b", type=str, required=True, help="The base folder to parse")

args = parser.parse_args()
base_folder = args.base_folder

## Appending the parent folder in the base folder
PARENT_FOLDER = "data/"

base_folder = PARENT_FOLDER + base_folder

# Getting all the experiments folders
experiment_folders = glob.glob(f"{base_folder}/*")

try:
    # Removing any .sh file
    sh_files = glob.glob(f"{base_folder}/*.sh")
    for f in sh_files:
        experiment_folders.remove(f)
except:
    pass

try:
    # Removing any previous csv folder
    csv_folders = glob.glob(f"{base_folder}/*csv")
    for f in csv_folders:
        experiment_folders.remove(f)
except:
    pass

try:
    # Removing any plots folder
    experiment_folders.remove(f"{base_folder}/plots")
except:
    pass

for exp_folder in experiment_folders:
    # Assuming that everything that it's inside the folder is a experiment.
    experiment_files = glob.glob(f"{exp_folder}/*")

    # If csv folder doesn't exist, create it
    if not os.path.exists(f"{exp_folder}_csv/"):
        os.mkdir(f"{exp_folder}_csv/")

    for experiment_file in experiment_files:
        print(f"Processing file {experiment_file}")
        # Opening the kernel file
        f = open(experiment_file, "r")

        # Creating the name of the csv file in the folder experiments_csv
        _, filename = os.path.split(experiment_file)
        csv_path = os.path.join(f"{exp_folder}_csv/", f"{filename}.csv")

        # Creating the csv file to save the results
        csv_file = open(csv_path, "w")

        # Starting process the results after finding the line with RESULTS:
        process_flag = False
        # First line of CSV must be the header, with column names
        write_header = True
        buffer_size_observed, buffer_size_interference = None, None
        for line in f.readlines():
            if re.match(r".*Buffer Size:.*", line):
                _, buffer_size = line.split(":")
                # Removing the whitespace
                buffer_size = buffer_size[1:]
                # Removing "\n" (if any)
                buffer_size = buffer_size.replace("\n", "")
                # The first occurence of Buffer Size is the observed.
                # The second occurence of Buffer Size is the Interference.
                if buffer_size_observed is None:
                    buffer_size_observed = buffer_size
                else:
                    buffer_size_interference = buffer_size
            
            if re.match(r"RESULTS:.*", line):
                process_flag = True
                continue
            
            # After we found RESULTS:
            if process_flag:
                if buffer_size_observed is None or buffer_size_interference is None:
                    raise Exception("Error found in the code. buffer_size_observed or buffer_size_interference are None.")
                # Split the line by ";" and save it in a list
                attributes = line.split(";")
                try:
                    attributes.remove(" \n")
                except:
                    pass
                key_str = ""
                value_str = ""
                # For each value in the list
                for attr in attributes:
                    # We have the structure of key: value
                    key, value = attr.split(":")
                    # Removing extra space after split
                    if key[0] == " ":
                        key = key.replace(" ", "", 1)
                    value = value.replace(" ", "", 1)
                    if "Perf." in key:
                        value = value.replace(", ", "/")

                    #value = value[1:] # Slicing (from the position 1 to the end)
                    key_str += f"{key},"
                    value_str += f"{value},"
                # Removing the last element (,)
                key_str = key_str[:-1]
                # Adding buffer sizes
                key_str += ",Buffer Size (Observed),Buffer Size (Interference)\n"
                # Removing the last element (,)
                value_str = value_str[:-1]
                # Remove "\n" (if any)
                value_str = value_str.replace("\n", "")
                value_str += f",{buffer_size_observed},{buffer_size_interference}\n" 
                
                # Write the header only once
                if write_header:
                    csv_file.writelines(key_str)
                    write_header = False
                csv_file.writelines(value_str)

        csv_file.close()

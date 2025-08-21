# Heterogeneous Memory Benchmarking Toolkit 🔬

[![Paper](https://img.shields.io/badge/paper-RTSS_2025-b31b1b.svg)](https://link-to-your-paper.com) [![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository provides the official implementation and data for the paper **"Heterogeneous Memory Benchmarking Toolkit"**, accepted at the IEEE Real-Time Systems Symposium (RTSS) 2025.

Our toolkit provides a suite of scripts to process raw performance data from **Memscope** and **RT-Bench**, enabling the reproduction of all figures and key findings presented in the paper.

---

## 📋 Table of Contents

- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Reproducing the Results](#-reproducing-the-results)
  - [Memscope Results](#memscope-results)
  - [RT-Bench Results](#rt-bench-results)
- [How to Cite](#-how-to-cite)
- [License](#-license)
- [Contributing](#-contributing)

---

## 📁 Repository Structure

The repository is organized to separate the concerns of the two benchmarking tools used in our study.

```
.
├── .gitignore             # Specifies intentionally untracked files to ignore
│
├── memscope/
│   ├── data/                           # Raw and processed Memscope data (.csv)
│   ├── plots/                          # Generated plots from Memscope data
│   ├── parsing.py                      # Helper: Parses raw experimental data
│   ├── parsing_isolbench.py            # Helper: Parses raw experimental data from Isolbench experiments
│   ├── concatenate_csv.py              # Helper: Merges individual CSV files
│   ├── concatenate_csv_isolbench.py    # Helper: Merges individual CSV files from Isolbench experiments
│   ├── plot_comparison_per_core.py     # Helper: Generate plots comparing Memory Targets BW per core
│   ├── plot_isolbench.py               # Helper: Generate plot comparing Memscope with Isolbench
│   ├── plots_latency.py                # Helper: Generate plots comparing Memory Targets Latency per core
│   ├── parsing_and_concat.sh           # Entry-point: Parses and merges all data
│   └── plot_all.sh                     # Entry-point: Generates all Memscope plots
│
├── rt-bench/
│   ├── data/              # RT-Bench experimental data
│   ├── plots/             # Generated plots from RT-Bench data
│   └── plots.py           # Python script to generate RT-Bench plots
│
├── requirements.txt       # Python dependencies
├── LICENSE                # Project software license
└── README.md              # This file
```

---

## 🚀 Getting Started

Follow these steps to set up your environment and prepare for reproducing the results.

### Prerequisites

- **Python 3.8** or newer.
- A `bash`-compatible shell.

### Installation

1.  **Clone the repository** to your local machine:
    ```sh
    git clone https://github.com/gaabrielfranco/heterogeneous-memory-benchmarking
    cd heterogeneous-memory-benchmark
    ```

2.  **Install the required Python packages** using `pip`:
    ```sh
    pip3 install -r requirements.txt
    ```
    This will install libraries such as `pandas`, `matplotlib`, and `seaborn` needed for data processing and plotting.

---

## 📊 Reproducing the Results

The raw data from all experiments is already included in the `data` subdirectories. You can directly proceed to generate the plots as shown in the paper.

### Memscope Results

To reproduce the plots and figures related to the Memscope analysis, navigate to the `memscope` directory and execute the provided shell scripts.

1.  **Navigate to the Memscope directory:**
    ```sh
    cd memscope
    ```

2.  **Parse and process the raw data:**
    This script reads the raw output files, processes them, and concatenates the results into unified `.csv` files for easy plotting.
    ```sh
    ./parsing_and_concat.sh
    ```

3.  **Generate all plots:**
    This script runs the Python plotting scripts to generate all figures related to Memscope, which will be saved in the `memscope/plots` directory.
    ```sh
    ./plot_all.sh
    ```



### RT-Bench Results

To reproduce the plots related to the RT-Bench, navigate to the `rt-bench` directory and run the main plotting script.

1.  **Navigate to the RT-Bench directory:**
    ```sh
    cd rt-bench
    ```

2.  **Generate all plots:**
    This Python script will process the data located in `rt-bench/data` and generate the corresponding figures, saving them in the `rt-bench/plots` directory.
    ```sh
    python3 plots.py
    ```

---

## 🎓 How to Cite

If you use this toolkit or the findings from our paper in your research, please cite our work.

```bibtex
# TODO
```

-----

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

-----

## 🙌 Contributing

We welcome contributions\! If you find a bug or have a suggestion for improvement, please open an issue or submit a pull request.
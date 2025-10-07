U2OS ER Network
![ER_Network](https://github.com/user-attachments/assets/0e0fc9fe-229a-4efa-bb0d-3565d4d78215)

Fluorescence Loss In PhotoBleaching (FLIP) 
![FLIP_Github](https://github.com/user-attachments/assets/d40cc975-25b9-4a96-b76e-eee6b7183f2a)









🧭 Repository Overview

This repository provides guidelines and part of the source code used in:

ShenGelashvili et al., 2024

Representative demo file outputs for testing the software.

Sample .stl files for 3D visualization.
(Note: Most .stl source files are too large to host on GitHub. We have provided one fragmented ER example as a representative demo.)





💻 System Requirements

Operating System

Windows 11 — any base or version (tested on Windows 11 v24H2 x64)

GPU Acceleration (Optional but Recommended)
For GPU-accelerated processing, install the CUDA 13.0 toolkit and enable CuPy
, which is later utilized by the pyclesperanto plugin | https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11 

Recommended Hardware (Minimum)

RAM: 64 GB+ DDR4/DDR5 @ 3600 MT/s

GPU: NVIDIA RTX Quadro P4000 / GeForce RTX 3070 or similar (≥ 8 GB VRAM)

CPU: Intel Core i5-8400 or AMD Ryzen 5 2600 (or better)


📦 Package Installation

All required packages are listed in my_current_env_list.txt.
To install dependencies:
you can recreate the environment from the provided .yml file using Conda:


conda env create -f environment.yml
conda activate Microscopy_Analysis_Advanced2  # example env name


Package Install:
The Repository contains a complete package list. Please perform a PIP install for the required and imported package versions as indicated in my_current_env_list.txt and the script (3D) or FLIP. 


🧰 Source Code Description

This repository includes two primary components:

3D Conversion Script

Converts .stl files into .html files for interactive 3D viewing in the browser.

Script: 3D_SuperRes_HTML.py

FLIP Analysis Script

Combines Fiji (ImageJ) ROI measurements (e.g., ROI_1, ROI_2, ROI_3 for nucleus and control regions)

Generates quantification plots used in the manuscript.

Source Code Listed Here Converts .STL file to .HTML for 3D interacitve view, and FLIP source code combines Fiji(Just Image J) ROI_1, ROI_2, ROI_3 Nucleus and Control quantifications to yield given plots. 


📋 Usage Guidelines

Download the Demo .stl File

Located in Demo_File_3D/

Place it in any easily accessible folder.

Set Up the Environment

Install the required packages as described above (YAML or pip).

Use the recommended Python environment (e.g., Microscopy_Analysis_Advanced2).

Run the 3D Conversion Script

Download 3D_SuperRes_HTML.py (main executable).

Open the file in VS Code or PyCharm.

Ensure the interpreter is set to the proper Python 3.9 environment.

Run the script to generate .html output.


The file has to be first opened in VS Code or Pycharm with Proper Python Interpreter (this is the Environment, 3.9 Python Base that should be installed from .yml file) - For example, Microscopy_Analysis_Advanced2 (My Current Environment). 

<img width="1729" height="1129" alt="image" src="https://github.com/user-attachments/assets/eb2c4999-1b95-487e-beab-8c28eec1ffdb" />
Output Example:
<img width="3683" height="1639" alt="image" src="https://github.com/user-attachments/assets/25977eb8-80b3-45d8-8feb-64b579b17531" />


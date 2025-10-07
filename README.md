U2OS ER Network
![ER_Network](https://github.com/user-attachments/assets/0e0fc9fe-229a-4efa-bb0d-3565d4d78215)

Fluorescence Loss In PhotoBleaching (FLIP) 
![FLIP_Github](https://github.com/user-attachments/assets/d40cc975-25b9-4a96-b76e-eee6b7183f2a)









This Particular Repository Provides Guidelines for Use of Source Code utilized in ShenGelashvili et al., 2024;
The Repository Includes representative demo file outputs as source for software test. Most .STL source file are too large to upload as demo on Github - yet we managed to provide one, fragmented ER representative.  












System Requirements: 
Windows 11 (Any Base or version works as long as Win 11)
Tested: W11 V:24H2 x64
For Assist with GPU processing requires the installation of CUDA 13.0 toolkit, enabling CuPy for Windows 11: https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11 | later utilized by pyclesperanto plugin https://pypi.org/project/pyclesperanto/ 

Windows Minimum System Recommendation:
DDR4 or DDR5 RAM: 64gb+ 3600 MT/s
Dedicated Graphics Card: RTX Quadro P4000 or GeForce RTX 3070 or similar at least 8gb+ VRM models (NVIDIA)
CPU: Intel or AMD at least: Intel Core i5-8400, AMD Ryzen 5 2600




Package Install:
The Repository contains a complete package list. Please perform PIP install for required and imported package versions as indicated in my_current_env_list.txt and script (3D) or FLIP. 


Source Code Listed Here Converts .STL file to .HTML for 3D interacitve view, and FLIP source code combines Fiji(Just Image J) ROI_1, ROI_2, ROI_3 Nucleus and Control quantifications to yield given plots. 

Guidelines:
Download the .stl file in Demo_File_3D folder
Place file in a folder anywhere that is easily availalbe later. 
Install the envrionment as guided by .yml file or by VS code erros. 
Download 3D_SuperRes_HTML.py - this is the main executable that can be opened in VS Code or PyCharm, it is a safe file for download. 
The file has to be first opened in VS Code or Pycharm with Proper Python Interpreter (this is the Environment, 3.9 Python Base that should be installed from .yml file) - For example, Microscopy_Analysis_Advanced2 (My Current Environment). 

<img width="1729" height="1129" alt="image" src="https://github.com/user-attachments/assets/eb2c4999-1b95-487e-beab-8c28eec1ffdb" />
Output Example:
<img width="3683" height="1639" alt="image" src="https://github.com/user-attachments/assets/25977eb8-80b3-45d8-8feb-64b579b17531" />


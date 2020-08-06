INFOBAR is a GUI tool to impletment ICA-AROMA, especially useful for processing large datasets and performing quality checks on the data.
## Installation

1. Extract contents of INFOBAR.zip to the local ICA-AROMA-master folder. 
2. Alternatively, extract the contents to any desired location. Upon first run, go to Settings and select the ICA-AROMA location in the panel, then click save. This will save the default configuration.

## Usage

The software is written in Python 3 and can be launched from a bash prompt. To start the software, open up a terminal and type: 

`python3 <path_to_file>/INFOBAR.py`

The software searches for `.feat` folders generated after pre rpocessing through FSL. 

In the main window, there are options to select the Database location, Search using task/dataset names, and Filter using additional strings.

1. To start, click the `Database` button and selecting the root directory of your database.

2. Click `Search` to search for all .feat folders in the root directory.
    
3. Type in a task name and click `Search` to search for a specific task/dataset name.
4. Type in filters to narrow search based on subjects/ groups etc.
5. To process all  subjects shown in the display panel, click `Process`.
6. Alternatively, select the datasets to be processed. Press `ctrl` to select multiple datasets. Click `Process` to process selected subjects. Click `Clear` to clear selection. 
7. Left click on a dataset to view *MCFLIRT rotation*, *translation* and *displacement* plots.
8. Right click on a dataset to view *zstat1 lightbox image* and *peak voxel activation model fit*.
       
## Preprocessing steps
INFOBAR requires the data to be processed through FSL. Preprocessing involves:
1. Motion correction
2. 4D mean intensity normalization
3. Spatial smoothing (6mm FWHM)

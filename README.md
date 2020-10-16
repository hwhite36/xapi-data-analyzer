# xapi-data-analyzer
This program was originally created by Walt Boettge and Harrison White, working under Dr. John Moore at the University 
of Wisconsin-Madison Department of Chemistry.

It was created with the goal of parsing and analyzing xAPI data created from H5P elements embedded within the CHEM 109 
Pressbooks online textbook. The program relies on the data being present as an exported .csv file from the UW-Madison 
Learning Locker (in the "raw" format).


## Installation
### For users:
Simply download the latest `xAPI Data Analyzer.exe` file and double-click it to launch the program. 

You may get a popup from Windows on your first launch warning about a potential security risk -- this is because the 
.exe is not signed by a registered Microsoft developer. Always exercise caution when running any unknown executables, 
but if you trust the source of the executable, proceed to run it.

### For developers: 
Clone the repository and navigate to the root directory.

To use the program, simply run `xapi_data_analyzer/Main.py`. The program depends on the following libraries, which must be installed for it to run:

* `pandas`
* `pysimplegui`
* `matplotlib`

#### Creating an executable
To create an executable, install PyInstaller (`pip install pyinstaller`) and run the following command in the same 
directory as `Main.py`:

`pyinstaller -wF Main.py`

This will create a standalone executable file named `Main` in the `dist` folder under the current directory 
(for whatever operating system you run the command on). This allows end users to run your program without having Python 
or any of the third-party libraries installed!

Do note that PyInstaller only works with up to Python 3.7. There is also currently a bug between the latest version of matplotlib
and PyInstaller, so you need to have matplotlib 3.0.3 installed (`pip install matplotlib==3.0.3`) to successfully create an exe.


## Usage
### Data CSV input
The first thing the program asks you to do is to select the .csv file containing the raw data from the DoIT Learning Locker.
Click the top "Browse" button and select the appropriate file. 

If you're using the JSON input (more on that below), it's recommended that this data be cumulative from the start of the
semester for maximum data output. __Add screenshot once GUI design finalized!__

#### A note on data format
The program looks for the following columns in the spreadsheet (in any order):

* `Email`
    * contains email addresses prefaced by `mailto:`
* `Verb`
    * contains H5P ID verbs, such as "interacted", "answered", etc
* `object id`
    * contains web links to H5P elements
* `Question/Slide`
    * contains names of H5P elements
* `Timestamp`
    * contains standard-format timestamps of interactions
* `Duration`
    * contains the seconds that someone spends interacting with an element (unreliable, but can still be helpful)

The raw data *should* already be in an appropriate format, but it's important to note that **the tool requires that these columns
exist with these exact names!**

### JSON input/ID list
The next part of the program gives you a choice: you can either choose a JSON file that maps H5P elements to "Days" in the
CHEM 109 textbook, or you can enter your own list of H5P IDs to analyze.

#### The recommended way: JSON input
Click the second "Browse" button and select the provided `DayElement.json` file. This file automatically tells the program
which H5P IDs correspond to which "Days" in the CHEM 109 curriculum, so the program can output data grouped by Day. __Add screenshot once GUI design finalized!__

If you select a JSON file, please leave the H5P ID list input blank.

#### For advanced users: enter your own H5P ID list
If you know the exact H5P IDs you want data on, enter their numbers as a comma-separated list into the H5P ID list input. __Add screenshot once GUI design finalized!__

### Running the tool
After you either select the JSON file or enter your H5P IDs, press the green "Go" button to run the program. __Add screenshot once GUI design finalized!__

Depending on the size of the data .csv, the tool may take a couple minutes to run.

After the program finishes, a popup will appear informing you that the data has been successfully analyzed.

The program saves all of the CSVs and graphs in a folder titled `xAPI-Data-Analyzer_$TIMESTAMP/`, which resides in the
directory that you executed the program. If you used the JSON input, there will be a folder for each Day within the main folder,
and each Day folder will contain a csv for the Day's data and student durations, as well as corresponding graphs saved as PNGs.
If you input your own list, the main folder will just contain one data csv, one student durations csv, and the corresponding graphs. __Add screenshot once GUI design finalized!__

Note: the timestamp is generated based on Central Time (US).

## License
This package is licensed under the MIT License. The full license text is available in LICENSE in the root directory.
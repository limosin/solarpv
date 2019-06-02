## Photovoltaic Solar Power Plant Performance model

### Steps to run the scripts-
- Clone the repository or download the zip file.
`git clone https://github.com/limosin/solarpv`
1. Copy weather data file, lets say `kota.csv` to the main folder.
2. Navigate to src folder. Run the weather_script.py file, passing weather file name as argument.<br>
      `python weather_script.py kota`
3. Once completed, you can remove the original copied weather data file.
4. Copy the solar data file to data/solar/ folder which will be created after the second step.
5. Run the match_time.py script from src folder.<br>
      `python match_time.py`
6. Make changes according to the plant configuration to `config.json` inside the data folder.
7. Now you can use the model.ipynb Ipython Notebook for viewing the analysis.

## Update: GUI Support

<p>To make experimenting easier, I have added a GUI support which lets you change the important parameters on the fly and visualize the changes in the app itself. The App has been made using Tkinter, hence does not have the best of the visuals
      
__Requirements__
1. Tkinter
2. os
3. json
4. pandas
5. matplotlib

###
__How to Run??__
1. Simply run `python App.py`
2. Browse the weather and solar data files. The app might take a few seconds to load.
3. Enter all the values, or simply click `Load Json` to load from the `data/config.json` file. This will automatically fill all the fields depending on the values in the json file.
4. Check for any missing field(Will happend automatically in further releases ;) ). Then Click Run Configurations Button.
5. Press the button  again if you wish to simulate for some other values.
6. Quit using the `Quit` button. 

### Main Window
![Main Window](/media/gui_main.png)

### On running the Configs
__NOTE__ : There are three __tabs__, showing the current, voltage and power graphs individually.
![Main Window](/media/gui_run1.png)

### Zooming and Maximizing
![Main Window](/media/gui_run2.png)
      
### Known Issues
- Currently using the high-level api for calculating the model output, which is quite inaccurate.
- The GUI on pressing the `Run Configurations` button goes blank, and returns back when the simulation finishes.
- Lots of knitty-gritty improvements required.
- Changing the value in tilt entry does not changes the slider location, while reverse happens.
- SaveAs Json button does not work right now.
- Directly closing the app from the windows close button does not terminate the app.

More features can be added as and when required and possible.
